import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.ticker import FixedLocator, MultipleLocator

DIRPATH = sys.argv[1]
RESULTS_FILE = "results.csv"
SERVICE_DEMANDS_FILE = "service_demands.csv"

def main():
    result_df = pd.read_csv(f"{DIRPATH}/{RESULTS_FILE}", index_col=False)
    generate_files(DIRPATH, result_df)

def generate_files(dirpath: str, result_df: pd.DataFrame):
    result_df.to_csv(f"{dirpath}/{RESULTS_FILE}", index=False)
    result_df["hue"] = result_df["service"] + "_" + result_df["endpoint"]

    # Drop first 2 replications, if there are more than 2 replications
    result_df["replication"] = result_df["replication"].astype("int64")
    replications = result_df["replication"].max()
    if replications > 2:
        corrected_df = result_df[result_df["replication"] > 2]
    else:
        corrected_df = result_df[result_df["replication"] == replications]

    demand_df = corrected_df[["service", "endpoint", "service_demand"]].groupby(["service", "endpoint"], sort=False).mean()
    demand_df.to_csv(f"{dirpath}/{SERVICE_DEMANDS_FILE}")

    visualize_experiment_course(dirpath, result_df)
    visualize_utilization(dirpath, corrected_df)
    visualize_demand(dirpath, corrected_df)

def visualize_experiment_course(dirpath: str, df: pd.DataFrame):

    ax: list[Axes]
    fig, ax = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    palette = ["gray"] * len(df["endpoint"].unique())

    # Plot the course of utilization over the replications
    sns.lineplot(ax=ax[0], data=df, x="replication", y="mean_utilization", hue="hue", palette=palette)
    ax[0].get_legend().remove()
    ax[0].xaxis.set_major_locator(MultipleLocator(1))
    ax[0].set_title("Utilization over replications by endpoint")
    ax[0].set_ylabel("Utilization")

    # Plot the course of service demand over the replications
    sns.lineplot(ax=ax[1], data=df, x="replication", y="service_demand", hue="hue", palette=palette)
    ax[1].get_legend().remove()
    ax[1].xaxis.set_major_locator(MultipleLocator(1))
    ax[1].set_title("Service Demand over replications by endpoint")
    ax[1].set_ylabel("Service Demand")

    plt.savefig(f"{dirpath}/experiment_course.svg", bbox_inches="tight")
    plt.close()

def visualize_utilization(dirpath: str, df: pd.DataFrame):

    ax = sns.barplot(data=df, y="hue", x="mean_utilization", orient="y")
    ax.yaxis.set_major_locator(FixedLocator(ax.get_yticks()))
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7)
    ax.set_ylabel("Endpoint")
    ax.set_xlabel("Utilization")
    plt.suptitle("Mean utilization of all replications over endpoints")
    plt.savefig(f"{dirpath}/utilization.svg", bbox_inches="tight")
    plt.close()

def visualize_demand(dirpath: str, df: pd.DataFrame):

    ax = sns.barplot(data=df, y="hue", x="service_demand", orient="y")
    ax.yaxis.set_major_locator(FixedLocator(ax.get_yticks()))
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7)
    ax.set_xlabel("Service Demand")
    ax.set_ylabel("Endpoint")
    plt.savefig(f"{dirpath}/service_demands.svg", bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    main()
