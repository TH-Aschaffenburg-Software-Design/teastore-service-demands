import datetime as dt
import json
import sys

from prometheus_api_client import MetricRangeDataFrame, PrometheusConnect
from properties.properties import get_property

PROMETHEUS_URL = f'{get_property("prometheus.ip")}:{get_property("prometheus.port")}'


def main():

    run_duration = 100
    warmup_before_run = 20
    request_index = int(sys.argv[1])
    time = dt.datetime.fromisoformat(sys.argv[2])
    result_file = sys.argv[3]

    requests = []
    with open("generated/callArray.json", "r") as read_file:
        requests: list[dict[str, str]] = json.load(read_file)

    call = requests[request_index]

    service = call["endpoint"].split(".")[-1].split("/")[0]
    prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
    query = f'rate(container_cpu_usage_seconds_total{{namespace="teastore", container!=""}}[1m])'
    start_time = time + dt.timedelta(seconds=warmup_before_run)
    end_time = start_time + dt.timedelta(seconds=run_duration)
    result = prom.custom_query_range(query, start_time, end_time, "1")

    df = MetricRangeDataFrame(result)

    df_service = df[df["container"] == f"teastore-{service}"]
    rps = call["rate"]
    mean = df_service["value"].mean()
    output_line = (
        ",".join(
            [
                service,
                get_endpoint_string(call),
                str(rps),
                str(mean),
            ]
        )
        + "\n"
    )

    with open(result_file, "a") as a_file:
        a_file.write(output_line)


def get_endpoint_string(call: dict[str, str]):

    endpoint = call["endpoint"].split(".")[-1]
    return f"{call["method"]} {endpoint}{call["path"]}"


if __name__ == "__main__":
    main()
