import json
import re
from utils import get_service_ip

call_hierarchy_file = "data_generation/callHierarchy.json"
call_array_file = "generated/callArray.json"

with open(call_hierarchy_file, "r") as read_file:
    call_hierarchy: dict = json.load(read_file)

options: dict[str, str] = call_hierarchy["options"]
services: dict[str, dict[str, list[dict[str, str | int]]]] = call_hierarchy["services"]
call_array = []

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
            call_array.append({
                "endpoint": endpoint,
                "method": method,
                "path": path,
                "body": request.get("body"),
                "rate": request.get("rate", options["default_rate"]),
                "name": request_name
            })

with open(call_array_file, "w") as write_file:
    json.dump(call_array, write_file, indent=4)
