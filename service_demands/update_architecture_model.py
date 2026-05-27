import json
import sys

import pandas as pd

architecture_file = sys.argv[1]
service_demands_file = sys.argv[2]

print(architecture_file)
print(service_demands_file)

capacity = 10000000
service_demands = pd.read_csv(service_demands_file)

service_demands["service_demand"] = (
    (service_demands["service_demand"].astype("float64") * capacity).round()
).astype("int64")

with open(architecture_file, "r") as r_file:
    architecture_model = json.load(r_file)

for service in architecture_model["microservices"]:
    service["capacity"] = capacity
    service_df = service_demands[
        service_demands["service"].str.contains(service["name"])
    ]

    for operation in service["operations"]:

        operation["demand"] = service_df[service_df["operation"] == operation["name"]][
            "service_demand"
        ].item()

with open(architecture_file, "w") as w_file:
    json.dump(architecture_model, w_file, indent=4)
