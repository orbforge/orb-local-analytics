# Orb Local Analytics - Technical Documentation

## Overview

This repository implements a local analytics solution for Orb network monitoring devices using the TIG (Telegraf, InfluxDB, Grafana) stack. It collects network performance metrics from multiple Orb devices and visualizes them in real-time dashboards.

## Architecture

### Core Components

1. **InfluxDB 2.7** - Time-series database storing all metrics
2. **Telegraf 1.30** - Data collection agent polling Orb APIs
3. **Grafana 10.3.1** - Visualization and dashboard platform
4. **Python Configure Script** - Automated configuration generator

### Data Flow

```
Orb Devices (HTTP APIs) → Telegraf (Polling) → InfluxDB → Grafana Dashboards
```

## InfluxDB Data Structure

### Database Configuration
- **Organization**: `orb`
- **Bucket**: `orb_metrics`
- **Token**: `orb-secret-token`
- **Username**: `admin`
- **Password**: `orbsupersecret`

### Measurements and Fields

#### 1. `responsiveness` Measurement
Tracks network responsiveness metrics with microsecond precision.

**Fields:**
- `lag_avg_us` - Average lag in microseconds
- `latency_avg_us` - Average latency in microseconds
- Additional fields from the API response (auto-discovered)

**Tags (Dimensions):**
- `orb_id` - Unique identifier for the Orb device
- `orb_name` - Human-readable name of the Orb
- `orb_version` - Software version running on the Orb
- `network_name` - Name of the network being monitored
- `network_type` - Type of network (e.g., WiFi, Ethernet)
- `country_code` - ISO country code
- `city` - City location
- `isp_name` - Internet Service Provider name
- `network_state` - Current network state
- `pingers` - Active pinger configuration

**Collection Intervals:** 1s, 15s, 1m (configurable)

#### 2. `scores` Measurement
Contains calculated performance scores (0-100 scale).

**Fields:**
- `orb_score` - Overall Orb performance score
- `responsiveness_score` - Network responsiveness score
- `reliability_score` - Connection reliability score
- `speed_score` - Network speed score
- Additional score fields from the API

**Tags (Dimensions):**
- All tags from `responsiveness` measurement
- `score_version` - Version of the scoring algorithm

**Collection Interval:** 1m (typical)

#### 3. `speed_results` Measurement
Speed test results for upload/download performance.

**Fields:**
- `download_kbps` - Download speed in kilobits per second
- `upload_kbps` - Upload speed in kilobits per second
- Additional speed metrics from the API

**Tags (Dimensions):**
- Same as `responsiveness` measurement (excluding `pingers`)

**Collection Interval:** Variable (based on speed test execution)

#### 4. `web_responsiveness` Measurement
Web-specific performance metrics.

**Fields:**
- `ttfb_us` - Time to First Byte in microseconds
- `dns_us` - DNS resolution time in microseconds
- Additional web timing metrics from the API

**Tags (Dimensions):**
- Same as `responsiveness` measurement (excluding `network_state` and `pingers`)

**Collection Interval:** 30s (typical)

### Data Retention

Default retention is managed by InfluxDB's bucket configuration. No custom retention policies are defined in the base configuration.

## Grafana Dashboard Structure

### Dashboard: "Orb Metrics Overview"
Located at: `/grafana/dashboards/orb-metrics-overview.json`

#### Panel 1: Scores (Time Series)
- **Query**: Aggregates all score fields with 1-minute mean windows
- **Fields Displayed**: `orb_score`, `responsiveness_score`, `reliability_score`, `speed_score`
- **Visualization**: Line chart with no fill
- **Y-Axis**: 0-100 scale (percentage)

#### Panel 2: Responsiveness (Time Series)
- **Query**: Shows lag and latency metrics with 15-second aggregation
- **Fields Displayed**: `lag_avg_us`, `latency_avg_us`
- **Unit**: Microseconds (µs)
- **Visualization**: Line chart

#### Panel 3: Speed (Time Series)
- **Query**: Download/upload speeds with 1-minute aggregation
- **Fields Displayed**: `download_kbps`, `upload_kbps`
- **Unit**: Decimal bytes (deckbytes)
- **Span Nulls**: 2 hours (handles intermittent speed tests)

#### Panel 4: Web Responsiveness (Time Series)
- **Query**: Web timing metrics with 15-second aggregation
- **Fields Displayed**: `ttfb_us`, `dns_us`
- **Unit**: Microseconds (µs)
- **Span Nulls**: 2 minutes

## Configuration System

### `configure.py` Script

The configuration script generates `telegraf.conf` dynamically based on:
1. **Orb Inputs**: Hostname and port combinations
2. **Dataset Selection**: Which metrics to collect
3. **Collector ID**: Random 5-digit identifier for tracking

### Telegraf Configuration Templates

Located in `/templates/`:

1. **`agent.conf`** - Base Telegraf agent settings
   - 30-second intervals
   - 1000 metric batch size
   - 10000 metric buffer limit

2. **`input_*.conf`** - HTTP input configurations for each metric type
   - Parameterized with `{url}`, `{collector_id}`, `{interval}`
   - JSON parsing with timestamp extraction
   - Tag key definitions for dimensions

3. **`output.conf`** - InfluxDB v2 output configuration

### Generated Configuration

The script creates `telegraf.conf` by:
1. Adding agent configuration
2. Creating HTTP inputs for each orb/dataset combination
3. Appending InfluxDB output configuration

## Orb API Endpoints

### Base URL Format
`http://{hostname}:{port}/api/v2/datasets/`

### Endpoints
1. `responsiveness_{interval}.json?id={collector_id}`
   - Intervals: 1s, 15s, 1m
2. `scores_{interval}.json?id={collector_id}`
   - Interval: 1m
3. `speed_results.json?id={collector_id}`
4. `web_responsiveness_results.json?id={collector_id}`

## Docker Compose Configuration

### Network
- Custom bridge network named `tig`
- All services communicate on this network

### Volumes
- `influxdb-data` - Persistent InfluxDB storage
- `grafana-data` - Persistent Grafana storage
- `./telegraf.conf` - Mounted Telegraf configuration
- `./grafana/provisioning` - Grafana provisioning configs
- `./grafana/dashboards` - Dashboard JSON files

### Service Dependencies
```
influxdb (base)
├── telegraf (depends on influxdb)
└── grafana (depends on influxdb)
```

## Grafana Provisioning

### Data Source
- **Name**: "Orb InfluxDB"
- **Type**: InfluxDB
- **Query Language**: Flux
- **Default**: Yes

### Dashboard Provider
- **Folder**: "Orb Dashboards"
- **Path**: `/etc/grafana/dashboards`
- **Update Interval**: 30 seconds
- **Editable**: Yes

## Usage Workflow

1. **Configure Orbs**
   ```bash
   ./configure.py
   ```
   - Select Orb hostnames/ports
   - Choose datasets to collect
   - Script generates `telegraf.conf`

2. **Configure Orb Cloud**
   - Apply generated JSON config to each Orb
   - Restart Orb sensors

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Access Grafana**
   - URL: http://localhost:3000
   - Default: admin/admin
   - Dashboard: Orb Dashboards → Orb Metrics Overview

5. **Restart After Changes**
   ```bash
   docker restart telegraf
   ```

## Creating Custom Grafana Dashboards

### Flux Query Examples

**Average Metric Over Time:**
```flux
from(bucket: "orb_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "responsiveness" and r._field == "latency_avg_us")
  |> aggregateWindow(every: 1m, fn: mean)
```

**Group by Orb:**
```flux
from(bucket: "orb_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "scores")
  |> group(columns: ["orb_name", "_field"])
```

**Filter by Location:**
```flux
from(bucket: "orb_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "responsiveness" and r.city == "San Francisco")
```

### Available Aggregations
- `mean`, `median`, `max`, `min`
- `count`, `sum`, `stddev`
- `first`, `last`
- `percentile` (e.g., 0.95 for 95th percentile)

### Dashboard Best Practices
1. Use appropriate time windows for each metric type
2. Set `spanNulls` based on collection intervals
3. Group by meaningful dimensions (orb_name, network_type, city)
4. Use thresholds for score visualizations (red < 50, yellow < 80, green >= 80)
5. Consider using stat panels for current values
6. Use table panels for multi-dimensional comparisons

## Troubleshooting

### Common Issues
1. **No Data in Grafana**
   - Check Telegraf logs: `docker logs telegraf`
   - Verify Orb API accessibility
   - Confirm Orb configuration matches

2. **Missing Metrics**
   - Ensure dataset is enabled in Orb config
   - Check collection interval timing
   - Verify InfluxDB bucket has data

3. **Dashboard Errors**
   - Confirm data source configuration
   - Check Flux query syntax
   - Verify field names match actual data

### Useful Commands
```bash
# View Telegraf logs
docker logs -f telegraf

# Check InfluxDB data
docker exec -it influxdb influx query 'from(bucket:"orb_metrics") |> range(start:-5m) |> limit(n:10)'

# Restart all services
docker-compose restart

# Full cleanup
docker-compose down -v --remove-orphans
```