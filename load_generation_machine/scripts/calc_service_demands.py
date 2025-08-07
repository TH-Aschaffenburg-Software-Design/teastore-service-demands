import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Read the output file
dirpath = sys.argv[1]
df = pd.read_csv(f"{dirpath}/result.csv", index_col=False)

# Normalize utilization to resource limit. Adjust to own resource limit
df["Utilization"] = df["mean"] / 0.6

# Plot utilization to check for medium utilization. Change rates in data_generation/callHierarchy.json to optimize
ax = sns.barplot(data=df, y="endpoint", x="Utilization", orient="y")
plt.savefig(f"{dirpath}/utilization.svg", bbox_inches="tight")

# Calculate service demand using Servuice Demand Law
df["demand"] = df["Utilization"] / df["rps"]

# Plot service demand
sns.barplot(data=df, y="endpoint", x="demand", orient="y")

# Calculate arithmetic mean of all experiment runs
mean_demands = df.groupby("endpoint", sort=False)["demand"].mean()

# Write service demands to file
mean_demands.to_csv(f"{dirpath}/demands.csv", index=False)
