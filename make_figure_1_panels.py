import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
#read tables
idf = pd.read_csv("global_fullout.tsv",sep='\t')
gdf = gpd.read_file('custom.geo.json')
#count clusters per region
crcs = dict(idf.drop_duplicates("introduction_node").region.value_counts())
#the way in which countries are labeled is somewhat inconsistent across files; we do our best to match them up
ccv = []
total = 0
misplaced = 0
for i,d in gdf.iterrows():
    total += 1
    if d.sovereignt in crcs.keys():
        ccv.append(crcs[d.sovereignt])
    elif d.sov_a3 in crcs.keys():
        ccv.append(crcs[d.sov_a3])
    elif d.iso_a3 in crcs.keys():
        ccv.append(crcs[d.iso_a3])
    elif d.sovereignt.replace(" ","") in crcs.keys():
        ccv.append(crcs[d.sovereignt.replace(" ","")])
    elif d.name in crcs.keys():
        ccv.append(crcs[d.name])
    elif d.sovereignt == "United Kingdom":
        ccv.append(crcs['England'])
    else:
        misplaced += 1
        ccv.append(0)
gdf['CluCount'] = ccv
from mpl_toolkits.axes_grid1 import make_axes_locatable
fig, ax = plt.subplots(1, 1, figsize=[16,12])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
gdf['LogCluCount'] = np.log10(gdf.CluCount+1)
gdf.plot("LogCluCount",figsize=[16,12],ax=ax,legend=True,cax=cax,legend_kwds={"label": "Log10 Cluster Count"})
ax.set_title("Transmission Clusters Across The Globe")
plt.savefig("fig_1A.png")
rvc = idf.region.value_counts(normalize=True)
x = list(rvc.index[:5])
y = list(rvc[:5])
ax = sns.barplot(x=x,y=y,color='grey')
ax.set_xlabel("Top 5 Countries")
ax.set_ylabel("Percentage of Samples")
plt.savefig("fig_1B.png")
bins = [0, 1,10,100,1000,10000]
x = []
y = []
r = []
for i,m in enumerate(bins[1:]):
    for region,sdf in idf.groupby("region"):
        csizes = sdf.introduction_node.value_counts()
        y.append(len([cs for cs in csizes if cs <= m and cs > bins[i]])/len(csizes))
        x.append(m)
        r.append(region)
ax = sns.boxplot(x=x,y=y,color='grey')
ax.set_xticklabels(["<=" + str(xv) for xv in bins[1:]])
ax.set_xlabel("Cluster Size")
ax.set_ylabel("Proportion of Clusters")
plt.savefig("fig_1C.png")
