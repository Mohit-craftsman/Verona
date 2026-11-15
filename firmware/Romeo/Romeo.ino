// Project Verona - ROMEO (transmitter / remote node)
// Board: "ESP32 Dev Module" (Arduino IDE)
// Hardware: ESP32 + Ra-02 (SX1278, 433 MHz) + u-blox GPS (NEO-6M / NEO-7M)
//
// Romeo reads its GPS position and sends it to Juliet as a PING:
//   "PING,<lat>,<lon>"          (Wherefore art thou?)
// Juliet answers with:
//   "ACK"                       (Here I am)
//
// Wiring:
//   LoRa  NSS->GPIO5  RST->GPIO14  DIO0->GPIO26
//         SCK->GPIO18 MISO->GPIO19 MOSI->GPIO23   (default VSPI pins)
//   GPS   TX -> GPIO32 (ESP32 RX)   RX -> GPIO33 (ESP32 TX)
//
// GPIO32/33 are used for the GPS instead of GPIO16/17 because GPIO16/17
// are reserved for PSRAM on WROVER boards. 32/33 work on every board.

#include <SPI.h>
#include <LoRa.h>
#include <TinyGPS++.h>

#define LORA_SS    5
#define LORA_RST   14
#define LORA_DIO0  26
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23

#define GPS_RX_PIN 32   // ESP32 RX <- GPS TX
#define GPS_TX_PIN 33   // ESP32 TX -> GPS RX
#define GPS_BAUD   9600

const unsigned long PING_INTERVAL_MS = 3000;
const unsigned long ACK_TIMEOUT_MS   = 1500;

TinyGPSPlus gps;
HardwareSerial gpsSerial(2);          // UART2 remapped to GPIO32/33
unsigned long lastPing = 0;

// Listen for Juliet's ACK, keep feeding the GPS while waiting
bool waitForAck() {
  unsigned long start = millis();
  while (millis() - start < ACK_TIMEOUT_MS) {
    while (gpsSerial.available()) {
      gps.encode(gpsSerial.read());
    }
    if (LoRa.parsePacket()) {
      String reply = "";
      while (LoRa.available()) {
        reply += (char)LoRa.read();
      }
      if (reply == "ACK") {
        Serial.print("ACK from Juliet (RSSI ");
        Serial.print(LoRa.packetRssi());
        Serial.println(" dBm)");
        return true;
      }
    }
  }
  return false;
}

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Romeo (transmitter) ready");

  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa Error");
    while (1);
  }
}

void loop() {
  // Feed every GPS byte to TinyGPS++
  while (gpsSerial.available()) {
    gps.encode(gpsSerial.read());
  }

  if (millis() - lastPing >= PING_INTERVAL_MS) {
    lastPing = millis();

    // valid fix updated within the last 5 s (isValid() alone stays true after a fix is lost)
    if (gps.location.isValid() && gps.location.age() < 5000) {
      String position = String(gps.location.lat(), 6) + "," + String(gps.location.lng(), 6);

      LoRa.beginPacket();
      LoRa.print("PING," + position);
      LoRa.endPacket();

      Serial.print("PING sent: ");
      Serial.println(position);

      if (!waitForAck()) {
        Serial.println("No ACK - is Juliet in range?");
      }
    } else {
      Serial.print("Waiting for GPS fix... satellites: ");
      Serial.println(gps.satellites.value());
    }
  }
}
