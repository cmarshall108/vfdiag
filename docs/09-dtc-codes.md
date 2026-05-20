# 09 — Diagnostic Trouble Codes (DTC) Reference

> ⚠️ **Important.** VinFast does not publish a comprehensive public DTC list. The codes below combine **generic SAE J2012** EV-applicable codes (which the VF 8 supports through OBD-II) and **commonly observed manufacturer-specific patterns** reported by independent technicians. Manufacturer-specific codes (prefix `U3xxx`, `P1xxx`, `P3xxx`, `B2xxx`, `C2xxx`) must be cross-referenced to the current VinFast Service Information system for authoritative interpretation.

The exact 2026-03-30 Autel MaxiCOM MK900-BT scan that contributed many observed manufacturer-specific base codes is preserved separately in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md). That appendix records the raw 7-character Autel DTCs, module names, and current/history status. The explanatory text in this file is an advisory working map, not an official VinFast definition list.

## DTC Format Refresher

```
 P  0  4 5 5
 │  │  │ │ └─ Specific fault
 │  │  └─┴─── Sub-system
 │  └──────── 0=generic SAE / 1=manufacturer specific
 └─────────── P=Powertrain  C=Chassis  B=Body  U=Network
```

## Generic EV-Applicable Codes (SAE J2012)

### Powertrain — Hybrid/EV (P0Axx – P0Dxx ranges)

| DTC | Description | Typical VF 8 cause |
|-----|-------------|--------------------|
| **P0A00** | Motor electronics coolant temperature sensor circuit | Inverter coolant temp sensor open/short |
| **P0A01** | Same — range/performance | Sensor drift |
| **P0A04** | Hybrid battery voltage system isolation fault | **HV isolation low** — IMD < ~100 Ω/V. Inspect HV cable damage, water ingress in OBC / DC-DC, contaminated coolant |
| **P0A09** | DC-DC converter status circuit low | 12 V system not being supplied from HV |
| **P0A0A** | High-voltage system interlock circuit | **HVIL open** — connector unseated or pinched harness |
| **P0A0B** | HV interlock circuit low | HVIL shorted to ground |
| **P0A0C** | HV interlock circuit high | HVIL open to high |
| **P0A0D** | HV interlock circuit signal | Intermittent HVIL — vibration / loose connector |
| **P0A1A** | Generator/motor electronics, internal performance | MCU internal fault — replace MCU |
| **P0A1F** | Battery energy control module — internal fault | BMS internal — replace BMS |
| **P0A2A** | Drive motor "A" temperature sensor circuit | Open/short on motor stator temp sensor |
| **P0A3A** | Drive motor "A" performance | Phase current imbalance; check motor windings, position sensor |
| **P0A3F** | Drive motor "A" position sensor circuit | Resolver fault |
| **P0A7D** | Hybrid battery pack low voltage | Pack below operating threshold; deep-discharge protection |
| **P0A7F** | Hybrid battery pack deterioration | SoH below threshold — pack assessment |
| **P0A80** | Replace hybrid battery pack | Severe degradation |
| **P0A93** | Inverter "A" cooling system performance | Pump weak, coolant low, clogged radiator |
| **P0A94** | DC-DC converter performance | Output voltage out of range |
| **P0A95** | High-voltage fuse | HV main fuse open — inspect MSD / BJB |
| **P0AA1** | Battery voltage sense "A" circuit low | BMS slave board fault |
| **P0AA6** | High-voltage system isolation fault sensed at MCU | Isolation loss detected by inverter |
| **P0ABF** | Battery current sensor circuit | Shunt or hall sensor fault |
| **P0AC4** | Hybrid battery pack air temperature sensor | Pack air-temp sensor |
| **P0AFA** | Hybrid battery system voltage low | Insufficient SoC for drive |
| **P0B22** | Drive motor "A" inverter performance | Inverter over-temp / desat fault |
| **P0B41** | Battery module 01 over-voltage | Single module above limit — check cell balance |
| **P0CBC** | Hybrid battery cell over-temperature | Battery cooling fault — pump/valve |
| **P0D05** | Hybrid battery charging system | OBC fault — replace or update FW |
| **P0D2F** | Hybrid powertrain control module memory | VCU FW corrupted — re-flash |

### Brake/Chassis (Cxxxx)
| DTC | Description |
|-----|-------------|
| **C0561** | ESC disabled — software-disabled mode |
| **C0594** | Invalid Data Sensed from Restraints Control Module (RCM) |
| **C0710** | Steering position signal — EPS calibration required (post alignment) |
| **C1210** | EPB actuator left / right circuit |
| **C1A00** | eBooster internal fault |

### Body (Bxxxx)
| DTC | Description |
|-----|-------------|
| **B1000** | ECU internal failure (generic) |
| **B1B23** | Driver airbag squib circuit |
| **B2AAA** | Charge port lock motor circuit |
| **B2AAB** | Charge port temperature sensor — CCS DC pins |
| **B2AAC** | Proximity Pilot (PP) circuit |
| **B2AAD** | Control Pilot (CP) circuit |

### Network (Uxxxx)
| DTC | Description |
|-----|-------------|
| **U0001** | High-speed CAN bus communication |
| **U0100** | Lost communication with ECM/PCM — (here = VCU) |
| **U0111** | Lost communication with BMS |
| **U0121** | Lost communication with ABS |
| **U0131** | Lost communication with EPS |
| **U0140** | Lost communication with BCM |
| **U0151** | Lost communication with restraint module |
| **U0293** | Lost communication with hybrid powertrain control module |
| **U0415** | Invalid data from ABS |
| **U3000** | Control module — generic (manufacturer-specific subcode follows) |

## VinFast-Specific Manufacturer DTCs (Confirmed Teardown/Recall References)

Unlike generic 5-character SAE codes, these manufacturer codes represent proprietary subsystem faults under the gateway and often carry UDS failure symptom bytes (suffix after the dash):

| DTC | Description | Suffix (Subtype) meaning | Typical VF 8 Root Cause |
|-----|-------------|--------------------------|-------------------------|
| **P1A0A** | BMS Battery Disconnect Collision Signal Activated | `-00` (No Sub-type) | Crash signal commanded hard battery cutoff from RCM. Relays locked open; requires authenticated reset protocol. |
| **P1A0D** | High Voltage interlock Loop (HVIL) Failure | `-13` (Circuit Open) | Unseated/pinched physical harness or loose connector latch on HV casing. |
| **P1A0E** | High Voltage Isolation Limit Exceeded (Level 2) | `-00` (No Sub-type) | Isolation resistance < 100 Ω/V on traction components (OBC, MCU, or DC-DC converter fluid ingress). |
| **U105B** | Lost Communication with On-board Charger (OBC) | `-87` (Missing Message) | Central Gateway lost telemetry loop with the AC/DC charger module. |
| **P1C05** | Coolant Valve Position Deviation | `-1C` (Voltage/Mechanical Out of Range) | 4-Way thermal loop switching valve jammed, blocked, or drift-out. |
| **B1A00** | Restraints Control Module (RCM) Crash Event Stored | `-F0` (Permanent Lock Memory) | Non-volatile EEPROM locked after squib or pyrofuse firing. Module requires specialized offline reprogram/replacement. |
| **U0923** | Invalid Data Sensed from Restraints Control Module (RCM) | `-00` (No Sub-type) | VCU receives CAN packets from RCM but rejects payload because the RCM is broadcasting active crash/deployment flags. |
| **C0594** | Invalid Data Sensed from Restraints Control Module (RCM) | `-01` (Signal Failure/Short) | Electronic Stability Control (ESC) disables stability control and emergency braking systems because RCM broadcasts active crash status. |
| **P1137** | VCU Crash Input Signal Hardwired Line Active | `-00` (No Sub-type) | Dedicated backup physical collision line from RCM to VCU is pulled active-high; prevents HV precharge system init. |
| **P1033** | VCU Pyrofuse Monitor Circuit Fault/Open | `-00` (No Sub-type) | The VCU detects a physical loop disruption or open-circuit status on the pyrofuse auxiliary feedback lines. |
| **P1150** | VCU Redundant Crash Input Channel A | `-00` (No Sub-type) | Dual-channel backup safety line A reports active crash signal or open loop. |
| **P1151** | VCU Redundant Crash Input Channel B | `-00` (No Sub-type) | Dual-channel backup safety line B reports active crash signal or open loop. |
| **P1188** | VCU High-Voltage Precharge Timeout Failure | `-00` (No Sub-type) | HV precharge sequence aborted because intermediate bus voltage failed to rise above safety threshold in time. |
| **U1130** | Lost Communication with Front Radar (ADAS) | `-89` (Received Message Fail) | ADAS controller lost contact with forward distance radar module (check alignment/connector). |
| **U1132** | Lost Communication with Rear Corner Radar Left | `-89` (Received Message Fail) | Blind spot / cross traffic radar left failed to send telemetry (rear bumper harness). |
| **U1134** | Lost Communication with Rear Corner Radar Right | `-89` (Received Message Fail) | Blind spot / cross traffic radar right failed to send telemetry (rear bumper harness). |
| **U1111** | Lost Communication with Front Camera / ADAS Cam | `-89` (Received Message Fail) | Lost connection with windshied-mounted forward ADAS lane/vision camera module. |
| **U1165** | Lost Communication with Driver Monitor Camera (DMS) | `-89` (Received Message Fail) | Steering column DMS camera communication interface missing or obscured. |
| **U1182** | Lost Communication with Ultrasonic Parking Sensor ECU | `-89` (Received Message Fail) | ADAS domain lost communication stream from PDC sensor hub. |
| **U1187** | Lost Communication with Intelligent Front Lights / Matrix LED | `-89` (Received Message Fail) | Adaptive matrix headlight module failed to communicate its status line to the ADAS controller. |
| **U1140** | Invalid Data Sensed from Steering Angle Sensor | `-81` (Invalid Serial Data) | ESC/EPS angle sensor broadcast is corrupted or out of calibration bounds following a crash impact. |
| **U1142** | Lost Communication with Inertial Measurement Unit (IMU) | `-89` (Received Message Fail) | Lost telemetry with Yaw Rate/Gravity sensor node; disables dynamic rollover calculations. |
| **U1196** | Lost Communication with Surround View Camera Module (AVM) | `-89` (Received Message Fail) | Lost telemetry with the high-speed overhead birds-eye-view camera controller. |
| **B1939** | Front Passenger Airbag Disable Indicator Circuit | `-04` (System Internal Fail) | Physical hardware fault or open circuit on the occupant classification status light cluster. |
| **B170E** | PTC Heater Control Circuit / Duty Cycle Range | `-54` (Missing Calibration) | High-voltage cabin PTC air heating fluid loop reports initialization or calibration mismatch. |
| **U1108** | Lost Communication with Battery Management System (BMS) | `-87` (Missing Message) | Network node/gateway fails to compile status telegrams from BMS (often due to HV safety lockout sleep state). |
| **U0292** | Lost Communication with Electric A/C Compressor | `-87` (Missing Message) | HV liquid-scroll scroll compressor failed to report on local LIN/CAN bus (no HV power supplied). |
| **B2001** | Extended Gateway Diagnostic Protocol Mismatch | `-01` (Signal Failure) | Central gateway rejects dynamic security key requests or encounters SecOC message signature errors. |
| **B2000** | Extended Gateway Secure Boot / Flash Checksum Error | `-01` (Signal Failure) | Internal gateway non-volatile memory diagnostic checksum or validation has failed. |
| **U160E** | MCU Internal Gateway Configuration Signature Loss | `-81` (Invalid Data) | MCU rejects session status because security verification signature fails. |
| **U1101** | System 12V Supply Circuit Voltage Out of Range | `-16`/`-17` (Circuit Low/High) | Low-voltage system (AGM 12V battery or DDC charger output) fell below nominal operating bounds (commonly <11.0V). |
| **U0146** | Lost Communication with Central Gateway (XGW) | `-87` (Missing Message) | Individual modular node fails to receive heartbeat CAN packet from gateway. |
| **U0155** | Lost Communication with Instrument Panel Cluster (IPC) | `-87` (Missing Message) | MCU/BCM displays offline state from the physical dashboard cluster telemetry link. |
| **U0423** | Invalid Data Sensed from Instrument Panel Cluster (IPC) | `-81` (Received Data Invalid) | Screen cluster handshake packets are corrupted or dynamic authentication is lost. |
| **P1800** | BMS Pyrofuse Deployment / HV Circuit Hardware Lockout | `-00` (No Sub-type) | BMS detects pyrofuse firing or main fuse open load; permanent lockout activated. |
| **P1241** | BMS Battery Pack Internal Temperature/Cell Drift | `-00` (No Sub-type) | Local slave boards measure cell sensor or thermistor deviations beyond safety margins. |
| **P1834** | BMS Contactor Coils Actuator Drive Circuit | `-01` (Short to Battery) | The BMS detects a short circuit or open circuit on the physical lines driving the HV contactor coils. |
| **P18D0** | BMS Battery Case Physical Crash Sensor Triggered | `-00` (No Sub-type) | Internal pack mechanical impact monitor triggered; battery is permanently isolated. |
| **P1240** | BMS High Voltage Battery Temp Sensor Line Low | `-03` (Voltage Below Limit) | High voltage thermal pack thermistor input shorted to ground or signal cut. |
| **P0ABF** | BMS Shunt Traction Current Sensor Performance Drift | `-86` (Offset Signal Drift) | Battery hall-effect or shunt current measurement drifted out of acceptable zero-point range. |
| **U0125** | BMS Lost Communication with Inertial/Yaw Sensor | `-87` (Missing Message) | BMS loses lateral/longitudinal acceleration CAN loop necessary for rollover contactor cuts. |
| **P1017** | VCU Auxiliary Coolant Pump System Flow Mismatch | `-16` (Voltage Low) | Coolant pump feedback motor speed deviates from VCU duty target (air bubble or jam). |
| **U1171** | Central Chassis CAN Bus-Off Active Fault | `-88` (Bus Off) | VCU or Gateway transceiver is forcefully knocked off CAN bus due to collision physical shorts/frame storm. |
| **P1129** | VCU Shift Position Actuator Drive Range Error | `-00` (No Sub-type) | VCU shifter actuator reports mechanical position mismatch or jam trying to shift park lock. |
| **P105D** | VCU Accelerator Pedal Sensor Dual-Channel Correlation | `-38` (Signal Correlation Mismatch) | Accelerator pedal sensors A and B signals drift apart too much (safety sensor integrity fault). |
| **P106B** | VCU Active Grille Shutter (AGS) Actuator Blocked | `-29` (Invalid Signal/Blocked) | Automated cooling vents in the bumper are jammed, ice-locked, or unplugged after front impact. |
| **U1191** | BCM Lost Communication with ADAS Domain Controller | `-88` (Signal Invalid) | Body controller loses lane keeping / auto-highbeam handshake telegram from ADAS. |
| **U020C** | BCM Lost Communication with On-board Charger (OBC) | `-87` (Missing Message) | Body controller drops contact with AC charge ECU. |
| **U01B0** | BCM Lost Communication with BMS | `-81` (Received Data Invalid) | BCM fails to decode battery safety state frames. |
| **P058D** | DC-DC Converter Output Voltage Sensor Circuit | `-09` (Component Fail) | Auxiliary voltage sensor on high-to-low power converter is out of spec limits. |
| **B1014** | BCM Right Reverse Lamp Circuit Fault | `-13` (Circuit Open/Below Limit) | Rear trunk/bumper lamp wiring cut or connector physical pin issue. |
| **B1015** | BCM Left Stop Lamp Circuit Open/Short | `-13` (Circuit Open/Below Limit) | Brake lamp circuit current below threshold (broken bulb / severed wire). |
| **B1016** | BCM Right Stop Lamp Circuit Open/Short | `-13` (Circuit Open/Below Limit) | Brake lamp circuit current below threshold (broken bulb / severed wire). |
| **B10B8** | BCM Daytime Running Light (DRL) General Failure | `-71` (Actuator Stuck) | Front LED assembly line open or driver chip reporting short circuit. |
| **B10EC** | Rain/Light Sensor LIN Bus Communication Timeout | `-00` (No Sub-type) | BCM cannot contact smart optical node on windshield via LIN bus. |
| **U0416** | Invalid Data Sensed from Electronic Stability Control (ESC) | `-82` (Alive Counter Error) | Received stability dynamics frames contain mismatched rolling parity counters. |
| **U045D** | Invalid Data Sensed from Multimedia Headunit (MHU) | `-82` (Alive Counter Error) | Gateway or BCM rejects infotainment screen packets. |
| **U0477** | Invalid Data Sensed from Airbag Restraints (ACM/RCM) | `-81` (Invalid Serial Data) | Safe cabin state indicators from restraint computer contain corrupted payloads. |
| **U019E** | XGW Lost Communication with Telematics Box (T-Box) | `-87` (Missing Message) | Gateway fails to route eSIM/TCU GPS cellular tracking signals. |
| **U0122** | XGW Lost Communication with Vehicle dynamics ABS/ESC | `-87` (Missing Message) | High-speed communication path to braking/stability processor cut. |
| **B2001A2** | XGW SecOC Sequence Key Verification Failed | `-A2` (Format/Memory Error) | Cryptographic fresh counter mismatches; security payload signature is rejected. |
| **B2000A2** | XGW Secure Flash Boot Checksum Verification Failure | `-A2` (Format/Memory Error) | Internal secure partition microchip checksum mismatch. |
| **B161A** | MHU USB Connectivity Port Interface Error | `-03`/`-01` (Voltage low/short) | Center console aux/data port reports hardware electrical line grounding. |
| **B1620** | MHU Internal Telematics Backup Cell Dead/Depleted | `-04` (Internal Failure) | Infotainment remote services backup nickel/lithium cell lacks capacity. |
| **U015C** | MHU Lost Communication with Audio Power Amplifier | `-87` (Missing Message) | Audio central gateway lost connection to digital cabin speaker driver. |
| **U1003** | RLS Windshield Rain Sensor Calibration Loop Failure | `-04` (Internal Failure) | Optical sensor fails self-calibration matrix on windshield interface. |
| **U1004** | RLS Optical Sensing Pathway Contaminated/Uncalibrated | `-04`/`-1C` (Fail/Out of range) | Sensor face dirty, blocked, or glass gel-pad adhesive unseated. |
| **C150C** | Dynamic Bumper Warning Buzzer Drive Line Error | `-1C` (Voltage Out of Range) | Parking sonar speaker open-load or line short. |
| **C1536** | Bumper Ultrasonic Radar Transceiver Target Unaligned | `-00` (No Sub-type) | Left physical parking sensor mechanically pushed in. |
| **C1537** | Bumper Ultrasonic Radar Transceiver Target Unaligned | `-00` (No Sub-type) | Right physical parking sensor mechanically pushed in. |

## Commonly Observed VinFast-Specific Symptom → Likely Code

| Symptom on HUD/IVI | Likely DTC family | First check |
|---------------------|-------------------|-------------|
| "EV System Check" + reduced power | P0A04, P0AA6 (isolation), P0B22 | HV isolation, coolant level, recent water exposure |
| "Charge fault — see manual" at DC station | B2AAB, B2AAD, P0D05 | Charge port temp sensor, CP/PP wiring, dirty pins |
| "12V battery low" repeatedly | P0A09, P0A94 | DC-DC converter and 12 V AGM health |
| "Steering Assist Reduced" | C0710, U0131 | Steering-angle sensor calibration after alignment |
| "AEB Unavailable" | U3000 + B-codes on ADAS-C | Camera calibration, radar alignment |
| "Park Brake Service Required" | C1210 | EPB caliper motor circuit |
| Constant LKA tugging / ghost steering | (no DTC, ADAS calibration) | Subject of NHTSA ODI investigation — TSB pending |

## Reading & Clearing

1. Connect scan tool, wake vehicle (open driver door + brake press).
2. Full system scan — record all DTCs with freeze frames.
3. Address mechanical/electrical root cause before clearing.
4. Clear via UDS 0x14 (Clear Diagnostic Information) — generic OBD Mode 04 will clear only emission-related codes; vendor codes need UDS clear per module.
5. Perform required relearns (steering-angle, EPB, ADAS) per the [worksheets](15-worksheets.md).
6. Drive cycle ~20–30 min mixed; re-scan to confirm.

For the VinFast-specific diagnostic/programming boundary, including J2534, UDS, SecOC, VDS/dealer tooling, and what independent tools can/cannot clear, see [19-diagnostic-programming-notes.md](19-diagnostic-programming-notes.md).

### Clear-and-Return Test Discipline

For the observed Autel scan set, do not clear codes blindly. Capture the complete report first, stabilize the 12 V system with an EV-safe maintainer, then clear only after physical crash/restraint/HV harness issues are addressed. After clearing, let the vehicle sleep, wake it again, and perform a second full scan. Codes that return immediately are more useful diagnostically than history codes that only reflect low voltage, connector unplugging, or module sleep during collision repair.

---

## Post-Collision / Pyrofuse Lockout Diagnostic & Reset Realities

On a salvage or rebuilt VinFast VF 8, physically replacing the deployment pyrofuse (pyrotechnic safety switch) does **not** restore the vehicle's high-voltage circuit or allow the powertrain to enter "READY" or "Drive" mode. A hard crash event triggers a cascading software lockout across three isolated system boundaries:

### 1. The RCM Crash State Loop
The Restraints Control Module (RCM) commands physical pyrofuse deployment upon high-G impact sensing or airbag activation.
*   **Behavior**: When a deployment occurs, the RCM writes the crash data segment into non-volatile internal EEPROM (commonly throwing hardware DTC `B1A00-F0`).
*   **Lockout Mechanism**: The RCM continuously broadcasts a high-priority "crash status active" CAN frame over the chassis network. Even if you replace the pyrofuse physically, the VCU and BMS read this constant network broadcast and refuse to initiate the high-voltage precharge cycle.
*   **Correction Path**: The RCM must either be replaced with a new/virgin module (and matched to the car's VIN via VDS) or physically removed and reprogrammed by specialized EEPROM repair tools to clear the crash-loop state.

### 2. The BMS Soft Relays Lockout (DTC P1A0A-00)
The Battery Management System monitors the restraints bus.
*   **Behavior**: Upon receiving the RCM deploy command, the BMS commits a hard internal lockout code (`P1A0A-00`) and opens its primary positive and negative contactor relays.
*   **Lockout Mechanism**: This soft-lockout state prevents contactor engagement to avoid driving high currents into potentially shorted or damaged electrical loops. Standard OBD-II Mode 04 requests cannot reach this service.
*   **UDS Session Security Access ($27)**: Clearing `P1A0A-00` requires establishing an Extended Diagnostic Session under Unified Diagnostic Services (UDS / ISO 14229). The diagnostic interface must authenticate using a rolling seed-key handshake. Without the proprietary VinFast seed-key cryptographic math generator, generic tools cannot authorize the clear sequence.
*   **SecOC (Secure Onboard Communication)**: Contemporary VinFast gateways utilize SecOC to cryptographically sign critical CAN messages. Contactor reset routines must be authorized by the Central Gateway using active freshness counters and valid HMAC keys. Attempting to replay clear commands or force contacts closed via brute-force scripts will result in packet rejection.

### 3. High-Voltage Interlock Loop (HVIL) & Isolation Checked
Even once RCM signals and BMS lockouts are cleared, the vehicle executes a pre-flight sanity sequence:
*   **HVIL Verification**: Consists of a continuous low-current loop passing through every high-voltage safety connector (including the MSD service disconnect, battery main lines, and high-voltage ancillary ports). Any contact pin micro-gap or shorted branch will register as an open loop, dropping the contactors instantly.
*   **IMD Validation**: The BMS actively queries the Isolation Monitoring Device. If moisture, compromised high-voltage wire insulation, or contaminated coolant registers a chassis leakage current yielding less than $100\,\Omega/\text{V}$ isolation resistance, the vehicle aborts pre-charge and resets the lockout cycle.

### Recommended Recovery Vector
For independent technicians or DIY rebuilders, attempting to program past the SecOC gateway or reverse-engineer the BMS cryptographic key generator without dealer equipment is highly likely to brick the affected microcontrollers. The only reliable strategy is:
1.  Physically restore structural, wiring, and high-voltage circuit integrity (pyrofuse swap, replace deployed airbags, inspect orange harness lines).
2.  Replace the RCM or have its non-volatile crash registers cleared.
3.  Perform the static isolation measurement manually using a megaohmmeter (CAT III 1000V rated) to ensure isolation is $> 100\,\Omega/\text{V}$.
4.  Acquire a factory VDS (VinFast Diagnostic System) tool link or secure mobile dealer support to clear module lockouts and re-authorize contactor routines within the gateway framework.

