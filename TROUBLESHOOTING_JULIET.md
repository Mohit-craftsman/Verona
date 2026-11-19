# Project Verona — Juliet (Receiver) Troubleshooting Guide

> **Hardware:** ESP32 Dev Module + Ra-02 (SX1278, 433 MHz) + 16×2 I2C LCD  
> **Firmware:** `src/juliet.cpp`  
> **PlatformIO env:** `juliet`

---

## Issue 1 — PlatformIO Stuck at "Configuring Project: 100%"

### Symptom
The VS Code status bar shows `PlatformIO: Configuring project: 100%` and freezes for
more than a few minutes.

### Root Cause
The `espressif32` platform toolchain (~400–600 MB) download was interrupted or cancelled,
leaving a corrupted partial package in the PlatformIO cache.

### Fix
Open a terminal inside VS Code and run the following commands in order:

```powershell
# 1. Delete the broken framework cache
Remove-Item -Recurse -Force "$env:USERPROFILE\.platformio\packages\framework-arduinoespressif32*" -ErrorAction SilentlyContinue

# 2. Delete the broken platform cache
Remove-Item -Recurse -Force "$env:USERPROFILE\.platformio\platforms\espressif32*" -ErrorAction SilentlyContinue

# 3. Reinstall the platform cleanly (do NOT cancel this)
~\.platformio\penv\Scripts\pio.exe platform install espressif32

# 4. Build Juliet
~\.platformio\penv\Scripts\pio.exe run -e juliet
```

> ⚠️ **Do not click Cancel during the install.** It will appear to hang at 100% while
> extracting — this is normal. Wait for the `has been installed!` message.

---

## Issue 2 — `pio` Not Recognised in PowerShell

### Symptom
```
pio : The term 'pio' is not recognized as the name of a cmdlet...
```

### Root Cause
PlatformIO installs into its own Python virtual environment. The VS Code terminal that
opened before PlatformIO finished installing does not have `pio` on its `PATH`.

### Fix — Option A: Use the PlatformIO built-in terminal
Press `Ctrl+Shift+P` → type `PlatformIO: New Terminal` → Enter.  
This terminal has `pio` pre-loaded.

### Fix — Option B: Use the full path
```powershell
~\.platformio\penv\Scripts\pio.exe run -e juliet --target upload
```

---

## Issue 3 — LCD Backlight ON but Screen Blank (No Text)

### Symptom
- LCD backlight glows
- No characters or text visible at all

### Root Cause (most likely)
The **contrast potentiometer** on the I2C backpack is set too low (fully counter-clockwise
from factory).

### Fix
Locate the small **blue rectangular potentiometer** on the back of the I2C module.
Using a small flat-head screwdriver, turn it **slowly clockwise** while the board is
powered. Text or black squares will appear at the correct position.

```
Back of I2C backpack:
┌──────────────────┐
│                  │
│   [blue pot] ◄── turn slowly clockwise until text appears
│                  │
└──────────────────┘
```

> If black filled squares (█) appear, the contrast is slightly too high — back off
> a tiny amount counter-clockwise until the squares resolve into readable characters.

---

## Issue 4 — LCD Shows Black Squares After Contrast Adjustment but Still No Text

### Symptom
- Contrast pot adjusted correctly (squares visible)
- Text never appears even after flashing

### Root Cause
The I2C address in the firmware does not match the actual address of the LCD module.
The two most common addresses are `0x27` and `0x3F`, but some modules ship with
non-default address jumper configurations (e.g. `0x26`).

### Diagnosis — Run the I2C Scanner

Flash the included scanner firmware to discover the real address:

```powershell
~\.platformio\penv\Scripts\pio.exe run -e i2c_scan --target upload
~\.platformio\penv\Scripts\pio.exe device monitor -e i2c_scan
```

**Expected output:**
```
I2C Scanner — scanning...
Device found at address: 0x26      ← your LCD's real address
Done. 1 device(s) found.
```

### Fix
Update the address in `src/juliet.cpp` line 31:

```cpp
// Before (default guess):
LiquidCrystal_I2C lcd(0x27, 16, 2);

// After (confirmed by scanner — specific to this module):
LiquidCrystal_I2C lcd(0x26, 16, 2);
```

Then re-flash Juliet:
```powershell
~\.platformio\penv\Scripts\pio.exe run -e juliet --target upload
```

> ℹ️ **Why 0x26?**  
> The I2C backpack uses a PCF8574 chip with three address-select pads (A0, A1, A2).
> The factory default (`0x27`) assumes all three pads open (HIGH). This module had
> **A0 bridged to GND**, shifting the address one step down to `0x26`. This is a valid
> hardware configuration, not a defect.

---

## Issue 5 — "No ACK — is Juliet in range?" on Romeo

### Symptom
Romeo transmits PING packets with valid GPS coordinates but never receives an ACK.

### Checklist

| Check | Expected |
|---|---|
| Juliet powered on | ✅ LED on, Serial Monitor shows `Juliet (base) ready` |
| LoRa frequency matches | Both set to `433E6` in respective `.cpp` files |
| LoRa DIO0 pin | Both wired to **GPIO26** |
| Romeo within range | Start within 10 m for initial test |
| Antenna attached | u.FL antenna cable snapped on securely |
| No other device on same LoRa channel | Interference from other 433 MHz devices |

### Quick test
Open Juliet's Serial Monitor while Romeo is transmitting. You should see:
```
PING from Romeo: 23.152040,72.889279  (RSSI -65 dBm)
ACK sent
```
If this appears in Juliet's monitor but Romeo still shows "No ACK", the ACK packet is
being lost — reduce the `ACK_TIMEOUT_MS` in `romeo.cpp` or move the boards closer.

---

## Issue 6 — LCD Shows Nothing After Re-flash

### Symptom
Juliet was working, then after re-flashing the LCD goes blank again.

### Fix
The contrast pot may need a tiny re-adjustment after each fresh boot (LCD re-initialises).
This is a one-time physical setup per session. Locking the pot with a small drop of
nail varnish after finding the right position prevents this.

---

## Verified Working Configuration

| Parameter | Value |
|---|---|
| LCD I2C address | `0x26` |
| LCD size | 16 columns × 2 rows |
| I2C SDA pin | GPIO21 |
| I2C SCL pin | GPIO22 |
| LCD VCC | VIN (5 V) — **not 3.3 V** |
| LoRa SS | GPIO5 |
| LoRa RST | GPIO14 |
| LoRa DIO0 | GPIO26 |
| LoRa SCK | GPIO18 |
| LoRa MISO | GPIO19 |
| LoRa MOSI | GPIO23 |
| LoRa frequency | 433 MHz |
| PlatformIO env | `juliet` |
| espressif32 version | 8.0.0 |
| LoRa library | `sandeepmistry/LoRa @ ^0.8.0` |
| LCD library | `marcoschwartz/LiquidCrystal_I2C @ ^1.1.4` |

---

*Document created during initial hardware bring-up of Project Verona — November 2026.*
