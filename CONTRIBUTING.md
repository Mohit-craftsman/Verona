# Contributing to Project Verona

Thank you for your interest in contributing to **Project Verona**! We welcome contributions from developers, embedded engineers, radio hobbyists, and documentation writers.

---

## 🧭 Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand our community expectations.

---

## 🛠️ Ways to Contribute

You can contribute to Verona in multiple ways:
* **Bug Reports:** Report hardware anomalies, brownout conditions, or edge-case software crashes using our [Issue Tracker](https://github.com/Mohit-craftsman/Verona/issues).
* **Hardware Validation:** Test the firmware on different ESP32 board revisions (e.g., 30-pin vs. 38-pin DevKit, WROVER with PSRAM, TTGO LoRa32) and submit range / performance logs.
* **Documentation & Schematics:** Improve wiring guides, add annotations, or fix typos in guides.
* **Firmware Improvements:** Optimize LoRa airtime, implement low-power sleep modes, or enhance GPS sentence parsing.

---

## 💻 Development Environment Setup

Project Verona supports two distinct workflows: PlatformIO (preferred for multi-node compilation) and the Arduino IDE (for single-file flashing).

### Option A: PlatformIO (Recommended)

1. **Prerequisites:** Install [PlatformIO Core (CLI)](https://docs.platformio.org/en/latest/core/installation/index.html) or the PlatformIO IDE extension in VS Code.
2. **Build Targets:**
   * Romeo (Field Transmitter):
     ```bash
     pio run -e romeo
     pio run -e romeo -t upload
     ```
   * Juliet (Base Station Receiver):
     ```bash
     pio run -e juliet
     pio run -e juliet -t upload
     ```
   * I2C Diagnostic Scanner:
     ```bash
     pio run -e i2c_scan
     pio run -e i2c_scan -t upload
     ```
3. **Serial Monitor:**
   All firmware environments default to **9600 baud**:
   ```bash
   pio device monitor -b 9600
   ```

### Option B: Arduino IDE

1. **Board Package:** Add the ESP32 board package URL in **Preferences -> Additional Boards Manager URLs**:
   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
2. **Required Libraries:** Install the following via Library Manager:
   * `LoRa` by *Sandeep Mistry* (v0.8.0+)
   * `TinyGPSPlus` by *Mikal Hart* (v1.0.3+)
   * `LiquidCrystal_I2C` by *Frank de Brabander* / *Marco Schwartz* (v1.1.4+)
3. **Firmware Structure & Relationship:**
   * `src/` contains the source compilation units managed by PlatformIO (`romeo.cpp`, `juliet.cpp`, `i2c_scan.cpp`).
   * `firmware/` contains standalone, zero-dependency Arduino sketches (`firmware/Romeo/Romeo.ino` and `firmware/Juliet/Juliet.ino`) for users who prefer Arduino IDE.
   * If you update core runtime logic in `src/`, please mirror the functional change in `firmware/` to keep both workflows identical.

---

## 🎨 Coding Style & Guidelines

* **Consistency First:** Match the surrounding code indentation (2 spaces), naming conventions, and comment formatting.
* **No Unrelated Formatting:** Avoid running auto-formatters over untouched files in a pull request. Keep diffs minimal and focused.
* **Safety First:** Keep pin assignments centralized or strictly documented. Ensure SPI NSS / RST / DIO0 pins and UART mappings do not conflict with ESP32 bootstrap pins (GPIO 0, 2, 12, 15) or PSRAM pins (GPIO 16, 17 on WROVER).

---

## 🔬 Hardware Testing & Evidence Expectations

Because Project Verona is an embedded RF project, code changes can alter hardware timing or power draw. Pull requests modifying firmware should provide validation evidence:

1. **Which Node(s) Were Tested:** Romeo, Juliet, or Both.
2. **Testing Level:** Real hardware breadboard / prototype testing, or compile-only validation.
3. **Verification Evidence:**
   * Attach a clean copy of the Serial Monitor log (at 9600 baud).
   * If modifying Juliet's display subsystem, attach a photo or video showing the 16x2 LCD rendering coordinates.

---

## 🚀 Pull Request Process

1. **Branch Naming:** Create a feature or fix branch from `main`:
   * `feat/your-feature-name`
   * `fix/bug-description`
   * `docs/documentation-update`
   * `chore/refactoring-task`
2. **Commit Conventions:** Follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: implement CAD sleep mode`, `docs: fix UART pin label in README`).
3. **Verification Gate:** Confirm that your changes compile cleanly under PlatformIO:
   ```bash
   pio run -e romeo
   pio run -e juliet
   pio run -e i2c_scan
   ```
4. **Submit PR:** Open a Pull Request targeting `main`. Complete all items in the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).

---

## 🐛 Reporting Bugs

Before opening a bug report:
1. Review [LIMITATIONS.md](LIMITATIONS.md) to verify whether the behavior is an intentional design boundary.
2. Review [TROUBLESHOOTING_ROMEO.md](TROUBLESHOOTING_ROMEO.md) and [TROUBLESHOOTING_JULIET.md](TROUBLESHOOTING_JULIET.md).
3. If the issue persists, submit a report using the [Bug Report Form](.github/ISSUE_TEMPLATE/bug_report.yml), providing your board revision, node type, firmware version, and Serial Monitor log.

---

## 📂 Repository Map

* **`src/`** — PlatformIO source compilation units (`romeo.cpp`, `juliet.cpp`, `i2c_scan.cpp`, `main.cpp`).
* **`include/`** — Master C++ configuration headers and pin definitions (`config.h`).
* **`firmware/`** — Standalone Arduino IDE sketches (`firmware/Romeo/`, `firmware/Juliet/`).
* **`docs/`** — Technical documentation, hardware schematics, and prototype photography.
* **`tools/`** — Build automation and schematic generation utilities (`gen_diagrams.py`).
* **`.github/`** — CI workflows and issue / pull request templates.
