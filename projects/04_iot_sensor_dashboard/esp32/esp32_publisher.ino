// ESP32 + DHT22 -> MQTT publisher
// Libraries (Arduino Library Manager): "PubSubClient" by Nick O'Leary, "DHT sensor library" by Adafruit
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char* WIFI_SSID   = "YOUR_WIFI_NAME";
const char* WIFI_PASS   = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER = "192.168.1.10";        // IP of the PC running the MQTT broker
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "iot/demo/esp32/sensors";

#define DHT_PIN  4          // DHT22 data pin connected to GPIO 4
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

void connectWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi connected: " + WiFi.localIP().toString());
}

void connectMqtt() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqtt.connect("esp32-01")) Serial.println("connected");
    else { Serial.printf("failed (rc=%d), retrying in 3 s\n", mqtt.state()); delay(3000); }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWifi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWifi();
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) {
    Serial.println("DHT read failed, skipping");
  } else {
    char payload[96];
    snprintf(payload, sizeof(payload), "{\"device\":\"esp32-01\",\"temp\":%.2f,\"hum\":%.2f}", t, h);
    mqtt.publish(MQTT_TOPIC, payload);
    Serial.println(payload);
  }
  delay(2000);   // DHT22 can be read about every 2 seconds
}
