import pandas as pd
tdf = pd.read_csv("introduce_times.txt", sep="\t")
tdf.groupby(['SCount']).mean().drop("Perm",axis=1).to_csv("collapsed_times.txt", sep="\t")
