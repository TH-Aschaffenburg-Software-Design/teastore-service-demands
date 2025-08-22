import os
import sys

import pandas as pd
from scipy.stats import f_oneway
from statsmodels.stats.multitest import multipletests

directories = sys.argv[1:]
df_list = []

for dir in directories:

    file = os.path.join(".", "outputs", dir, "results.csv")
    if not os.path.exists(file):
        print(f"{file} does not exist")
        continue
    _df = pd.read_csv(file)
    _df['configuration'] = dir
    df_list.append(_df)

df = pd.concat(df_list, ignore_index=True)
endpoints = df['endpoint'].unique()
results = []

for endpoint in endpoints:
    sub_df: pd.DataFrame = df[df['endpoint'] == endpoint]
    groups = sub_df.groupby('configuration')['service_demand'].apply(list)
    
    stat, pval = f_oneway(*groups)
    results.append({'endpoint': endpoint, 'p-value': pval})

# Multiple testing correction (Bonferroni)
pvals = [r['p-value'] for r in results]
_, pvals_corrected, _, _ = multipletests(pvals, method='bonferroni')

for i, row in enumerate(results):
    row['p-corrected'] = pvals_corrected[i]
    row['significant'] = pvals_corrected[i] < 0.05

results_df = pd.DataFrame(results)
print(results_df[['endpoint', 'p-value', 'p-corrected', 'significant']])
