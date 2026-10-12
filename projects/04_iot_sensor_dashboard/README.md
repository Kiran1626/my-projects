# IoT Sensor Data Dashboard (ESP32 + MQTT + Python)

**Stack:** Python, ESP32 (Arduino C++), MQTT (paho-mqtt), Matplotlib

Streams temperature and humidity from an ESP32 (DHT22 sensor) over MQTT, logs it to CSV, raises threshold alerts and plots live data.

## Files
- `esp32/esp32_publisher.ino`: firmware; reads a DHT22 and publishes JSON over Wi-Fi/MQTT every 2 s
- `simulator.py`: publishes fake readings so you can test without hardware
- `dashboard.py`: subscribes, validates, logs to `readings.csv`, prints alerts, live plot
- `sensor_core.py`: payload parsing, range validation, alert rules, rolling statistics
- `tests/test_core.py`: 8 unit tests

## Run
```bash
pip install -r requirements.txt
# 1. Start an MQTT broker (e.g. Mosquitto: `mosquitto -v`) on this PC
# 2. In one terminal:  python dashboard.py            (live plot; add --no-plot for headless)
# 3. In another:       python simulator.py            (or flash the ESP32 sketch)
python -m pytest -q tests
```
Use `--broker IP --port 1883 --topic ...` or the `MQTT_BROKER` environment variable to point at another broker.

## ESP32 wiring
DHT22 VCC to 3V3, GND to GND, DATA to GPIO 4 (add a 10k pull-up resistor between DATA and VCC if your module has none). Set Wi-Fi name, password and broker IP at the top of the sketch. Install the "PubSubClient" and "DHT sensor library" libraries.

## Alerts
Temperature above 35 C or humidity above 80% prints an `ALERT` line (limits are in `sensor_core.py`).

## Payload
`{"device":"esp32-01","temp":27.4,"hum":55.2}` on topic `iot/demo/esp32/sensors`. Invalid or out-of-range values are ignored.
