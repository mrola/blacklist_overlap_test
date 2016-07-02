
# Blacklist overlap test <img align="right", src="http://i.imgur.com/ln57AGi.png" width="386">

The blacklist overlap test provides a measure on the degree to which one feed is contained within some other feed. It is a metric that may be used to exclude blacklist feeds that is already contained in other feeds.

This project is inspired by the combine and tiq-test project (written in R) by [@alexcpsec](https://twitter.com/alexcpsec), [@kylemaxwell](https://twitter.com/kylemaxwell) and others. While the tiq-test project provides additional quality metrics and also supports enrichment, this project is pure Python and at this point only provides the overlap test. That said, if overlap test is the goal just running the Jupyter notebook or `overlap_test.py` will do the fetch data, extract IP addresses, calculate overlap between each pair, and build heatmap steps. It is designed to be standalone. 

If you prefer R and ggplot heatmaps you've probably stopped reading by now, if not there's an option to save a .csv file with a format that is expected by tiq.test. See [Importing into tiq-test](#tiq-test) for an example. However, if [Seaborn](http://stanford.edu/~mwaskom/software/seaborn/) is your prefered choise of visualisation library and you'd like to gain insight into degree of overlap between different feeds with minimal effort then please continue reading.


## Purpose
The purpose of this project is to provide a means to measure the degree to which blacklists overlap in terms of IPv4 entries. 

IP addresses are fetched from public and private (optional) blacklists and two plots are given as output, a barchart showing sizes per blacklist and a heatmap showing the degree of overlap between the blacklists. There is also support for importing blacklists from the local filesystem.

The Jupyter notebook found in notebooks directory gives transparancy into the code and plots as you run it, the [Standalone .py version](#standalone) saves the plots and a .csv on disk and has a separate config file that contains some additional settings not available in the notebook. 

URLs to feeds, or paths to local files to be imported are all set within the notebook or in overlap.conf if running the .py version. There are no assumptions on the formats of these feeds or local files, a regexp is used to search for IPv4 addresses line by line.


## Plots
Example output is shown below.

### Blacklist feed sizes
This barchart shows the blacklist feed sizes, with entry count on x-axis and the feeds (sources) on the y-axis.

![Barchart with sizes of blacklist feeds](http://i.imgur.com/WeZbd8R.png)

### Heatmaps displaying overlap between feeds 
The heatmap is used to show the overlap between pairs of feeds. The color of a cell reveals the degree to which a blacklist feed on the y-axis contains some feed on the x-axis.

An example is shown below. Here we note that e.g: 
* *alienvault.generic* contains all of *openbl.base*
* *emergingthreats.emerging* contains 100% of *feodotracker.ipblocklist, palevotracker.ipblocklist, spamhaus.drop* and *zeustracker.badips*.
* *rulez.blist* and *emergingthreats.compromised* are almost identical as they both contain above 93% of each other.

Setting ANNOTATE to *True* or *False* determines whether the actual value are shown in the cell or not.

**Regular**

![Heatmap showing overlap](http://i.imgur.com/Pac06u9.png)

**Annotated**

![Heatmap showing overlap - annoteated](http://imgur.com/VeJhXln.png)


## I/O
#### Input
- List of URLs that points to text or html files that contain IPv4 addresses (one per row) assumed to be blacklisted.
- List of local files that contain blacklisted IPv4 addresses.


#### Output
- Two plots: barchart and heatmap. Rendered inline if running Jupyter notebook version or optionally saved to disk if running .py version.
- In the standalone .py version a file that contains a concatenation of the input data, together with feed name and date may be saved in a .csv format (with gz compression). 


## Usage

Make sure the [requirements](#requirements) are fullfilled. 

### Notebook
```bash
$ cd notebooks/
$ jupyter notebook overlap_test.ipynb
```
All configuration are done within the notebook.

A static version of the notebook rendered by GitHub is found here: [overlap_test.ipynb](https://github.com/mrola/blacklist_overlap_test/blob/master/notebooks/overlap_test.ipynb)

### <a name="standalone"></a>Standalone .py version
```bash
$ cd src/scripts/
$ python overlap_test.py
```

A partial output from the execution of the standalone version is shown below. 


```bash
(ml)ola-lx3:ola 21:32 ~/projs/blacklist_overlap_test develop > python src/scripts/overlap_test.py 
2016-06-27 21:32:47,921 main          : INFO     ------------------++++++++BEGIN+++++++++++----------------------
2016-06-27 21:32:47,927 GetData       : INFO     >>>> Fetching public inbound blacklisted IPv4 addresses from URLs <<<<
2016-06-27 21:32:47,927 GetData       : INFO     Fetching: https://www.spamhaus.org/drop/edrop.txt
2016-06-27 21:32:48,265 GetData       : INFO     Fetching: https://www.dragonresearchgroup.org/insight/vncprobe.txt
2016-06-27 21:32:49,527 GetData       : INFO     Fetching: https://www.badips.com/get/list/ssh/3?age=2w
2016-06-27 21:32:50,722 GetData       : INFO     Fetching: https://www.dragonresearchgroup.org/insight/sshpwauth.txt
2016-06-27 21:32:52,710 GetData       : INFO     Fetching: https://www.dragonresearchgroup.org/insight/http-report.txt
2016-06-27 21:32:54,656 GetData       : INFO     Fetching: http://lists.blocklist.de/lists/all.txt
2016-06-27 21:32:55,527 GetData       : INFO     Fetching: https://zeustracker.abuse.ch/blocklist.php?download=badips
2016-06-27 21:32:56,335 GetData       : INFO     Fetching: https://palevotracker.abuse.ch/blocklists.php?download=ipblocklist
2016-06-27 21:32:57,594 GetData       : INFO     Fetching: http://www.openbl.org/lists/base.txt
2016-06-27 21:32:58,951 GetData       : INFO     Fetching: https://feodotracker.abuse.ch/blocklist/?download=ipblocklist
2016-06-27 21:33:01,157 GetData       : INFO     Fetching: http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv
2016-06-27 21:33:01,684 GetData       : INFO     Fetching: http://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt
2016-06-27 21:33:02,140 GetData       : INFO     Fetching: https://www.badips.com/get/list/http/3?age=2w
2016-06-27 21:33:03,084 GetData       : INFO     Fetching: http://www.malwaredomainlist.com/hostslist/ip.txt
2016-06-27 21:33:04,020 GetData       : INFO     Fetching: http://danger.rulez.sk/projects/bruteforceblocker/blist.php
2016-06-27 21:33:04,715 GetData       : INFO     Fetching: https://www.dan.me.uk/torlist/
2016-06-27 21:33:06,144 GetData       : INFO     Fetching: http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv
2016-06-27 21:33:06,369 GetData       : INFO     Fetching: http://malc0de.com/database/
2016-06-27 21:33:07,092 GetData       : WARNING  Skipped 2 lines due to utf-8 decode failures. Set logging mode to DEBUG to write decode failure lines to /tmp/
2016-06-27 21:33:07,128 GetData       : INFO     Fetching: https://sslbl.abuse.ch/blacklist/sslipblacklist.csv
2016-06-27 21:33:07,913 GetData       : INFO     Fetching: http://malc0de.com/bl/IP_Blacklist.txt
2016-06-27 21:33:08,174 GetData       : INFO     Fetching: http://www.spamhaus.org/drop/drop.txt
2016-06-27 21:33:08,327 GetData       : INFO     Fetching: http://rules.emergingthreats.net/blockrules/compromised-ips.txt
2016-06-27 21:33:08,742 GetData       : INFO     Fetching: https://feodotracker.abuse.ch/blocklist/?download=badips
2016-06-27 21:33:10,659 GetData       : WARNING  Found no valid ipv4 addresses.
2016-06-27 21:33:10,660 GetData       : INFO     Fetching: https://www.badips.com/get/list/postfix/3?age=2w
2016-06-27 21:33:11,940 GetData       : INFO     Fetching: https://reputation.alienvault.com/reputation.generic
2016-06-27 21:33:14,555 GetData       : INFO     Fetching: http://www.autoshun.org/files/shunlist.csv
2016-06-27 21:33:21,307 GetData       : WARNING  Got status 404
2016-06-27 21:33:21,343 WrapItUp      : INFO     Verify we got all sources:
0     spamhaus.edrop             
1     dragonresearch.vnc         
2     badips.ssh                 
3     dragonresearch.ssh         
4     dragonresearhc.http  
...
...
23    alienvault.generic         
dtype: object

2016-06-27 21:33:21,357 WrapItUp      : INFO     First few frame rows:
        entity  type direction          source notes        date
0  5.8.63.0     IPv4  inbound   spamhaus.edrop        2016-06-27
1  27.112.32.0  IPv4  inbound   spamhaus.edrop        2016-06-27
2  37.9.53.0    IPv4  inbound   spamhaus.edrop        2016-06-27
3  41.71.144.0  IPv4  inbound   spamhaus.edrop        2016-06-27
4  41.71.171.0  IPv4  inbound   spamhaus.edrop        2016-06-27

2016-06-27 21:33:21,358 WrapItUp      : INFO     Frame contains 65161 entries.

2016-06-27 21:33:22,271 WrapItUp      : INFO     Successfully saved data to: data/public_inbound/output/raw_20160627.csv.gz
2016-06-27 21:33:23,632 WrapItUp      : INFO     Successfully saved data to: data/public_inbound/output/barchart_20160627.png
2016-06-27 21:33:23,638 PlotData      : INFO     Doing heatmap calculations...
2016-06-27 21:33:30,662 WrapItUp      : INFO     Successfully saved data to: data/public_inbound/output/heatmap_20160627.png
2016-06-27 21:33:30,669 main          : INFO     Done!

```

#### Configuration
Configuration options are found in `src/config/overlap_test.conf`

- `save` If True, save data to dirs defined in `[path]` section.
- `get_urls` If True, fetch data from public sources defined in `[inbound_urls]` section.
- `read_prefetched` If True, fetch data from local filesystem as defined in `[path]` and `[inbound_prefetched]` sections.
- `test` If True, save data to path_tmp defined in `[path]` section and get url and prefetched from `[*_test]` conf sections.
- `dump` If True, save raw contents for each url in `path_tmp` defined in [path] section.
- `annotate` If True, show actual value in each cell of heatmap.

- `loglevel` By default INFO is set (and output to stdout). DEBUG will have the additional effect of saving utf-8 decode errors to `path_tmp`.

- `date` Set if you don't want today as date, format "YYYY-MM-DD".
- `timeout` number of seconds Requests will wait for a response from the server (both connect and between reads).

- `path`
    - `out_url` path to save .csv and .png when processing public sources.
    - `out_prefetched` path to save .csv and .png when processing local filesystem sources.
    - `in_prefetched` path to input files when processing local filesystem sources.
    - `path_tmp` path to tmp dir. Used if `dump` is True or failure to find output paths. 

- `inbound_urls` <br>Key: Description of source. <br>Value: URL to be fetched.

<pre>
   malwaredomainlist_ip.txt =              http://www.malwaredomainlist.com/hostslist/ip.txt
   malc0de_IP_Blacklist.txt =              http://malc0de.com/bl/IP_Blacklist.txt 
   ...
</pre>

- `inbound_prefetched`<br>Key: Description of source. <br>Value: file to be read.

<pre>
   compromised-ips =                   compromised-ips.ioc
   ips  =                              ips.ioc 
   ...
</pre>


## <a name="requirements"></a>Requirements

* Python >= 2.7 <small>(tested with 2.7 and 3.4)</small>
* Pandas > 0.16 <small>(tested with 0.16 and 0.18)</small>
    * http://pandas.pydata.org/pandas-docs/stable/index.html
    * https://github.com/pydata/pandas
* Seaborn >= 0.6.0 <small>(tested with 0.6.0 and 0.7.0)</small>
    * https://github.com/mwaskom/seaborn
    * http://stanford.edu/~mwaskom/software/seaborn/
* Requests > 2.5 <small>(tested with 2.5.3 and 2.9.0)</small>
    * http://docs.python-requests.org/en/latest/
    * https://github.com/kennethreitz/requests

For the standalone version, the configparser package is required as well.

If the above requirements are not met then installing miniconda is probably the simplest and fastest way to get ahead. Conda will allow you to create a local "environment" that contains all the necessary packages with all dependencies met without interfering with any global Python installation

>*Conda is a cross-platform and Python-agnostic package manager and environment manager program that quickly   installs, runs and updates packages and their dependencies and easily creates, saves, loads and switches   between environments on your local computer. Conda is included in all versions of Anaconda, Miniconda and Anaconda Server.*

Reference: http://conda.pydata.org/miniconda.html

----
#### <a name="tiq-test"></a>Importing into tiq-test

Example on import data into tiq-test (assuming file is saved as 20160520.csv.gz): 
<pre>
 > print(tiq.data.getAvailableDates("raw", "public_inbound"))
[1] "20160520"
 > overlap = tiq.test.overlapTest("public_inbound", "20160520", "raw", select.sources=NULL)
 > overlap.plot = tiq.test.plotOverlapTest(overlap, title="Overlap Test - Inbound blacklists - 20160520")
 > print(overlap.plot)
</pre>

References on tiq-test:
- https://github.com/mlsecproject/combine
- https://github.com/mlsecproject/tiq-test
- http://rpubs.com/alexcpsec/tiq-test-Winter2015
