# 14 — System Block Diagrams & Connector Pinouts

> ASCII block diagrams for reference. Full schematics are VinFast IP and ship only via the official Service Information portal. Do not attempt to fabricate or splice HV harnesses from these.

## HV Power Flow

```
                    ┌──────────────────┐
                    │  Charge Port     │  CCS1
                    │  (J1772 + CCS)   │◀── External station
                    └────────┬─────────┘
                       AC│       │DC
                         ▼       ▼
                 ┌──────────┐ ┌──────────────┐
                 │   OBC    │ │ DC Fast      │
                 │ 11 kW    │ │ direct path  │
                 └─────┬────┘ └──────┬───────┘
                       └──────┬──────┘
                              ▼
                 ┌──────────────────────────┐
                 │  HV Junction Box (BJB)   │
                 │  • Main contactors (±)    │
                 │  • Pre-charge contactor   │
                 │  • Pre-charge resistor    │
                 │  • Current shunt          │
                 │  • IMD                    │
                 │  • MSD                    │
                 └──┬────────┬─────────┬─────┘
                    │HV      │HV       │HV
                    ▼        ▼         ▼
              ┌──────────┐┌──────────┐┌────────────┐
              │  MCU-F + ││  MCU-R + ││ DC-DC +    │
              │  motor   ││  motor   ││ A/C compr. │
              └──────────┘└──────────┘│ + PTC htr  │
                                       └────────────┘
                                              │12V
                                              ▼
                                       12V AGM Battery
                                       → All LV ECUs
```

## CAN/Ethernet Backbone

```
        Diag/OBD-II (Pin 6/14)
              │
              ▼
   ┌──────────────────────┐
   │    Central Gateway    │◀── 100BASE-T1 ── IVI Head Unit
   │  • Routing            │
   │  • SecOC              │
   │  • DoIP server        │◀── 100BASE-T1 ── ADAS Domain Ctrlr ─┐
   │  • OTA endpoint       │                                       │
   └──┬───┬───┬───┬───┬───┬┘                                       │
      │   │   │   │   │   │                                        │
   PT-CAN│ HV-CAN│ Chassis-CAN│ Body-CAN│ Diag-CAN│ Infotainment-CAN│
      │   │   │   │   │   │                                        │
      ▼   ▼   ▼   ▼   ▼   ▼                                  Cameras/Radars
    VCU  BMS  ABS  BCM  TBOX  HUD                              (T1 Ethernet)
   MCU-F      EPS  Doors      
   MCU-R      EPB  Lights     
   OBC                          
   DC-DC                        
   TCM-E                        
```

## OBD-II Connector Pinout (Vehicle-Side, J1962)

```
Looking at vehicle DLC face (trapezoidal, narrow side up):

   8  7  6  5  4  3  2  1
  ┌─────────────────────────┐
  │  ·  ·  ·  ·  ·  ·  ·  · │
  │  ·  ·  ·  ·  ·  ·  ·  · │
  └─────────────────────────┘
  16 15 14 13 12 11 10  9

  Pin 4  – Chassis ground
  Pin 5  – Signal ground
  Pin 6  – CAN-H (HS-CAN, 500 kbps)
  Pin 14 – CAN-L (HS-CAN, 500 kbps)
  Pin 16 – +12V battery (always hot)
  Pin 3  – Manufacturer (DoIP TX+ / private CAN-H, gated by gateway)
  Pin 11 – Manufacturer (DoIP RX+ / private CAN-L)
  Pin 12 – Manufacturer (DoIP TX-)
  Pin 13 – Manufacturer (DoIP RX-)
```

## CCS1 Charge Inlet Pinout

```
       ╭────────────╮
       │   ●   ●    │   ← AC L1, AC L2/N (J1772 portion)
       │ ●   ●   ●  │   ← Proximity Pilot, Control Pilot, PE
       │            │
       │   ●   ●    │   ← DC+ , DC− (CCS portion, large pins below)
       ╰────────────╯
   • L1, L2/N  - AC line(s)
   • PP        - Proximity Pilot (resistor-coded current capability)
   • CP        - Control Pilot (PWM duty = available amps)
   • PE        - Protective Earth
   • DC+ / DC- - DC fast charge power
```

## Charge Port Lock Solenoid

- 12 V actuator, ~1.2 A inrush, ~150 mA holding
- Driven by Charge Port Controller (CPC)
- Fault → **B2AAA** (lock motor circuit) or **B2AAB** (temp sensor)

## HVIL Loop (conceptual)

```
   BMS  ─►  HV J-Box ─► OBC ─► DC-DC ─► AC compressor ─► PTC ─► MCU-F ─► MCU-R ─► back to BMS
              (and through MSD socket)
```

Any single break opens the loop → BMS opens contactors and stores a P0A0A/B/C/D code.

## Diagnostic Network Evidence from Autel Scan

The Autel scan archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md) is useful as a real-world module visibility check. It enumerated MCU, BCM, BMS, VCU, ESC, EPS, ADAS, CCU, DDC, MHU, RLS, and XGW from the J1962 diagnostic connector using Autel's VinFast VF e34 profile on a 2024 VF 8.

Repeated current `U110887` entries in MCU, BCM, ESC, CCU, and XGW show that multiple buses/modules reported missing airbag/restraints communication in that scan. XGW also recorded `U117188` as "Chassis CAN - bus off" history and `U012287` as lost communication with the vehicle dynamics control module. These are observed scan facts, not wiring-pin proof; use them to choose inspection areas, then confirm with physical continuity checks and the official wiring diagram.

