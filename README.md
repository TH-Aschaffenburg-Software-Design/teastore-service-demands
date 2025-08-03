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
3. Adjust the `teastore.yml` manifest (e.g. the resource limits)
4. Apply the `teastore.yml` manifest
5. Setup kube-state-metrics and configure it to export metrics to prometheus


#### On the load generation machine:

1. Install Python 3
2. Install requirements.txt into a local virtual environment `.venv`
3. Copy the content of directory `load_generation_machine/` to the machine and `cd` into it
4. Enter all required properties into the `properties/setup.properties` file
5. Warmup the TeaStore for several hours with `warmup.sh` (use the screen utility to keep the session alive)
6. Install k6 https://grafana.com/docs/k6/latest/set-up/install-k6
7. Build a k6 binary with the extensions `xk6-file` and `xk6-fasthttp` and place it next to `calibration.sh` https://grafana.com/docs/k6/latest/extensions/build-k6-binary-using-go/
9. Run the experiment script `calibration.sh <number_runs>` (Specify the number of runs, use the screen utility)
10. Find the outputs in the generated folder `outputs/<TIMESTAMP>`

### Outputs

- `k6_log.log` Log file of k6 load generator. Should be empty, otherwise, parameters such as the arrival rates or virtual users have to be adjusted
- `times.csv` Log file of which endpoint was executed at which time. Can be used to query prometheus with the timestamps.
- `result.csv` Results during the experiment. Each line contains the information of one endpoint run (100s)
- `demands.csv` The mean service demands for each endpoint over all replications.
- `utilization.png` A diagram of the mean utilization during the measurements. The utilization should be medium, e.g. between 0.3 and 0.7. Adjust arrival rates accordingly.

### Application to MiSim

The `misim` folder contains all files needed to run a [MiSim](https://github.com/Cambio-Project/MiSim) simulation of TeaStore.

To insert your own service demands:

- Find a factor to scale the service demands to integer level (e.g. 10000)
- Insert the service demands into the `architecture_model.json`
- Scale the capacity of each service (originally 1) by the same factor.
