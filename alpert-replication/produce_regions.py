with open("custom_sample_regions.tsv","w+") as outf:
    with open("custom_samples.txt") as inf:
        for entry in inf:
            country = entry.split("/")[0]
            if country != "USA":
                print(entry.strip() + "\t" + country, file = outf)
            else:
                state = country
                print(entry.strip() + "\t" + state, file = outf)