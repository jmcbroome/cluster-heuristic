This folder contains code for replicating the results of Alpert et al 2021.

They provide a nextstrain JSON containing all needed information to replicate their results directly, copied here as CT-SARS-CoV-2_paper5.json. We also obtained their sample labels from the supplementary information for their paper, copied here as fig3b_labels.csv. We thank the authors for their well-documented and easily available data!

The first step for applying our heuristic with matUtils is to convert the json into a MAT PB. This is accomplished either by passing it directly to matUtils extract or by applying the included python script. 

```
python3 ../auspice_json_to_mat.py
matUtils extract -i alpert.pb -u alpert_samples.txt
python3 produce_regions.py
matUtils introduce -i alpert.pb -s alpert_sample_regions.tsv -o alpert_fullout.tsv
python3 validate.py
```

Python package dependencies include: Pandas, Numpy, scikit-learn

To run auspice_json_to_mat.py, you need to obtain a parsimony_pb2 python parser. One is included in this repository, or it can be generated from the UShER installation via Protoc. 