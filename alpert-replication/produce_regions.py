import pandas as pd
tl = pd.read_csv("fig3b_labels.csv",skiprows=[0])
samples_to_use = set()
for sl in tl.Taxa.dropna():
    for s in sl.split(","):
        samples_to_use.add(s)
print(len(samples_to_use))
with open("alpert_sample_regions.tsv","w+") as outf:
    with open("alpert_samples.txt") as inf:
        for entry in inf:
            country = entry.split("/")[0]
            if country != "USA":
                print(entry.strip() + "\t" + country, file = outf)
            else:
                if entry.strip() in samples_to_use:
                    print(entry.strip() + "\t" + country, file = outf)
