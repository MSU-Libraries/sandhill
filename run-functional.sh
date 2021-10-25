#!/bin/bash

# Find directory where this script resides
CUR_DIR=$( dirname "$0" )
CUR_DIR=$( readlink -f "$CUR_DIR" )

# Go to the script directory
pushd $CUR_DIR

# Read in local env vars
source .env

# Set instance dir
INSTANCE_DIR=$CUR_DIR/instance
export INSTANCE_DIR

# Run the tests
pytest -m functional --no-cov -n 4

# Return
popd
