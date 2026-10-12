"""Publishes fake ESP32 readings so you can test the dashboard without hardware."""
import argparse
import json
import math
import os
import random
import time

import paho.mqtt.client as mqtt

p = argparse.ArgumentParser()
p.add_argument("--broker", default=os.getenv("MQTT_BROKER", "localhost"))
p.add_argument("--port", type=int, default=int(os.getenv("MQTT_PORT", "1883")))
p.add_argument("--topic", default="iot/demo/esp32/sensors")
p.add_argument("--count", type=int, default=0, help="number of messages (0 = forever)")
p.add_argument("--interval", type=float, default=1.0)
args = p.parse_args()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(args.broker, args.port, keepalive=60)
client.loop_start()
i = 0
while args.count == 0 or i < args.count:
    temp = 30 + 6 * math.sin(i / 8) + random.uniform(-0.5, 0.5)   # swings past the 35 C alert
    hum = 60 + 15 * math.cos(i / 10) + random.uniform(-1, 1)
    payload = json.dumps({"device": "esp32-sim", "temp": round(temp, 2), "hum": round(hum, 2)})
    client.publish(args.topic, payload)
    print("published", payload)
    i += 1
    time.sleep(args.interval)
client.loop_stop()
client.disconnect()
