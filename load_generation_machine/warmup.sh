source .venv/bin/activate

host=${properties/get_property kubernetes.master.ip}

locust --config scripts/locust.conf --host $host:30080
