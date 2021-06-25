#!/usr/bin/env bash

# Runs some bash script, $1 every $2 minutes.

while true; do 
  bash "$1"
  sleep "$2"
done 
