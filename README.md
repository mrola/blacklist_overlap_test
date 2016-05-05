# Blacklist overlap test
The blacklist overlap test provides a measure on the degree to which one feed is contained within some other feed. It is a metric that may be used to exclude blacklist feeds that is already contained in other feeds.

## Purpose
The purpose of this Jupyter notebook is to provide a measure on the degree to which blacklists overlap in terms of IPv4 entries. The notebook extract IPv4 addresses from public and private blacklists and then provides a barchart showing sizes per blacklist and a heatmap showing the degree of overlap between the blacklists. The notebook also supports importing blacklists from the local filesystem.

Names of feeds or local files to be imported are all set within the notebook. There are no assumption on the formats of these files, the notebook simply uses a regexp to search for IPv4 addresses line by line.

See [Standalone .py version](#standalone) for details on the standalone version.

## Plots
The notebook outputs two plots, one that shows blacklist feed sizes and one that shows the actual overlap between feeds. Example output is shown below.

### Blacklist feed sizes
This barchart shows the blacklist feed sizes, with entry count on x-axis and the feeds (called sources) on the y-axis.

![Barchart with sizes of blacklist feeds](http://i.imgur.com/sVf38Xs.png)

### Heatmaps displaying overlap between feeds 
The heatmap is used to show the overlap between pairs of feeds. The color of a cell reveals the degree to which a blacklist feed on the y-axis contains some feed on the x-axis.

An example is shown below. Here we note that e.g. *alienvault_reputation.generic* contains all of *openbl.org_base.txt*. We also note that *emergingthreats_emerging-Block-IPs.txt* cotains close to 100% of both *feodotracker_blocklists_ipblocklist* and *zeustracker_blocklist_badips*.

Setting ANNOTATE to *True* or *False* determines whether the actual value are shown in the cell or not.

**Regular**

![Heatmap showing overlap](http://i.imgur.com/709Ov5s.png)

**Annotated**

![Heatmap showing overlap - annoteated](http://i.imgur.com/1dVE22w.png)


## <a name="standalone"></a>Standalone .py version
A partial output from the execution of the standalone version is shown below. The only differences to the notebook versions are the possibility to save the plots to disk and that the config is located in a separate file.

<pre>
lx3:ola 22:44 ~/projs/blacklist_overlap_test/src/scripts master > python overlap_test.py 
2016-05-05 22:44:31,995  INFO:main: ------------------++++++++BEGIN+++++++++++----------------------
2016-05-05 22:44:32,004  INFO:main: >>>> Fetching public inbound blacklisted IPv4 addresses from URLs <<<<
2016-05-05 22:44:32,010  INFO:GetData: Fetching: http://malc0de.com/bl/IP_Blacklist.txt
2016-05-05 22:44:32,309  INFO:GetData: Got status 200 back...
2016-05-05 22:44:32,344  INFO:GetData: Fetching: http://lists.blocklist.de/lists/all.txt
2016-05-05 22:44:32,731  INFO:GetData: Got status 200 back...
2016-05-05 22:44:33,005  INFO:GetData: Fetching: http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv
2016-05-05 22:44:33,274  INFO:GetData: Got status 200 back...
2016-05-05 22:44:33,379  INFO:GetData: Fetching: http://www.malwaredomainlist.com/hostslist/ip.txt
2016-05-05 22:44:33,775  INFO:GetData: Got status 200 back...
2016-05-05 22:44:43,558  INFO:GetData: Fetching: https://feodotracker.abuse.ch/blocklist/?download=badips
2016-05-05 22:44:45,395  INFO:GetData: Got status 200 back...
2016-05-05 22:44:45,396  WARNING:GetData: Found no valid ipv4 addresses.

...
...

2016-05-05 22:44:45,431  INFO:WrapItUp: Verify we got all sources:
0     malc0de_ip_blacklist.txt      
1     blocklist.de_all.txt          
2     blutmagie_tor_ip_list_all     
3     malwaredomainlist_ip.txt      
4     emergingthreats_block-ips.txt 
5     alienvault_reputation.generic 
6     palevotracker_ipblocklist     
7     zeustracker_blocklist_badips  
8     emergingthreats_compro-ips.txt
9     feodotracker__ipblocklist     
10    blutmagie_tor_ip_list_exit    
dtype: object

2016-05-05 22:44:45,446  INFO:WrapItUp: First few frame rows:
            entity  type direction                    source notes        date
0  192.254.235.178  IPv4  inbound   malc0de_ip_blacklist.txt        2016-05-05
1  94.73.147.76     IPv4  inbound   malc0de_ip_blacklist.txt        2016-05-05
2  199.30.57.225    IPv4  inbound   malc0de_ip_blacklist.txt        2016-05-05
3  192.185.157.121  IPv4  inbound   malc0de_ip_blacklist.txt        2016-05-05
4  212.227.247.242  IPv4  inbound   malc0de_ip_blacklist.txt        2016-05-05

2016-05-05 22:44:45,446  INFO:WrapItUp: Frame contains 60603 entries.

</pre>

## Requirements

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

For the standalone version, the confiparser package is required as well.

----
If the above requirements are not met then installing miniconda is probably the simplest and fastest way to get ahead. Conda will allow you to create a local "environment" that contains all the necessary packages with all dependencies met without interfering with any global Python installation

>*Conda is a cross-platform and Python-agnostic package manager and environment manager program that quickly   installs, runs and updates packages and their dependencies and easily creates, saves, loads and switches   between environments on your local computer. Conda is included in all versions of Anaconda, Miniconda and Anaconda Server.*

Reference: http://conda.pydata.org/miniconda.html


