import pandas as pd
import numpy as np
from sklearn.metrics import adjusted_rand_score as ari

idf = pd.read_csv("alpert_fullout.tsv",sep='\t')
stateconv = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
def get_state(sn):
    if "USA" == sn.split("/")[0]:
        return sn.split("/")[1].split("-")[0]
    else:
        return "N/A"    
idf['State'] = idf['sample'].apply(get_state)
#take the labels from Alpert et al and load them into a dictionary
tl = pd.read_csv("fig3b_labels.csv",skiprows=[0])
tsd = {}
for i,sl in enumerate(tl.Taxa):
    if type(sl) != float:
        samples = [s.strip() for s in sl.split(",")]
        tsd[i] = samples
#invert the dictionary and apply it as a column
inv = {}
for k,v in tsd.items():
    for s in v:
        inv[s] = k
idf['TC'] = idf['sample'].apply(lambda x:inv.get(x,np.nan))
ariv = ari(idf[~idf.TC.isna()].introduction_node, idf[~idf.TC.isna()].TC)
print("ARI:",ariv)
with open("my_labels.tsv","w+") as outf:
    print("sample\tmy_node\tlabel",file=outf)
    for i,d in idf[~idf.TC.isna()].iterrows():
        print(d['sample'] + "\t" + d.introduction_node + "\t" + str(d.TC),file=outf)