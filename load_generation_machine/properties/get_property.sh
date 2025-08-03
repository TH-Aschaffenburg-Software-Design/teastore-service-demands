#!/bin/bash

line=${cat setup.properties | grep $1}
value=${str#*=}

echo -n $value
