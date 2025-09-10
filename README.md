# orb-local-analytics
Tools and documentation for setting up local Orb analytics.

This guide will enable you to self-host a TIG (Telegraf, InfluxDB, Grafana) analytics stack and configure Orbs to send data to that stack for analysis.

## Pre-Reqs
1. You will need an active [Orb Cloud](https://cloud.orb.net) account to configure your Orbs for local data analytics
2. You will need to have one or more Orb sensors or apps linked to your Orb Cloud account
3. You will need a Docker-enabled host for the analytics stack, which can communicate with the Orbs you intend to collect data from.

## Configuration

1. Run `./configure.py` to generate configs (`telegraf.conf` and Orb Cloud config)
2. Follow all instructions in the configure.py output to run your selected configuration

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