#!/bin/bash

# CONFIG
KAFKA_CONTAINER="broker"
KAFKA_BIN="/opt/kafka/bin/kafka-topics.sh"
KAFKA_BOOTSTAP_SERVER="broker:9092"

TOPICS=(
    "btc-price"
    "btc-price-moving"
    "btc-price-zscore"
)

for topic in "${TOPICS[@]}"; do
    echo "Deleting topic: $topic"
    docker exec -it "$KAFKA_CONTAINER" "$KAFKA_BIN" --bootstrap-server "$KAFKA_BOOTSTAP_SERVER" --delete --topic "$topic"
done

for topic in "${TOPICS[@]}"; do
    while docker exec -it "$KAFKA_CONTAINER" "$KAFKA_BIN" --bootstrap-server "$KAFKA_BOOTSTAP_SERVER" --list | grep -q "^$topic$"; do
        echo "   Waiting for topic $topic to be deleted..."
        sleep 2
    done
done

for topic in "${TOPICS[@]}"; do
    docker exec -it "$KAFKA_CONTAINER" "$KAFKA_BIN" --bootstrap-server "$KAFKA_BOOTSTAP_SERVER" \
        --create --topic "$topic" --partitions 1 --replication-factor 1
done
