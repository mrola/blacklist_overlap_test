
# Blacklist overlap test <img align="right", src="http://i.imgur.com/ln57AGi.png" width="386">

The blacklist overlap test provides a measure on the degree to which one feed is contained within some other feed. It is a metric that may be used to exclude blacklist feeds that is already contained in other feeds.

This project is inspired by the combine and tiq-test project (written in R) by [@alexcpsec](https://twitter.com/alexcpsec), [@kylemaxwell](https://twitter.com/kylemaxwell) and others. While the tiq-test project provides additional quality metrics and also supports enrichment, this project is pure Python and at this point only provides the overlap test. That said, if overlap test is the goal just running the Jupyter notebook or `overlap_test.py` will do the fetch data, extract IP addresses, calculate overlap between each pair, and build heatmap steps. It is designed to be standalone. 

If you prefer ggplot heatmaps, there's an option to save a .csv file with a format that is expected by tiq.test. See [Importing into tiq-test](#tiq-test) for an example. However, if [Seaborn](http://stanford.edu/~mwaskom/software/seaborn/) is your prefered choise of visualisation library and you'd like to gain insight into degree of overlap between different feeds with minimal effort then please continue reading.


## Purpose
The purpose of this project is to provide a means to measure the degree to which blacklists overlap in terms of IPv4 entries. 

Addresses are fetched from public and private (optional) blacklists and two plots are given as output, a barchart showing sizes per blacklist and a heatmap showing the degree of overlap between the blacklists. There is also support for importing blacklists from the local filesystem.

The Jupyter notebook found in notebooks directory gives transparancy into the code and plots as you run it, the [Standalone .py version](#standalone) saves the plots on disk and has a separate config file. But in terms of functionality the .py and notebook versions don't differ apart from the option to save the data in a .csv file if running the .py version.

URLs to feeds or paths to local files to be imported are all set within the notebook or in overlap.conf (if running the .py version). There are no assumptions on the formats of these feeds or local files, a regexp is used to search for IPv4 addresses line by line.


## Plots
Example output is shown below.

### Blacklist feed sizes
This barchart shows the blacklist feed sizes, with entry count on x-axis and the feeds (sources) on the y-axis.

![Barchart with sizes of blacklist feeds](http://i.imgur.com/ZV5oCRk.png)

### Heatmaps displaying overlap between feeds 
The heatmap is used to show the overlap between pairs of feeds. The color of a cell reveals the degree to which a blacklist feed on the y-axis contains some feed on the x-axis.

An example is shown below. Here we note that e.g. *alienvault_reputation.generic* contains all of *openbl.org_base.txt*. We also note that *emergingthreats_emerging-Block-IPs.txt* cotains close to 100% of both *feodotracker_blocklists_ipblocklist* and *zeustracker_blocklist_badips*.

Setting ANNOTATE to *True* or *False* determines whether the actual value are shown in the cell or not.

**Regular**

![Heatmap showing overlap](http://i.imgur.com/52OfM8Q.png)

**Annotated**

![Heatmap showing overlap - annoteated](http://i.imgur.com/JLFqlVH.png)


## I/O
#### Input
- List of URLs that points to text files that contain IPv4 addresses assumed to be blacklisted.
- List of local text files that contain blacklisted IPv4 addresses.


#### Output
- Two plots: barchart and heatmap. Rendered inline if running Jupyter notebook version or optionally saved to disk if running .py version.
- In the standalone .py version a .csv file that basically contains a concatenation of the input data may be saved in a format accepted by tiq-test.


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

A partial output from the execution of the standalone version is shown below. The only differences to the notebook versions are the possibility to save the plots to disk and that the config is located in a separate file.


```bash
(ml)ola-lx3:ola 08:26 ~/projs/blacklist_overlap_test/src/scripts develop > python overlap_test.py 
2016-05-23 08:26:54,698 main          : INFO     ------------------++++++++BEGIN+++++++++++----------------------

2016-05-23 08:26:54,709 GetData       : INFO     >>>> Fetching public inbound blacklisted IPv4 addresses from URLs <<<<
2016-05-23 08:26:54,709 GetData       : INFO     Fetching: https://feodotracker.abuse.ch/blocklist/?download=ipblocklist
2016-05-23 08:26:56,689 GetData       : INFO     Fetching: https://reputation.alienvault.com/reputation.generic
2016-05-23 08:26:58,060 GetData       : INFO     Fetching: http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv
2016-05-23 08:26:58,708 GetData       : INFO     Fetching: http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv
2016-05-23 08:26:58,937 GetData       : INFO     Fetching: http://rules.emergingthreats.net/blockrules/compromised-ips.txt
2016-05-23 08:26:58,973 GetData       : INFO     Fetching: https://feodotracker.abuse.ch/blocklist/?download=badips
2016-05-23 08:27:00,842 GetData       : WARNING  Found no valid ipv4 addresses.
2016-05-23 08:27:00,844 GetData       : INFO     Fetching: https://palevotracker.abuse.ch/blocklists.php?download=ipblocklist
2016-05-23 08:27:02,125 GetData       : INFO     Fetching: http://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt
2016-05-23 08:27:02,174 GetData       : INFO     Fetching: http://www.malwaredomainlist.com/hostslist/ip.txt
2016-05-23 08:27:02,234 GetData       : INFO     Fetching: http://lists.blocklist.de/lists/all.txt
2016-05-23 08:27:02,584 GetData       : INFO     Fetching: http://www.openbl.org/lists/base.txt
2016-05-23 08:27:03,065 GetData       : INFO     Fetching: https://zeustracker.abuse.ch/blocklist.php?download=badips
2016-05-23 08:27:03,883 GetData       : INFO     Fetching: http://malc0de.com/bl/IP_Blacklist.txt
2016-05-23 08:27:03,952 WrapItUp      : INFO     Verify we got all sources:
0     feodotracker__ipblocklist     
1     alienvault_reputation.generic 
2     blutmagie_tor_ip_list_all     
3     blutmagie_tor_ip_list_exit    
4     emergingthreats_compro-ips.txt
5     palevotracker_ipblocklist     
6     emergingthreats_block-ips.txt 
7     malwaredomainlist_ip.txt      
8     blocklist.de_all.txt          
9     openbl.org_base.txt           
10    zeustracker_blocklist_badips  
11    malc0de_ip_blacklist.txt      
dtype: object

2016-05-23 08:27:03,970 WrapItUp      : INFO     First few frame rows:
          entity  type direction                     source notes        date
0  1.178.179.217  IPv4  inbound   feodotracker__ipblocklist        2016-05-23
1  1.179.170.7    IPv4  inbound   feodotracker__ipblocklist        2016-05-23
2  1.93.0.224     IPv4  inbound   feodotracker__ipblocklist        2016-05-23
3  103.13.29.158  IPv4  inbound   feodotracker__ipblocklist        2016-05-23
4  103.16.26.228  IPv4  inbound   feodotracker__ipblocklist        2016-05-23

2016-05-23 08:27:03,970 WrapItUp      : INFO     Frame contains 60239 entries.
2016-05-23 08:27:04,334 WrapItUp      : INFO     Successfully saved data to: ../../data/public_inbound/output/raw_20160523.csv
2016-05-23 08:27:05,303 WrapItUp      : INFO     Successfully saved data to: ../../data/public_inbound/output/barchart_20160523.png
2016-05-23 08:27:05,312 PlotData      : INFO     Doing heatmap calculations...
2016-05-23 08:27:07,527 WrapItUp      : INFO     Successfully saved data to: ../../data/public_inbound/output/heatmap_20160523.png

2016-05-23 08:27:07,537 GetData       : INFO     >>>> Fetching private inbound blacklisted IPv4 addresses from disk <<<<
2016-05-23 08:27:07,537 GetData       : INFO     Reading data...
2016-05-23 08:27:07,537 GetData       : INFO     ../../data/private_inbound/input/compromised-ips.ioc
2016-05-23 08:27:07,560 GetData       : INFO     ../../data/private_inbound/input/zeus_ipblocklist.ioc
2016-05-23 08:27:07,585 GetData       : INFO     ../../data/private_inbound/input/all.ioc
2016-05-23 08:27:08,601 GetData       : INFO     ../../data/private_inbound/input/all1.ioc
2016-05-23 08:27:09,256 GetData       : INFO     ../../data/private_inbound/input/all2.ioc
2016-05-23 08:27:10,914 GetData       : INFO     ../../data/private_inbound/input/blocklist_sample.ioc.in
2016-05-23 08:27:10,988 GetData       : INFO     ../../data/private_inbound/input/ips.ioc
2016-05-23 08:27:11,143 WrapItUp      : INFO     Verify we got all sources:
0    compromised-ips 
1    zeus_ipblocklist
2    all             
3    all1            
4    all2            
5    blocklist_sample
6    ips             
dtype: object

2016-05-23 08:27:11,154 WrapItUp      : INFO     First few frame rows:
        entity  type direction           source notes        date
0  1.85.21.181  IPv4  inbound   compromised-ips        2016-05-23
1  1.85.62.51   IPv4  inbound   compromised-ips        2016-05-23
2  1.9.79.191   IPv4  inbound   compromised-ips        2016-05-23
3  1.9.79.193   IPv4  inbound   compromised-ips        2016-05-23
4  1.93.51.221  IPv4  inbound   compromised-ips        2016-05-23

2016-05-23 08:27:11,154 WrapItUp      : INFO     Frame contains 508953 entries.
2016-05-23 08:27:12,949 WrapItUp      : INFO     Successfully saved data to: ../../data/private_inbound/output/raw_20160523.csv
2016-05-23 08:27:23,343 WrapItUp      : INFO     Successfully saved data to: ../../data/private_inbound/output/barchart_20160523.png
2016-05-23 08:27:23,388 PlotData      : INFO     Doing heatmap calculations...
2016-05-23 08:27:24,590 WrapItUp      : INFO     Successfully saved data to: ../../data/private_inbound/output/heatmap_20160523.png
2016-05-23 08:27:24,590 main          : INFO     Done!
```

#### Configuration
Configuration options are found in src/config/overlap_test.conf.

- `save` If True, save data to dirs defined in [path] section.
- `get_urls` If True, fetch data from public sources defined in [inbound_urls] section.
- `read_prefetched` If True, fetch data from local filesystem as defined in [path] and [inbound_prefetched] sections.
- `annotate` If True, show actual value in each cell of heatmap.

- `loglevel` By default INFO is set (and output to stdout).

- `date` Set if you don't want today as date, format "YYYY-MM-DD".
- `timeout` number of seconds Requests will wait for a response from the server (both connect and between reads).

- `path`
    - `out_url` path to save .csv and .png when processing public sources.
    - `out_prefetched` path to save .csv and .png when processing local filesystem sources.
    - `in_prefetched` path to input files when processing local filesystem sources.

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
