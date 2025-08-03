#!/bin/bash

namespace=teastore

ip=$(properties/get_property.sh kubernetes.master.ip | tr -d '[:space:]')
user=$(properties/get_property.sh kubernetes.master.user | tr -d '[:space:]')

ssh $user@$ip "kubectl get pods -n $namespace -o wide --field-selector='status.phase==Running' | grep 'teastore-$1' | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}'"
