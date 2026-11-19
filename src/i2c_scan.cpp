// I2C Scanner - finds the address of your LCD (or any I2C device)
// Flash this, open Serial Monitor at 9600 baud, note the address printed.

#include <Wire.h>
#include <Arduino.h>

#define LCD_SDA 21
#define LCD_SCL 22

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Wire.begin(LCD_SDA, LCD_SCL);

  Serial.println("\nI2C Scanner — scanning...");
  int found = 0;

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    byte err = Wire.endTransmission();
    if (err == 0) {
      Serial.print("Device found at address: 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      found++;
    }
  }

  if (found == 0) {
    Serial.println("No I2C devices found!");
    Serial.println("Check SDA->GPIO21 and SCL->GPIO22 wiring.");
  } else {
    Serial.print("Done. ");
    Serial.print(found);
    Serial.println(" device(s) found.");
  }
}

void loop() {}