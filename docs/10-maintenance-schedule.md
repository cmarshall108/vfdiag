# 10 — Maintenance Schedule (2024 VF 8)

VinFast publishes a maintenance schedule based on **time OR mileage, whichever comes first**. EV maintenance is minimal — no engine oil, no spark plugs, no transmission service. The HV battery and drive units are largely "fill-for-life" with periodic inspections.

> Always verify the *current* schedule in the latest VinFast Owner's Manual / SmartService app, as VinFast has revised intervals via TSB.

## General Interval Table

| Service Item | First | Then every | Action |
|--------------|-------|------------|--------|
| Tire rotation | 7,500 mi / 12,000 km | 7,500 mi / 12,000 km | Cross-rotate, re-torque to 140 N·m, reset TPMS learn |
| Brake fluid (DOT 4 LV) | 2 years | 2 years | Full flush via scan-tool actuated bleed |
| Cabin air filter | 1 year / 15,000 mi | 1 year / 15,000 mi | Replace (HEPA-grade) |
| HVAC condenser filter (some markets) | 2 years | 2 years | Inspect/replace |
| 12 V AGM battery test | 1 year | 1 year | Conductance test; replace ≤ ~50 % SoH |
| Wiper blades | 1 year | 1 year | Replace |
| Body lubrication (latches, hinges) | 1 year | 1 year | Lubricate |
| Brake pad/disc inspection | 1 year / 15,000 mi | 1 year / 15,000 mi | Visual + thickness measure |
| Suspension/steering inspection | 1 year / 15,000 mi | 1 year / 15,000 mi | Boots, bushings, end-links |
| HV coolant (battery loop) | 5 years / 60,000 mi | 5 years / 60,000 mi | Specific EV OAT coolant only |
| Power-electronics coolant loop | 5 years / 60,000 mi | 5 years / 60,000 mi | Same |
| Reduction-gearbox oil | "Lifetime fill" | Inspect at 100,000 mi | Replace only if contaminated |
| A/C system check (R-1234yf) | 2 years | 2 years | Leak check, performance check |
| HV battery health check | 1 year | 1 year | Scan-tool SoH report, cell-balance review |
| ADAS calibration verification | 1 year | 1 year | Static targets + dynamic drive |
| Software updates | OTA, ongoing | — | Accept all published updates |

## Recommended Pre-Trip (Owner) Checks

- Cold tire pressures (see door-jamb placard, typically 36/38 psi front/rear)
- Wipers + washer fluid
- 12 V battery age (years stamped on top)
- Charge port pins — visually inspect for foreign debris
- Cabin air filter (under glovebox)

## Things Owners Frequently Get Wrong

- **Coolant top-off with conventional ethylene glycol** — DO NOT. Use only VinFast-specified low-conductivity EV OAT coolant. Wrong coolant triggers **P0A04** isolation faults that can sideline the car.
- **Rear pad change without EPB service mode** — destroys the EPB actuator.
- **Tire rotation without TPMS relearn** — can leave wrong-corner pressure on HUD; some 2024 firmware auto-learns.
- **12 V battery disconnect with car awake** — see [05-electrical-hv-system.md](05-electrical-hv-system.md).

