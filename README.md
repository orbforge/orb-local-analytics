# Orb Local Analytics
Tools and documentation for setting up local Orb analytics.

This guide will enable you to self-host a TIG (Telegraf, InfluxDB, Grafana) analytics stack and configure Orbs to send data to that stack for analysis.

> [!WARNING]
> If you have an existing installation of this repository that is older than February 26, 2026, See the [Deprecation Notice](#deprecation-of-the-old-influxdb-v2-based-local-analytics) for important information.

## Pre-Reqs
1. You will need an active [Orb Cloud](https://cloud.orb.net) account to configure your Orbs for local data analytics
2. You will need to have one or more Orb sensors or apps linked to your Orb Cloud account
3. You will need a Docker-enabled host for the analytics stack, which can communicate with the Orbs you intend to collect data from.
4. Clone this repository on the Docker-enabled host you want to use. `git clone https://github.com/orbforge/orb-local-analytics.git`

## Configuration

1. Run `python3 configure.py` to generate configs (`telegraf.conf` and Orb Cloud config)
2. Follow all instructions in the configure.py output to run your selected configuration

## Setup

1. Start services
```sh
docker compose up -d
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

## Deprecation of the old InfluxDB v2-based Local Analytics
The first version of this repository used a TIG stack based on InfluxDB v2. This has worked well for us but required us to write complex queries in a proprietary language. InfluxDB v3 now supports using SQL, meaning we can build charts in Grafana much more quickly and more easily. 

Unfortunately, there is no easy path from InfluxDB v2 to InfluxDB v3. Moving to InfluxDB v3 will mean losing your history. You can stay on your current setup for now, but updates will probably be limited to package updates. The code was moved to a [influx-v2 branch](https://github.com/orbforge/orb-local-analytics/tree/influx-v2).

If you want to upgrade your Orb Local Analytics stack and move to Influx DB v3, you can perform the following steps 
```
# stop Orb Local Analytics
docker compose down
# cleanup the old components
docker volume rm orb-local-analytics_influxdb-data
docker container rm influxdb
docker container rm telegraf
# pull the latest version from Github
git pull
# rerun the configuration step to create the updated telegraf pointing at InfluxDB v3
python3 configure.py
# start Orb Local Analytics
docker compose pull
docker compose up -d
```
