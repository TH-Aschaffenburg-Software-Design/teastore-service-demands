import json
import os
import re
import sys
from collections.abc import Iterator

import pandas as pd
from utils import get_service_ip

dirpath = sys.argv[1]

config_file = "data_generation/requestConfig.json"
flat_file = "generated/requests.json"
results_file = f"{dirpath}/results.csv"

with open(config_file, "r") as read_file:
    request_config: dict = json.load(read_file)

options: dict[str, str] = request_config["options"]
services: dict[str, dict[str, list[dict[str, str | int]]]] = request_config["services"]

START_RATE = options["start_rate"]
TARGET_UTILIZATION = options["target_utilization"]

df = None
if os.path.exists(results_file):
    df = pd.read_csv(results_file)
    df["replication"] = df["replication"].astype("int64")
    df = df[df["replication"] == df["replication"].max()]
    max_total_demand = df["max_total_demand"]
    df["new_rate"] = (TARGET_UTILIZATION // max_total_demand).astype("int64")

request_list = []
query_param_sub = re.compile(r"={.+?}")
path_param_sub = re.compile(r"[{}]")

for service, endpoints in services.items():
    ip = get_service_ip(service)
    service_url = f"http://{ip}:8080/tools.descartes.teastore.{service}/rest/"
    service_df = df[df["service"] == service]
    for endpoint_name, requests in endpoints.items():
        endpoint = service_url + endpoint_name
        for request in requests:
            method = request.get("method", "GET")
            path = request.get("path", "")
            request_name = request.get("name")
            new_rate_series = service_df[service_df["endpoint"] == request_name]["new_rate"]
            if len(new_rate_series) == 1:
                new_rate = new_rate_series.item()
            else:
                new_rate = request.get("rate", START_RATE)
            request_list.append({
                "endpoint": endpoint,
                "method": method,
                "path": path,
                "body": request.get("body"),
                "rate": new_rate,
                "key": "_".join([service, request_name]),
                "service": service,
                "name": request_name
            })

with open(flat_file, "w") as write_file:
    json.dump(request_list, write_file, indent=4)
