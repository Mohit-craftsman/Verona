## Description

Brief summary of changes and the motivation behind them.

Linked Issue: Fixes # (if applicable)

---

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Documentation update (wiring, guides, schematics)
- [ ] CI / Toolchain improvement

---

## Subsystem / Node(s) Touched

- [ ] Romeo (Field Transmitter)
- [ ] Juliet (Base Station Receiver)
- [ ] Shared configuration (`include/config.h`)
- [ ] Hardware schematics / BOM (`docs/hardware/`)
- [ ] Documentation / CI

---

## Validation & Verification Checklist

- [ ] **Hardware Testing:**
  - [ ] Tested on physical hardware breadboard / prototype.
  - [ ] Compile-only validation.
  - *Details / Serial Log:* Attached serial log (at 9600 baud) or photo of LCD output.
- [ ] **PlatformIO Compilation:**
  - [ ] Verified `pio run -e romeo` passes without warnings.
  - [ ] Verified `pio run -e juliet` passes without warnings.
  - [ ] Verified `pio run -e i2c_scan` passes without warnings.
- [ ] **Documentation:**
  - [ ] Updated `README.md`, `DEPLOYMENT_GUIDE.md`, or schematics if pinouts or behavior changed.
  - [ ] Updated `CHANGELOG.md` under `[Unreleased]`.
- [ ] **Code Hygiene:**
  - [ ] No unrelated reformatting or whitespace changes in existing code.
  - [ ] No hardcoded personal paths or secrets.
