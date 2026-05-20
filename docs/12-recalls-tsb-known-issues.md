# 12 — Recalls, Investigations & Known Issues (2024 MY)

> Per NHTSA's vehicle page for **2024 VINFAST VF8 SUV AWD** (as queried for this document): **5 active safety recalls, 1 open investigation, 18 consumer complaints**. NHTSA overall safety rating: **4/5** (Frontal 2/5, Side 5/5, Rollover 5/5). Forward Collision Warning was marked **"Failed Test"** despite standard fitment.

Always look up the **current** list with your specific VIN at:
- https://www.nhtsa.gov/recalls (search by VIN)
- VinFast app → Safety & Recalls

## Recalls Affecting 2023-2024 MY (publicly documented)

| Campaign | Title | Affected | Remedy |
|----------|-------|----------|--------|
| **NHTSA 23V-355** *(May 2023)* | MHU Infotainment Screen and HUD Blanking on Startup — Watchdog boot timing issue (Bulletin 8-23-NA-35-005, internal docs 1002970 / 1002963). | 999 units (MY2023 produced 10/19/2022 to 04/29/2023) | Free OTA software update to FRS 9.6 or later (TBOX SOW30052001 Rev 14, MHU SOW30051001 Rev 29). |
| **NHTSA 24V-116** *(Feb 2024)* | Left Front Turn Signal and High Beam Inoperative — Connector pin tension or controller pin routing causes circuit open. | Under 300 units (subset of early 2024 MY) | Dealer inspects/repairs connector harness or replaces front lighting module. |
| **NHTSA 24V-274** *(Apr 2024)* | Occupant Detection System (ODS) Passenger Airbag Warning Logic Error — Passenger airbag off light fails to display properly. | Subset of 2023–2024 units | Free OTA software calibration update or seat cushion ODS pressure sensor replacement. |
| **NHTSA 24V-355** *(May 2024)* | Front Airbag Crash Sensor Bracket Deformation — Minor collisions or vibration could deform brackets, affecting timing. | Subset of 2023-2024 units | Dealer reinforcing bracket mounts and recalibration. |
| **NHTSA 24V-426** *(Jun 2024)* | Brake Fluid Logic Error & Master Cylinder Monitoring fault — Dashboard warning light fails to illuminate under low-fluid situations. | Subset of 2024 units | Free software re-flash of the brake actuator (eBooster) control unit. |

*(Exact campaign numbers and remedy bulletins change as VinFast files supplements. Confirm with current NHTSA query — the 2024 VF8 AWD page shows active recalls at time of writing.)*

## Open NHTSA Investigation

| ID | Subject | Status |
|----|---------|--------|
| **ODI PE24-003** (opened Sep 2024) | Lane Keeping Assist (LKA) — system reportedly applies incorrect steering inputs, difficulty for driver to override. 14 complaints at opening. | Preliminary Evaluation, open |

Background: NHTSA's Office of Defects Investigation cited that drivers reported the LKA system difficult to override and providing erroneous lane-centering inputs that could elevate crash risk.

## Common Owner Complaints (NHTSA + forums)

1. **LKA "ping-ponging" / phantom braking** under ACC, especially on lane-marking transitions or construction zones.
2. **Charge session failures** at certain Electrify America stations — usually resolved by retrying the session or a software update; some traced to **CP signaling timing** sensitivity.
3. **12 V battery drain** from gateway/TBOX staying awake — addressed by multiple OTA updates; if recurring, test 12 V AGM and confirm latest firmware.
4. **Infotainment freezes / reboots** — substantially improved by OTA updates from 2023 → 2024; force-reboot via two-finger long-press on the screen.
5. **HVAC odors** at first use after long sit — replace cabin filter and run "vent dry" cycle.
6. **Wind noise** at A-pillar / mirror — TSB realigns mirror gaskets.
7. **Soft brake pedal feel** after eBooster wake — known characteristic; not a fault unless DTC stored.
8. **Range below EPA estimate** in cold weather without preconditioning — expected for any BEV; use scheduled departure + preconditioning.

## Reviewer-Documented Hardware Limitations (not recalled)

- Soft, under-damped suspension tuning
- EPS calibration: numb on-center, inconsistent build-up
- Build quality variance unit-to-unit (panel gaps, trim alignment)
- Brake feel: numb top of pedal due to eBooster blending

## TSB-Style Topics (commonly addressed via OTA on 2024 MY)

| Area | Improvement delivered via OTA |
|------|-------------------------------|
| Regen blending | Smoother transition between regen levels and from regen → friction brake |
| ACC tuning | Reduced overshoot and harsh approach to slower lead vehicles |
| LKA | Sensitivity sliders + reduced unprompted intervention (subject of ongoing investigation) |
| HUD | New layouts, dim/auto-dim tuning |
| CarPlay / Android Auto | Wireless support added |
| Battery preconditioning | More aggressive precondition trigger when routing to DCFC |
| Charge curve | Slight peak-power & taper tuning improvements |

