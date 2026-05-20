# 04 — Charging

## Charge Port

- **Location:** Driver-side rear quarter panel
- **Connector (North America):** SAE J1772 (AC) combined with CCS1 (DC fast)
- **Connector (Europe):** Type 2 / CCS2
- **NACS (Tesla) compatibility:** Not native on 2024 MY — requires NACS-to-CCS1 adapter (VinFast announced future NACS support on later MY)
- **Port lock:** Solenoid-actuated, opens when vehicle unlocked

## AC Charging

| Source | Connector | Power | 0–100% (~87.7 kWh) |
|--------|-----------|-------|--------------------|
| 120 V / 12 A NEMA 5-15 | J1772 via portable EVSE | ~1.4 kW | ~60+ hours |
| 240 V / 48 A wallbox | J1772 | **11 kW** | ~9 hours |
| 240 V / 32 A wallbox | J1772 | ~7.7 kW | ~13 hours |

- **On-Board Charger:** 11 kW, 3-phase capable (used in EU markets); 7.4–11 kW single-phase in NA depending on circuit.

## DC Fast Charging

| Metric | Value |
|--------|-------|
| Connector (NA) | CCS1 |
| Peak power | ~150 kW |
| Typical sustained (10–80 %) | ~80–110 kW |
| 10–80 % time | ~31 min (best case on 150 kW station) — ~44 min in real-world testing |
| Architecture | 400 V (single-pack series) |
| Preconditioning | Yes, triggered automatically when routing to a DC station via the built-in navigation |

### Charging Curve (approximate, 150 kW station, 25 °C battery, preconditioned)

```
 kW
150 |█████
140 |█████ █
130 |█████ ██
120 |█████ ████
110 |█████ ███████
100 |█████ █████████
 90 |█████ ███████████
 80 |█████ █████████████
 70 |█████ ███████████████
 60 |█████ █████████████████
 50 |                          ██████
 40 |                                 ████
 30 |                                     ██
 20 |
    +----------------------------------------- SoC
     0   10   20   30   40   50   60   70   80   90  100
```

- Peak ~150 kW held briefly between ~10–25 % SoC
- Tapers significantly past 60 %, dropping below 50 kW above 80 %
- Recommended DC stop window: **10 → 70 %**

## Network Compatibility (North America)

| Network | Compatible | Notes |
|---------|------------|-------|
| Electrify America | ✅ | Native CCS1 |
| EVgo | ✅ | CCS1 |
| ChargePoint DC | ✅ | CCS1 |
| Tesla Supercharger (V3/V4 Magic Dock) | ⚠️ | Requires Magic Dock site; many sites still NACS-only |
| Tesla Supercharger (legacy NACS-only) | ❌ | Until VinFast issues a verified NACS adapter |
| Greenlots / Shell Recharge | ✅ | CCS1 |
| Blink | ✅ | CCS1 |

## Driver Charging Behaviors

- Charge port LED indicators:
  - **Solid white:** Idle / unlocked
  - **Blinking green:** Charging in progress
  - **Solid green:** Charge complete
  - **Blinking amber:** Pending / waiting for schedule
  - **Solid red:** Fault — see [09-dtc-codes.md](09-dtc-codes.md), check P0CBC / P0D05 family
- Set charge limit via touchscreen (default 80 %, raise to 100 % for road-trip departure)
- Charge schedules via VinFast app

