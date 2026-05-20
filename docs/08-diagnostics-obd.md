# 08 — Diagnostics & OBD Interface

## OBD-II Port

- **Location (2024 MY US):** Under the driver-side dashboard, left of the steering column, above the parking-brake pedal-area panel. Some units have it behind a small plastic cover labelled "OBD".
- **Connector:** Standard SAE J1962 16-pin trapezoidal DLC.
- **Power:** Pin 16 = battery +12 V (continuous, even when car is "off"). Pins 4, 5 = chassis/signal ground.
- **Powered when:** Always-on. Most modules require a "wake" event — open driver door or press brake pedal — to respond.

### Active Pins (typical EV configuration)

| Pin | Signal |
|-----|--------|
| 4 | Chassis ground |
| 5 | Signal ground |
| 6 | CAN-High (HS-CAN, OBD legislated bus) |
| 14 | CAN-Low (HS-CAN) |
| 16 | +12 V battery |
| 1, 3, 8, 11, 12, 13 | Manufacturer-defined (gateway to private CAN/CAN-FD/DoIP via gateway) |

> The VinFast Central Gateway enforces **SecOC / SecureOnboardCommunication** and gated access for manufacturer-specific DIDs. Generic scan tools will see emissions/OBD PIDs and basic readiness only; deeper module access (BMS cell voltages, BMS isolation, MCU phase currents, ADAS calibration) requires VinFast diagnostic credentials or DoIP/Ethernet pinout via pin 3/11/12/13 with proper VAG/UDS-style authentication.

## Supported Protocols

| Protocol | Supported | Notes |
|----------|-----------|-------|
| ISO 15765-4 CAN (11-bit, 500 kbps) | ✅ | Generic OBD-II / mode 01–0A |
| ISO 15765-4 CAN (29-bit, 500 kbps) | ✅ | UDS over CAN (mfr) |
| ISO 14229 UDS | ✅ | All non-gateway-restricted services |
| DoIP (ISO 13400) over Ethernet | ✅ (via dealer interface) | Required for OTA verification, ADAS calibration |
| K-Line / KWP2000 | ❌ | Not present |
| J1850 PWM/VPW | ❌ | Not present |

## What Generic Scan Tools Can Read

EV-relevant Mode 01 PIDs that the VF 8 supports (typical):
- 01 01 — Monitor status
- 01 0C — *(Engine RPM — returns 0)*
- 01 0D — Vehicle speed
- 01 42 — Control module voltage (12 V system)
- 01 5B — Hybrid/EV battery pack remaining life (%) ← **State of Charge proxy**
- 01 5C — Engine oil temp *(not applicable)*
- 01 A6 — Odometer (where supported by FW)
- Mode 03 / 07 / 0A — Stored / pending / permanent DTCs
- Mode 09 — VIN, CALID, CVN

Recommended consumer tools (verify VF 8 coverage before purchase — see §3 below):
- **OBDLink MX+** or **OBDLink CX** (Bluetooth) with *Car Scanner ELM OBD2* — pulls generic OBD-II PIDs reliably; deeper module data requires known custom PIDs (community-sourced, incomplete for VF 8).
- **Professional aftermarket tools (Autel MaxiSys, Launch X-431, Topdon, XTOOL, etc.)** — coverage of VinFast is uncertain and changes frequently; see §3.

### Known Autel Scan Evidence

A supplied Autel MaxiCOM MK900-BT report dated 2026-03-30 successfully produced a full-system VinFast diagnostic report on a 2024 VF 8 by selecting the closest available Autel profile, **VinFast / VF e34**. The report identified 12 scanned systems and 125 DTC rows. Autel did not provide plain-English definitions for most manufacturer-specific codes, often printing only "Please refer to vehicle service manual." The exact observed DTC list is preserved in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md).

This confirms that at least one Autel platform can enumerate multiple VF 8 modules through a non-VF8 VinFast profile, but it does **not** prove that Autel has authoritative VF 8 service definitions, bidirectional tests, security access, or reset routines for those modules.

## Diagnostic Workflow (general)

1. **Read all modules** (full scan) — do not rely on the dash warning lamp; many EV faults set only in BMS/MCU and report as a generic "EV system check" message on the HUD.
2. **Capture freeze-frame** data for each DTC.
3. **Inspect HV system status:** IMD reading (target ≥ 100 Ω/V), contactor state, pack voltage vs. cell-sum.
4. **Cross-check thermal:** coolant temps for battery loop and inverter loop, fan/pump duty cycles.
5. **Inspect CAN bus health:** bus-off counters, missing-message counters per module.
6. **Clear DTCs**, drive cycle, re-scan. Many EV monitors complete on a single 20–30 min mixed-speed drive once preconditions met.

## Drive-Cycle Notes (EV-Specific)

For EVs there is no engine warm-up cycle. Readiness monitors that apply:
- **Comprehensive component** (cont.)
- **Fuel system / Misfire** — N/A, reported "complete" or "not supported"
- **EV-specific monitors** (vendor): BMS isolation, contactor weld check, charger insulation. Many run automatically at every key-on and pre-charge sequence.

---

## Diagnostic Software & Tool Coverage

Status as of **May 2026**. The VF 8 is still a low-volume nameplate in most aftermarket tool databases — coverage is improving but uneven. Anything behind the **central gateway (SecOC)** still requires VinFast dealer credentials.

### 1. VinFast Factory / Dealer Tool

- **VinFast Diagnostic System (VDS / "VF Diag")** — internal dealer-only application.
  - Runs on a Windows tablet with a VinFast-branded VCI (J2534-class pass-thru).
  - Required for: module coding, VIN write, BMS cell-level diagnostics & rebalancing, SecOC key provisioning, OTA campaign force/rollback, recall reflashes, ADAS end-of-line calibration.
  - **Not sold to the public.** Independent shops must refer cars to a VinFast service center for any gateway-restricted operation.

### 2. Generic OBD-II — Works Today (limited)

Anything speaking ISO 15765 (CAN) / ISO 13400 (DoIP) connects through the J1962 port. Because the VF 8 is a BEV, generic OBD-II coverage is thin (no fuel trims, no O2). Useful for:
- VIN read (Mode 09)
- Generic P/B/C/U DTC read & clear (Mode 03/04/07/0A)
- Pack-SoC proxy (Mode 01 PID 5B), 12 V system, vehicle speed

Confirmed to at least pull VIN + generic DTCs:
- **OBDLink MX+ / CX** with OBDLink app or Car Scanner Pro
- **Autel MaxiAP200 / AP200M** (generic mode)
- **Launch CRP-series** (generic mode)
- **ELM327 clones** + Torque Pro / Car Scanner — very limited, no UDS auth

### 3. Third-Party Aftermarket Tools — VF 8 Coverage

> ⚠️ **Honest status:** As of this writing, **no major aftermarket scan-tool vendor publicly advertises explicit 2024 VinFast VF 8 coverage**. VinFast is a low-volume, new-market OEM and is largely absent from published coverage charts. Any claim of "VF 8 supported" should be verified against the vendor's current coverage database **before purchase**.

**Tools that are plausible candidates** (because they typically add new EV OEMs first) — coverage **must be confirmed per VIN with the vendor**:

| Tool family | What to ask the vendor | Verification URL |
|-------------|------------------------|------------------|
| **Autel MaxiSys Ultra / MS909EV / MS919 / BT609** | Does the current firmware list "VinFast" as a brand? If yes, which models/years and which systems (BMS, MCU, ADAS)? | https://www.autel.com/ — use "Coverage" / "Vehicle Compatibility" lookup |
| **Launch X-431 PRO5 / PAD VII / PAD VII EV** | Same questions; ask specifically about the EV Diagnostic Upgrade Kit | https://www.launchtechusa.com/ — request coverage chart |
| **Topdon Phoenix Max / Phoenix Smart / Elite Plus** | Same | https://www.topdon.com/ |
| **XTOOL D9 Pro / IP900 / X100 PAD Elite** | Same | https://www.xtooltech.com/ |
| **Thinkcar Platinum S20 / ThinkTool Master X** | Same | https://www.thinkcar.com/ |
| **TEXA IDC5 Car** (EU primarily) | Check the latest IDC5 Car release notes & coverage PDF for "VinFast" / "VF 8" | https://www.texa.com/software-releases/  •  https://www.texa.co.uk/software-releases/ |
| **Snap-on Zeus / Solus / Modis Edge** | Ask dealer rep whether VinFast is in current SureTrack/software bundle | https://www.snapon.com/diagnostics/ |
| **Bosch ADS / Mahle TechPRO** | Same | https://www.boschdiagnostics.com/ |
| **Mac Tools / Matco Maximus** | These OEM-rebadge from Autel/Launch — coverage follows upstream | Vendor sites |

**The only reliable verification methods:**

1. **Call the vendor's tech-support line with your VIN.** They can run a coverage check against the current database in seconds.
2. **Download the vendor's current "Vehicle Coverage" PDF** from the URLs above and search for "VinFast" or "VF 8".
3. **Ask in vendor user forums / Facebook groups** (e.g., Autel Users, Launch Owners) — techs post first-hand connection reports.
4. **For TEXA specifically**, every IDC5 release page links a per-release coverage chart; check the most recent release at https://www.texa.com/software-releases/ rather than trusting any version number quoted here.

**What I do not know** and will not invent:
- Specific firmware/software version numbers that added VF 8 support.
- Which specific systems (BMS, MCU, ADAS, EPB) each tool can read.
- Whether any of these tools can perform bidirectional tests or service resets on the VF 8.
- Whether US-spec and EU-spec VF 8 are handled identically.

### 4. Pass-Thru / J2534 Reflashing

- VinFast has **not published a J2534 reflash portal** for the VF 8 (no equivalent of GM SPS2, Ford FDRS, Stellantis wiTECH, Hyundai GDS-Mobile).
- US Right-to-Repair (Massachusetts 2013 MOU + 2020 Data Access Law) technically obligates VinFast, but enforcement against new OEMs has not begun.
- Until VinFast opens a portal:
  - **No legal indie reflash path.**
  - Recall and TSB reflashes are delivered **OTA** (preferred) or at a VinFast service center.

### 4a. TEXA / Generic J2534 Pass-Thru Use

TEXA Navigator Nano S2 hardware can be used as a generic SAE J2534-1 pass-thru interface **if** the Windows TEXA PassThru driver installs a compliant `FunctionLibrary` DLL. Our Python helper can load that DLL with `--dll` the same way it loads `MVCI32.dll`.

What this enables:

- Standard J2534 device open/close and voltage checks.
- ISO 15765-4 CAN access on pins 6/14.
- Generic OBD requests such as VIN, stored/pending/permanent DTC reads, and Mode 04 clear on modules that respond to functional address `0x7DF`.

What it does **not** enable by itself:

- Native VinFast coverage inside TEXA IDC software.
- SecOC/key-protected gateway access.
- RCM/BMS crash data reset, ADAS calibration, coding, immobilizer/security operations, or reflashing without OEM authorization.

### 5. Open-Source & Community Projects

> ⚠️ I cannot verify specific community projects targeting the VF 8. The platforms below **support EVs generally**; whether anyone has published working VF 8 profiles is something to check on each project's repo/forum directly.

| Platform | General purpose | Where to check for VF 8 support |
|----------|-----------------|----------------------------------|
| **SavvyCAN** + CANable / Macchina M2 / Comma Panda | Reverse-engineering CAN traffic; importing community DBC files | https://github.com/collin80/SavvyCAN — search GitHub for "vinfast" DBC repos |
| **OVMS (Open Vehicle Monitor System)** | Cellular telematics for EVs; per-model vehicle drivers | https://www.openvehicles.com/ — check supported-vehicles list |
| **ABRP (A Better Routeplanner)** | Trip planning with live SoC | https://abetterrouteplanner.com/ — check vehicle list and OBDLink integration docs |
| **EVNotify** | SoC logging via OBD dongle | https://github.com/EVNotify — check for VF 8 PID profile |
| **Home Assistant** | Cloud telematics integrations | https://www.home-assistant.io/integrations/ and HACS — search "vinfast" |

### 6. Practical Recommendations

**For an indie EV shop:**

1. **Before investing in a tool, verify VF 8 coverage with the vendor using your customer's VIN.** Coverage charts change with every software release.
2. Among general-purpose EV-capable platforms commonly recommended in the trade, the most likely candidates to have or to add VF 8 support are **Autel MaxiSys (with EVDiag Box for pack-level work)** and **Launch X-431 (with EV upgrade kit)** — but verify first.
3. **OBDLink CX + Car Scanner Pro** is a low-cost chairside option for generic OBD-II reads regardless of brand coverage.
4. For research/undocumented PIDs: **CANable / Macchina M2 + SavvyCAN**, then check public GitHub for any community DBC contributions.
5. **Refer to a VinFast service center** for anything requiring: module coding, key learning, BMS rebalance/replacement, SecOC-protected access, ADAS calibration after sensor/windshield replacement, or any module reflash.

**For an owner:**

- An **OBDLink CX** with Car Scanner Pro (iOS/Android) is a reasonable low-cost setup for SoC monitoring and generic DTC reads.
- Avoid leaving no-name ELM327 dongles plugged in continuously — many keep the gateway awake and can drain the 12 V battery over days.

> ⚠️ **Security note:** Any third-party tool claiming "VinFast SecOC unlock" outside of the VinFast dealer channel is almost certainly either using leaked/illegitimate credentials or is fraudulent. Verified gateway access is dealer-only.

See [19-diagnostic-programming-notes.md](19-diagnostic-programming-notes.md) for the consolidated VinFast-specific programming, J2534, UDS, clear-and-rescan, and tool-routing notes.

