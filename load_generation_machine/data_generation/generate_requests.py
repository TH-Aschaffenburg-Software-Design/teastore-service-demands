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
demands_file = f"{dirpath}/service_demands.csv"

with open(config_file, "r") as read_file:
    request_config: dict = json.load(read_file)

options: dict[str, str] = request_config["options"]
services: dict[str, dict[str, list[dict[str, str | int]]]] = request_config["services"]

START_RATE = options["start_rate"]
TARGET_UTILIZATION = options["target_utilization"]

rate_iter: Iterator | None = None
if os.path.exists(demands_file):
    df = pd.read_csv(demands_file)
    new_rate = TARGET_UTILIZATION // df["service_demand"]
    rate_iter = new_rate.__iter__()

request_list = []
query_param_sub = re.compile(r"={.+?}")
path_param_sub = re.compile(r"[{}]")

for service, endpoints in services.items():
    ip = get_service_ip(service)
    service_url = f"http://{ip}:8080/tools.descartes.teastore.{service}/rest/"
    for endpoint_name, requests in endpoints.items():
        endpoint = service_url + endpoint_name
        for request in requests:
            method = request.get("method", "GET")
            path = request.get("path", "")
            request_name = re.sub(path_param_sub, "", re.sub(query_param_sub, "", f"{method}_{service}-{endpoint_name}{path}")).replace("?", "_").replace("/", "-").replace("&", "-").replace("=", "")
            request_list.append({
                "endpoint": endpoint,
                "method": method,
                "path": path,
                "body": request.get("body"),
                "rate": rate_iter.__next__() if rate_iter is not None else START_RATE,
                "name": request_name
            })

with open(flat_file, "w") as write_file:
    json.dump(request_list, write_file, indent=4)
