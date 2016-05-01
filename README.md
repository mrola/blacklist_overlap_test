# Blacklist overlap test
The blacklist overlap test provides a measure on the degree to which one feed is contained within some other feed. It is a metric that may be used to exclude blacklist feeds that is already contained in other feeds.

## Purpose
The purpose of this Jupyter notebook is to provide a measure on the degree to which blacklists overlap in terms of IPv4 entries. The notebook extract IPv4 addresses from public and private blacklists and then provides a barchart showing sizes per blacklist and a heatmap showing the degree of overlap between the blacklists. The notebook also supports importing blacklists from the local filesystem.

Names of feeds or local files to be imported are all set within the notebook. There are no assumption on the formats of these files, the notebook simply uses a regexp to search for IPv4 addresses line by line.

### Plots
The notebook outputs two plots, one that shows blacklist feed sizes and one that shows the actual overlap between feeds. Example output is shown below.

#### Blacklist feed sizes
This barchart shows the blacklist feed sizes, with entry count on x-axis and the feeds (called sources) on the y-axis.

![Barchart with sizes of blacklist feeds](http://i.imgur.com/sVf38Xs.png)

#### Heatmaps displaying overlap between feeds 
The heatmap is used to show the overlap between pairs of feeds. The color of a cell reveals the degree to which a blacklist feed on the y-axis contains some feed on the x-axis.

An example is shown below. Here we note that e.g. *alienvault_reputation.generic* contains all of *openbl.org_base.txt*. We also note that *emergingthreats_emerging-Block-IPs.txt* cotains close to 100% of both *feodotracker_blocklists_ipblocklist* and *zeustracker_blocklist_badips*.

Setting ANNOTATE to *True* or *False* determines whether the actual value are shown in the cell or not.

**Regular**

![Heatmap showing overlap](http://i.imgur.com/709Ov5s.png)

**Annotated**

![Heatmap showing overlap - annoteated](http://i.imgur.com/1dVE22w.png)
