#!/bin/bash

docker cp transform-moving.py hadoop:/home/transform-moving.py
docker cp transform-zscore.py hadoop:/home/transform-zscore.py
docker cp load.py hadoop:/home/load.py
docker cp .env hadoop:/home/.env

docker exec hadoop pip install dotenv

docker exec hadoop spark-submit \
    --master local[*] \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    /home/transform-moving.py &

sleep 5

docker exec hadoop spark-submit \
    --master local[*] \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    /home/transform-zscore.py &

sleep 5

docker exec hadoop spark-submit \
    --master local[*] \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.5.0 \
    /home/load.py &

wait
