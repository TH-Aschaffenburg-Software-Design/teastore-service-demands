#!/bin/sh

# The script is designed to be canceled anytime

start_date=$(date -Ih | grep -Eo "[^+]+" | head -1)
output_dir="outputs/$start_date"

result_file="$output_dir/results.csv"
k6_log_file="$output_dir/k6.log"
times_csv_file="$output_dir/times.csv"

mkdir -p $output_dir

# Add header to output csv files
echo "service,endpoint,rps,mean_utilization,std_utilization,service_demand" > $result_file
echo "timestamp,call_index" > $times_csv_file

source .venv/bin/activate
export PYTHONPATH=$(pwd)

# Generate session blobs file if it does not exist
if [ ! -f "generated/sessionBlobs.json" ] || [ ! -f "generated/products.json" ]; then

    python3 data_generation/generate_resources.py
fi

replications=${1:-3}

for i in $(seq 1 $replications) ; do # Replications

    # Recreate fresh database
    persistence_ip=$(scripts/get_service_ip.sh persistence)
    curl -s --request GET --location "http://$persistence_ip:8080/tools.descartes.teastore.persistence/rest/generatedb"
    python3 data_generation/generate_requests.py $output_dir

    for i in $(seq 0 31) ; do # Endpoints
        echo "$i"
        time=$(date -Iseconds)
        ./k6 run --no-usage-report --log-output file=$k6_log_file scripts/calibration.js -e REQUEST=$i
        echo "$time,$i" >> $times_csv_file
        python3 scripts/process_results.py $i $time $output_dir
        sleep 5  # Pause between runs
    done
done
