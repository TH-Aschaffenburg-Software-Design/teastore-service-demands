# Service Demands for TeaStore

This repository offers indirectly measured service demands of the [TeaStore](https://github.com/DescartesResearch/TeaStore) as well as scripts for reproduction.

## Service Demands

The service demands were calculated from directly measured CPU utilization of the TeaStore.

## Reproduction

### Hardware requirements

- Kubernetes cluster consisting of two machines minimum (One isolated for load generation)
- Make sure there are enough resources available to run the TeaStore
- Consider having an isolated kubernetes master node without scheduled pods for a stable deployment
- Setup ssh connection between the load generation machien and the kubernetes master

### Steps

#### On one of the machines

- Setup prometheus

#### On the kubernetes master:

1. Copy the content of directory `kubernetes_master/` to the machine
2. Create the namespace `teastore`
3. Adjust the `teastore.yml` manifest (e.g. the resource limits, node taints or garbage collection params)
4. Apply the `teastore.yml` manifest
5. Setup kube-state-metrics and configure it to export metrics to prometheus


#### On the load generation machine:

1. Install Python 3
2. Install requirements.txt into a local virtual environment `.venv`
3. Copy the content of directory `load_generation_machine/` to the machine and `cd` into it
4. Enter all required properties into the `properties/setup.properties` file
5. Warmup the TeaStore for several hours with `warmup.sh` (use the screen utility to keep the session alive)
6. Build a k6 binary with the extensions `xk6-file` and `xk6-fasthttp`
    - This requires either Go or Docker! Setting up Go can be tedious, so building with Docker is recommended.
    - Look into https://grafana.com/docs/k6/latest/extensions/ for detailed description
    - Place the binary next to `calibration.sh`
7. Run the experiment script `calibration.sh <number=3>` (Optional: specify the number of replications, use the screen utility)
8. Find the outputs in the generated folder `outputs/<TIMESTAMP>/`


### Outputs

- `k6_log.log` Log file of k6 load generator. Should be empty, otherwise, parameters such as the arrival rates or virtual users have to be adjusted
- `times.csv` Log file of which endpoint was executed at which time. Can be used to query prometheus with the timestamps.
- `result.csv` Results during the experiment. Each line contains the information of one endpoint run (100s)
- `service_demands.csv` & `service_demands.svg` The final service demands for each endpoint over all replications.
- `utilization.svg` A diagram of the final utilization by endpoint.
- `utilization_course.svg` The utilization by endpoint over the replications.

### How to control and adjust

- Resource limits should be applied depending on the environment's available resources. Adjust it in the `teastore.yml` file.
- Garbage collection params can be applied using the `CATALINA_OPTS` variable in the `teastore.yml`.
- The config file `data_generation/requestConfig.json` is used to specify the arrival rate for the first replication. For subsequent replications, the arrival rate is determined based on the service demands from the previous run and the specified target utilization. If the target utilization is never reached over multiple replications, lower it to a reachable value.

### Application to MiSim

The `misim` folder contains all files needed to run a [MiSim](https://github.com/Cambio-Project/MiSim) simulation of TeaStore.

To insert your own service demands:

- Find a factor to scale the service demands to integer level (e.g. 10000)
- Insert the service demands into the `architecture_model.json`
- Scale the capacity of each service (originally 1) by the same factor.
