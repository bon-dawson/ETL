# Cryptocurrency ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for cryptocurrency data. It extracts real-time Bitcoin price data from Binance API, processes it using Apache Spark, and stores the results in a MongoDB Atlas database.

## Project Overview

The ETL pipeline consists of three main components:

1. **Extract**: Fetches real-time BTC/USDT price data from Binance API and publishes it to a Kafka topic
2. **Transform**: Processes the raw data using Apache Spark to calculate:
   - Moving averages
   - Z-score anomaly detection
3. **Load**: Stores the processed data into MongoDB Atlas

## Prerequisites

- Docker and Docker Compose
- Python 3.12 or higher
- UV package manager (for Python dependency management)
- MongoDB Atlas account (for data storage)

## Setup and Running Instructions

### 1. Configure MongoDB Atlas

Before running the pipeline, you must configure the MongoDB Atlas connection with these two required settings:

```bash
MONGODB_DATABASE=<your_database_name>
MONGODB_URI=<your_mongodb_connection_uri>
```

> **Important**: Make sure to add your current IP address to the MongoDB Atlas IP allowlist in the Network Access settings.

### 2. Start the Infrastructure

First, start the required infrastructure (Kafka, Hadoop) using Docker Compose:

```bash
docker-compose up -d
```

### 3. Run the Transform and Load Pipeline

Make the run script executable and execute it:

```bash
chmod +x run.sh
./run.sh
```

### 4. Run the Extract Process

Start the data extraction process to produce data to the Kafka topic:

```bash
uv run extract.py

# or if you're using pip, install dependencies directly
python -m pip install requests kafka-python
python extract.py
```

This will fetch real-time BTC/USDT price data from Binance and publish it to the Kafka topic.

### 5. Monitor Kafka Topics

To view the data being published to the Kafka topic:

```bash
docker exec -it broker /opt/kafka/bin/kafka-console-consumer.sh --topic btc-price --bootstrap-server broker:9092 --from-beginning
```

### 6. View Results

You can connect to the MongoDB Atlas database to view the processed results using MongoDB Atlas UI or a MongoDB client like MongoDB Compass:

1. Login to your MongoDB Atlas account
2. Navigate to your cluster
3. Click on "Collections" and select your database and collection
4. You should see the processed cryptocurrency data with timestamps, prices, moving averages, and anomaly detection flags

### 7. Stop the Pipeline

When you're done, shut down all services:

```bash
docker-compose down
```

## Utilities

### Reset Kafka Topics

If you need to reset Kafka topics:

```bash
chmod +x reset_topic.sh
./reset_topic.sh
```

### Reset Spark Checkpoints

To reset Spark checkpoint directories:

```bash
chmod +x reset_checkpoint.sh
./reset_checkpoint.sh
```

## Project Dependencies

This project uses the following main technologies:
- Apache Kafka for data streaming
- Apache Spark for data processing
- MongoDB Atlas for cloud-based data storage
- Python for scripting

Python dependencies are managed via `pyproject.toml` and can be installed using UV.

## Monitoring

- Hadoop UI: http://localhost:9870
- Spark UI: http://localhost:4040
- Kafka: Accessible on localhost:9094

## Troubleshooting

- If the extract process fails to connect to Kafka, ensure that the broker is running and accessible
- If the Spark jobs fail, check the Spark UI for detailed error messages
- If data is not being stored in MongoDB Atlas:
  - Verify your MONGODB_URI setting is correct (including username, password, and connection parameters)
  - Check that your MONGODB_DATABASE name is correct
  - Ensure your MongoDB Atlas IP allowlist includes your current IP address
- If you receive authentication errors, verify your MongoDB Atlas credentials are correct
