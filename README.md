# Weather Station

Homelab services that grab data from an Ecowitt weather station (WS3802 console with a WS85 sensor).

The station publishes measurements over MQTT. This stack runs a local Mosquitto broker, stores parsed readings in PostgreSQL, and consumes `ecowitt/#` topics with `mqtt-ws3802`.

## Services

| Service | Description | Host port |
| --- | --- | --- |
| **mosquitto** | MQTT broker for Ecowitt station ingest | 1886, 9004 (WebSocket) |
| **postgresql** | Database for weather readings | 5436 |
| **mqtt-ws3802** | MQTT consumer — parses Ecowitt payloads and writes them to PostgreSQL | — |

## Quick Start

```bash
cp .env.example .env
docker compose up -d
docker compose logs -f
```
