import datetime as dt
import json
import sys

import pandas as pd
from generate_results import generate_files
from prometheus_api_client import MetricRangeDataFrame, PrometheusConnect
from properties.properties import get_property

REQUEST_INDEX = int(sys.argv[1])
TIME = dt.datetime.fromisoformat(sys.argv[2])
DIRPATH = sys.argv[3]
REPETITION = sys.argv[4]

RESULTS_FILE = "results.csv"
PROMETHEUS_URL = get_property("prometheus.url")


def main():

    requests = []
    with open("generated/requests.json", "r") as read_file:
        requests: list[dict[str, str]] = json.load(read_file)

    call = requests[REQUEST_INDEX]
    service = call["endpoint"].split(".")[-1].split("/")[0]
    rps = call["rate"]

    df = retrieve_utilization(PROMETHEUS_URL, TIME)
    df["cpu_rate"] = df["cpu_rate"] / 1 # Normalize to resource limit
    max_total_demand = df["cpu_rate"].max() / rps

    service_utilization = df[df.index == f"teastore-{service}"]["cpu_rate"].item()

    service_demand = service_utilization / rps # Service Demand Law

    result_df = pd.read_csv(f"{DIRPATH}/{RESULTS_FILE}", index_col=False)
    result_df.loc[len(result_df)] = [
                REPETITION,
                service,
                call["name"],
                TIME.strftime("%Y-%m-%dT%H:%M:%S%:z"),
                rps,
                service_utilization,
                service_demand,
                max_total_demand
            ]
    generate_files(DIRPATH, result_df)

def retrieve_utilization(prometheus_url: str, time: dt.datetime) -> pd.DataFrame:

    run_duration = 100
    warmup_before_run = 20

    prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
    query = f'container_cpu_usage_seconds_total{{namespace="teastore", container!=""}}'
    start_time = time + dt.timedelta(seconds=warmup_before_run)
    end_time = start_time + dt.timedelta(seconds=run_duration)
    result = prom.custom_query_range(query, start_time, end_time, "1")

    df = MetricRangeDataFrame(result)
    df = df.drop_duplicates(["container", "value"], keep="first").reset_index()
    df = df.groupby("container").agg(first_timestamp=("timestamp", "first"),
          last_timestamp=("timestamp", "last"),
          first_cpu=("value", "first"),
          last_cpu=("value", "last"))

    df["duration_seconds"] = (
        df["last_timestamp"] - df["first_timestamp"]
    ).dt.total_seconds()

    df["cpu_rate"] = (
        df["last_cpu"] - df["first_cpu"]
    ) / df["duration_seconds"]
    return df


if __name__ == "__main__":
    main()
