// Schema Exploration Query for Orb Metrics
// Run this on your TIG machine with:
// docker exec influxdb influx query -f /path/to/explore-schema.flux > schema-output.txt

// 1. List all measurements
measurements = from(bucket: "orb_metrics")
  |> range(start: -7d)
  |> group()
  |> distinct(column: "_measurement")
  |> keep(columns: ["_measurement"])

measurements
  |> yield(name: "measurements")

// 2. Get all fields for each measurement
fields_responsiveness = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "responsiveness")
  |> group()
  |> distinct(column: "_field")
  |> keep(columns: ["_field"])

fields_responsiveness
  |> yield(name: "fields_responsiveness")

fields_scores = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "scores")
  |> group()
  |> distinct(column: "_field")
  |> keep(columns: ["_field"])

fields_scores
  |> yield(name: "fields_scores")

fields_speed = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "speed_results")
  |> group()
  |> distinct(column: "_field")
  |> keep(columns: ["_field"])

fields_speed
  |> yield(name: "fields_speed_results")

fields_web = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "web_responsiveness")
  |> group()
  |> distinct(column: "_field")
  |> keep(columns: ["_field"])

fields_web
  |> yield(name: "fields_web_responsiveness")

// 3. Get all tags (dimensions)
tags = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "responsiveness")
  |> limit(n: 1)
  |> keys()
  |> filter(fn: (r) => r._value != "_time" and r._value != "_value" and r._value != "_field" and r._value != "_measurement" and r._value != "_start" and r._value != "_stop")

tags
  |> yield(name: "available_tags")

// 4. Get sample tag values for key dimensions
orb_names = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "responsiveness")
  |> group()
  |> distinct(column: "orb_name")
  |> keep(columns: ["orb_name"])

orb_names
  |> yield(name: "orb_names")

network_types = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "responsiveness")
  |> group()
  |> distinct(column: "network_type")
  |> keep(columns: ["network_type"])

network_types
  |> yield(name: "network_types")

cities = from(bucket: "orb_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "responsiveness")
  |> group()
  |> distinct(column: "city")
  |> keep(columns: ["city"])

cities
  |> yield(name: "cities")

// 5. Get recent sample data
sample_data = from(bucket: "orb_metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "responsiveness" and r._field == "latency_avg_us")
  |> limit(n: 5)

sample_data
  |> yield(name: "sample_recent_data")