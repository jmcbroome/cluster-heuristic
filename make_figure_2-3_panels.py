import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
conversion = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
rconv = {v:k for k,v in conversion.items()}
# Code for parsing country names out of sample names. Commented out as it does not apply without access to the GISAID containing protobuf.
# badsamples = open("unlabeled_samples.txt","w+")
# global_sample_regions = open('global_sample_regions.tsv','w+')
# countries_repped = {}
# with open("samplenames.txt") as inf:
#     with open("sample_regions.tsv","w+") as outf:
#         for entry in inf:
#             country = entry.split("/")[0]
#             if country == "USA":
#                 state = entry.split("/")[1].split("-")[0]
#                 if state in conversion:
#                     print(entry.strip() + "\t" + state, file = outf)
#                 else:
#                     print(entry.strip(), file = badsamples)
#             if country not in countries_repped:
#                 countries_repped[country] = []
#             countries_repped[country].append(entry.strip())
#         for k,v in countries_repped.items():
#             if len(v) > 5000 and k != 'United_States' and k != "USA":
#                 if k == 'Northern_Ireland':
#                     k = "NorthernIreland"
#                 elif k == "AUS":
#                     k = 'Australia'
#                 for c in v:
#                     print(c + "\t" + k, file = outf)
#             if len(v) > 500 and k != "mink" and k != "env":
#                 if k == "United_States":
#                     k = 'USA'
#                 elif k == 'Northern_Ireland':
#                     k = "NorthernIreland"
#                 elif k == "AUS":
#                     k = 'Australia'
#                 elif k == "MEX":
#                     k = 'Mexico'
#                 for c in v:
#                     print(c + "\t" + k, file = global_sample_regions)
#             else:
#                 for c in v:
#                     print(c, file = badsamples)
# badsamples.close()
# global_sample_regions.close()

idf = pd.read_csv("full_gisaid.txt",sep='\t')
ivc = idf.introduction_node.value_counts()
#convert ivc counts to cumulative percentage
order = []
cump = []
tc = sum(ivc)
total = 0
for i in ivc.index:
    order.append(i)
    cump.append((ivc[i] + total) / tc)
    total += ivc[i]
print("The largest 20 percent of clusters contain " + str(cump[int(len(order) * .2)*100]) + " of all samples.")

#for this mapping, we are going to construct a more complex geopandas from multiple sources
globaldf = gpd.read_file('custom.geo.json')
globaldf['short'] = globaldf['iso_a2']
statedf = gpd.read_file('us-states.geo.json')
statedf['subregion'] = "Northern America"
statedf['short'] = statedf.name.apply(lambda x:rconv[x])
ukdf = gpd.read_file("uk.geojson")
def get_uk_name(nnm):
    if 'England' in nnm or nnm == 'London' or nnm == 'Yorkshire and The Humber':
        return 'England'
    else:
        return nnm
ukdf['name'] = ukdf['nuts118nm'].apply(get_uk_name)
ukdf['short'] = 'GB'
ukdf['subregion'] = 'Northern Europe'
gdf = pd.concat([globaldf[(globaldf.name != 'United States') & (globaldf.name != 'United Kingdom')][['name','geometry','short','subregion']],statedf[['name','geometry','short','subregion']],ukdf[['name','geometry','short','subregion']]], axis=0).reset_index() 


from mpl_toolkits.axes_grid1 import make_axes_locatable
fig, ax = plt.subplots(1, 1, figsize=[16,12])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
gdf[(gdf.name.isin(rconv.keys())) & (~gdf.name.isin(['Hawaii','Alaska',"Puerto Rico"])) & (gdf.subregion == "Northern America")].plot("LogCluCount",ax=ax,legend=True,legend_kwds={"label": "Log10 Cluster Count"},cax=cax)
ax.set_title("Clusters Identified across the Continental USA")
plt.savefig("figure_2A.png")

x = []
y = []
y2 = []
reg = []
for r,sdf in idf[(idf.origins != 'indeterminate') & (idf.region.isin(conversion.keys()))].groupby("region"):
    reg.append(r)
    x.append(sdf.shape[0])
    y.append(sdf[~sdf.Internal].introduction_node.nunique()/sdf.introduction_node.nunique())
    y2.append(sdf.introduction_node.nunique())
for i,l in enumerate(reg):
    if l in ["CA",'TX','FL','NY',"MA",'PR','CO','NM','TN','SD']:
        plt.text(x=x[i],y=y[i],s=l)
ax = sns.scatterplot(x=x,y=y,color='grey')
ax.set_xlabel("Samples Collected")
ax.set_ylabel("Proportion of International Introductions")
plt.savefig("figure_2B.png")

bins = [0, 1,10,100,1000,10000]
x = []
y = []
r = []
for i,m in enumerate(bins[1:]):
    for region,sdf in idf[idf.region.isin(conversion.keys())].groupby("region"):
        csizes = sdf.introduction_node.value_counts()
        y.append(len([cs for cs in csizes if cs <= m and cs > bins[i]])/len(csizes))
        x.append(m)
        r.append(region)
ax = sns.boxplot(x=x,y=y,color='grey')
ax.set_xticklabels(["<=" + str(xv) for xv in bins[1:]])
ax.set_xlabel("Cluster Size")
ax.set_ylabel("Proportion of Clusters")
plt.savefig("figure_2C.png")

def get_lfec(source):
    extro = idf.drop_duplicates('introduction_node').origins.value_counts()[source]
    total = idf.introduction_node.nunique()
    lfe = {}
    for r,sdf in idf.groupby('Region'):
        if r == source:
            lfe[r] = np.nan
        else:
            intro = sdf.introduction_node.nunique()
            lf = sdf[sdf.origins == source].introduction_node.nunique() / intro / extro * total
            lfe[r] = lf
    return lfe

lfes = {}
for s in idf[idf.region.isin(conversion.keys())].region.value_counts().index:
    print(s)
    lfes[s] = get_lfec(s)

lfeca = {}
for c,v in lfes['CA'].items():
    if c in rconv.keys():
        if rconv[c] == "CA":
            lfeca['CA'] = np.nan
        else:
            lfeca[rconv[c]] = v
fig, ax = plt.subplots(1, 1, figsize=[16,12])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
t = gdf[(gdf.name.isin(rconv.keys())) & (~gdf.name.isin(['Hawaii','Alaska',"Puerto Rico"])) & (gdf.subregion == "Northern America")]
t['IL'] = t.name.apply(lambda x:lfeca[rconv[x]])
t.plot("IL",ax=ax,cax=cax,missing_kwds={"color":"yellow","edgecolor":'blue'},figsize=[16,12],legend=True,legend_kwds={"label": "Log-Fold Enrichment of Introductions"})
ax.set_title("Log-Fold Introductions Into California")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.savefig("figure_3A.png")

lfeil = {}
for c,v in lfes['IL'].items():
    if c in rconv.keys():
        if rconv[c] == "IL":
            lfeca['IL'] = np.nan
        else:
            lfeca[rconv[c]] = v
fig, ax = plt.subplots(1, 1, figsize=[16,12])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
t = gdf[(gdf.name.isin(rconv.keys())) & (~gdf.name.isin(['Hawaii','Alaska',"Puerto Rico"])) & (gdf.subregion == "Northern America")]
t['IL'] = t.name.apply(lambda x:lfeca[rconv[x]])
t.plot("IL",ax=ax,cax=cax,missing_kwds={"color":"yellow","edgecolor":'blue'},figsize=[16,12],legend=True,legend_kwds={"label": "Log-Fold Enrichment of Introductions"})
ax.set_title("Log-Fold Introductions Into Illinois")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.savefig("figure_3B.png")
