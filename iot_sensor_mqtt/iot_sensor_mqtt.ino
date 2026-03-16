#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
    Serial.println("IP: " + WiFi.localIP().toString());
}

void reconnect_mqtt() {
    while (!client.connected()) {
        Serial.print("Connecting to MQTT...");
        if (client.connect("ESP32_001")) {
            Serial.println("✅ MQTT connected!");
        } else {
            Serial.println("Failed, retrying in 5s");
            delay(5000);
        }
    }
}

void publish_simulated_data() {
    // Generate random sensor values
    float waste_level  = random(0, 1000) / 10.0;    // 0.0 - 100.0 %
    float distance_cm  = random(5, 300) / 10.0;     // 0.5 - 30.0 cm
    int   battery      = random(20, 100);            // 20 - 100 %

    // Build JSON payload
    StaticJsonDocument<200> doc;
    doc["sensor_id"]   = "ESP32_001";
    doc["location"]    = "Zone A - Bin 1";
    doc["waste_level"] = waste_level;
    doc["distance_cm"] = distance_cm;
    doc["battery"]     = battery;
    doc["unit"]        = "%";
    doc["simulated"]   = true;          // flag so you know it's test data

    char payload[200];
    serializeJson(doc, payload);

    client.publish("iot/sensors", payload);
    Serial.println("✅ Published: " + String(payload));
}

void setup() {
    Serial.begin(115200);
    randomSeed(analogRead(0));  // seed random with noise from floating pin
    setup_wifi();
    client.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
    if (!client.connected()) {
        reconnect_mqtt();
    }
    client.loop();
    publish_simulated_data();
    delay(5000);  // send every 5 seconds
}