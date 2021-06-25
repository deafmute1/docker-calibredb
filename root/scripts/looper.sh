#!/usr/bin/env bash

# Runs some bash command every $1 minutes. The remaining paramters passed are interpreted as the command

time="$1"
shift
comm="$@"

while true; do 
  bash "$comm"
  sleep "$time"
done 
