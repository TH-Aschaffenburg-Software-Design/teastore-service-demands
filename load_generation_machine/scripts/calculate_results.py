import datetime as dt
import json
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FixedLocator, MultipleLocator
from prometheus_api_client import MetricRangeDataFrame, PrometheusConnect
from properties.properties import get_property

PROMETHEUS_URL = get_property("prometheus.url")

request_index = int(sys.argv[1])
time = dt.datetime.fromisoformat(sys.argv[2])
dirpath = sys.argv[3]

def main():

    requests = []
    with open("generated/requests.json", "r") as read_file:
        requests: list[dict[str, str]] = json.load(read_file)

    call = requests[request_index]
    service = call["endpoint"].split(".")[-1].split("/")[0]

    raw_utilization = retrieve_utilization(service)
    rps = call["rate"]

    utilization = raw_utilization * 0.6 # Normalize to resource limit
    mean_utilization = utilization.mean()
    std_utilization = utilization.std()
    service_demand = mean_utilization / rps # Service Demand Law

    results_file = f"{dirpath}/results.csv"
    result_df = pd.read_csv(results_file, index_col=False)
    result_df.loc[len(result_df)] = [
                service,
                get_endpoint_string(call),
                rps,
                mean_utilization,
                std_utilization,
                service_demand
            ]
    
    result_df.to_csv(results_file, index=False)
    
    final_demand = result_df[["endpoint", "service_demand"]].drop_duplicates(subset="endpoint", keep="last")
    final_demand.to_csv(f"{dirpath}/service_demands.csv", index=False)

    visualize_utilization(result_df)
    visualize_demand(final_demand)
    
def retrieve_utilization(service: str) -> pd.Series:
    
    run_duration = 100
    warmup_before_run = 20

    prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
    query = f'rate(container_cpu_usage_seconds_total{{namespace="teastore", container!=""}}[1m])'
    start_time = time + dt.timedelta(seconds=warmup_before_run)
    end_time = start_time + dt.timedelta(seconds=run_duration)
    result = prom.custom_query_range(query, start_time, end_time, "1")

    df = MetricRangeDataFrame(result)
    df_service = df[df["container"] == f"teastore-{service}"]
    return df_service["value"]

def visualize_utilization(df: pd.DataFrame):

    # Plot utilization in latest replication to verify a medium utilization
    ax = sns.barplot(data=df.drop_duplicates(subset="endpoint", keep="last"), y="endpoint", x="mean_utilization", orient="y")
    ax.yaxis.set_major_locator(FixedLocator(ax.get_yticks()))
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7)
    ax.set_ylabel("Endpoint")
    ax.set_xlabel("Utilization")
    plt.suptitle("Mean utilization of all replications over endpoints")
    plt.savefig(f"{dirpath}/utilization.svg", bbox_inches="tight")
    plt.close()

    # Plot the course of utilization over the replications
    df["Replication"] = df.groupby("endpoint").cumcount() + 1
    ax = sns.lineplot(data=df, x="Replication", y="mean_utilization", hue="endpoint")
    ax.get_legend().remove()
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.set_title("Utilization over replications by endpoint")
    ax.set_ylabel("Utilization")
    plt.savefig(f"{dirpath}/utilization_course.svg", bbox_inches="tight")
    plt.close()

def visualize_demand(df: pd.DataFrame):

    # Plot service demand
    ax = sns.barplot(data=df, y="endpoint", x="service_demand", orient="y")
    ax.set_xlabel("Service Demand")
    ax.set_ylabel("Endpoint")
    plt.savefig(f"{dirpath}/service_demands.svg", bbox_inches="tight")
    plt.close()

def get_endpoint_string(call: dict[str, str]):

    endpoint = call["endpoint"].split(".")[-1]
    return f"{call["method"]} {endpoint}{call["path"]}"

if __name__ == "__main__":
    main()
