#!/bin/bash

SPARK_CONTAINER="hadoop"

CHECKPOINTS=(
   "/tmp/spark_checkpoints/moving"
   "/tmp/spark_checkpoints/zscore"
   "/tmp/spark_checkpoints/load"
)

for path in "${CHECKPOINTS[@]}"; do
    echo " - Removing $path"
    docker exec "$SPARK_CONTAINER" rm -rf "$path"
done
