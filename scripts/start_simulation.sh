#!/bin/bash

# Define variables to hold the parsed values
N_ADDED_ROWS_PER_STEP=
N_SIM_TIME_SECONDS=
N_PAUSE_TIME_SECONDS=

# Function to parse arg=val format
parse_arg_val() {
    local arg_val=$1
    local arg=${arg_val%%=*}
    local val=${arg_val#*=}
    case $arg in
        N_ADDED_ROWS_PER_STEP) N_ADDED_ROWS_PER_STEP=$val ;;
        N_SIM_TIME_SECONDS) N_SIM_TIME_SECONDS=$val ;;
        N_PAUSE_TIME_SECONDS) N_PAUSE_TIME_SECONDS=$val ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
}

# Loop through all command line arguments
for arg_val in "$@"; do
    parse_arg_val "$arg_val"
done

# Check if all required arguments are set
if [ -n "$N_ADDED_ROWS_PER_STEP" ] && [ -n "$N_SIM_TIME_SECONDS" ] && [ -n "$N_PAUSE_TIME_SECONDS" ]; then
    echo "All keywords are present and have values."
else
    echo "Not all keywords are present or have values."
fi

# Print the parsed values
echo "N_ADDED_ROWS_PER_STEP: $N_ADDED_ROWS_PER_STEP"
echo "N_SIM_TIME_SECONDS: $N_SIM_TIME_SECONDS"
echo "N_PAUSE_TIME_SECONDS: $N_PAUSE_TIME_SECONDS"

echo "starting cdc simulation"
echo python scripts/postgres/simulate_cdc.py $N_ADDED_ROWS_PER_STEP $N_SIM_TIME_SECONDS $N_PAUSE_TIME_SECONDS
python scripts/postgres/simulate_cdc.py $N_ADDED_ROWS_PER_STEP $N_SIM_TIME_SECONDS $N_PAUSE_TIME_SECONDS