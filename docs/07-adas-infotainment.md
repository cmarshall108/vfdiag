# 07 — ADAS, Infotainment & Connected Services

## ADAS Sensor Suite

| Sensor | Location | Function |
|--------|----------|----------|
| Forward camera (mono/stereo, Mobileye-based) | Windshield, near rearview mirror | Lane detection, traffic-sign recognition, AEB target tracking |
| Forward radar (long-range, 77 GHz) | Behind lower front grille | ACC, AEB, FCW |
| Corner radars (4×, 77 GHz) | Front & rear bumpers, corners | Blind spot, rear cross-traffic |
| Surround-view cameras (4×) | Front grille, mirrors, tailgate | 360° view, parking |
| Ultrasonic sensors (12×) | Front + rear bumpers | Parking assist, low-speed AEB |
| Driver Monitoring Camera (DMC) | Steering column / A-pillar | Drowsiness/attention monitoring |
| Interior cabin camera | Headliner | Selfie / OMS (some markets) |

## ADAS Feature Set (2024 MY)

- Adaptive Cruise Control (ACC) with stop & go
- Lane Departure Warning (LDW)
- Lane Keeping Assist (LKA) — subject of NHTSA investigation (see [12-recalls-tsb-known-issues.md](12-recalls-tsb-known-issues.md))
- Lane Centering / "Highway Assist" (Level 2)
- Forward Collision Warning (FCW)
- Autonomous Emergency Braking (AEB) — pedestrian & cyclist detection
- Blind Spot Detection (BSD) + BS Intervention
- Rear Cross-Traffic Alert + Brake
- Door Open Warning (cyclist)
- Traffic Sign Recognition (TSR) with intelligent speed assist
- 360° surround view + transparent hood view
- Auto Park Assist (parallel & perpendicular)
- Smart Summon (low-speed) — market-dependent rollout
- Driver Drowsiness/Inattention monitoring

> NHTSA Forward Collision Warning evaluation marked the 2024 VF8 as **"Failed Test"** despite standard fitment — a documented data point on the NHTSA vehicle page.

### ADAS Calibration
- **Static** calibration required for the forward camera after windshield replacement; uses VinFast-specified target board at defined distance.
- Front/corner radars require static calibration after bumper R&R or collision repair.
- 360 cameras require dynamic calibration (driving pattern) plus scan-tool routine.

### Observed ADAS Scan Evidence

The 2026-03-30 Autel report archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md) logged 30 ADAS DTC rows. Current ADAS rows were `U111189`, `U116589`, `U118789`, `U114081`, `U119689`, and `B193904`; the rest were history at the time of that scan.

This scan supports a conservative collision-repair workflow: verify sensor power/ground, bumper harness continuity, camera/radar mounting, windshield camera condition, steering-angle data quality, and restraints communication before attempting ADAS calibration. A current communication DTC should be resolved before trusting calibration results.

## Infotainment ("VinFast Smart Services")

- **15.6" central touchscreen**, ~1920 × 1080, capacitive, portrait-leaning landscape orientation
- SoC: ARM-based (Qualcomm Snapdragon Automotive-class)
- OS: Android Automotive-based VinFast OS skin
- Connectivity:
  - Wi-Fi 802.11 a/b/g/n/ac
  - Bluetooth 5.0
  - LTE / 5G (TBOX)
  - USB-C × 2 front, USB-C × 2 rear
- Apple CarPlay: **wireless** (added via OTA after launch)
- Android Auto: **wireless** (added via OTA)
- Embedded apps: Spotify, TIDAL, browser, weather, navigation (HERE-based, with EV routing & DC-station preconditioning)
- Voice assistant: "Hi VinFast" — natural-language commands for HVAC, navigation, media, vehicle settings
- HUD: full-color, projects speed, ACC/LKA state, turn-by-turn, alerts

### Observed MHU / RLS Scan Evidence

The same Autel report logged 10 MHU rows and 4 RLS rows. MHU current rows were `U014687` and `B161A01`; RLS current rows were `U100304`, `U100404`, `U10041C`, and `U110116`. The report did not provide authoritative service definitions for these rows, so they should be used as module-status evidence only.

## OTA Updates

- Full vehicle OTA (firmware + IVI) over Wi-Fi or LTE
- User must accept and park to install; install windows typically 20–90 min
- All ECU groups updatable: VCU, BMS, MCUs, OBC, ADAS, IVI, HUD, BCM
- Historical update cadence has been frequent; many early reviewer complaints (regen feel, ACC behavior, HVAC bugs) addressed by OTA in 2024.

## VinFast Mobile App

- Remote start (preconditioning), lock/unlock, charge schedule, charge status
- Find My Car, valet mode
- Trip history, energy log, SoC graphs
- Service appointment booking, recall lookup
- Push notifications on alarm/door/charge events

