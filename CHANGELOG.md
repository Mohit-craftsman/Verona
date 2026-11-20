# Changelog

All notable changes to **Project Verona** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- AES-128-CTR hardware radio payload encryption.
- ESP32 deep-sleep cycling with LoRa Channel Activity Detection (CAD).
- Web-based telemetry dashboard with local WebSocket Leaflet map rendering.
- Multi-node LoRa APRS mesh networking.

---

## [1.1] - 2026-11-19

### Added
- **Romeo Transmitter Node:** Real-time u-blox NEO-6M / NEO-7M NMEA parsing via UART2 remapped to GPIO 32/33, automatic ASCII coordinate packetization (`PING,<lat>,<lon>`), and stop-and-wait ARQ with ACK timeout handling.
- **Juliet Receiver Node:** 433 MHz SX1278 LoRa continuous listening, packet CRC integrity checking, RSSI and SNR link margin computation, immediate ACK return (`ACK`), and HD44780 16x2 I2C LCD rendering (confirmed address `0x26`).
- **Circuit Schematics (Rev 1.1):** Clean vector SVG schematics for both Romeo and Juliet incorporating TP4056 single-cell charging with protection, MT3608 DC-DC boost step-up to 5.0V, SPST power isolation switch, and $100\,\mu\text{F}$ electrolytic decoupling buffers across the Ra-02 3.3V rail.
- **Field Troubleshooting Guides:** Authored dedicated, exhaustive diagnostic manuals [TROUBLESHOOTING_ROMEO.md](TROUBLESHOOTING_ROMEO.md) and [TROUBLESHOOTING_JULIET.md](TROUBLESHOOTING_JULIET.md) covering SPI init freezes, GPS satellite fix acquisition, brownout loops, and I2C LCD contrast calibration.
- **Hardware Prototype Photography:** Real-world breadboard assembly photography added for transmitter, base station, and power subsystem.
- **Multi-Toolchain Build Support:** Dual PlatformIO configuration (`platformio.ini` with `romeo`, `juliet`, and `i2c_scan` environments) alongside standalone Arduino IDE sketches under `firmware/`.
- **Engineering Governance:** Published [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [LIMITATIONS.md](LIMITATIONS.md) outlining physical assembly requirements and operational RF boundaries.
