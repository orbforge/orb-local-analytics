# orb-local-analytics
Tools and documentation for setting up local Orb Analytics

## Pre-Setup

1. Decide which Orb hostnames you'd like to pull data from
2. Run `./configure.py` to generate configs (`telegraf.conf` and Orb Cloud)
3. (optional) Confirm you can reach the orb at `http://localhost:8000/api/v2/datasets/responsiveness_15s.json?id=123` (example `localhost`, use orb hostname)

## Setup

1. Start services
```sh
docker-compose up -d
```

2. Go to http://localhost:3000 in your browser
3. Login with default grafana credentials (`admin` / `admin`)
4. Setup new password when prompted
5. Go to "Dashboards" (in hamburger menu) and open "Orb Metrics Overview" in "Orb Dashboards" folder
6. Enjoy the minimal but beautiful dashboard with with data flowing (ideally)

## Restart Telegraf
After any changes to `telegraf.conf`, you only need to restart telegraf for changes to apply.
```sh
docker restart telegraf
```

## Tear down

```sh
docker-compose down -v --remove-orphans
```