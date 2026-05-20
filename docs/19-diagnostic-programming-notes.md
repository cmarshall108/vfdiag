# 19 — Diagnostic & Programming Notes

This document collects VinFast-specific diagnostic and programming facts that are useful for a 2024 VF 8, while separating known behavior from things that still require official VinFast Service Information.

## Known Access Layers

| Layer | What it can do | Public/independent status |
|-------|----------------|---------------------------|
| Generic OBD-II on J1962 pins 6/14 | VIN, generic Mode 01 live data, Mode 03/07/0A DTC reads, Mode 04 clear on responding legislated OBD modules | Works with generic scan tools and the local `vf-obd` J2534 script |
| UDS over CAN / ISO 14229 | Per-module DTCs, data identifiers, routines, clears, actuator tests, session control | Module access depends on gateway routing, session level, and security access |
| DoIP / ISO 13400 | High-bandwidth diagnostics, programming, OTA/service operations, ADAS calibration workflows | Dealer/tool dependent; not exposed as a public VF 8 programming path |
| VinFast Diagnostic System (VDS / dealer tool) | Full module scan, programming, coding, secure routines, calibration, campaign/reflash workflows | Dealer/service-center channel; not publicly distributed as an independent-shop package |
| OTA update system | Vehicle firmware delivery and campaign updates | Owner-facing only for released packages; not an independent programming tool |

## J2534 Reality on the VF 8

SAE J2534 is a hardware/API standard. It lets software talk through a pass-thru adapter such as Toyota Mini-VCI, TEXA Navigator Nano S2, Mongoose-style hardware, or other compliant VCIs. It does **not** by itself grant VinFast diagnostic coverage, security credentials, or programming files.

What a J2534 device can reasonably do with the local Python script:

- Load a vendor PassThru DLL such as `MVCI32.dll` or a TEXA PassThru DLL on Windows.
- Open an ISO 15765-4 CAN channel at 500 kbps on OBD pins 6/14.
- Read 12 V supply voltage through `READ_VBATT` when the driver supports it.
- Send generic OBD-II requests to functional address `0x7DF`.
- Read generic DTC responses from `0x7E8` through `0x7EF`.
- Issue Mode 04 clear to modules that respond on the legislated OBD bus.
- Passively log CAN traffic on pins 6/14.

What a J2534 device cannot do alone:

- Bypass VinFast gateway authorization.
- Generate SecOC signatures or freshness counters.
- Unlock UDS SecurityAccess (`0x27`) without the correct OEM algorithm/keys.
- Program modules without OEM calibration files, programming sequence, power-state control, and authorization.
- Clear crash data stored inside an RCM/ACM or BMS permanent safety latch if the module requires a protected routine.

## Programming and Reflash Status

As of May 2026, this documentation set has no verified public VinFast VF 8 J2534 reflash portal equivalent to GM SPS2, Ford FDRS, Stellantis wiTECH, Hyundai/Kia service programming, or Toyota Techstream calibration download workflows.

Practical implications:

- Recall and software campaign programming should be treated as OTA or VinFast service-center work.
- Module replacement, VIN writing, immobilizer/key functions, ADAS calibration, gateway provisioning, BMS replacement, and RCM/airbag operations require official VinFast tooling or service support.
- A pass-thru adapter may be the physical interface used by a dealer tool, but the tool subscription/credentials/calibration files are the important part.

## Secure Gateway and UDS Notes

The VF 8 uses a central gateway architecture. Generic OBD requests are allowed for legally mandated diagnostics, while deeper module functions are routed and controlled by the gateway.

Relevant UDS services in normal automotive diagnostics:

| UDS service | Purpose | VF 8 practical note |
|-------------|---------|--------------------|
| `0x10` DiagnosticSessionControl | Switch default/extended/programming sessions | Higher sessions may be refused without authentication |
| `0x11` ECUReset | Reset a module | Protected on safety/security modules |
| `0x14` ClearDiagnosticInformation | Clear DTC groups | Generic OBD Mode 04 is not equivalent to per-module protected clears |
| `0x19` ReadDTCInformation | Read detailed DTC/status records | Often available only through a tool with correct routing/coverage |
| `0x22` ReadDataByIdentifier | Read module data identifiers | DID list is OEM-specific |
| `0x27` SecurityAccess | Seed/key unlock | Requires OEM algorithm/credentials; do not brute force |
| `0x2E` WriteDataByIdentifier | Write configuration/coding values | High risk; gateway/security protected |
| `0x31` RoutineControl | Run service routines such as calibrations or resets | Used for many service functions; routine IDs are OEM-specific |
| `0x34`/`0x36`/`0x37` | RequestDownload/TransferData/TransferExit | Programming path; requires correct files and authorization |

Do not attempt blind programming or security-access brute force on the VF 8. Failed or malformed programming/session attempts can leave a module in a nonfunctional state and may create new security/gateway faults.

## Clear-and-Rescan Strategy

For a post-collision or salvage VF 8, the cleanest independent workflow is:

1. Stabilize the 12 V system with an EV-safe maintainer; low voltage appears in the observed scan as `U110116` on EPS/XGW and can pollute the fault list.
2. Save the full pre-clear report, including module names, current/history status, freeze-frame data, and 7-character Autel-style suffixes.
3. Repair visible physical faults first: restraint module/connectors, pyrofuse path, orange HV harness damage, HVIL connectors, bumper sensor harnesses, grounds, and 12 V supply.
4. Clear only what the tool can legitimately clear.
5. Let the vehicle sleep fully, wake it, and rescan.
6. Prioritize current faults that return immediately over history faults caused by unplugged modules or low-voltage work.
7. Stop independent clearing/programming attempts if BMS, RCM/ACM, gateway, or ADAS protected routines are required.

## Tool Routing Matrix

| Task | Local J2534 script | Autel/TEXA generic profile | VinFast dealer/VDS |
|------|--------------------|----------------------------|--------------------|
| Read VIN | Yes | Yes | Yes |
| Read generic OBD DTCs | Yes | Yes | Yes |
| Clear generic OBD DTCs | Yes, Mode 04 only | Usually yes | Yes |
| Full multi-module scan | No, not through current script | Observed possible with Autel VF e34 profile; coverage uncertain | Yes |
| Decode all VinFast DTC meanings | Local advisory map only | Often says refer to service manual | Yes |
| BMS cell data/rebalance | No | Unknown/coverage dependent | Yes |
| RCM/ACM crash data reset | No | Not verified | Yes or module replacement/service path |
| ADAS calibration | No | Coverage dependent; not verified for VF 8 | Yes |
| Module coding/VIN write | No | Not verified | Yes |
| Reflash/programming | No public path verified | No public path verified | Yes/OTA/service campaign |
| SecOC/security access | No | Not verified | Yes |

## Observed Autel Scan Lessons

The 2026-03-30 Autel MaxiCOM MK900-BT report, archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md), is the strongest local evidence we have for aftermarket visibility. It shows that an Autel VF e34 profile can enumerate modules on a 2024 VF 8 and produce DTC/status rows for MCU, BCM, BMS, VCU, ESC, EPS, ADAS, CCU, MHU, RLS, XGW, and a final section labeled `DC Converter)`.

Solid conclusions from that scan:

- Multiple modules reported missing airbag/restraint communication (`U110887` current in several modules).
- The BMS had current high-voltage-related DTC rows, including `P180000`, `P124100`, `P183401`, `P124003`, and `P0A9500`.
- ADAS had several current communication/sensor-related rows.
- XGW recorded chassis CAN bus-off history and current airbag communication loss.
- EPS/XGW low-voltage history means 12 V stabilization is mandatory before trusting a post-clear scan.

What that scan does **not** prove:

- That VF e34 definitions exactly match VF 8 definitions.
- That Autel can run VF 8 service routines, secure clears, or programming operations.
- That any manufacturer-specific description is authoritative unless VinFast service data confirms it.

## Practical Best Route

For diagnostics with the tools currently discussed:

1. Use the local Python/J2534 script with Mini-VCI or TEXA PassThru for generic OBD checks, voltage checks, live standard PIDs, and non-invasive CAN observation.
2. Use Autel or another professional scanner for full-module inventory if it can enumerate VinFast modules, but preserve the report as evidence rather than assuming definitions are exact.
3. Use official VinFast service support for programming, RCM/ACM crash handling, BMS safety lockouts, ADAS calibration, gateway/security operations, and module replacement coding.

This route avoids inventing unsupported programming access while still extracting every safe, useful diagnostic fact from independent tools.