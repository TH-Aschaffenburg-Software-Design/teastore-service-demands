#!/bin/bash

value=$(cat properties/setup.properties | grep $1 | cut -d "=" -f2)

echo $value
