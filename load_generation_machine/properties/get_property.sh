#!/bin/bash

line=$(cat properties/setup.properties | grep $1)
value=${str#*=}

echo -n $value
