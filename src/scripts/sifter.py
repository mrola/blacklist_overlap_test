#!/usr/bin/env python3

import os
import re
import sys
import time
import socket
import logging
import platform
import itertools
import requests as req
from os.path import expanduser

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt



# Today is used as date unless DATE is set here, format"YYYY-MM-DD"
DATE = None

# If True, save data to DIR_OUTPOUT_* as defined below
SAVE = False

# GET_URLS=True means that ioc data is fetched from public/internet sources, see inbound URLs section
GET_URLS = True

# READ_PREFETCH=True means that ioc data is fetched from private/local files, see Prefetched section
READ_PREFETCH = True

# TIMEOUT - number of seconds Requests will wait for a response from the server (both connect and between reads)
TIMEOUT = 4

# ANNOTATE - Set to True if actual value should be written in each heatmap cell
ANNOTATE=True

# Paths
home = expanduser("~")
base = '/projs/blacklist_overlap_test/data/raw'
DIR_OUTPUT_URL = home + base + '/public_inbound/from_url/'
DIR_OUTPUT_PREFETCHED = home + base + '/private_inbound/prefetched/output/'
DIR_INPUT_PREFETCHED = home + base + '/private_inbound/prefetched/input/'

# Pandas - global display options
pd.set_option('display.width', 120)
pd.set_option('max_colwidth', 0)

# Seaborn - plot options
sns.set()
sns.set(style="whitegrid", rc={"figure.figsize": (14, 8)})
sns.set_palette("bone")
sns.palplot(sns.color_palette())


# Key: URL to be fetched
# Value: Description of source.

inbound_urls = {
    'http://www.malwaredomainlist.com/hostslist/ip.txt': 'malwaredomainlist_ip.txt',
    'http://malc0de.com/bl/IP_Blacklist.txt': 'malc0de_IP_Blacklist.txt',
    'http://www.openbl.org/lists/base.txt': 'openbl.org_base.txt',
    'http://lists.blocklist.de/lists/all.txt': 'blocklist.de_all.txt',
    'https://reputation.alienvault.com/reputation.generic': 'alienvault_reputation.generic',
    'http://rules.emergingthreats.net/blockrules/compromised-ips.txt': 'emergingthreats_compromised-ips.txt',
    'http://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt': 'emergingthreats_emerging-Block-IPs.txt',
    'https://zeustracker.abuse.ch/blocklist.php?download=badips': 'zeustracker_blocklist_badips',
    'https://palevotracker.abuse.ch/blocklists.php?download=ipblocklist': 'palevotracker_blocklists_ipblocklist',
    'https://feodotracker.abuse.ch/blocklist/?download=ipblocklist': 'feodotracker_blocklists_ipblocklist',
    'https://feodotracker.abuse.ch/blocklist/?download=badips': 'feodotracker_blocklists_badips',
    'http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv': 'blutmagie_Tor_ip_list_EXIT',
    'http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv': 'blutmagie_Tor_ip_list_ALL'
}

inbound_urls_test = {
    'http://www.malwaredomainlist.com/hostslist/ip.txt': 'malwaredomainlist_ip.txt',
    'http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv': 'torstatus_Tor_ip_list_ALL',
    'http://malc0de.com/bl/IP_Blacklist.txt': 'malc0de_IP_Blacklist.txt',
    'http://www.openbl.org/lists/base.txt': 'openbl.org_base.txt',
    'http://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt': 'emergingthreats_emerging-Block-IPs.txt'
}



inbound_prefetched = {
    DIR_INPUT_PREFETCHED + 'compromised-ips.ioc': 'compromised-ips.ioc',
    DIR_INPUT_PREFETCHED + 'ips.ioc': 'ips.ioc',
    DIR_INPUT_PREFETCHED + 'zeus_ipblocklist.ioc': 'zeus_ipblocklist.ioc'
}

inbound_prefetched_test = {
    DIR_INPUT_PREFETCHED + 'compromised-ips.ioc': 'compromised-ips.ioc',
    DIR_INPUT_PREFETCHED + 'compromised-ips_test.ioc': 'compromised-ips_test.ioc',
    DIR_INPUT_PREFETCHED + 'zeus_ipblocklist.ioc': 'zeus_ipblocklist.ioc',
    DIR_INPUT_PREFETCHED + 'zeus_ipblocklist_test.ioc': 'zeus_ipblocklist_test.ioc'
}


class Common:

    def set_date(self):
        if DATE:
            return DATE    
        else:
            return(time.strftime("%Y-%m-%d"))


class GetData(Common):
    def __init__(self):
        self.cols = ["entity","type","direction","source","notes","date"]
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

        tup = (ips, 'IPv4', 'inbound',name, "", date)
        (df_ips['entity'], df_ips['type'], df_ips['direction'], \
             df_ips['source'], df_ips['notes'], df_ips['date']) = tup 
        self.df = self.df.append(df_ips, ignore_index=True)
        return self.df


    def valid_ip(self, address):
        '''
        Checks if an IPv4 address is valid
        '''
        logger = logging.getLogger("GetData.valid_ip")
        try: 
            socket.inet_aton(address)
        except:
            logger.warning("WARNING: Invalid address: %s" % address)
            return False
        return True


    def parse_content(self, source):
        '''
        Extract IPv4 address from a list of rows
        '''
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
        '''
        Fetch blacklist feeds from urls (as defined in inbound_urls)
        '''
        logger = logging.getLogger("GetData.get_url")
        fail_count = 0
        for url, name in iter(urls.items()):
            logger.info('Fetching: %s' % url)
            try:
                r = req.get(url, timeout=TIMEOUT)
                if r.status_code == 200:
                    logger.info('Got status 200 back...')
                    ips = self.parse_content(r.content.splitlines())
                    if ips:
                        self.df = self.do_pandas(ips, name)
                    else:
                        logger.warning(' WARNING: Found no valid ipv4 addresses.')
                else:
                    logger.warning(' WARNING: Got status %d' % r.status_code)
            except req.ConnectionError as e:            
                logger.error(' ERROR: Failed to fetch url due connectivity issues.')
                logger.error(' Error msg: %s' % e)
                fail_count += 1
                if fail_count > 2:
                    logger.error('\nConnectivity issues assumed to be permanent. Will abort.')
                    break
            except Exception as e:
                logger.error(' ERROR: Failed to fetch url.\nError msg: %s' % e)
        return self.df



    def get_prefetched(self, files):
        '''
        Read files defined in the "inbound_prefetched" dictionary.
        '''
        dflist = []
        print('Reading data:')
        for filen, description in iter(files.items()):
            if not os.path.exists(filen): 
                print(' WARNING: Failed to read data from:\n\t%s...' % filen) 
            else:
                try: 
                    print('%s...' % (filen)) 
                    with open(filen, 'rb') as f:
                        ips = self.parse_content(f.readlines())
                        if ips:
                            self.df = self.do_pandas(ips, description)
                        else:
                            print(' WARNING: Failed to find valid entries.')
                except Exception as e:
                    print(' ERROR: Caught exception: %s\nAbort...' % e)
                    break
        return self.df



class PlotData(Common):
    def __init__(self, df):
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

        df_heat = pd.DataFrame({'contains': pd.unique(self.df.source), 'is contained': pd.unique(self.df.source)})
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
        ax = sns.countplot(y="source", data=self.df.sort_index(axis=1, ascending=False), palette="bone");
        ax.set(title="Barplot showing the count of entries per source - %s\n" % (self.set_date()));
#        fig.savefig("testing.png", bbox_inches='tight', pad_inches=1)
#        plt.show()


    def plot_heat(self):
        ''' Heatmap showing the overlap between blacklist feeds '''
        df_heat = self.do_heatframes()

        fig, ax = plt.subplots()
        ax = sns.heatmap(df_heat, linewidths=.5, annot=ANNOTATE, cmap="bone");    
        ax.set(title="Overlap test - heatmap showing overlap between blacklists - %s\n" % (self.set_date()))
        plt.xticks(rotation=40, horizontalalignment='right');
        plt.yticks(rotation=0);
#        fig.savefig("testing.png")
        fig.savefig("testing.png", bbox_inches='tight', pad_inches=1)
#        plt.show()



class WrapItUp(Common):
    def __init__(self, df, dir_output):
        self.df = df
        self.path= dir_output
        self.doit()

    def show_info(self):  
        ''' Print some info to verify result '''
        print('\n>> General info to verify everything is ok <<')
        print('\nVerify we got all sources:\n%s\n' % pd.Series(pd.unique(self.df.source)))
        print('First few frame rows:\n%s\n' % self.df.head())
        print('Frame contains %d entries.\n\n' % self.df.shape[0])   

    def save_frame(self):
        ''' Write to .csv '''
        date = self.set_date()
        udate = date.replace('-', '')
        savepath = self.path + udate + '.csv'
        if not os.path.exists(self.path):
            print("Failed to find path: %s" % self.path)
            print("Setting path to '/tmp/'")
            savepath = '/tmp/' + udate + '.csv'
        print("Attempting to save frame...")
        try:
            self.df.to_csv(savepath, index=False)
            print("Successfully saved frame to:\n\t%s" % savepath)
        except Exception as e:
            print("ERROR: %s\n" % e)

    def doit(self):
        '''
        '''
        if self.df.values.size > 0:
            self.show_info()
            plotdata = PlotData(self.df)
            barplot = plotdata.plot_counts()
            if (len(pd.unique(self.df.source)) > 1):
                print("\n\n")
                heatplot = plotdata.plot_heat()
            else:
                print("Only got a single blacklist feed. No overlap to display.")
            if SAVE:
                self.save_frame()
        else:
            print("WARNING: Got empty data frame...")
    
        print('\nDone!\n\n')



def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s:%(name)s: %(message)s', stream=sys.stdout)
    logger = logging.getLogger("main")
    logger.info("------------------++++++++BEGIN+++++++++++----------------------")
    
    getdata = GetData()

    if GET_URLS:
        logger.info("\n\n>>>> Fetching public inbound blacklisted IPv4 addresses from URLs <<<<\n")
        df = getdata.get_url(inbound_urls_test)
        wrapitup = WrapItUp(df, DIR_OUTPUT_URL)
        
    if READ_PREFETCH:
        logger.info("\n\n>>>> Fetching private inbound blacklisted IPv4 addresses from disk <<<<\n")
        df = getdata.get_prefetched(inbound_prefetched)
        wrapitup = WrapItUp(df, DIR_OUTPUT_PREFETCHED)

if __name__ == '__main__':
    main()
