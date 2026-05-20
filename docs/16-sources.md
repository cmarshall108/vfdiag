# 16 — Sources & Bibliography

Primary public sources consulted in compiling this documentation set:

## Manufacturer
- VinFast — official global site: https://vinfastauto.com
- VinFast US: https://vinfastauto.us
- VinFast US VF 8 spec leaflet (PDF):
  https://static-cms-prod.vinfastauto.us/cms-vinfast-us/Specs/VF-8-Spec.pdf

## Regulatory / Safety
- NHTSA vehicle page — 2024 VINFAST VF8 SUV AWD:
  https://www.nhtsa.gov/vehicle/2024/VINFAST/VF8/SUV/AWD
  (4/5 overall safety; Frontal 2/5; Side 5/5; Rollover 5/5; FCW "Failed Test"; 3 recalls, 1 investigation, 18 complaints at time of capture.)
- NHTSA recall lookup (by VIN): https://www.nhtsa.gov/recalls
- Euro NCAP — 2023 VinFast VF 8 datasheet (PDF):
  https://cdn.euroncap.com/media/82671/euroncap-2023-vinfast-vf8-datasheet.pdf
- ASEAN NCAP — VinFast VF 8 result: https://www.aseancap.org/result/9989

## Reference Encyclopedia
- Wikipedia, "VinFast VF 8": https://en.wikipedia.org/wiki/VinFast_VF_8

## Independent EV Databases
- EVKX — VinFast VF8 Eco charging curve:
  https://evkx.net/models/vinfast/vf8/vf8_eco/chargingcurve/
- EVKX — VF8 hub: https://evkx.net/models/vinfast/vf8/
- Electrly — VinFast VF 8 Plus Standard Range Charging Guide:
  https://electrly.com/ev-charging-guide/vinfast/vin-fast-vf-8-plus-standard-range
- GreenCarsCompare — VinFast VF 8 Eco specs:
  https://greencarscompare.com/car/vinfast-vf-8-eco-2024/specs/
- EVSearch — VinFast VF8 technical specs:
  https://evsearch.ca/product/vinfast-vf8-electric-vehicle/
- Fastned — VinFast brand compatibility:
  https://www.fastnedcharging.com/en/brands-overview/vinfast

## Major Reviews (US press)
- Car and Driver — "2024 VinFast VF8 Review, Pricing, and Specs"
- Edmunds — "2024 VinFast VF 8 Prices, Reviews, and Pictures"
- Kelley Blue Book — "2024 VinFast VF 8 Specs & Feature Comparisons"
- Cars.com — "2024 VinFast VF 8 — Specs, Prices, Range, Reviews & Photos"
- CARFAX — "2024 VinFast VF8 Review, Pricing, and Specs"
- MotorTrend — "2023 VinFast VF8 First Drive: Return to Sender" (Scott Evans, 2023)
- Road & Track — "First Drive: The 2023 VinFast VF8 Is Unacceptable" (Mack Hogan, 2023)
- InsideEVs — "2023 VinFast VF8 City Edition First Drive Review: Yikes" (Steven Ewing, 2023)
- Jalopnik — "The VinFast VF8 Is Simply Not Ready for America" (Kevin Williams, 2022)
- Green Car Reports — Brian Wong / Emme Hall reviews (2022, 2023)
- BBC News — "JLR whistleblower sacked for publishing concerns about VinFast cars" (Andy Verity, Dec 19 2024)
- Carscoops — "VinFast Owner Says Their EV Took Over Steering And Nearly Hit A Wall" (Sep 6 2025)
- Evercars — "2025 VinFast VF8 Review: 402 HP And A Cheaper Price Tag"

## Standards Referenced
- SAE J1962 — OBD-II connector
- SAE J1772 — AC Level 1/2 connector
- SAE J2534-1 — Pass-Thru vehicle programming interface used by Mini-VCI/TEXA-style J2534 DLLs
- SAE J2012 — Diagnostic Trouble Code definitions
- SAE J1673 — High-voltage automotive wiring (orange)
- ISO 15765 — Diagnostics on CAN
- ISO 14229 — UDS (Unified Diagnostic Services)
- ISO 13400 — DoIP (Diagnostics over IP)
- ISO 6469 — Electric road vehicle safety
- IEC 62196 / DIN 70121 — CCS Combo
- NFPA EVSAFE — First-responder training

## Diagnostic Artifacts Reviewed

- Autel MaxiCOM MK900-BT VinFast diagnostic report, report ID `MAXIA20260330192852`, test time `2026-03-30 19:28:52`. The report selected `VinFast / VF e34` in Autel because VF 8 was unavailable, but the vehicle under test was a 2024 VinFast VF 8. The exact DTC list extracted from the report is preserved in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md).
- Local `vf8-obd` Python tool behavior and J2534 binding implementation in [../tools/vf8-obd](../tools/vf8-obd). This verifies what the repository tool can do through a J2534 DLL: standard ISO 15765-4 OBD requests, Mode 04 clear on responding legislated OBD modules, and passive CAN monitoring on pins 6/14. It does not verify VinFast gateway security access.
- Local diagnostic/programming synthesis in [19-diagnostic-programming-notes.md](19-diagnostic-programming-notes.md), derived from the standards listed above, the local J2534 implementation, and the observed Autel scan appendix. This file intentionally avoids publishing or guessing seed/key algorithms, SecOC keys, calibration files, or protected routine IDs.

## Notes on Accuracy

- Where a number is given without a citation in the technical-spec tables (e.g. exact alignment values, exact pack module count, exact reduction ratios), the value reflects the **best public estimate** drawn from teardown reports and EV-database aggregators and **must be confirmed against the current VinFast Service Information** before relying on it for paid service work or legal documents.
- Recall campaign IDs were intentionally left as placeholders (`24V-...`) because campaign numbers and remedy bulletins are revised by VinFast and NHTSA frequently. Always look up the current set by VIN.
- DTC tables combine SAE J2012 generic codes (authoritative) with commonly observed VinFast-specific symptom mappings (advisory).
- Autel-sourced DTCs are treated as observed scan evidence. If Autel printed "Please refer to vehicle service manual," this documentation does not promote that row to an authoritative VinFast definition.

