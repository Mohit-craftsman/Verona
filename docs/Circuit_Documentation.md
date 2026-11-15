# Project Verona: Complete Connection List and Circuit Analysis

Board: ESP32 Dev Module (classic ESP32). There is no SIM or GSM module in this project: position travels over LoRa, not a cellular network.

## 1. Bill of materials with reference designators

### Romeo (transmitter)
| Ref | Part | Notes |
|-----|------|-------|
| U1 | ESP32 Dev Module | 5 V in at VIN (5V on 38-pin boards), 3V3 out |
| U2 | Ra-02 (SX1278) LoRa on breakout board | 3.3 V only, 433 MHz |
| U3 | u-blox GPS (GY-GPS6MV2, NEO-6M / NEO-7M) | VCC / GND / TX / RX header |
| U4 | TP4056 Type-C charger **with protection** (B+, B-, OUT+, OUT-) | DW01A + FS8205 protection |
| U5 | MT3608 boost converter | Set to 5.0 V (trimmer RV1) |
| BT1 | 3.7 V Li-ion / LiPo cell | 1000 mAh or larger |
| SW1 | Power switch | In series with the positive line |
| C1 | 100 uF electrolytic, 10 V or higher | Across Ra-02 3.3V and GND |
| D1 | 1N5819 Schottky diode (optional) | MT3608 OUT+ to VIN, stripe toward VIN |
| ANT1 | 433 MHz SMA rubber-duck antenna | |
| J1 | u.FL (IPEX) to SMA-female bulkhead pigtail | 50 ohm coax |
| ANT2 | GPS ceramic patch antenna with u.FL cable | |

### Juliet (receiver / base)
U1 ESP32 Dev Module, U2 Ra-02 on breakout, U3 16x2 LCD with I2C backpack (HD44780 + PCF8574), C1 100 uF, ANT1 433 MHz antenna, J1 pigtail, J3 USB data cable (power and Serial Monitor), breadboard, 14 jumper wires.

## 2. Netlists

### Romeo
| Net | Connected pins |
|-----|----------------|
| VBAT+ | BT1 (+), U4 B+ |
| VBAT- | BT1 (-), U4 B- |
| USB_5V | USB-C charging input of U4 |
| VSW_IN | U4 OUT+, SW1 pin 1 |
| VSW_OUT | SW1 pin 2, U5 IN+ |
| +5V | U5 OUT+ (through D1 if fitted), U1 VIN |
| GND | U4 OUT-, U5 IN-, U5 OUT-, U1 GND, U2 GND (both pins), U3 GND, C1 (-) |
| +3V3 | U1 3V3, U2 3.3V, U3 VCC, C1 (+) |
| LORA_NSS / RST / DIO0 | U2 pin to U1 GPIO5 / GPIO14 / GPIO26 |
| LORA_SCK / MISO / MOSI | U2 pin to U1 GPIO18 / GPIO19 / GPIO23 |
| GPS_TX | U3 TX, U1 GPIO32 (UART2 RX) |
| GPS_RX | U3 RX, U1 GPIO33 (UART2 TX) |
| RF_LORA | U2 u.FL, J1, ANT1 |
| RF_GPS | U3 u.FL, ANT2 |

**VBAT- and GND are different nets.** On the protected TP4056 the battery negative (B-) reaches OUT- only through the protection MOSFET. The battery negative goes to B-; all load grounds go to OUT-. Never join B- and OUT- with a wire. Not connected: Ra-02 DIO1-DIO5.

### Juliet
| Net | Connected pins |
|-----|----------------|
| +5V (VBUS) | J3 VBUS, U1 5V/VIN, U3 VCC |
| GND | J3 GND, U1 GND, U2 GND, U3 GND, C1 (-) |
| +3V3 | U1 3V3, U2 3.3V, C1 (+) |
| LORA_* | Same six SPI/control nets as Romeo |
| I2C_SDA | U3 SDA, U1 GPIO21 |
| I2C_SCL | U3 SCL, U1 GPIO22 |
| RF_LORA | U2 u.FL, J1, ANT1 |

The LCD backpack pulls SDA and SCL up to its own supply (5 V here). This usually works with an ESP32 but exceeds its 3.3 V pin rating. A 0.96 inch SSD1306 OLED on 3V3 (same four wires) avoids this. The I2C address is 0x27 on most backpacks, 0x3F on some.

## 3. Circuit analysis

**Romeo supply chain**
- Cell: 4.2 V (full) to about 3.0 V (empty). The protection IC disconnects at about 2.4-2.5 V.
- The ESP32 must not be fed from the cell directly: the board's 3.3 V regulator needs about 4.5 V or more at its input, and injecting the cell into the 3V3 pin would exceed the ESP32's 3.6 V limit. The MT3608 lifts the 3.0-4.2 V cell to a steady 5.0 V for VIN. Set the trimmer to 5.0 V with a multimeter before connecting the ESP32.
- The ESP32 board's regulator (5 V to 3.3 V) supplies the ESP32, Ra-02 and GPS.

**Romeo power budget (3.3 V rail, estimates)**

| Load | Typical | Peak |
|------|---------|------|
| ESP32 (Wi-Fi and Bluetooth off) | 50 mA | 80 mA |
| Ra-02 (transmit about 17 dBm in short bursts; listens for ACK) | 5 mA average | 120 mA |
| GPS module | 45 mA | 50 mA |
| Total | about 100 mA | about 250 mA |

- Cell side (MT3608 at about 85 % efficiency): about 175 mA average, about 400 mA peak.
- Runtime: roughly 9-10 hours on a 2000 mAh cell, about 5 hours on 1000 mAh. These are calculated estimates, not measurements.
- Heat in the board's regulator: (5 - 3.3) V x 0.1 A = 0.17 W typical, 0.43 W at peak. Acceptable.

**Juliet power (estimates):** ESP32 about 50 mA, Ra-02 receiving about 12 mA, LCD with backlight about 25 mA: roughly 90-100 mA from the 5 V USB supply, well inside a 500 mA USB port.

**Charging (Romeo)**
- The TP4056 module charges at 1 A by default. For cells below 2000 mAh, lower it to 0.5C by raising the programming resistor (I in mA = 1200 / R in kohm; 2.4 kohm gives 500 mA).
- Switch SW1 off while charging: the TP4056 has no load sharing.
- Do not connect the ESP32's USB port while the boost converter feeds VIN unless D1 is fitted.

**Signals**
- All logic is 3.3 V: Ra-02 (3.6 V max), GPS TTL and ESP32 are compatible without level shifters.
- GPS UART crossover: GPS TX to ESP32 RX (GPIO32), GPS RX to ESP32 TX (GPIO33), 9600 baud.
- LoRa SPI uses the ESP32 default VSPI pins. GPIO5 (NSS) is a boot strapping pin but idles high, so boot is unaffected.
- C1 absorbs the 120 mA transmit pulses so the 3.3 V rail does not dip (a dip causes brownouts and `LoRa Error`).

**RF**
- Connect the 433 MHz antenna before applying power; transmitting into an open connector can damage the Ra-02's power amplifier.
- Mount the GPS patch flat, metal side down, facing the sky, a few centimetres from the LoRa antenna and the ESP32 metal shield.

## 4. Build checklist

1. Set the MT3608 to 5.0 V (no load).
2. Wire Romeo's power chain with SW1 off; verify 5.0 V at the ESP32 VIN pin and GND.
3. Wire LoRa, C1, antennas, then GPS.
4. Continuity-test each net above before the first power-on.
5. Wire Juliet (LoRa, C1, antenna, LCD), upload `Juliet.ino`, then upload `Romeo.ino` to Romeo.
6. Take Romeo outdoors, wait for a GPS fix, and confirm the PING/ACK exchange and the LCD readout.
