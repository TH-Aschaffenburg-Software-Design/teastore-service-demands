import datetime as dt
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

    # Drop first 2 replications, if there are more than 2 replications
    replications = result_df.value_counts(["endpoint"]).min()
    if replications > 2:
        result_df["_group_idx"] = result_df.groupby("endpoint").cumcount()
        corrected_df = result_df[result_df["_group_idx"] >= 2]
    else:
        corrected_df = result_df.drop_duplicates(subset="endpoint", keep="last")

    demand_df = corrected_df[["endpoint", "service_demand"]].groupby("endpoint").mean()
    demand_df.to_csv(f"{dirpath}/{SERVICE_DEMANDS_FILE}")

    visualize_experiment_course(dirpath, result_df)
    visualize_utilization(dirpath, corrected_df)
    visualize_demand(dirpath, corrected_df)
    
def retrieve_utilization(prometheus_url: str, time: dt.datetime, service: str) -> pd.Series:
    
    from prometheus_api_client import MetricRangeDataFrame, PrometheusConnect

    run_duration = 100
    warmup_before_run = 20

    prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
    query = f'rate(container_cpu_usage_seconds_total{{namespace="teastore", container!=""}}[1m])'
    start_time = time + dt.timedelta(seconds=warmup_before_run)
    end_time = start_time + dt.timedelta(seconds=run_duration)
    result = prom.custom_query_range(query, start_time, end_time, "1")

    df = MetricRangeDataFrame(result)
    df_service = df[df["container"] == f"teastore-{service}"]
    return df_service["value"]

def visualize_experiment_course(dirpath: str, df: pd.DataFrame):

    df["Replication"] = df.groupby("endpoint").cumcount() + 1
    ax: list[Axes]
    fig, ax = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    palette = ["gray"] * len(df["endpoint"].unique())

    # Plot the course of utilization over the replications
    sns.lineplot(ax=ax[0], data=df, x="Replication", y="mean_utilization", hue="endpoint", palette=palette)
    ax[0].get_legend().remove()
    ax[0].xaxis.set_major_locator(MultipleLocator(1))
    ax[0].set_title("Utilization over replications by endpoint")
    ax[0].set_ylabel("Utilization")

    # Plot the course of service demand over the replications
    sns.lineplot(ax=ax[1], data=df, x="Replication", y="service_demand", hue="endpoint", palette=palette)
    ax[1].get_legend().remove()
    ax[1].xaxis.set_major_locator(MultipleLocator(1))
    ax[1].set_title("Service Demand over replications by endpoint")
    ax[1].set_ylabel("Service Demand")

    plt.savefig(f"{dirpath}/experiment_course.svg", bbox_inches="tight")
    plt.close()

def visualize_utilization(dirpath: str, df: pd.DataFrame):

    ax = sns.barplot(data=df, y="endpoint", x="mean_utilization", orient="y")
    ax.yaxis.set_major_locator(FixedLocator(ax.get_yticks()))
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7)
    ax.set_ylabel("Endpoint")
    ax.set_xlabel("Utilization")
    plt.suptitle("Mean utilization of all replications over endpoints")
    plt.savefig(f"{dirpath}/utilization.svg", bbox_inches="tight")
    plt.close()

def visualize_demand(dirpath: str, df: pd.DataFrame):

    ax = sns.barplot(data=df, y="endpoint", x="service_demand", orient="y")
    ax.yaxis.set_major_locator(FixedLocator(ax.get_yticks()))
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7)
    ax.set_xlabel("Service Demand")
    ax.set_ylabel("Endpoint")
    plt.savefig(f"{dirpath}/service_demands.svg", bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    main()
