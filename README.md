# Project Verona

A two-node GPS tracking system built on ESP32 and 433 MHz LoRa. **Romeo** (transmitter / remote) is a battery-powered tracker that reads its position from a u-blox GPS module. **Juliet** (receiver / base) is a USB-powered station with a 16x2 LCD. Romeo asks *"Wherefore art thou?"* with a `PING` carrying its coordinates; Juliet answers *"Here I am"* with an `ACK` and shows the position.

```
ROMEO (battery)                                                   JULIET (USB)
[GPS + antenna] -UART-> [ESP32] -SPI-> [Ra-02] ))) 433 MHz ((( [Ra-02] <-SPI- [ESP32] -USB-> PC
                                          PING,lat,lon  ->                           |-I2C-> [16x2 LCD]
                                          <-  ACK
```

## Radio protocol

| Packet | From | Payload (ASCII) | Meaning |
|--------|--------|-----------------|---------|
| `PING` | Romeo | `PING,22.572646,88.363895` | "Wherefore art thou?": position with six decimals |
| `ACK` | Juliet | `ACK` | "Here I am": Juliet received the PING |

Romeo sends a PING every 3 seconds, only when the GPS has a valid fix updated within the last 5 seconds, then listens for the ACK for up to 1.5 seconds. Radio: Ra-02 (SX1278) at 433 MHz with the LoRa library defaults, single channel, half-duplex. Packets are not encrypted or addressed.

## Documentation

| File | Contents |
|------|----------|
| `docs/Romeo_Circuit_Diagram.png` / `.svg` | Full Romeo schematic with bill of materials |
| `docs/Juliet_Circuit_Diagram.png` / `.svg` | Full Juliet schematic (with LCD) with bill of materials |
| `docs/Circuit_Documentation.md` | Netlists, power budget and circuit analysis |
| `tools/gen_diagrams.py` | Regenerates the diagrams: `python tools/gen_diagrams.py docs` (needs `cairosvg` and the DejaVu Sans font) |

![Romeo](docs/Romeo_Circuit_Diagram.png)
![Juliet](docs/Juliet_Circuit_Diagram.png)

## Components

### Romeo (transmitter)

| Ref | Component | Qty |
|-----|-----------|-----|
| U1 | ESP32 Dev Module (classic ESP32, 30 or 38 pin) | 1 |
| U2 | Ra-02 LoRa module (SX1278, 433 MHz) on 2.54 mm breakout board | 1 |
| U3 | GPS module GY-GPS6MV2 (u-blox NEO-6M or NEO-7M) | 1 |
| ANT1 | 433 MHz SMA rubber-duck antenna | 1 |
| J1 | u.FL (IPEX) to SMA-female pigtail | 1 |
| ANT2 | GPS ceramic patch antenna with u.FL cable | 1 |
| U4 | TP4056 Type-C charger board **with protection** (B+, B-, OUT+, OUT-) | 1 |
| BT1 | 3.7 V Li-ion / LiPo cell, 1000 mAh or more | 1 |
| U5 | MT3608 boost converter, set to 5.0 V | 1 |
| SW1 | Power switch (SPST, 1 A or more) | 1 |
| C1 | 100 uF electrolytic capacitor, 10 V or higher | 1 |
| D1 | 1N5819 Schottky diode (optional) | 1 |
| - | Breadboard, 20 male-to-male jumper wires, USB-C and micro-USB cables | - |

### Juliet (receiver / base)

| Ref | Component | Qty |
|-----|-----------|-----|
| U1 | ESP32 Dev Module | 1 |
| U2 | Ra-02 LoRa module on breakout board | 1 |
| U3 | 16x2 LCD with I2C backpack (HD44780 + PCF8574, 4 pins) | 1 |
| ANT1 / J1 | 433 MHz SMA antenna and u.FL-to-SMA pigtail | 1 each |
| C1 | 100 uF electrolytic capacitor | 1 |
| J3 | Micro-USB (or USB-C) data cable | 1 |
| - | Breadboard, 14 male-to-male jumper wires | - |

## Pin map (all classic ESP32 boards)

| Signal | GPIO | 30-pin label | 38-pin label |
|--------|------|--------------|--------------|
| LoRa NSS | 5 | D5 | IO5 |
| LoRa RST | 14 | D14 | IO14 |
| LoRa DIO0 | 26 | D26 | IO26 |
| LoRa SCK | 18 | D18 | IO18 |
| LoRa MISO | 19 | D19 | IO19 |
| LoRa MOSI | 23 | D23 | IO23 |
| GPS TX to ESP32 RX (Romeo) | 32 | D32 | IO32 |
| GPS RX from ESP32 TX (Romeo) | 33 | D33 | IO33 |
| LCD SDA (Juliet) | 21 | D21 | IO21 |
| LCD SCL (Juliet) | 22 | D22 | IO22 |

GPIO16 and 17 are intentionally unused: WROVER boards reserve them for PSRAM.

## Wiring

**Ra-02 to ESP32 (Romeo and Juliet):** 3.3V to 3V3, GND to GND, NSS to GPIO5, RST to GPIO14, DIO0 to GPIO26, SCK to GPIO18, MISO to GPIO19, MOSI to GPIO23. Fit C1 (+ to 3.3V, - to GND) next to the module. DIO1 to DIO5 are unused. The Ra-02 is 3.3 V only.

**GPS to ESP32 (Romeo):** VCC to 3V3, GND to GND, TX to GPIO32, RX to GPIO33 (TX and RX cross over).

**LCD to ESP32 (Juliet):** GND to GND, VCC to VIN (5 V), SDA to GPIO21, SCL to GPIO22.

**Romeo power chain:**

```
Cell (+) -> U4 B+             Cell (-) -> U4 B-
U4 OUT+ -> SW1 -> U5 IN+      U4 OUT- -> U5 IN-
U5 OUT+ (5.0 V) -> ESP32 VIN  U5 OUT- -> ESP32 GND
```

U4 B- and OUT- are different nets joined only by the protection circuit: never connect them together. Set U5 to 5.0 V with a multimeter before connecting it to the ESP32. Switch SW1 off while charging through U4's USB-C port.

**Antennas:** Ra-02 u.FL -> J1 pigtail -> ANT1. GPS u.FL -> ANT2 (metal side down, sky view). Always fit the 433 MHz antenna before powering a Ra-02.

## Firmware

| Sketch | Board | Purpose |
|--------|-------|---------|
| `firmware/Romeo/Romeo.ino` | Romeo ESP32 | Reads the GPS on UART2 (GPIO32/33), sends a PING with the position every 3 s once a fix is valid, waits for the ACK |
| `firmware/Juliet/Juliet.ino` | Juliet ESP32 | Receives the PING, replies ACK, prints position and RSSI on Serial, shows `Lat:` / `Lon:` on the LCD |

1. Install **Arduino IDE 2.x** and the **esp32 by Espressif** board package (board: *ESP32 Dev Module*).
2. Install the libraries **LoRa** (Sandeep Mistry), **TinyGPSPlus** (Mikal Hart) and **LiquidCrystal I2C** (Frank de Brabander).
3. Open each sketch folder, upload to its board, and open the Serial Monitor at **9600 baud**.

## Expected output

Romeo: `PING sent: 22.572646,88.363895` then `ACK from Juliet (RSSI -62 dBm)`
Juliet: `PING from Romeo: 22.572646,88.363895  (RSSI -62 dBm)` then `ACK sent`; the LCD shows `Lat:22.572646` and `Lon:88.363895`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `LoRa Error` | Check 3.3 V, GND, the four SPI wires, NSS and RST |
| Romeo: satellites stay 0 | Go outdoors; check the GPS TX/RX crossover and the patch antenna |
| Romeo: `No ACK` | Fit both antennas; keep the nodes close for the first test; check Juliet is powered |
| LCD blank | Try address `0x3F` in `Juliet.ino`; turn the contrast screw on the backpack; check SDA/SCL on GPIO21/22 |
| Romeo resets on battery | Set U5 to 5.0 V, fit C1, check every connection |

## Status and limitations

Schematics, firmware and documentation are complete. Radio range, real battery life and ACK reliability have not yet been measured. No encryption or node addressing: any 433 MHz device using the same radio settings can hear Romeo.
