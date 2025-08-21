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

RESULTS_FILE = "results.csv"
PROMETHEUS_URL = get_property("prometheus.url")

def main():

    requests = []
    with open("generated/requests.json", "r") as read_file:
        requests: list[dict[str, str]] = json.load(read_file)

    call = requests[REQUEST_INDEX]
    service = call["endpoint"].split(".")[-1].split("/")[0]

    raw_utilization = retrieve_utilization(PROMETHEUS_URL, TIME, service)
    rps = call["rate"]

    utilization = raw_utilization * 0.6 # Normalize to resource limit
    mean_utilization = utilization.mean()
    std_utilization = utilization.std()
    service_demand = mean_utilization / rps # Service Demand Law

    result_df = pd.read_csv(f"{DIRPATH}/{RESULTS_FILE}", index_col=False)
    result_df.loc[len(result_df)] = [
                service,
                get_endpoint_string(call),
                TIME.strftime("%Y-%m-%dT%H:%M:%S%:z"),
                rps,
                mean_utilization,
                std_utilization,
                service_demand
            ]
    generate_files(DIRPATH, result_df)

def retrieve_utilization(prometheus_url: str, time: dt.datetime, service: str) -> pd.Series:

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

def get_endpoint_string(call: dict[str, str]):

    endpoint = call["endpoint"].split(".")[-1]
    return f"{call["method"]} {endpoint}{call["path"]}"

if __name__ == "__main__":
    main()
