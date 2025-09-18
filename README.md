# RF Telemetry Pipeline (Edge → MQTT → Telegraf → InfluxDB → Grafana)

Spin up a full edge-to-cloud telemetry stack locally with Docker. Includes:
- **Mosquitto** (MQTT broker)
- **Telegraf** (MQTT → InfluxDB bridge)
- **InfluxDB 2.x** (time-series store)
- **Grafana** (dashboards)
- **Edge agent** simulator (Python) publishing RF-ish stats

> **Latency note:** We intentionally let InfluxDB timestamp points on *ingest*. The payload still contains `t_send_unix_ms`. Grafana computes **end-to-end latency** as `ingest_time - t_send_unix_ms`.

## 1) Start services

```bash
docker compose up -d
```

Wait ~5–10 seconds for InfluxDB & Grafana to be ready.

## 2) Run the edge simulator(s)

Install the small dependency:
```bash
pip install -r edge/requirements.txt
```

Run one or more devices:
```bash
python edge/rf_edge_agent.py --device edge01
python edge/rf_edge_agent.py --device edge02 --center 433.92e6 --period 0.5
```

## 3) Wire Grafana to InfluxDB

Open http://localhost:3000 (login: `admin` / `admin`).
- **Add data source → InfluxDB**
  - Query Language: **Flux**
  - URL: `http://influxdb:8086`
  - Organization: `lab`
  - Token: `supersecrettoken`
  - Default Bucket: `rf`

## 4) Import the dashboard

- Grafana → Dashboards → **Import** → Upload `dashboards/grafana_rf_dashboard.json`  
- When prompted, select the InfluxDB data source you created.

## 5) What you should see

- **RSSI / SNR / Noise floor** time series per device
- **Occupied bandwidth (kHz)**
- **Latency (ms)** derived from ingest vs. `t_send_unix_ms`
- **Packet loss (%)** derived from gaps in the `seq` counter

## 6) Fault injection ideas

- Stop InfluxDB: `docker stop influxdb` for 10–20 s → observe backlog/loss
- Increase publish rate: `--period 0.1` → stress buffers
- Kill/restart the edge while Grafana is live

## 7) Schema (stable core)

```json
{
  "device_id": "edge01",
  "seq": 12345,
  "t_send_unix_ms": 1725970000123,
  "center_freq_hz": 100100000.0,
  "sample_rate_hz": 2400000.0,
  "rssi_dbm": -57.3,
  "snr_db": 23.1,
  "noise_floor_dbm": -100.2,
  "occupied_bw_hz": 18000.0,
  "cpu_pct": 22.1,
  "mem_pct": 13.2,
  "fpga_temp_c": 40.7,
  "fw_version": "0.1.0"
}
```

## 8) Tear down

```bash
docker compose down
```

---

**CV Bullet (example):** Designed and deployed an edge-to-cloud RF telemetry pipeline (MQTT→Telegraf→InfluxDB→Grafana) with p95 E2E latency tracking and packet-loss analytics; reproducible via Docker Compose.
