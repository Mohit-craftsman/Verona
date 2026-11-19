# ⚖️ Engineering Scope & Limitations

> **Read this before deploying or judging field performance claims.**

Project Verona is a functional, verified hardware prototype for long-range GPS tracking and base station telemetry using ESP32 and SX1278 (Ra-02) transceivers at 433 MHz. To maintain engineering honesty and transparency, the following design boundaries and real-world considerations are documented.

---

## 1. RF Range & Propagation
* **Calculated Link Budget vs. Real Walked Field Tests:**
  * In free-space line-of-sight (LOS) conditions with standard 433 MHz omnidirectional whip antennas (+17 dBm TX power, SF7, 125 kHz BW), the calculated link budget predicts a theoretical range exceeding 2–5 km.
  * In urban, wooded, or heavy foliage environments, attenuation and Fresnel zone obstruction significantly reduce range (typically 300 m – 1.2 km).
  * Field range is strongly governed by antenna height above ground and polarization alignment.

## 2. RF Protocol & Security
* **Unencrypted Broadcast:**
  * Packets (`PING,lat,lon` and `ACK`) are transmitted in cleartext ASCII over the 433 MHz ISM band.
  * Any listener tuned to 433 MHz with the matching sync word (`0xF3`), bandwidth, and spreading factor can receive and decode transmissions.
  * **Production Recommendation:** For sensitive tracking, payload encryption using AES-128-CTR or Speck cipher should be implemented along with HMAC authentication.
* **Half-Duplex Contention:**
  * The protocol uses point-to-point half-duplex ping-pong communication. Romeo transmits a PING and listens for 1.5 s for an ACK.
  * There is currently no CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance) or random exponential backoff. Multiple transmitter nodes operating simultaneously on the same channel may cause packet collisions.

## 3. Power Supply & Battery Autonomy
* **Power Budget Estimation:**
  * Standby / listening current for Romeo averages ~100 mA, with short TX peaks up to 250 mA.
  * Estimated battery endurance on a 3.7 V 1000 mAh Li-ion cell is ~4–5 hours; on a 2000 mAh cell, ~8–10 hours.
  * **Deep Sleep Optimization:** Romeo currently delays between pings. Implementing ESP32 deep sleep and LoRa CAD (Channel Activity Detection) between fixes would extend battery life to days or weeks.
* **TP4056 Charging Safety:**
  * The TP4056 module does not feature automatic load-sharing (power path management). **Switch SW1 must be OFF while charging via USB-C** to ensure the charger correctly terminates charging when the cell reaches 4.2 V.
  * The boost converter (MT3608) MUST be calibrated to exactly 5.0 V with a multimeter before connecting to the ESP32 VIN pin.

## 4. GPS Acquisition & Antenna Sensitivity
* **Cold Start vs. Warm Start:**
  * u-blox NEO-6M / NEO-7M modules require 30–60 seconds for a cold start GPS fix under open sky.
  * Ceramic patch antennas require a clear, unobstructed upward view of the sky. Indoors or under dense building roofs, the satellite count may remain 0.
* **Fix Freshness:**
  * Romeo only transmits coordinates when `gps.location.isValid()` is true and the fix age is less than 5000 ms (`gps.location.age() < 5000`). If satellite tracking is lost (e.g. entering a tunnel), Romeo halts PING broadcasts and logs fix status over serial.

## 5. Base Station LCD (Juliet)
* **Logic Level Pull-Ups:**
  * Standard 16x2 HD44780 LCD backpacks powered from 5V pull the I2C SDA/SCL lines up to 5V. While the ESP32 GPIOs tolerate this in bench testing due to internal clamping diodes, prolonged operation may stress the pins.
  * A 3.3V I2C display (such as a 0.96" SSD1306 OLED) or bi-directional level shifter is recommended for long-term deployments.
