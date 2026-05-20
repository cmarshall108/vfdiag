# 17 — Engineering Menu, OS Developer Settings & TOTP Security

This document covers the technical architecture, access methods, and security protocols surrounding the VinFast VF 8's Android Automotive OS infotainment head unit (MHU), including the hidden **Engineering Menu**, **Developer Options**, and the **Time-Based One-Time Password (TOTP)** cryptographic gate.

---

## 1. Infotainment (MHU) Architecture Overview

The VF 8's Media Head Unit (MHU/IVI) runs on a modern telematics and cockpit architecture:
*   **Operating System**: Android Automotive OS (AAOS), heavily customized with VinFast's proprietary launcher skin.
*   **SoC (System on Chip)**: Qualcomm Snapdragon Automotive Cockpit Platform (usually SA8155P or similar Tier-1 hardware).
*   **Storage & Partitioning**: eMMC/UFS flash partitioned using standard Android A/B redundancy for fail-safe OTA flashing.
*   **Security Barrier**: The Android subsystem is isolated from critical traction components (such as BMS, MCU, and VCU). It connects to the vehicle's High-Speed CAN-FD loops via a **Central Gateway (GW)** that enforces **SecOC (Secure Onboard Communication)**. You cannot write CAN messages directly from Android without routing through GW authentication firmware.

---

## 2. Entering the Infotainment Engineering Menu

Sub-menus are hidden inside the infotainment system for field engineers, assembly QA, and development testers. Access techniques vary by software version (FRS 9.x vs. FRS 10.x):

### The Tap Sequence (Standard Entry)
1.  On the 15.6" central touchscreen, tap **Settings** (gear icon).
2.  Navigate to **System / About** or **System / Software Information**.
3.  Locate the line item displaying the **VinFast OS Version** (or **Baseband Version** / **Build Number**).
4.  Tap this line rapidly **7 times**.
5.  A security overlay prompt pop-up will appear on-screen demanding an **Access Password** or **Response Token**.

---

## 3. The TOTP Dynamic Password System

To prevent owners or unauthorized repair facilities from accessing deep diagnostic levels (which would permit disabling speed limits, sideloading untested Android package files, or altering safety margins), VinFast implements a rolling **Time-Based One-Time Password (TOTP)** protocol for Engineering Mode authorization.

### Cryptographic Derivation Flow

```
┌─────────────────────────────────┐
│     Vehicle VIN String          │──┐
└─────────────────────────────────┘  │
                                     │   HMAC-SHA256
┌─────────────────────────────────┐  ├──► [Key Derivation]
│     Rolling Epoch Base Time     │──┘         │
└─────────────────────────────────┘            ▼
                                    ┌───────────────────────┐
                                    │  Dynamic TOTP Token   │
                                    └───────────────────────┘
```

1.  **Secret Root Key (Seed)**: The head unit contains a unique cryptographic private key built-in at the factory or written during post-assembly module calibration.
2.  **Input Vector**: The derivation uses:
    *   The vehicle's unique **17-Character VIN** (ensures tokens cannot be used/copied from other cars).
    *   The current **UTC system epoch time** divided into a defined duration block (typically **60 minutes** / 1 hour step, or $T_0 = 3600\,\text{seconds}$).
3.  **Hash Function**: The engine evaluates an `HMAC-SHA-256` or `HMAC-SHA-1` profile using the root seed and input vector:
    $$\text{Token} = \text{Truncate}(\text{HMAC-SHA-256}(\text{Root-Key}, \text{VIN} \mathbin{\Vert} \text{Time-Block})) \pmod{10^6}$$
    This produces a dynamic **6-digit or 8-digit numeric passcode** that expires when the system time crosses into the next hour window.

### Official Field Generation Method
Because tokens expire, VinFast field engineers and technicians on-site cannot use static password lists. 
*   **VDS Portal Generation**: Technicians must log into the web-based **VinFast Diagnostic System (VDS)** portal using dealer credentials.
*   **Requesting a Passcode**: The tech inputs the car’s VIN, selects "Engineering Mode OTP", and the portal server (which shares the car's private keys in its secure database) generates the matches-the-hour passcode.

### Historic Static Passcodes / Vulnerabilities
On earlier firmware versions (pre-deliveries or early 2023 beta testing builds), the passcode was temporarily static to ease field delivery logistics. These static fallback PINs have been disabled in modern secure FRS updates, but include:
*   `20220910` (Celebrates the first 100 customer deliveries date in Vietnam)
*   `112233`
*   `000000` / `123456`

---

## 4. Unlocking Android Settings, ADB & SSH

Unlocking the Engineering Menu exposes deeper system settings and enables interfaces used during active development and module debugging.

### ADB Over Wi-Fi
Once authenticated, the user can toggle **USB Debugging** or **ADB over Wi-Fi**:
*   The head unit switches on an ADB daemon listening passively on target IP port `5555`.
*   A user connected to the vehicle's local diagnostic Wi-Fi SSID network can drop to shell:
    ```bash
    adb connect <vehicle_ip_address>:5555
    adb shell
    ```
*   **Security Restrictions**: Modern builds enforce ADB RSA key authorization. Upon terminal connection, a dialogue prompts on the 15.6" screen asking the operator to trust the requesting device's RSA public key fingerprint.

### Sideloading (APKs)
The Engineering Mode provides a directory file-manager with permissions to install third-party `.apk` software bundles. This bypasses the proprietary VinFast App Store to allow sideloading of telemetry apps, diagnostic readouts, or alternative navigation maps.

---

## 5. Physical Debugging & Hidden Interfaces

For severe failures where the Android system fails to boot (boot-loop or black screen on startup) and cannot be recovered via touchscreen utilities, direct physical connectors exist inside the cabin:

### Hardware Debugging Location
Behind the glovebox/cowl passenger area or behind the main infotainment panel bezel sits the physical **MHU Processor Module**:
*   **USB Device Port**: A dedicated micro-USB or USB-C female port for establishing physical OTG device connections.
*   **Serial UART Pins**: A 3-pin or 4-pin $3.3\,\text{V}$ TTL UART header (Transmit `TX`, Receive `RX`, and Ground `GND`). Connecting a USB-to-UART converter at **115200 baud** exposes the bootloader log console (U-Boot/Qualcomm LK bootloader log) and the system kernel ring logs (`dmesg`).

---

## 6. Sideload and Recovery Modes

For recovery operations (restoring system images after corrupted OTA events):
*   **Qualcomm EDL (Emergency Download Mode)**: Triggered by bridging specific hardware pins on the MHU daughterboard during power-up or via command line if ADB is accessible:
    ```bash
    adb reboot edl
    ```
    This turns the system into an EDL target, allowing direct firmware partition flashing using Qualcomm's native QFIL software.
*   **Recovery Partition Boot**: Triggered via:
    ```bash
    adb reboot recovery
    ```
    Provides access to low-level standard partition formatting, cache clearing, and local USB update zip flashing.
