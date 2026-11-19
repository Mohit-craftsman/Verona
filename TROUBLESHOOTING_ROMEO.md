# Project Verona — Romeo (Transmitter) Troubleshooting Guide

> **Hardware:** ESP32 Dev Module + Ra-02 (SX1278, 433 MHz) + u-blox NEO-6M GPS (HW-248) + TP4056 + MT3608  
> **Firmware:** `src/romeo.cpp`  
> **PlatformIO env:** `romeo`

---

## Issue 1 — "LoRa Error" on Startup (SPI Init Fails)

### Symptom
On boot, the Serial Monitor outputs:
```
Romeo (remote) ready
LoRa Error
```
The program enters an infinite loop (`while (1);`) and halts.

### Root Cause
The ESP32 cannot communicate with the Semtech SX1278 transceiver over SPI. Common causes:
1. Floating or loose SPI wires (`NSS`, `RST`, `DIO0`, `SCK`, `MISO`, `MOSI`).
2. Ra-02 module powered from 5V (damage) or unpowered.
3. Missing 100 µF decoupling capacitor `C1` across the 3.3V rail.

### Fix Checklist

| Pin Name | Ra-02 Breakout Pin | ESP32 Silkscreen | ESP32 GPIO | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **NSS** | `NSS` | **D5** | GPIO 5 | SPI Chip Select |
| **RST** | `RST` | **D14** | GPIO 14 | Hardware Reset |
| **DIO0**| `DIO0`| **D26** | GPIO 26 | Packet Interrupt (CRITICAL: ensure not D2) |
| **SCK** | `SCK` | **D18** | GPIO 18 | SPI Clock |
| **MISO**| `MISO`| **D19** | GPIO 19 | SPI Master-In |
| **MOSI**| `MOSI`| **D23** | GPIO 23 | SPI Master-Out |
| **VCC** | `3.3V`| **3V3** | 3.3V Rail | **NEVER connect to 5V or VIN!** |
| **GND** | `GND` | **GND** | GND Rail | Common ground |

> 💡 **Decoupling Capacitor:** Place the 100 µF capacitor directly across the Ra-02 `3.3V` and `GND` pins. Without this buffer, the instant the SX1278 powers up its internal synthesizer, the 3.3V rail dips, causing SPI register reads to return garbage.

---

## Issue 2 — GPS Stuck on "Waiting for GPS fix..." (CHARS=0 or No Fix)

### Symptom
Romeo initializes LoRa, but the Serial Monitor repeatedly logs:
```
Waiting for GPS fix... (Chars: 0, Sentences: 0)
```
or logs characters arriving, but coordinates never appear.

### Case A: Chars = 0 (No Data Received from GPS Module)
* **Root Cause:** UART RX/TX wiring reversed or wired to wrong pins.
* **Fix:** Verify the UART2 crossover:
  * **GPS `TX`** must connect to **ESP32 `D32`** (GPIO 32, remapped as UART2 RX).
  * **GPS `RX`** must connect to **ESP32 `D33`** (GPIO 33, remapped as UART2 TX).
  * Confirm GPS module `VCC` is connected to the 3.3V rail and `GND` to common ground.
  * Check that baud rate in code matches the module default: `Serial2.begin(9600, SERIAL_8N1, 32, 33);`.

### Case B: Chars > 0, but Fix Never Locks (Fix Age > 5000ms / Satellites = 0)
* **Root Cause:** Indoor attenuation or ceramic patch antenna orientation.
* **Fix:**
  1. **Sky View:** GPS signals (1575.42 MHz) cannot penetrate concrete walls, metallic window coatings, or multi-story ceilings. **Take Romeo outdoors or place the patch antenna outside an open window.**
  2. **Antenna Orientation:** Ensure the ceramic patch antenna is resting **flat with the ceramic face pointing directly UP toward the sky** (do not leave it on its side or upside down).
  3. **Cold Start Time:** Under open sky, cold start takes **30–90 seconds**. Once satellites are locked, the red **PPS LED** on the GPS module will begin blinking at 1 Hz.

---

## Issue 3 — ESP32 Brownout Reset Loop on Battery Power

### Symptom
When powered via the Li-ion battery and MT3608 boost converter, Romeo resets repeatedly. The Serial Monitor shows:
```
Brownout detector was triggered
ets Jun  8 2016 00:22:57
rst:0xc (SW_CPU_RESET)
```
This typically occurs right when the LoRa module attempts to transmit its `PING` packet.

### Root Cause
During RF packet transmission at +17 dBm (50 mW), the Ra-02 draws an instantaneous current burst of ~120–150 mA. If the MT3608 boost converter output dips below ~4.5V, the ESP32 internal low-dropout regulator drops below 2.8V, tripping the internal hardware brownout detector.

### Fix
1. **Calibrate MT3608:** Using a multimeter, probe MT3608 `OUT+` and `OUT-` under load. Ensure the output is adjusted via trimmer `RV1` to **exactly 5.00 V** (not 4.2V or 4.5V).
2. **Add Decoupling:** Confirm the **100 µF electrolytic capacitor** is installed across the 3.3V and GND rails near the Ra-02.
3. **Battery Voltage:** Check the 18650 / LiPo cell voltage. If the battery is depleted (<3.4V), the MT3608 cannot maintain regulated 5V output under surge current.
4. **Jumper Wires:** Avoid thin, high-resistance jumper wires between the MT3608 output and ESP32 `VIN` / `GND`. Loose breadboard contacts introduce significant voltage drops during RF pulses.

---

## Issue 4 — MT3608 Boost Calibration & ESP32 Overvoltage Hazard

### Symptom
ESP32 fails to turn on, smells hot, or burns out upon battery connection.

### Root Cause
MT3608 boost converter modules straight from the factory are often adjusted to output **18V–28V**. Connecting an uncalibrated boost converter directly to the ESP32 `VIN` pin will instantly destroy the ESP32 onboard regulator!

### Safe Calibration Procedure
1. Disconnect the wire going to the ESP32 `VIN` pin.
2. Turn switch `SW1` ON so the MT3608 is powered by the battery.
3. Probe MT3608 `OUT+` and `OUT-` with a digital multimeter on DC Volts.
4. Rotate trimmer `RV1` **counter-clockwise** (often requires 10 to 20 full rotations) until the multimeter reads steadily at **5.00 V (±0.05 V)**.
5. Turn switch `SW1` OFF. Only now reconnect `OUT+` to the ESP32 `VIN` pin.

---

## Issue 5 — TP4056 Battery Charging & Power Path Safety Rule

### Symptom
Battery overheats during charging, or charging status LEDs flicker erratically.

### Root Cause
The standard TP4056 charger module does **not** feature automatic power path management (dynamic load sharing). If switch `SW1` remains closed (ON) while a USB-C charging cable is plugged into the TP4056:
* The ESP32 and modules continuously draw 100–200 mA from the charger.
* The TP4056 cannot detect the standard charge termination current ($C/10$), preventing it from cleanly ending the charging cycle at 4.20V.

### Safe Charging Rule
```
               [USB-C 5V Input]
                      │
                      ▼
┌───────────────────────────────────────────┐
│               TP4056 Module               │
│   B+ / B-                     OUT+ / OUT- │
└──────┬─────────────────────────────┬──────┘
       │                             │
 [3.7V Battery]               [SW1 Switch] ◄── MUST BE "OFF" WHILE CHARGING
                                     │
                             [MT3608 -> ESP32]
```
> ⚠️ **Always turn switch SW1 OFF before plugging in the USB-C charger.** Charge until the blue LED illuminates, unplug the USB-C cable, and only then flip SW1 back ON.

---

## Issue 6 — "No ACK — is Juliet in range?" on Romeo

### Symptom
Romeo transmits valid coordinates via `PING,lat,lon`, waits for up to 1500 ms, and outputs:
```
PING sent: 23.152040,72.889279
No ACK - is Juliet in range?
```

### Root Cause & Checklist

| Area | Diagnostic Step | Expected State |
| :--- | :--- | :--- |
| **Antenna** | Inspect u.FL pigtail connector on both nodes | Cable must be firmly snapped onto the gold IPEX socket on Ra-02. |
| **Juliet Status** | Check Juliet Serial Monitor / LCD | Juliet must display `Juliet ready` and show `ACK sent` upon receipt. |
| **Frequency** | Check `romeo.cpp` and `juliet.cpp` | Both must initialize with `LoRa.begin(433E6)`. |
| **Sync Word** | Check `config.h` or sketches | If sync word is set, both must match (default `0xF3` or library default). |
| **Turnaround Time** | Juliet ACK delay | In `juliet.cpp`, ensure `delay(30)` is present before sending ACK to allow Romeo time to switch from TX to RX mode. |

---

## Issue 7 — PlatformIO Upload Fails (`Timed out waiting for packet header`)

### Symptom
```
A fatal error occurred: Failed to connect to ESP32: Timed out waiting for packet header
```

### Root Cause
The auto-reset circuit on some ESP32 DevKit boards fails to pull GPIO 0 low when PlatformIO attempts to initiate the bootloader.

### Fix
1. Hold down the physical **BOOT** (or `IO0`) button on the ESP32 board.
2. In VS Code, start the upload: `pio run -e romeo --target upload`.
3. When the terminal displays `Connecting........_____.....`, release the **BOOT** button.
4. Flashing will proceed to 100%.

---

## Verified Working Configuration

| Parameter | Value | Notes |
|---|---|---|
| LoRa Frequency | `433 MHz` (`433E6`) | Ra-02 transceiver |
| LoRa SS (NSS) | `GPIO 5` | Hardware SPI Chip Select |
| LoRa RST | `GPIO 14` | Hardware Reset |
| LoRa DIO0 | `GPIO 26` | Packet Rx/Tx interrupt |
| LoRa SCK | `GPIO 18` | Hardware SPI Clock |
| LoRa MISO | `GPIO 19` | Hardware SPI Master-In |
| LoRa MOSI | `GPIO 23` | Hardware SPI Master-Out |
| GPS RX (ESP32 TX) | `GPIO 33` | Connects to GPS `RX` |
| GPS TX (ESP32 RX) | `GPIO 32` | Connects to GPS `TX` |
| GPS Baud Rate | `9600 baud` | Default for u-blox NEO-6M |
| Supply Voltage (VIN)| `5.00 V` | Regulated via MT3608 boost converter |
| Decoupling Buffer | `100 µF, 10V+` | Across Ra-02 3V3/GND |
| PlatformIO env | `romeo` | `platformio.ini` |
| Core Framework | `arduino` | `framework-arduinoespressif32` |

---

*Document created during initial hardware bring-up of Project Verona — November 2026.*
