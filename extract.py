from concurrent.futures.thread import ThreadPoolExecutor
import requests
import json
import time
import threading
import logging
from datetime import datetime, timezone
from queue import Queue, Empty
from kafka import KafkaProducer

# --- Configuration ---
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
KAFKA_BROKER = 'localhost:9094'
KAFKA_TOPIC_EXTRACT = 'btc-price'
TARGET_INTERVAL_SECONDS = 0.1
NUM_THREADS = 4
API_TIMEOUT_SECONDS = 2

def create_kafka_producer():
    """Create and return a Kafka producer"""
    print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=2,
        )
        print(f"Successfully connected to Kafka broker and ready to send messages to topic '{KAFKA_TOPIC_EXTRACT}'.")
        return producer
    except Exception as e:
        print(f"Error: Cannot connect to Kafka broker: {e}")
        return None

api_session = requests.Session()

def fetch_price():
    """Fetch BTC price from Binance API"""
    try:
        response = api_session.get(BINANCE_API_URL, timeout=API_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        if 'symbol' in data and 'price' in data:
            try:
                data['price'] = float(data['price'])
                return data
            except ValueError:
                print(f"Error: 'price' is not a valid number: {data.get('price')}")
                return None
        else:
            print("Error: API response format is invalid.")
            return None
    except Exception as e:
        print(f"Error calling API: {e}")
    return None

def format_timestamp(precision_ms=100):
    """Format current timestamp with specified millisecond precision"""
    event_time = datetime.now(timezone.utc)
    milliseconds = event_time.microsecond // 1000
    rounded_milliseconds = milliseconds - (milliseconds % precision_ms)
    event_time = event_time.replace(microsecond=rounded_milliseconds * 1000)
    return event_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

class LastValueQueue(Queue):
    """Queue that only keeps the most recent value"""
    def put(self, item, block=True, timeout=None):
        with self.mutex:
            self.queue.clear()
            self.queue.append(item)
            self.unfinished_tasks = len(self.queue)
            self.not_empty.notify()

data_queue = LastValueQueue()

def fetch_thread():
    """Thread function to continuously fetch price data"""
    while True:
        data = fetch_price()
        if data:
            data_queue.put(data)
        time.sleep(0.01)

def main():
    """Main function to run the price extractor"""
    producer = create_kafka_producer()
    if not producer:
        print("Exiting program because Kafka Producer could not be created.")
        return

    try:
        # Start fetch threads
        executor = ThreadPoolExecutor(max_workers=NUM_THREADS)
        for _ in range(NUM_THREADS):
            executor.submit(fetch_thread)

        last_send = 0

        while True:
            try:
                data = data_queue.get(timeout=5)

                now = time.time()
                sleep_time = TARGET_INTERVAL_SECONDS - (now - last_send)

                if sleep_time > 0:
                    time.sleep(sleep_time)

                last_send = time.time()

                data['timestamp'] = format_timestamp()

                producer.send(KAFKA_TOPIC_EXTRACT, value=data)

            except Empty:
                break

    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        if producer:
            print("Closing Kafka producer...")
            producer.flush(timeout=10)
            producer.close()
            print("Kafka producer closed.")
        if 'api_session' in locals() and api_session:
            print("Closing API session...")
            api_session.close()
            print("API session closed.")

if __name__ == "__main__":
    main()
