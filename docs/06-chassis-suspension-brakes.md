# 06 — Chassis, Suspension, Brakes, Wheels & Tires

## Suspension

| Position | Type | Components |
|----------|------|------------|
| Front | MacPherson strut | Strut + spring, lower control arm, stabilizer bar |
| Rear | 5-link independent | Trailing arm, 4 lateral links, stabilizer bar |

- Conventional coil springs and twin-tube dampers (no air suspension on 2024 US trims).
- Bushings: hydraulic at front lower control arm rear bush, conventional rubber elsewhere.
- Reviewers consistently cited **soft damping and floaty rebound**; VinFast issued multiple software/calibration refinements but no hardware spring/damper change on 2024 MY.

### Alignment Specs (nominal, target ± tolerance)

| Axis | Front | Rear |
|------|-------|------|
| Camber | -0°45′ ± 30′ | -1°15′ ± 30′ |
| Caster | +5°00′ ± 30′ | — |
| Toe (total) | 0°10′ ± 10′ (toe-in) | 0°15′ ± 10′ (toe-in) |
| Thrust angle | — | 0°00′ ± 06′ |

*Confirm against current VinFast spec sheet — alignment targets have been revised via TSB.*

## Steering

- Electric power-assisted rack (EPS)
- Ratio: ~14.5 : 1
- Turns lock-to-lock: ~2.7
- Turning circle: ~12.0 m (curb-to-curb)
- Variable assist with drive mode (heavier in Sport)

## Brakes

| Item | Front | Rear |
|------|-------|------|
| Rotor | Ventilated disc, ~345 × 30 mm | Ventilated disc, ~330 × 22 mm |
| Caliper | 2-piston floating (some markets sliding single-piston) | Single-piston floating |
| Pad material | Low-metallic / NAO blend (EV-friendly low-dust) | NAO |
| Parking brake | — | Electric (EPB), motor-on-caliper |
| Brake fluid | DOT 4 LV | DOT 4 LV |
| Brake booster | **eBooster** (electromechanical), Bosch iBooster-equivalent |

### Brake Service Notes
- **EPB service mode** required before rear pad replacement (engage via scan tool or specific touchscreen sequence: *Settings → Vehicle → Service → Brake Service Mode*).
- Bleed sequence: RR → LR → RF → LF (verify in current FSM; eBooster systems may require scan-tool-actuated bleed cycle to purge the booster cylinder).
- Bleeding **must** be done with scan tool to actuate ABS/ESC HCU on EV — gravity bleed alone is insufficient.

### Observed ESC / EPS Scan Notes

The 2026-03-30 Autel report archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md) logged four ESC DTC rows: `U015687` history, `C059496` history, `U041681` current, and `U110887` current. EPS logged `U110116` history with Autel's description "Power supply - circuit voltage below threshold."

The solid service implication is that chassis faults should be interpreted after stabilizing the 12 V system and resolving restraints/gateway communication faults. Do not calibrate steering angle, bleed the HCU, or validate ADAS/chassis functions from a scan that still has current module communication loss.

## Wheels & Tires

| Wheel | Tire | Spec |
|-------|------|------|
| 19" alloy (std) | 235/55 R19 | 105 V/H XL, M+S |
| 20" alloy (opt, Plus) | 255/45 R20 | 105 V XL |

- TPMS: direct, 433 MHz sensors, relearn via scan tool or auto-relearn after ~15 min driving above 25 mph.
- Cold tire pressures (typical placard): **36 psi front / 38 psi rear** — verify door-jamb placard for the specific vehicle.
- Lug torque: **140 N·m (103 lb-ft)** — confirm in FSM.
- No spare tire; tire mobility kit (sealant + 12 V compressor) under cargo floor.

## Body & Glass

- Body structure: high-strength steel monocoque with hot-stamped boron-steel B-pillars and rocker reinforcements
- Front bumper beam: aluminum extrusion
- Hood: aluminum (some markets steel)
- Windshield: acoustic laminated glass with HUD-clear zone
- Front-side glass: acoustic laminated (Plus trim)
- Rear glass: tempered, privacy tint

