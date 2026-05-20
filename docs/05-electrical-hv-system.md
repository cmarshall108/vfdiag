# 05 — Electrical & HV System Architecture

## Voltage Levels

| Bus | Voltage | Purpose |
|-----|---------|---------|
| HV traction | ~280–410 V DC | Motors, OBC, DC-DC, A/C compressor, PTC, battery heater |
| LV body | 12 V DC (AGM) | All conventional ECUs, lighting, infotainment, low-side sensors |
| 5 V / 3.3 V sensor | regulated | Sensor reference rails |

## Electronic Control Units (typical)

| Acronym | Module | Function |
|---------|--------|----------|
| VCU | Vehicle Control Unit | Master coordinator; torque/charge/thermal arbitration |
| BMS | Battery Management System | Cell monitoring, SoC/SoH, contactor control, IMD oversight |
| MCU-F | Front Motor Control Unit | Inverter for front e-axle |
| MCU-R | Rear Motor Control Unit | Inverter for rear e-axle |
| OBC | On-Board Charger | AC→DC for charging |
| DC-DC | HV→12 V Converter | LV system supply |
| TCM-EV | Thermal Control Module | Coolant valves, pumps, heat pump |
| ABS/ESC | Brake Control / ESP | ABS, ESC, TCS, eBooster integration |
| EPS | Electric Power Steering | Steering assist |
| EPB | Electric Park Brake | Rear-caliper actuators |
| BCM | Body Control Module | Lights, locks, windows |
| GW | Central Gateway | CAN/CAN-FD/Ethernet routing, OTA endpoint |
| TBOX | Telematics | LTE/5G, GNSS, eCall |
| IVI / HU | Head Unit | 15.6" touchscreen, Android-based |
| ADAS-C | ADAS Controller | Mobileye / domain controller; camera + radar fusion |
| HUD | Head-Up Display | Drive info projection |
| AC-COMP | A/C Compressor ECU | HV electric scroll compressor |
| CHG-PORT | Charge Port Controller | Locking, CP/PP signaling, LED ring |

## Modules Observed in Autel Full-System Scan

An Autel MaxiCOM MK900-BT report captured during VF 8 diagnostics, using Autel's VinFast VF e34 profile because VF 8 was not listed, enumerated these systems: MCU, BCM, BMS, VCU, ESC, EPS, ADAS, CCU, DDC, MHU, RLS, and XGW. The exact scan is archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md).

This is useful topology evidence, but not a substitute for VinFast wiring diagrams. The scan confirms module names exposed through that Autel profile and shows repeated network faults involving airbag/restraints communication, chassis CAN bus-off history, 12 V supply history, and ADAS sensor communication loss.

## Network Topology

```
                    ┌─────────────────────────────────┐
                    │  Central Gateway (GW) + TBOX    │◀── LTE/GNSS
                    └────┬────────────┬────────────┬──┘
                         │ Ethernet   │ CAN-FD     │ CAN-FD
                         │            │            │
        ┌────────────────┼──┐    ┌────┼────┐  ┌────┼───────┐
        │ IVI / HU       │  │    │ VCU │   │  │ ADAS-C     │
        │ 15.6" screen   │  │    └────┬────┘  └────┬───────┘
        └────────────────┘  │         │            │
                            │   ┌─────┴───┐   ┌────┴────┐
                            │   │ HV-CAN  │   │ Cam/Rad │
                            │   └────┬────┘   └─────────┘
                            │        │
            ┌───────────────┼────────┼────────┬────────┬────────┐
            │               │        │        │        │        │
        ┌───┴──┐         ┌──┴───┐ ┌──┴──┐ ┌───┴──┐ ┌───┴───┐ ┌──┴──┐
        │ BMS  │         │ MCU-F│ │MCU-R│ │ OBC  │ │ DC-DC │ │TCM-E│
        └──────┘         └──────┘ └─────┘ └──────┘ └───────┘ └─────┘

       Body CAN ──── BCM ── BCM-slaves ── doors ── lights ── EPB
        Chassis CAN ──── ABS/ESC ── EPS ── HUD ── steering-angle sensor
```

- Multiple **CAN / CAN-FD** segments isolated by the Central Gateway.
- **FlexRay** is *not* used.
- **Automotive Ethernet (100BASE-T1)** for camera/ADAS and IVI backbone.

## HV Interlock Loop (HVIL)

- Daisy-chained low-current loop through every HV connector and the MSD socket.
- Break in HVIL → BMS opens main contactors and sets a stored DTC (P0AA6 / vendor-specific equivalent).
- Always verify HVIL continuity after reassembling any HV connector.

## 12 V Battery

- Type: AGM, ~80 Ah, Group H7 footprint
- Location: under-hood, passenger side
- Charging: from HV via DC-DC converter (~2.5 kW continuous)
- **Caution:** Disconnecting the 12 V battery while the HV system is awake can leave contactors in an undefined state and may trigger isolation faults. Always:
  1. Vehicle OFF, doors closed, key fob ≥ 5 m away
  2. Wait 2 min for buses to sleep
  3. Then disconnect 12 V negative

## HV Cable Color Codes

- **Orange** — energized HV power cabling (per SAE J1673)
- **Blue** — HV signal / HVIL
- **Black** — chassis ground / LV negative
- **Red** — 12 V positive

Never cut, splice, or repair orange HV cabling in the field. Replace full assemblies only.

