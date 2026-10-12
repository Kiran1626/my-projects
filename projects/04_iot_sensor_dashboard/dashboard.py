"""Subscribe to ESP32 sensor data over MQTT, log to CSV, raise alerts and (optionally) plot live."""
import argparse
import csv
import os
import time
from pathlib import Path

import paho.mqtt.client as mqtt

from sensor_core import Window, check_alerts, parse_payload

p = argparse.ArgumentParser()
p.add_argument("--broker", default=os.getenv("MQTT_BROKER", "localhost"))
p.add_argument("--port", type=int, default=int(os.getenv("MQTT_PORT", "1883")))
p.add_argument("--topic", default="iot/demo/esp32/sensors")
p.add_argument("--csv", default="readings.csv")
p.add_argument("--no-plot", action="store_true", help="log only (for servers / headless)")
p.add_argument("--duration", type=int, default=0, help="stop after N seconds (0 = run forever)")
args = p.parse_args()

window = Window(60)
csv_path = Path(args.csv)
new_file = not csv_path.exists()
csv_file = csv_path.open("a", newline="")
writer = csv.writer(csv_file)
if new_file:
    writer.writerow(["timestamp", "device", "temperature_c", "humidity_pct"])


def on_connect(client, _userdata, _flags, reason_code, _props=None):
    print(f"Connected to {args.broker}:{args.port} (code {reason_code}); subscribing to {args.topic}")
    client.subscribe(args.topic)


def on_message(_client, _userdata, msg):
    try:
        r = parse_payload(msg.payload)
    except ValueError as err:
        print("Ignored:", err)
        return
    window.add(r)
    writer.writerow([r.ts.isoformat(timespec="seconds"), r.device, r.temperature, r.humidity])
    csv_file.flush()
    print(f"{r.ts:%H:%M:%S} {r.device}: {r.temperature:.1f} C, {r.humidity:.1f} %")
    for a in check_alerts(r):
        print("  ALERT:", a)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect, client.on_message = on_connect, on_message
client.connect(args.broker, args.port, keepalive=60)

if args.no_plot:
    client.loop_start()
    end = time.time() + args.duration if args.duration else None
    try:
        while end is None or time.time() < end:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    client.loop_stop()
    print("Summary:", window.stats())
else:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    client.loop_start()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(9, 6))

    def update(_frame):
        pts = list(window.data)
        if not pts:
            return
        xs = [r.ts for r in pts]
        ax1.clear(); ax2.clear()
        ax1.plot(xs, [r.temperature for r in pts], color="tab:red")
        ax1.axhline(35, ls="--", color="grey"); ax1.set_ylabel("Temperature (C)")
        ax2.plot(xs, [r.humidity for r in pts], color="tab:blue")
        ax2.axhline(80, ls="--", color="grey"); ax2.set_ylabel("Humidity (%)")
        ax1.set_title("ESP32 live sensor data (MQTT)")
        fig.autofmt_xdate()

    ani = FuncAnimation(fig, update, interval=1000, cache_frame_data=False)
    plt.show()
    client.loop_stop()
csv_file.close()
