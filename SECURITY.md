# Security Policy

## Supported Versions

The following versions of **Project Verona** firmware and documentation are currently supported with security and bug updates:

| Version | Supported | Notes |
| :--- | :--- | :--- |
| **1.1** | :white_check_mark: | Current active release branch. |
| < 1.1 | :x: | Legacy / prototype revisions. Please upgrade to 1.1. |

---

## ⚠️ Documented Architectural Limitations

Project Verona operates as an educational and open-source hardware reference design. Before reporting a vulnerability, please review our documented boundaries in [LIMITATIONS.md](LIMITATIONS.md):

* **Cleartext Radio Link:** The 433 MHz ISM radio link uses unencrypted, unauthenticated ASCII frames (`PING,<lat>,<lon>` and `ACK`). Broadcast transmissions can be received, inspected, or spoofed by any compliant SX1278 transceiver in radio range. This is an intentional, documented architecture limitation of Rev 1.1 rather than an implementation vulnerability. Cryptographic authentication (e.g. AES-128-CTR) is tracked for future milestones.
* **Open Serial Interfaces:** The USB UART serial monitor outputs plaintext GPS coordinates and link diagnostics without authentication. Physical access to the nodes grants direct telemetry access.

---

## Reporting a Vulnerability

If you discover a software bug that compromises local device operation (such as buffer overruns in NMEA/packet decoding, integer overflows, memory corruption, or unsafe pointer handling), please disclose it responsibly.

### Disclosure Process

1. **Do not open a public issue.**
2. Send an email to the project maintainer at [mohitsihagg@gmail.com](mailto:mohitsihagg@gmail.com).
3. Include detailed information:
   * Affected node (`Romeo`, `Juliet`, or core library).
   * Exact steps to reproduce the exploit or fault.
   * Serial logs, memory dump, or proof-of-concept sketch.
4. Maintainers will acknowledge receipt within 48 hours and work toward a coordinated remediation.