# InfluxDB Data Schemas

## Database Configuration
- **Organization**: orb
- **Bucket**: orb_metrics
- **Token**: orb-secret-token

## Measurements

### 1. responsiveness
Network responsiveness metrics with microsecond precision.

| Field | Type | Description |
|-------|------|-------------|
| lag_avg_us | float | Average lag in microseconds |
| latency_avg_us | float | Average latency in microseconds |

| Tag | Description |
|-----|-------------|
| orb_id | Unique identifier for the Orb device |
| orb_name | Human-readable name of the Orb |
| orb_version | Software version running on the Orb |
| network_name | Name of the network being monitored |
| network_type | Type of network (e.g., WiFi, Ethernet) |
| country_code | ISO country code |
| city | City location |
| isp_name | Internet Service Provider name |
| network_state | Current network state |
| pingers | Active pinger configuration |

**Collection Intervals**: 1s, 15s, 1m

### 2. scores
Calculated performance scores (0-100 scale).

| Field | Type | Description |
|-------|------|-------------|
| orb_score | float | Overall Orb performance score |
| responsiveness_score | float | Network responsiveness score |
| reliability_score | float | Connection reliability score |
| speed_score | float | Network speed score |

| Tag | Description |
|-----|-------------|
| orb_id | Unique identifier for the Orb device |
| orb_name | Human-readable name of the Orb |
| orb_version | Software version running on the Orb |
| network_name | Name of the network being monitored |
| network_type | Type of network (e.g., WiFi, Ethernet) |
| country_code | ISO country code |
| city | City location |
| isp_name | Internet Service Provider name |
| network_state | Current network state |
| pingers | Active pinger configuration |
| score_version | Version of the scoring algorithm |

**Collection Interval**: 1m

### 3. speed_results
Speed test results for upload/download performance.

| Field | Type | Description |
|-------|------|-------------|
| download_kbps | float | Download speed in kilobits per second |
| upload_kbps | float | Upload speed in kilobits per second |

| Tag | Description |
|-----|-------------|
| orb_id | Unique identifier for the Orb device |
| orb_name | Human-readable name of the Orb |
| orb_version | Software version running on the Orb |
| network_name | Name of the network being monitored |
| network_type | Type of network (e.g., WiFi, Ethernet) |
| country_code | ISO country code |
| city | City location |
| isp_name | Internet Service Provider name |

**Collection Interval**: Variable (based on speed test execution)

### 4. web_responsiveness
Web-specific performance metrics.

| Field | Type | Description |
|-------|------|-------------|
| ttfb_us | float | Time to First Byte in microseconds |
| dns_us | float | DNS resolution time in microseconds |

| Tag | Description |
|-----|-------------|
| orb_id | Unique identifier for the Orb device |
| orb_name | Human-readable name of the Orb |
| orb_version | Software version running on the Orb |
| network_name | Name of the network being monitored |
| network_type | Type of network (e.g., WiFi, Ethernet) |
| country_code | ISO country code |
| city | City location |
| isp_name | Internet Service Provider name |

**Collection Interval**: 30s

## API Endpoints

Base URL: `http://{hostname}:{port}/api/v2/datasets/`

- `responsiveness_{interval}.json?id={collector_id}` - Intervals: 1s, 15s, 1m
- `scores_{interval}.json?id={collector_id}` - Interval: 1m
- `speed_results.json?id={collector_id}`
- `web_responsiveness_results.json?id={collector_id}`