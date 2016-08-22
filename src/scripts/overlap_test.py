#!/usr/bin/env python

import os
import re
import sys 
import time
import gzip
import socket
import logging
import itertools
import configparser
import requests as req

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

# Path to config file
path_script = sys.path[0]
path_config = path_script + '/../config/overlap_test.conf'
datadir = path_script + '/../../data/'

# Pandas - global display options
pd.set_option('display.width', 120)
pd.set_option('max_colwidth', 0)

# Seaborn - plot options
sns.set()
sns.set(style='whitegrid', rc={'figure.figsize': (14, 8)})
sns.set_palette('bone')

# Suppress INFO log messages from requests lib
logging.getLogger('requests').setLevel(logging.WARNING)


class Common:
    """ Checking if date is set is done from multiple places so
    putting the check in a separare class that may be inhereted by others. 
    """
    def __init__(self):
        self.logger = logging.getLogger('Common')
    

    def set_date(self):
        DATE = ReadConf().retrieve('get', 'misc', 'DATE')
        if DATE:
            return DATE
        else:
            return(time.strftime('%Y-%m-%d'))

    def dumper(self, dumppath, content, msg, mode):
        """ Saves utf-8 decode failure to tmpdir (set in conf). 
        Saves raw content of url:s to tmpdir if DUMP is True. 
        """
        try:
            with gzip.open(dumppath, mode) as f:
                f.write(content)
                self.logger.debug("Successfully saved %s to %s" % (msg, dumppath))
        except Exception as e:
            self.logger.error("Failed to dump %s to %s: %s" % (msg, dumppath, e))
            pass


class ReadConf:
    def __init__(self):
        self.logger = logging.getLogger('ReadConf')
        self.confparse = configparser.ConfigParser(allow_no_value=True, delimiters=['='])
        try:
            self.confparse.read(path_config)
        except Exception as e:
            self.logger.error('Failed attempt to read config at %s: %s' % (path_config, e))
            sys.exit('Abort!')


    def retrieve(self, method, section, key=None):
        """ Retrieves conf settings """

        try:
            if method == 'get':
                return self.confparse.get(section, key)
            elif method == 'items':
                return self.confparse.items(section)
            elif method == 'getboolean':
                return self.confparse.getboolean(section, key)
        except Exception as e:
            self.logger.error('Failed to access conf values: %s' % e)
            sys.exit('Abort!')


class GetData(Common):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('GetData')
        self.cols = ['entity', 'type', 'direction', 'source', 'notes', 'date']
        self.df = pd.DataFrame(columns=self.cols)
        self.ipv4 = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

        self.readconf = ReadConf()
        self.TEST = self.readconf.retrieve('getboolean', 'bools', 'TEST')
        self.DUMP = self.readconf.retrieve('getboolean', 'bools', 'DUMP')
        self.do_url = kwargs.get('do_url') 
        self.do_prefetched = kwargs.get('do_prefetched')
        self.path_tmp = self.readconf.retrieve('get', 'path', 'tmpdir')
        self.debug = self.readconf.retrieve('get', 'loglevel', 'LEVEL')
        self.getdata()

    def getdata(self):
        """ Fetches dict with url:s or files from conf and calls get_url() or get_prefetched(). """

        if self.do_url is True:
            self.inbound_urls = dict(self.readconf.retrieve('items', 'inbound_urls'))
            if self.TEST is True:
                self.inbound_urls = dict(self.readconf.retrieve('items', 'inbound_urls_test'))
            self.df = self.get_url(self.inbound_urls)

        if self.do_prefetched is True:
            self.inbound_prefetched = dict(self.readconf.retrieve('items', 'inbound_prefetched'))
            if self.TEST is True:
                self.inbound_prefetched = dict(self.readconf.retrieve('items', 'inbound_prefetched_test'))
            self.indata_path = datadir + self.readconf.retrieve('get', 'path', 'in_prefetched')
            self.df = self.get_prefetched(self.inbound_prefetched, self.indata_path)

    def do_pandas(self, ips, name):
        """ Takes a list of IPv4 addresses as input and stores those in a Pandas DataFrame.
         DataFrame columns: 
         'entity','type','direction','source','notes','date'
        '1.234.27.146','IPv4','inbound','http://malc0de.com/bl/IP_Blacklist.txt','','2016-01-27

         DATE is set to today, override this in config if needed.
        """

        df_ips = pd.DataFrame()
        date = self.set_date()

        tup = (ips, 'IPv4', 'inbound', name, '', date)
        (df_ips['entity'], df_ips['type'], df_ips['direction'],
         df_ips['source'], df_ips['notes'], df_ips['date']) = tup
        self.df = self.df.append(df_ips, ignore_index=True)
        return self.df.drop_duplicates()


    def valid_ip(self, address):
        """ Checks if an IPv4 address is valid """

        try:
            socket.inet_aton(address)
        except:
            self.logger.warning('Invalid address: %s' % address)
            return False
        return True


    def parse_content(self, source):
        """ Extract IPv4 address from a list of rows """

        ips = []
        failcount = 0
        for line in source:
            try:
                m = re.search(self.ipv4, line.decode('utf-8'))
                if m:
                    address = m.group(0)
                    if self.valid_ip(address):
                        ips.append(address)
            except UnicodeDecodeError as e:
                failcount += 1
                if self.debug == 'DEBUG':
                    t = time.asctime()
                    msg = t + '; ' + str(e) + '; ' + str(line) + '\n'
                    mode = 'at'
                    dumppath = os.path.join(self.path_tmp, 'overlap_test_utf8_parse_failures.txt.gz')
                    self.dumper(dumppath, msg, "line", mode)
                pass
            except Exception as e:
                self.logger.error("Unexpected exception. Skipping line. %s" % e)
                pass
        if failcount > 0:
            self.logger.warning("Skipped %d lines due to utf-8 decode failures. Set logging mode to DEBUG to write decode failure lines to %s" % (failcount, self.path_tmp))
        if ips:
            return ips
        else:
            return False



    def get_url(self, urls):
        """ Fetch blacklist feeds from urls (as defined in inbound_urls) """

        self.logger.info('>>>> Fetching public inbound blacklisted IPv4 addresses from URLs <<<<')
        if self.DUMP:
            self.logger.info('DUMP is True so will dump raw contents to %s' % self.path_tmp)
        fail_count = 0
        timeout = int(self.readconf.retrieve('get', 'misc', 'TIMEOUT'))
        for desc, url in iter(urls.items()):
            self.logger.info('Fetching: %s' % url)
            try:
                r = req.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
                if r.status_code == 200:
                    self.logger.debug('Got status 200 back...')
                    ips = self.parse_content(r.content.splitlines())
                    if ips:
                        self.df = self.do_pandas(ips, desc)
                        if self.DUMP:
                            dumppath = os.path.join(self.path_tmp, desc + '.gz')
                            self.dumper(dumppath, r.text, "url content", "wt")
                    else:
                        self.logger.warning('Found no valid ipv4 addresses.')
                else:
                    self.logger.warning('Got status %d' % r.status_code)
            except req.ConnectionError as e:
                self.logger.error('Failed to fetch url due connectivity issues.')
                self.logger.error('Error msg: %s' % e)
                fail_count += 1
                if fail_count > 2:
                    self.logger.error('Connectivity issues assumed to be permanent. Will abort.')
                    break
            except Exception as e:
                self.logger.error('Failed to fetch url: %s' % e)
        return self.df



    def get_prefetched(self, files, indata_path):
        """ Read files defined in the inbound_prefetched dictionary.  """

        self.logger.info('>>>> Fetching private inbound blacklisted IPv4 addresses from disk <<<<')
        self.logger.info('Reading data...')
        for desc, filen in iter(files.items()):
            filen = os.path.join(indata_path, filen)
            if not os.path.exists(filen):
                self.logger.info('Failed to read data from: %s' % os.path.relpath(filen))
            else:
                try:
                    self.logger.info('%s' % (os.path.relpath(filen)))
                    with open(filen, 'rb') as f:
                        ips = self.parse_content(f.readlines())
                        if ips:
                            self.df = self.do_pandas(ips, desc)
                        else:
                            self.logger.warning('Failed to find valid entries.')
                except Exception as e:
                    self.logger.error('Caught exception: %s Abort...' % e)
                    break
        return self.df



class PlotData(Common):
    def __init__(self, df):
        self.logger = logging.getLogger('PlotData')
        self.df = df
        self.readconf = ReadConf()

    def fill_heatmap(self, cols, dfp, df_heat):
        """ Calculate proportion of items in intersection between two blacklists to each blacklist.

         dfp: contains data for calculations.
         df_heat: put results in this frame.
         cols: pair of columns (blacklists) used as input to calculations.
        """

        s = dfp.eq(dfp[cols[0]], axis='index')[cols].all(1)
        common = s[s.values == True].count()

        col0_sum = dfp[cols[0]].sum()
        col1_sum = dfp[cols[1]].sum()

        df_heat[cols[0]].loc[cols[1]] = common/col0_sum
        df_heat[cols[1]].loc[cols[0]] = common/col1_sum


    def do_heatframes(self):
        """ Create frames used in calculation of overlap.

         dfp: DataFrame with ipv4 as index and name of blacklists as columns. Used to find entries in common
         df_heat: DataFrame that will contain the actual overlap values
         colpairs: list of 2-tuples where each tuple contains a unique pair of blacklists
        """

        self.logger.info('Doing heatmap calculations...')
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
        """ Barchart showing size of each blacklist feed """

        gby = self.df.groupby(["source"])
        s = gby.size().sort_values(ascending=False)
        sns.set(style='whitegrid', font_scale=1.0, rc={'figure.figsize': (14, 4)})
        fig, ax = plt.subplots()
        ax = sns.barplot(orient='h', x=s, y=s.index, palette="bone")
        ax.set(title='Barplot showing the count of entries per source - %s\n' %
                (self.set_date()))
        return fig


    def plot_heat(self):
        """ Heatmap showing the overlap between blacklist feeds """

        annotate = self.readconf.retrieve('getboolean', 'bools', 'ANNOTATE')
        df_heat = self.do_heatframes()
        sns.set(style='whitegrid', font_scale=1.0, rc={'figure.figsize': (14, 4)})
        fig, ax = plt.subplots()
        asize = None
        if df_heat.shape[0] > 10:
            asize = {'size': 7}
        ax = sns.heatmap(df_heat, linewidths=.5, annot=annotate, fmt=".2g", annot_kws=asize, cmap='bone')
        ax.set(title='Overlap test - heatmap showing overlap between blacklists - %s\n' %
               (self.set_date()))
        plt.xticks(rotation=40, horizontalalignment='right')
        plt.yticks(rotation=0)
        return fig


class WrapItUp(Common):
    def __init__(self, df, action, path_output):
        self.logger = logging.getLogger('WrapItUp')
        self.df = df
        self.action = action
        self.path = path_output

        self.readconf = ReadConf()
        self.TEST = self.readconf.retrieve('getboolean', 'bools', 'TEST')
        self.save = self.readconf.retrieve('getboolean', 'bools', 'SAVE')
        self.path_tmp = self.readconf.retrieve('get', 'path', 'tmpdir')
        if self.action:
            self.doit()

    def show_info(self):
        """ Print some info to verify result """

        self.logger.info('Verify we got all sources:\n%s\n' %
                         pd.Series(pd.unique(self.df.source)))
        self.logger.info('First few frame rows:\n%s\n' % self.df.head())
        self.logger.info('Frame contains %d entries.\n' % self.df.shape[0])


    def save_data(self, data, dtype, ext, desc):
        """ Write to disk """

        if self.save:
            date = self.set_date()
            udate = date.replace('-', '')
            savepath = os.path.join(self.path, desc + '_' + udate + ext)
            if self.TEST is True:
                savepath = os.path.join(self.path_tmp, desc + '_' + udate + ext)
            elif not os.path.exists(self.path):
                self.logger.warning('Failed to find path: %s' % self.path)
                self.logger.warning('Setting base dir to %s' % self.path_tmp)
                savepath = os.path.join(self.path_tmp, desc + '_' + udate + ext)
            self.logger.debug('Attempting to save data...')
            try:
                if dtype == 'frame':
                    savepath = savepath + '.gz'
                    self.df.to_csv(savepath, index=False, encoding='utf-8', compression='gzip')
                if dtype == 'fig':
                    data.savefig(savepath, bbox_inches='tight', pad_inches=1)
                self.logger.info('Successfully saved data to: %s' % os.path.relpath(savepath))
            except Exception as e:
                self.logger.error('%s' % e)

    def doit(self):
        """ Delegates the main tasks """

        if self.df.values.size > 0:
            self.show_info()
            if self.TEST is True:
                self.logger.info('TEST is True so setting base dir to \'/tmp/\'')
            self.save_data(self.df, 'frame', '.csv', 'raw')
            plotdata = PlotData(self.df)
            barplot = plotdata.plot_counts()
            self.save_data(barplot, 'fig', '.png', 'barchart')
            if (len(pd.unique(self.df.source)) > 1):
                heatplot = plotdata.plot_heat()
                self.save_data(heatplot, 'fig', '.png', 'heatmap')
            else:
                self.logger.info('Only got a single blacklist feed. No overlap to display.')
        else:
            self.logger.info('Got empty data frame...\n')


def main():
    readconf = ReadConf()

    loglevels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR, 'critical': logging.CRITICAL}
    loglevel = readconf.retrieve('get', 'loglevel', 'LEVEL')
    lev = loglevels.get(loglevel.lower(), logging.NOTSET)

    logging.basicConfig(level=lev, format='%(asctime)s %(name)-14s: %(levelname)-8s %(message)s', stream=sys.stdout)
    logger = logging.getLogger('main')
    logger.info('------------------++++++++BEGIN+++++++++++----------------------')


    path_output_url = datadir + readconf.retrieve('get', 'path', 'out_url')
    path_output_prefetched = datadir + readconf.retrieve('get', 'path', 'out_prefetched')

    do_url = readconf.retrieve('getboolean', 'bools', 'GET_URLS')
    do_prefetched = readconf.retrieve('getboolean', 'bools', 'READ_PREFETCHED')

    gd = GetData(do_url = do_url)
    WrapItUp(gd.df, gd.do_url, path_output_url)

    gd = GetData(do_prefetched = do_prefetched)
    WrapItUp(gd.df, gd.do_prefetched, path_output_prefetched)

    logger.info('Done!\n\n')

if __name__ == '__main__':
    main()
