#!/bin/bash

echo "=== InfluxDB Schema Exploration for Orb Metrics ==="
echo

echo "1. Available Measurements:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -7d) |> group() |> distinct(column: "_measurement") |> keep(columns: ["_measurement"])'

echo -e "\n2. Fields in 'responsiveness' measurement:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "responsiveness") |> group() |> distinct(column: "_field") |> keep(columns: ["_field"])'

echo -e "\n3. Fields in 'scores' measurement:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "scores") |> group() |> distinct(column: "_field") |> keep(columns: ["_field"])'

echo -e "\n4. Fields in 'speed_results' measurement:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "speed_results") |> group() |> distinct(column: "_field") |> keep(columns: ["_field"])'

echo -e "\n5. Fields in 'web_responsiveness' measurement:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "web_responsiveness") |> group() |> distinct(column: "_field") |> keep(columns: ["_field"])'

echo -e "\n6. Available Tags (from responsiveness measurement):"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "responsiveness") |> limit(n: 1) |> keys() |> filter(fn: (r) => r._value != "_time" and r._value != "_value" and r._value != "_field" and r._value != "_measurement" and r._value != "_start" and r._value != "_stop")'

echo -e "\n7. Orb Names:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "responsiveness") |> group() |> distinct(column: "orb_name") |> keep(columns: ["orb_name"]) |> limit(n: 20)'

echo -e "\n8. Cities:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "responsiveness") |> group() |> distinct(column: "city") |> keep(columns: ["city"]) |> limit(n: 20)'

echo -e "\n9. Network Types:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "responsiveness") |> group() |> distinct(column: "network_type") |> keep(columns: ["network_type"]) |> limit(n: 10)'

echo -e "\n10. Sample Recent Data:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -5m) |> filter(fn: (r) => r._measurement == "responsiveness" and r._field == "latency_avg_us") |> limit(n: 3)'