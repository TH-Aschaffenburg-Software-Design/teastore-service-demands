source .venv/bin/activate

host=http://$(properties/get_property.sh kubernetes.master.ip):30080

locust --config scripts/locust.conf --host $host
