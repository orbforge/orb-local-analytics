#!/bin/bash

echo "=== Unique Values from Orb Metrics ==="
echo

echo "Orb Devices:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "responsiveness") |> distinct(column: "orb_name") |> group() |> sort()'

echo -e "\nCities:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "responsiveness") |> distinct(column: "city") |> group() |> sort()'

echo -e "\nISPs:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "responsiveness") |> distinct(column: "isp_name") |> group() |> sort()'

echo -e "\nNetwork Types:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "responsiveness") |> distinct(column: "network_type") |> group() |> sort()'

echo -e "\nNetwork States:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "responsiveness") |> distinct(column: "network_state") |> group() |> sort()'

echo -e "\nAll Fields in responsiveness:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "responsiveness") |> distinct(column: "_field") |> group() |> sort()'

echo -e "\nAll Fields in scores:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "scores") |> distinct(column: "_field") |> group() |> sort()'

echo -e "\nAll Fields in speed_results:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "speed_results") |> distinct(column: "_field") |> group() |> sort()'

echo -e "\nAll Fields in web_responsiveness:"
docker exec influxdb influx query 'from(bucket: "orb_metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "web_responsiveness") |> distinct(column: "_field") |> group() |> sort()'