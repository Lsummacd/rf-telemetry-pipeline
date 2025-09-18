import json, time, random, argparse
import paho.mqtt.client as mqtt

def jitter(base, span):
    return base + random.uniform(-span, span)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--broker", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--device", default="edge01")
    ap.add_argument("--center", type=float, default=100.1e6)  # Hz
    ap.add_argument("--sr", type=float, default=2.4e6)        # Hz
    ap.add_argument("--period", type=float, default=1.0)
    ap.add_argument("--loss-pct", type=float, default=0.0)       # e.g., 5.0
    ap.add_argument("--extra-latency-ms", type=int, default=0)   # e.g., 200
      # seconds
    args = ap.parse_args()

    topic = f"rf/{args.device}/telemetry"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.broker, args.port, keepalive=60)

    seq = 0
    temp = 40.0
    rssi = -58.0
    snr = 22.0
    noise = -102.0
    occ_bw = 18000.0

    while True:
        now_ms = int(time.time() * 1000)
        # simple correlated walk to look RF-ish
        rssi += random.uniform(-0.6, 0.6)
        snr  += random.uniform(-0.8, 0.8)
        noise += random.uniform(-0.3, 0.3)
        occ_bw += random.uniform(-400, 400); occ_bw = max(5_000, min(60_000, occ_bw))
        temp += random.uniform(-0.1, 0.1)

        payload = {
            "device_id": args.device,
            "seq": seq,
            "t_send_unix_ms": now_ms,
            "center_freq_hz": args.center,
            "sample_rate_hz": args.sr,
            "rssi_dbm": rssi,
            "snr_db": snr,
            "noise_floor_dbm": noise,
            "occupied_bw_hz": occ_bw,
            "cpu_pct": jitter(22, 4),
            "mem_pct": jitter(14, 3),
            "fpga_temp_c": temp,
            "fw_version": "0.1.0"
        }

        if random.random() < (args.loss_pct / 100.0):
            seq += 1
            time.sleep(args.period)
            continue

        if args.extra_latency_ms > 0:
            time.sleep(args.extra_latency_ms / 1000.0)

        client.publish(topic, json.dumps(payload), qos=0, retain=False)
        seq += 1
        time.sleep(args.period)

if __name__ == "__main__":
    main()
