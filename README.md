<div align="center">

# 📡 Project Verona
### Long-Range Off-Grid GPS Telemetry & Base Station System

[![ESP32](https://img.shields.io/badge/Platform-ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![LoRa 433MHz](https://img.shields.io/badge/RF-SX1278%20433MHz-005B96?style=for-the-badge)](https://www.semtech.com/products/wireless-rf/lora-connect/sx1278)
[![GPS](https://img.shields.io/badge/Sensor-u--blox%20NEO--6M-008080?style=for-the-badge)](https://www.u-blox.com/)
[![PlatformIO](https://img.shields.io/badge/IDE-PlatformIO-orange?style=for-the-badge&logo=platformio&logoColor=white)](https://platformio.org/)
[![Arduino](https://img.shields.io/badge/Framework-Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white)](https://www.arduino.cc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <b>A reliable, off-grid telemetry link named after Shakespeare's star-crossed lovers.</b><br>
  <b>Romeo</b> (remote transmitter) traverses the field broadcasting its exact GPS coordinates,<br>
  while <b>Juliet</b> (base station receiver) listens, acknowledges, and renders real-time telemetry on an LCD.
</p>

[Quickstart](#-quickstart--flashing-guide) • [Circuit Schematics](#-project-showcase--circuit-schematics) • [Pinout Reference](#-pin-mapping--wiring-reference) • [Limitations](LIMITATIONS.md) • [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

</div>

## 📑 Table of Contents
- [📖 Overview & Operational Narrative](#-overview--operational-narrative)
- [🎯 Problem Statement](#-problem-statement)
- [💡 Proposed Architecture](#-proposed-architecture)
- [📸 Project Showcase & Circuit Schematics](#-project-showcase--circuit-schematics)
- [🛠️ Hardware Stack & Bill of Materials](#️-hardware-stack--bill-of-materials)
- [⚡ Pin Mapping & Wiring Reference](#-pin-mapping--wiring-reference)
- [📡 Radio Protocol & Packet Specification](#-radio-protocol--packet-specification)
- [🚀 Quickstart & Flashing Guide](#-quickstart--flashing-guide)
- [📂 Project Structure](#-project-structure)
- [⚖️ Engineering Scope & Limitations](#️-engineering-scope--limitations)
- [🔮 Future Scope & Roadmap](#-future-scope--roadmap)
- [📄 License & Authors](#-license--authors)

---

## 📖 Overview & Operational Narrative

Modern search-and-rescue, wilderness trekking, drone recovery, and agricultural tracking operations frequently take place in radio-denied, remote environments where cellular networks (4G/5G) and Wi-Fi are non-existent.

**Project Verona** solves this problem by pairing low-power sub-GHz **SX1278 LoRa (433 MHz)** radio transceivers with high-performance **ESP32 dual-core microcontrollers**:
* **Romeo (Remote Mobile Tracker):** Operates untethered on a single-cell Li-ion battery (3.7V boosted to 5.0V via MT3608). It ingests real-time NMEA sentences from a u-blox GPS module over hardware UART. Once a verified satellite lock is achieved, Romeo encapsulates its latitude and longitude into an RF packet and broadcasts across the ISM band: *"Wherefore art thou?"*
* **Juliet (Fixed Base Station):** Powered continuously via USB. Juliet monitors the 433 MHz channel. Upon capturing Romeo's packet, Juliet verifies packet integrity, extracts geographic coordinates, computes the signal RSSI / SNR, renders the live position to an HD44780 16x2 I2C LCD display, outputs telemetry to the host workstation over serial, and instantly returns an `ACK` packet: *"Here I am."*

---

## 🎯 Problem Statement

| Operational Challenge | Conventional Limitations | Project Verona Solution |
| :--- | :--- | :--- |
| **Zero Cellular Coverage** | GSM/4G trackers stop transmitting when outside cell tower reach | Point-to-point sub-GHz LoRa RF provides km-scale link budget without external infrastructure |
| **High Subscription Costs** | Commercial satellite trackers (e.g., Iridium, Garmin inReach) require monthly data fees | 100% license-free ISM 433 MHz band operation with zero recurring expenses |
| **Power Inefficiency** | High-draw cellular modules exhaust portable batteries within hours | Power-managed ESP32 + LoRa link enables multi-hour field autonomy on a single 18650 cell |
| **Field Diagnostic Visibility**| Headless trackers offer no physical status feedback to ground teams | Integrated 16x2 I2C display on Juliet shows instant coordinates without requiring a PC |

---

## 💡 Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PROJECT VERONA TOPOLOGY                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ROMEO (Field Mobile Node)                              JULIET (Base Station)
  ┌───────────────────────┐                              ┌───────────────────┐
  │ 3.7V Li-ion + TP4056  │                              │ USB 5V Main Power │
  │    + MT3608 (5.0V)    │                              └─────────┬─────────┘
  └───────────┬───────────┘                                        │
              ▼                                                    ▼
  ┌───────────────────────┐                              ┌───────────────────┐
  │     ESP32 Node U1     │                              │   ESP32 Node U1   │
  │   (Classic DevKit)    │                              │ (Classic DevKit)  │
  └───┬───────────────┬───┘                              └───┬───────────┬───┘
      │ UART          │ SPI                                  │ SPI       │ I2C
      ▼ (D32/D33)     ▼ (D5/14/26/18/19/23)                  ▼           ▼ (D21/D22)
  ┌───────────┐   ┌───────────┐                      ┌───────────┐   ┌───────────┐
  │ u-blox    │   │  Ra-02    │                      │  Ra-02    │   │ 16x2 LCD  │
  │ NEO-6M GPS│   │  SX1278   │                      │  SX1278   │   │ (PCF8574) │
  └─────┬─────┘   └─────┬─────┘                      └─────┬─────┘   └───────────┘
        │               │                                  │
    [Patch Ant]    [433MHz Ant]                       [433MHz Ant]
                        │                                  │
                        └─── ))) 433 MHz LoRa RF ((( ──────┘
                                  PING,lat,lon ──>
                                  <── ACK
```

---

## 📸 Project Showcase & Circuit Schematics

> [!NOTE]
> *Hardware photo gallery is currently being shot and rendered. Until live hardware studio photography is pushed, the production-grade, verified **Rev 1.1 vector circuit schematics** are embedded below as full visual references.*

### 1. Romeo (Transmitter Node) — Schematic Rev 1.1
Full schematic displaying the TP4056 charger, MT3608 boost converter, ESP32 microcontroller, SX1278 Ra-02 transceiver, and GY-GPS6MV2 module with power rails, decoupling capacitor, and RF interfaces.

<p align="center">
  <img src="docs/Romeo_Circuit_Diagram.svg" alt="Project Verona - Romeo Transmitter Circuit Diagram" width="100%">
</p>

### 2. Juliet (Receiver / Base Station) — Schematic Rev 1.1
Full schematic displaying the USB-powered ESP32 base station, SX1278 Ra-02 transceiver, and 16x2 HD44780 LCD display with PCF8574 I2C backpack.

<p align="center">
  <img src="docs/Juliet_Circuit_Diagram.svg" alt="Project Verona - Juliet Receiver Circuit Diagram" width="100%">
</p>

---

## 🛠️ Hardware Stack & Bill of Materials

### Romeo (Transmitter Node)

| Ref Des | Component | Specification / Value | Function |
| :--- | :--- | :--- | :--- |
| **U1** | ESP32 Dev Module | Dual Core Xtensa 240MHz, 30/38-pin | Central processing & telemetry controller |
| **U2** | Ai-Thinker Ra-02 | Semtech SX1278, 433 MHz, SPI | Long-range RF transceiver |
| **U3** | GY-GPS6MV2 | u-blox NEO-6M / NEO-7M GPS | Position sensor (NMEA 9600 baud) |
| **BT1**| Li-ion Battery | 3.7 V, 1000 mAh+ (18650 or LiPo) | Portable DC power source |
| **U4** | TP4056 Board | Type-C USB with battery protection | Constant-current / constant-voltage charging |
| **SW1**| SPST Switch | Slide or toggle rated 1A+ | System power toggle (OFF during charging) |
| **U5** | MT3608 Module | DC-DC Step-Up (boost to 5.00 V) | Voltage booster to ESP32 VIN |
| **C1** | Electrolytic Cap | 100 µF, 10V+ | Decoupling buffer across Ra-02 3V3/GND |
| **J1** | RF Pigtail Cable | IPEX (u.FL) to SMA-Female | Antenna connection for Ra-02 |
| **ANT1**| Whip Antenna | 433 MHz SMA rubber-duck (50 Ω) | RF transmission antenna |
| **ANT2**| Ceramic Antenna | Patch antenna with u.FL cable | GPS satellite reception antenna |

### Juliet (Receiver / Base Station)

| Ref Des | Component | Specification / Value | Function |
| :--- | :--- | :--- | :--- |
| **U1** | ESP32 Dev Module | Dual Core Xtensa 240MHz, 30/38-pin | Base station controller |
| **U2** | Ai-Thinker Ra-02 | Semtech SX1278, 433 MHz, SPI | Long-range RF transceiver |
| **U3** | 16x2 LCD Display | HD44780 + PCF8574 I2C backpack (5V) | On-station coordinates display |
| **C1** | Electrolytic Cap | 100 µF, 10V+ | Decoupling buffer across Ra-02 3V3/GND |
| **J1** | RF Pigtail Cable | IPEX (u.FL) to SMA-Female | Antenna connection for Ra-02 |
| **ANT1**| Whip Antenna | 433 MHz SMA rubber-duck (50 Ω) | RF reception antenna |
| **J3** | USB Cable | Micro-USB or USB-C data cable | 5V PC power & serial telemetry link |

---

## ⚡ Pin Mapping & Wiring Reference

### Master GPIO Allocation (ESP32 Dev Module)

| Subsystem | Signal Name | DevKit Silkscreen | ESP32 GPIO | Connected Module Pin | Logic Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LoRa (SPI)** | `LORA_NSS` | **D5** | GPIO 5 | Ra-02 `NSS` | 3.3 V |
| **LoRa (SPI)** | `LORA_RST` | **D14** | GPIO 14 | Ra-02 `RST` | 3.3 V |
| **LoRa (SPI)** | `LORA_DIO0`| **D26** | GPIO 26 | Ra-02 `DIO0` (Rx/Tx Done) | 3.3 V |
| **LoRa (SPI)** | `LORA_SCK` | **D18** | GPIO 18 | Ra-02 `SCK` | 3.3 V |
| **LoRa (SPI)** | `LORA_MISO`| **D19** | GPIO 19 | Ra-02 `MISO` | 3.3 V |
| **LoRa (SPI)** | `LORA_MOSI`| **D23** | GPIO 23 | Ra-02 `MOSI` | 3.3 V |
| **GPS (UART2)**| `GPS_TX_PIN`| **D32** | GPIO 32 | GPS Module `TX` | 3.3 V |
| **GPS (UART2)**| `GPS_RX_PIN`| **D33** | GPIO 33 | GPS Module `RX` | 3.3 V |
| **LCD (I2C)**  | `I2C_SDA`   | **D21** | GPIO 21 | LCD Backpack `SDA` | 5.0 V / 3.3 V |
| **LCD (I2C)**  | `I2C_SCL`   | **D22** | GPIO 22 | LCD Backpack `SCL` | 5.0 V / 3.3 V |

> [!IMPORTANT]
> **1. D32 / D33 UART Crossover:** Pins `D32` and `D33` are ordinary GPIOs mapped to `HardwareSerial(2)` in software. They leave hardware `RX2/TX2` (GPIO 16/17) unencumbered, preventing memory bus crashes on ESP32-WROVER boards with PSRAM. Note the crossover: **GPS TX connects to ESP32 D32**, and **GPS RX connects to ESP32 D33**.
>
> **2. 3.3V Ra-02 Voltage Warning:** NEVER connect the Ra-02 module to 5V. It must always be powered from the regulated 3.3V rail.

---

## 📡 Radio Protocol & Packet Specification

### Transaction Flow
The communication link operates on a half-duplex, stop-and-wait ARQ (Automatic Repeat reQuest) sequence:

```
  ROMEO (Transmitter)                                      JULIET (Receiver)
         │                                                         │
         │─── [PING,lat,lon] (433 MHz LoRa) ──────────────────────>│
         │    e.g. "PING,12.971600,77.594600"                      │ [Decode lat/lon]
         │                                                         │ [Update 16x2 LCD]
         │                                                         │ [Compute RSSI/SNR]
         │<── [ACK] ───────────────────────────────────────────────│
         │    "ACK"                                                │
         │ [Link verified, wait 3s]                                │
```

### Packet Definitions

| Packet ID | Direction | Format (ASCII) | Example | Description |
| :--- | :--- | :--- | :--- | :--- |
| **PING** | Romeo → Juliet | `PING,<lat>,<lon>` | `PING,12.971600,77.594600` | Carries 6-decimal floating-point latitude and longitude. Only broadcast when GPS fix age < 5000 ms. |
| **ACK**  | Juliet → Romeo | `ACK` | `ACK` | Acknowledgment packet sent immediately upon valid receipt of PING. |

### RF Modulation Parameters
* **Carrier Frequency:** 433.00 MHz
* **Bandwidth (BW):** 125 kHz
* **Spreading Factor (SF):** 7 (default)
* **Coding Rate (CR):** 4/5
* **Preamble Length:** 8 symbols
* **Sync Word:** `0xF3` (SX127X private network)

---

## 🚀 Quickstart & Flashing Guide

For a full step-by-step assembly and hardware calibration walkthrough, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

### Method 1: PlatformIO (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/Mohit-craftsman/Verona.git
   cd Verona
   ```
2. Build and upload Romeo (Transmitter):
   ```bash
   pio run -e romeo --target upload
   pio device monitor -b 9600
   ```
3. Connect Juliet (Receiver), build and upload:
   ```bash
   pio run -e juliet --target upload
   pio device monitor -b 9600
   ```
4. Optional I2C Scanner (to verify LCD backpack address):
   ```bash
   pio run -e i2c_scan --target upload
   pio device monitor -b 9600
   ```

### Method 2: Arduino IDE

1. Install **Arduino IDE v2.x**.
2. Add ESP32 board support via Boards Manager:
   `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Install required libraries via Library Manager:
   * `LoRa` by *Sandeep Mistry*
   * `TinyGPSPlus` by *Mikal Hart*
   * `LiquidCrystal_I2C` by *Frank de Brabander*
4. Flash Romeo:
   * Open `firmware/Romeo/Romeo.ino`
   * Select Board: `DOIT ESP32 DEVKIT V1` (or your model)
   * Select Port and click **Upload**
5. Flash Juliet:
   * Open `firmware/Juliet/Juliet.ino`
   * Select Port and click **Upload**

---

## 📂 Project Structure

```text
Verona/
├── .gitignore                      # Git exclusion rules
├── LICENSE                         # MIT open-source license
├── README.md                       # Main architectural documentation & overview
├── DEPLOYMENT_GUIDE.md             # Hardware assembly, MT3608 calibration & flashing guide
├── LIMITATIONS.md                  # Honest engineering design scope & boundaries
├── platformio.ini                  # Multi-environment PlatformIO build configuration
├── include/                        # Unified C++ header definitions
│   └── config.h                    # Master pin definitions, frequencies & timeouts
├── src/                            # PlatformIO build sources
│   ├── romeo.cpp                   # Romeo transmitter runtime
│   ├── juliet.cpp                  # Juliet base station runtime
│   └── i2c_scan.cpp                # Diagnostic I2C address scanner
├── firmware/                       # Standalone Arduino IDE sketches
│   ├── Romeo/
│   │   └── Romeo.ino               # Romeo Arduino sketch
│   └── Juliet/
│       └── Juliet.ino              # Juliet Arduino sketch
├── docs/                           # Schematics and technical documentation
│   ├── Romeo_Circuit_Diagram.svg   # Romeo schematic (Rev 1.1)
│   ├── Juliet_Circuit_Diagram.svg  # Juliet schematic (Rev 1.1)
│   └── Circuit_Documentation.md    # Detailed circuit analysis & electrical notes
└── tools/                          # Automation scripts
    └── gen_diagrams.py             # Python script for generating SVG schematics
```

---

## ⚖️ Engineering Scope & Limitations

In the spirit of honest and transparent engineering, Project Verona documents all operational boundaries in [LIMITATIONS.md](LIMITATIONS.md). Key points include:

1. **RF Propagation Realities:** While theoretical line-of-sight range exceeds 2–5 km, real-world urban and dense foliage environments attenuate signals to 300 m – 1.2 km.
2. **Cleartext Transmission:** Telemetry packets are sent unencrypted over 433 MHz. Commercial deployments should incorporate AES-128 payload encryption.
3. **Power Path Management:** The TP4056 module lacks dynamic load sharing; switch SW1 must remain OFF during USB battery charging.
4. **GPS TTFF:** Cold starts require 30–60 seconds under an unobstructed open sky.

---

## 🔮 Future Scope & Roadmap

- [ ] **AES-128-CTR Radio Encryption:** Securing the ASCII payload against unauthorized eavesdropping and spoofing.
- [ ] **ESP32 Deep Sleep & LoRa CAD:** Transitioning Romeo into low-power deep sleep between GPS fixes to extend battery life from 5 hours to weeks.
- [ ] **Web Telemetry Dashboard:** Juliet bridging received GPS packets over local Wi-Fi or WebSockets to display real-time Leaflet / OpenStreetMap pins on a tablet or laptop.
- [ ] **Multi-Node Mesh (LoRa APRS):** Extending from point-to-point ping-pong to a multi-hop mesh network for multi-agent asset tracking.
- [ ] **Solar Energy Harvesting:** Integrating a 5V/6V solar cell and MPPT controller into Romeo for autonomous off-grid operation.

---

## 📄 License & Authors

Project Verona is distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

Developed with ❤️ for open-source hardware, radio telemetry enthusiasts, and search-and-rescue teams.
