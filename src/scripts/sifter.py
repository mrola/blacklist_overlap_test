#!/usr/bin/env python3

import os
import re
import sys
import time
import socket
import logging
import itertools
import configparser
import requests as req
from os.path import expanduser

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

home = expanduser("~")

# Path to config file
path_config = home + '/projs/blacklist_overlap_test/src/config/sifter.conf'

# Pandas - global display options
pd.set_option('display.width', 120)
pd.set_option('max_colwidth', 0)

# Seaborn - plot options
sns.set()
sns.set(style="whitegrid", rc={"figure.figsize": (14, 8)})
sns.set_palette("bone")


class Common:
    ''' Checking if date is set is done from multiple places so
        putting the check in a separare class that may be inhereted by others. '''

    def set_date(self):
        DATE = ReadConf().retrieve('get', 'misc', 'DATE')
        if DATE:
            return DATE
        else:
            return(time.strftime("%Y-%m-%d"))


class ReadConf():
    def __init__(self):
        self.logger = logging.getLogger("ReadConf")
        self.confparse = configparser.ConfigParser(delimiters=['='])
        try:
            self.confparse.read(path_config)
        except Exception as e:
            self.logger.error("Failed attempt to read config at %s: %s" % (path_config, e))
            sys.exit('Failed to read conf. Abort.')

    def retrieve(self, method, section, key=None):
        ''' Retrieves conf settings '''
        try:
            if method == 'get':
                return self.confparse.get(section, key)
            elif method == 'items':
                return self.confparse.items(section)
            elif method == 'getboolean':
                return self.confparse.getboolean(section, key)
        except Exception as e:
            self.logger.error("Failed to access conf values: %s" % e)


class GetData(Common):
    def __init__(self):
        self.logger = logging.getLogger("GetData")
        self.cols = ["entity", "type", "direction", "source", "notes", "date"]
        self.df = pd.DataFrame(columns=self.cols)
        self.ipv4 = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    def do_pandas(self, ips, name):
        '''
        Takes a list of IPv4 addresses as input and stores those in a Pandas DataFrame.
         DataFrame columns: "entity","type","direction","source","notes","date"

         "1.234.27.146","IPv4","inbound","http://malc0de.com/bl/IP_Blacklist.txt","","2016-01-27
         DATE is set to today, override this in Defaults section above if needed
        '''

        df_ips = pd.DataFrame()
        date = self.set_date()

        tup = (ips, 'IPv4', 'inbound', name, "", date)
        (df_ips['entity'], df_ips['type'], df_ips['direction'],
         df_ips['source'], df_ips['notes'], df_ips['date']) = tup
        self.df = self.df.append(df_ips, ignore_index=True)
        return self.df


    def valid_ip(self, address):
        ''' Checks if an IPv4 address is valid '''

        try:
            socket.inet_aton(address)
        except:
            self.logger.warning("WARNING: Invalid address: %s" % address)
            return False
        return True


    def parse_content(self, source):
        ''' Extract IPv4 address from a list of rows '''

        ips = []
        for line in source:
            m = re.search(self.ipv4, line.decode('utf-8'))
            if m:
                address = m.group(0)
                if self.valid_ip(address):
                    ips.append(address)
        if ips:
            return ips
        else:
            return False


    def get_url(self, urls):
        ''' Fetch blacklist feeds from urls (as defined in inbound_urls) '''

        fail_count = 0
        timeout = int(ReadConf().retrieve('get', 'misc', 'TIMEOUT'))
        for desc, url in iter(urls.items()):
            self.logger.info('Fetching: %s' % url)
            try:
                r = req.get(url, timeout=timeout)
                if r.status_code == 200:
                    self.logger.info('Got status 200 back...')
                    ips = self.parse_content(r.content.splitlines())
                    if ips:
                        self.df = self.do_pandas(ips, desc)
                    else:
                        self.logger.warning(' WARNING: Found no valid ipv4 addresses.')
                else:
                    self.logger.warning(' WARNING: Got status %d' % r.status_code)
            except req.ConnectionError as e:
                self.logger.error(' ERROR: Failed to fetch url due connectivity issues.')
                self.logger.error(' Error msg: %s' % e)
                fail_count += 1
                if fail_count > 2:
                    self.logger.error('Connectivity issues assumed to be permanent. Will abort.')
                    break
            except Exception as e:
                self.logger.error(' ERROR: Failed to fetch url: %s' % e)
        return self.df



    def get_prefetched(self, files, indata_path):
        ''' Read files defined in the "inbound_prefetched" dictionary.  '''

        self.logger.info('Reading data:')
        for desc, filen in iter(files.items()):
            filen = indata_path + filen
            if not os.path.exists(filen):
                self.logger.info(' WARNING: Failed to read data from: %s...' % filen)
            else:
                try:
                    self.logger.info('%s...' % (filen))
                    with open(filen, 'rb') as f:
                        ips = self.parse_content(f.readlines())
                        if ips:
                            self.df = self.do_pandas(ips, desc)
                        else:
                            self.logger.warning(' WARNING: Failed to find valid entries.')
                except Exception as e:
                    self.logger.error(' ERROR: Caught exception: %s Abort...' % e)
                    break
        return self.df



class PlotData(Common):
    def __init__(self, df):
        self.logger = logging.getLogger("PlotData")
        self.df = df

    def fill_heatmap(self, cols, dfp, df_heat):
        '''
        Calculate proportion of items in intersection between two blacklists to each blacklist per se.
         dfp: contains data for calculations.
         df_heat: put results in this frame.
         cols: pair of columns (blacklists) used as input to calculations.
        '''

        s = dfp.eq(dfp[cols[0]], axis='index')[cols].all(1)
        common = s[s.values == True].count()

        col0_sum = dfp[cols[0]].sum()
        col1_sum = dfp[cols[1]].sum()

        df_heat[cols[0]].loc[cols[1]] = common/col0_sum
        df_heat[cols[1]].loc[cols[0]] = common/col1_sum


    def do_heatframes(self):
        '''
        Create frames used in calculation of overlap.
         dfp: DataFrame with ipv4 as index and blacklist as columns. Used to find entries in common
         df_heat: DataFrame that will contain the actual overlap values
         colpairs: list of 2-tuples where each tuple contains a unique pair of blacklists
        '''

        self.df['one'] = 1
        dfp = pd.pivot_table(self.df, values='one', index=['entity'], columns=['source'])

        df_heat = pd.DataFrame({'contains': pd.unique(self.df.source),
            'is contained': pd.unique(self.df.source)})
        df_heat['diag'] = 1
        df_heat = df_heat.pivot('contains','is contained', 'diag')

        colpairs = itertools.combinations(pd.unique(self.df.source), 2)
        for colpair in colpairs:
            self.fill_heatmap(list(colpair), dfp, df_heat)
        return df_heat


    def plot_counts(self):
        ''' Barchart showing size of each blacklist feed '''

        fig, ax = plt.subplots()
        sns.set(style="whitegrid", font_scale=1.1, rc={"figure.figsize": (14, 4)})
        ax = sns.countplot(y="source", data=self.df.sort_index(axis=1, 
            ascending=False), palette="bone")
        ax.set(title="Barplot showing the count of entries per source - %s\n" % 
                (self.set_date()))
        return fig


    def plot_heat(self):
        ''' Heatmap showing the overlap between blacklist feeds '''

        annotate = ReadConf().retrieve('getboolean', 'bools', 'ANNOTATE')
        df_heat = self.do_heatframes()
        fig, ax = plt.subplots()
        ax = sns.heatmap(df_heat, linewidths=.5, annot=annotate, cmap="bone")
        ax.set(title="Overlap test - heatmap showing overlap between blacklists - %s\n" %
               (self.set_date()))
        plt.xticks(rotation=40, horizontalalignment='right')
        plt.yticks(rotation=0)
        return fig


class WrapItUp(Common):
    def __init__(self, df, dir_output):
        self.logger = logging.getLogger("WrapItUp")
        self.df = df
        self.path= dir_output
        self.doit()

    def show_info(self):
        ''' Print some info to verify result '''

        self.logger.info('Verify we got all sources:\n%s\n' %
                         pd.Series(pd.unique(self.df.source)))
        self.logger.info('First few frame rows:\n%s\n' % self.df.head())
        self.logger.info('Frame contains %d entries.\n' % self.df.shape[0])


    def save_data(self, data, dtype, ext, desc):
        ''' Write to disk '''

        save = ReadConf().retrieve('getboolean', 'bools', 'SAVE')
        if save:
            date = self.set_date()
            udate = date.replace('-', '')
            savepath = self.path + desc + '_' + udate + ext
            if not os.path.exists(self.path):
                self.logger.warning("Failed to find path: %s" % self.path)
                self.logger.warning("Setting path to '/tmp/'")
                savepath = '/tmp/' + desc + '_' + udate + ext
            self.logger.debug("Attempting to save data...")
            try:
                if dtype == 'frame':
                    self.df.to_csv(savepath, index=False)
                if dtype == 'fig':
                    data.savefig(savepath, bbox_inches='tight', pad_inches=1)
                self.logger.info("Successfully saved data to: %s" % savepath)
            except Exception as e:
                self.logger.error("ERROR: %s" % e)

    def doit(self):
        ''' Delegates the main tasks '''

        if self.df.values.size > 0:
            self.show_info()
            self.save_data(self.df, 'frame', '.csv', 'raw')
            plotdata = PlotData(self.df)
            barplot = plotdata.plot_counts()
            self.save_data(barplot, 'fig', '.png', 'barchart')
            if (len(pd.unique(self.df.source)) > 1):
                heatplot = plotdata.plot_heat()
                self.save_data(heatplot, 'fig', '.png', 'heatmap')
            else:
                self.logger.info("Only got a single blacklist feed. No overlap to display.")
        else:
            self.logger.info("WARNING: Got empty data frame...")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s:%(name)s: %(message)s', 
            stream=sys.stdout)
    logger = logging.getLogger("main")
    logger.info("------------------++++++++BEGIN+++++++++++----------------------")

    readconf = ReadConf()
    base = readconf.retrieve('get', 'path','base')

    inbound_prefetched = dict(readconf.retrieve('items', 'inbound_prefetched'))
    inbound_prefetched_test = dict(readconf.retrieve('items', 'inbound_prefetched_test'))

    inbound_urls = dict(readconf.retrieve('items', 'inbound_urls'))
    inbound_urls_test = dict(readconf.retrieve('items', 'inbound_urls_test'))

    DIR_OUTPUT_URL = home + base + readconf.retrieve('get', 'path', 'out_url')
    DIR_OUTPUT_PREFETCHED = home + base + readconf.retrieve('get',  'path', 'out_prefetched')
    DIR_INPUT_PREFETCHED = home + base + readconf.retrieve('get', 'path', 'in_prefetched')

    get_urls = readconf.retrieve('getboolean', 'bools', 'GET_URLS')
    read_prefetched = readconf.retrieve('getboolean', 'bools', 'READ_PREFETCHED')

    if get_urls:
        logger.info(">>>> Fetching public inbound blacklisted IPv4 addresses from URLs <<<<")
        df = GetData().get_url(inbound_urls)
        WrapItUp(df, DIR_OUTPUT_URL)

    if read_prefetched:
        logger.info(">>>> Fetching private inbound blacklisted IPv4 addresses from disk <<<<")
        df = GetData().get_prefetched(inbound_prefetched, DIR_INPUT_PREFETCHED)
        WrapItUp(df, DIR_OUTPUT_PREFETCHED)

    logger.info('Done!\n\n')

if __name__ == '__main__':
    main()
