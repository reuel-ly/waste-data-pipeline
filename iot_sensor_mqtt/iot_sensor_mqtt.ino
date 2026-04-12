#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"

#define TRIG_PIN 25    
#define ECHO_PIN 26    
#define BIN_HEIGHT 24 
#define EXTRA_HEIGHT 5

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

float get_distance_cm() {
    // Send ultrasonic pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Measure echo duration with timeout
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    if (duration == 0) {
        return -1;  // timeout = no reading
    }

    return duration * 0.034 / 2;  // convert to cm
}

// Percentage of amount of waste in a Bin
float get_waste_level(float distance_cm) {
    if (distance_cm <= 0) return -1;  // invalid reading

    float fill_percent = ((BIN_HEIGHT - distance_cm) / BIN_HEIGHT) * 100;

    return constrain(fill_percent, 0, 100);
}

void publish_sensor_data() {
    float distance_cm  = get_distance_cm() - EXTRA_HEIGHT;
    float waste_level  = get_waste_level(distance_cm);

    // Edge Cleaning
    if (distance_cm < 0) {
        Serial.print("⚠️ No reading from sensor (got: ");
        Serial.print(distance_cm);
        Serial.println(" cm) — skipping");
        return;
    }

    if (waste_level < 0) {
        Serial.println("⚠️ Invalid waste level — skipping");
        return;
    }
    // ────────────────────────────────────────
    
    bool is_full = (waste_level >= 100);

    // JSON payload
    StaticJsonDocument<200> doc;
    doc["sensor_id"]   = "ESP32_001";
    doc["location"]    = "Zone A - Bin 1";
    doc["distance_cm"] = round(distance_cm * 10) / 10.0;   
    doc["waste_level"] = round(waste_level * 10) / 10.0;
    doc["is_full"]     = is_full;
    doc["unit"]        = "%";

    char payload[200];
    serializeJson(doc, payload);

    client.publish("iot/sensors", payload);
    Serial.println("✅ Published: " + String(payload));
}


// for testing without Ultrasonic Sensor
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
    doc["unit"]        = "%";

    char payload[200];
    serializeJson(doc, payload);

    client.publish("iot/sensors", payload);
    Serial.println("✅ Published: " + String(payload));
}

void setup() {
    Serial.begin(115200);

    // for testing
    //randomSeed(analogRead(0));  // seed random with noise from floating pin

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    setup_wifi();
    client.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
    if (!client.connected()) {
        reconnect_mqtt();
    }
    client.loop();
    
    publish_sensor_data();

    //publish_simulated_data();

    delay(5000); 
}