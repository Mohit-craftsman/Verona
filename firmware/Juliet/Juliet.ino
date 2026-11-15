// Project Verona - JULIET (receiver / base station)
// Board: "ESP32 Dev Module" (Arduino IDE)
// Hardware: ESP32 + Ra-02 (SX1278, 433 MHz) + 16x2 I2C LCD
//
// Juliet listens for Romeo's PING ("PING,<lat>,<lon>"), answers "ACK"
// (Here I am), prints the position on the Serial Monitor and shows it on the LCD.
//
// Wiring:
//   LoRa  NSS->GPIO5  RST->GPIO14  DIO0->GPIO26
//         SCK->GPIO18 MISO->GPIO19 MOSI->GPIO23
//   LCD   GND->GND  VCC->VIN (5 V)  SDA->GPIO21  SCL->GPIO22
//
// Library needed: LiquidCrystal I2C (Frank de Brabander)

#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define LORA_SS    5
#define LORA_RST   14
#define LORA_DIO0  26
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23

#define LCD_SDA    21
#define LCD_SCL    22

// Change 0x27 to 0x3F if the screen stays blank
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  Serial.println("Juliet (base) ready");

  Wire.begin(LCD_SDA, LCD_SCL);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Juliet ready");

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa Error");
    lcd.clear();
    lcd.print("LoRa Error");
    while (1);
  }

  lcd.setCursor(0, 1);
  lcd.print("Waiting Romeo...");
}

void loop() {
  if (!LoRa.parsePacket()) {
    return;
  }

  String data = "";
  while (LoRa.available()) {
    data += (char)LoRa.read();
  }
  int rssi = LoRa.packetRssi();

  // Only answer valid PINGs from Romeo: "PING,<lat>,<lon>"
  if (!data.startsWith("PING,")) {
    return;
  }

  delay(30);                  // give Romeo time to switch to receive
  LoRa.beginPacket();
  LoRa.print("ACK");          // Here I am
  LoRa.endPacket();

  String body = data.substring(5);
  int comma = body.indexOf(',');
  if (comma <= 0) {
    return;
  }
  String lat = body.substring(0, comma);
  String lon = body.substring(comma + 1);

  Serial.print("PING from Romeo: ");
  Serial.print(body);
  Serial.print("  (RSSI ");
  Serial.print(rssi);
  Serial.println(" dBm)");
  Serial.println("ACK sent");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Lat:" + lat);
  lcd.setCursor(0, 1);
  lcd.print("Lon:" + lon);
}
