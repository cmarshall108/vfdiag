# 18 — Autel DTC Scan Appendix (2026-03-30)

This appendix records the exact DTCs captured from an Autel MaxiCOM MK900-BT PDF diagnostic report supplied during VF 8 troubleshooting.

## Report Context

| Field | Value |
|-------|-------|
| Scanner | Autel MaxiCOM MK900-BT |
| Autel report ID | MAXIA20260330192852 |
| Test time | 2026-03-30 19:28:52 |
| Autel selected vehicle | VinFast / VF e34 |
| Actual vehicle under test | 2024 VinFast VF 8 |
| Systems scanned | 12 |
| Total DTCs reported | 125 |

The Autel software did not list VF 8 as a native vehicle profile and was run through the closest available VinFast profile, VF e34. Treat these codes as **observed scan evidence**, not as official VinFast service definitions. Where Autel printed "Please refer to vehicle service manual," this appendix preserves that limitation rather than inventing a description.

## Status and Suffix Notes

Autel prints most VinFast DTCs as a 7-character string. The first 5 characters are the SAE-style base DTC; the final 2 characters are the UDS failure symptom byte or OEM subtype.

Examples:

| Autel code | Base DTC | Suffix |
|------------|----------|--------|
| U110887 | U1108 | 87 |
| C059496 | C0594 | 96 |
| P0ABF86 | P0ABF | 86 |
| B2001A2 | B2001 | A2 |

The exact meaning of each suffix must be verified through VinFast service information. In this documentation set, suffix meanings are advisory unless the scanner supplied a plain-English label.

## Exact DTC Dump

### MCU (Motor Control Unit) - 4 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U015587 | Please refer to vehicle service manual. | History |
| U042381 | Please refer to vehicle service manual. | History |
| U160E81 | Please refer to vehicle service manual. | History |
| U110887 | Airbag Control Module (ACM) ECU message missing | Current |

### BCM (Body Control Module) - 15 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U110116 | Please refer to vehicle service manual. | History |
| U110887 | Please refer to vehicle service manual. | Current |
| U014687 | Please refer to vehicle service manual. | History |
| U119188 | Please refer to vehicle service manual. | Current |
| U020C87 | Please refer to vehicle service manual. | Current |
| B101413 | Right reverse lamp circuit current below threshold/open load | History |
| B101513 | Left stop lamp circuit current below threshold/open load | History |
| B101613 | Right stop lamp circuit current below threshold/open load | History |
| B10B871 | Please refer to vehicle service manual. | History |
| B10EC00 | Please refer to vehicle service manual. | History |
| U041682 | Please refer to vehicle service manual. | History |
| U045D82 | Please refer to vehicle service manual. | History |
| U047781 | Please refer to vehicle service manual. | History |
| U01B081 | Please refer to vehicle service manual. | Current |
| P058D09 | Please refer to vehicle service manual. | Current |

### BMS (Battery Management System) - 11 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U110116 | Please refer to vehicle service manual. | History |
| P180000 | Please refer to vehicle service manual. | Current |
| P124100 | Please refer to vehicle service manual. | Current |
| P183401 | Please refer to vehicle service manual. | Current |
| P18D000 | Please refer to vehicle service manual. | History |
| P124003 | Please refer to vehicle service manual. | Current |
| P0A9500 | Please refer to vehicle service manual. | Current |
| U014687 | Please refer to vehicle service manual. | Current |
| U110117 | Please refer to vehicle service manual. | History |
| P0ABF86 | Please refer to vehicle service manual. | History |
| U012587 | Please refer to vehicle service manual. | History |

### VCU (Vehicle Control Unit) - 14 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U125517 | Please refer to vehicle service manual. | History |
| U125516 | Please refer to vehicle service manual. | History |
| U092300 | Please refer to vehicle service manual. | Current |
| P101716 | Please refer to vehicle service manual. | History |
| U117188 | Please refer to vehicle service manual. | History |
| P112900 | Please refer to vehicle service manual. | History |
| P113700 | Please refer to vehicle service manual. | Current |
| P103300 | Please refer to vehicle service manual. | History |
| P115000 | Please refer to vehicle service manual. | History |
| P115100 | Please refer to vehicle service manual. | History |
| P118800 | Please refer to vehicle service manual. | History |
| U110116 | Please refer to vehicle service manual. | History |
| P105D38 | Please refer to vehicle service manual. | History |
| P106B29 | Please refer to vehicle service manual. | History |

### ESC (Electronic Stability Control) - 4 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U015687 | Please refer to vehicle service manual. | History |
| C059496 | Please refer to vehicle service manual. | History |
| U041681 | Please refer to vehicle service manual. | Current |
| U110887 | Please refer to vehicle service manual. | Current |

### EPS (Electric Power Steering) - 1 DTC

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U110116 | Power supply - circuit voltage below threshold | History |

### ADAS (Advanced Driver Assistance System) - 30 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U113187 | Please refer to vehicle service manual. | History |
| U30031C | Please refer to vehicle service manual. | History |
| U113387 | Please refer to vehicle service manual. | History |
| U113087 | Please refer to vehicle service manual. | History |
| U113287 | Please refer to vehicle service manual. | History |
| U112987 | Please refer to vehicle service manual. | History |
| U111189 | Please refer to vehicle service manual. | Current |
| U113081 | Please refer to vehicle service manual. | History |
| U116589 | Please refer to vehicle service manual. | Current |
| U111489 | Please refer to vehicle service manual. | History |
| U118289 | Please refer to vehicle service manual. | History |
| U113381 | Please refer to vehicle service manual. | History |
| U118789 | Please refer to vehicle service manual. | Current |
| U114081 | Please refer to vehicle service manual. | Current |
| U114289 | Please refer to vehicle service manual. | History |
| U119689 | Please refer to vehicle service manual. | Current |
| B193504 | Please refer to vehicle service manual. | History |
| B193104 | Please refer to vehicle service manual. | History |
| B193704 | Please refer to vehicle service manual. | History |
| B19084A | Please refer to vehicle service manual. | History |
| B193304 | Please refer to vehicle service manual. | History |
| B193404 | Please refer to vehicle service manual. | History |
| B193204 | Please refer to vehicle service manual. | History |
| B194004 | Please refer to vehicle service manual. | History |
| B193904 | Please refer to vehicle service manual. | Current |
| B194204 | Please refer to vehicle service manual. | History |
| B194104 | Please refer to vehicle service manual. | History |
| U119387 | Please refer to vehicle service manual. | History |
| U119287 | Please refer to vehicle service manual. | History |
| U113681 | Please refer to vehicle service manual. | History |

### CCU (Climate Control Unit) - 2 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| B170E54 | Please refer to vehicle service manual. | Current |
| U110887 | Lost communication with airbag control module | Current |

### MHU (Multimedia Headunit) - 10 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| B161A03 | Please refer to vehicle service manual. | History |
| U300004 | Please refer to vehicle service manual. | History |
| U014687 | Please refer to vehicle service manual. | Current |
| U015C87 | Please refer to vehicle service manual. | History |
| B160D14 | Please refer to vehicle service manual. | History |
| B160E14 | Please refer to vehicle service manual. | History |
| U110116 | Please refer to vehicle service manual. | History |
| B162004 | Please refer to vehicle service manual. | History |
| B161B01 | Please refer to vehicle service manual. | History |
| B161A01 | Please refer to vehicle service manual. | Current |

### RLS (Rain/Light Sensor) - 4 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| U100304 | Please refer to vehicle service manual. | Current |
| U100404 | Please refer to vehicle service manual. | Current |
| U10041C | Please refer to vehicle service manual. | Current |
| U110116 | Please refer to vehicle service manual. | Current |

### XGW (Extendable Gateway) - 9 DTCs

| DTC | Autel description | Status |
|-----|-------------------|--------|
| B200101 | Please refer to vehicle service manual. | History |
| B200001 | Please refer to vehicle service manual. | Current |
| U117188 | Chassis CAN - bus off | History |
| U110887 | Lost communication with airbag control module | Current |
| U019E87 | Please refer to vehicle service manual. | History |
| U012287 | Lost communication with vehicle dynamics control module | History |
| U110116 | Power supply circuit voltage below threshold | History |
| B2001A2 | Please refer to vehicle service manual. | History |
| B2000A2 | Please refer to vehicle service manual. | History |

### Additional Autel Section Labeled "DC Converter)" - 21 DTCs

The PDF table labels this final section as "DC Converter)" even though the scan summary earlier lists DDC with 0 DTCs. The label is preserved exactly as extracted; the module identity should be verified with a follow-up scan.

| DTC | Autel description | Status |
|-----|-------------------|--------|
| C150C1C | Please refer to vehicle service manual. | History |
| U113787 | Please refer to vehicle service manual. | History |
| U113887 | Please refer to vehicle service manual. | History |
| U124329 | Please refer to vehicle service manual. | History |
| C153700 | Please refer to vehicle service manual. | History |
| C153600 | Please refer to vehicle service manual. | History |
| U113987 | Please refer to vehicle service manual. | History |
| U114087 | Please refer to vehicle service manual. | History |
| U114187 | Please refer to vehicle service manual. | History |
| U111589 | Please refer to vehicle service manual. | History |
| U112081 | Please refer to vehicle service manual. | History |
| U112389 | Please refer to vehicle service manual. | History |
| U112681 | Please refer to vehicle service manual. | History |
| U113081 | Please refer to vehicle service manual. | History |
| U113381 | Please refer to vehicle service manual. | History |
| U114081 | Please refer to vehicle service manual. | Current |
| U114881 | Please refer to vehicle service manual. | History |
| U118789 | Please refer to vehicle service manual. | Current |
| U119389 | Please refer to vehicle service manual. | History |
| U113581 | Please refer to vehicle service manual. | History |
| U119689 | Please refer to vehicle service manual. | Current |

## Evidence-Based Interpretation

The only firm conclusion from this scan alone is that the vehicle has active/current network, restraint-message, low-voltage, ADAS, and HV-related faults across multiple modules. The repeated current `U110887` entries in MCU, BCM, ESC, CCU, and XGW show several modules reporting missing airbag/restraints communication. The EPS and XGW both report low 12 V supply history (`U110116`), which can create or preserve communication faults during diagnosis. The BMS current set includes `P180000`, `P124100`, `P183401`, `P124003`, and `P0A9500`, all of which must be treated as high-voltage safety-relevant until verified by VinFast service data.

Do not assume a DTC is repaired because it clears once. Clear only after recording the full report, stabilizing 12 V supply, repairing physical harness/HV/restraint damage, and rescanning after a complete sleep/wake cycle.