#!/bin/bash

cd "$(dirname "$0")/cris"

echo "🛑 Stopping old CRIS containers..."
docker compose down -v

echo "🧹 Cleaning unused Docker volumes..."
docker volume prune -f

echo "🚀 Starting CRIS environment..."
docker compose up -d

echo "⏳ Waiting for Kafka listener to open..."
while ! (echo > /dev/tcp/localhost/9092) >/dev/null 2>&1; do
  sleep 1
done

echo "⏳ Waiting for Kafka server to finish initialization..."
sleep 20   # <-- CRITICAL!!!

echo "📡 Starting Transactions Producer..."
python3 ingestion/streaming/kafka_producers/transaction_producer.py
