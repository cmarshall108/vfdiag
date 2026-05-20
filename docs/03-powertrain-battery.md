# 03 — Powertrain & High-Voltage Battery

## Drive Units

The VF 8 uses two independently controlled permanent-magnet AC synchronous machines (PMSM) — one per axle — coupled to single-speed reduction gearboxes.

### Front e-Axle
- Type: PMSM with hairpin stator windings
- Inverter: SiC/IGBT 3-phase, integrated on top of motor housing
- Reduction ratio: ~9.0 : 1
- Cooling: shared low-temperature loop with rear unit, oil-spray rotor cooling
- Function: primary traction + regen, decoupled in coast for efficiency

### Rear e-Axle
- Type: PMSM, slightly larger rotor than front (Plus trim adds higher peak phase current)
- Reduction ratio: ~9.5 : 1
- Cooling: integrated oil-water heat exchanger
- Function: primary launch torque, dominant in "Sport" mode

### Torque Vectoring
- Software-based front/rear bias via motor torque allocation. No mechanical LSD.

## Inverter / Power Electronics

| Block | Function |
|-------|----------|
| Front MCU (Motor Control Unit) | Drives front motor 3-phase output |
| Rear MCU | Drives rear motor 3-phase output |
| OBC (On-Board Charger) | 11 kW AC→DC, bidirectional-capable |
| DC-DC Converter | HV → 12 V LV, ~2.5 kW continuous |
| HV Junction Box (PDU) | Main contactors, pre-charge resistor, MSD, fuses, IMD |
| PTC Heater / Heat Pump | Cabin + battery conditioning |

All HV components communicate via the **HV CAN bus** under direction of the VCU (Vehicle Control Unit).

## High-Voltage Battery Pack

### Two Battery Pack Variations (US Market)

The VinFast VF 8 transitioned between two distinct high-voltage battery packs, each with different cell manufacturers, operating voltages, capacities, and charging performance:

| Parameter | Samsung SDI Pack (Early / "City Edition") | CATL Pack (2024 MY Extended Range / Standard) |
|-----------|------------------------------------------|---------------------------------------------|
| **Manufacturer** | Samsung SDI | CATL |
| **Cell Type** | Prismatic Lithium NMC | Prismatic High-Density Lithium NMC |
| **Gross Capacity** | ~88.3 kWh | ~92.0 kWh |
| **Usable Capacity** | ~82.0 kWh | ~87.7 kWh |
| **Configuration** | 96S2P | 108S1P |
| **Nominal Voltage** | ~352 V | ~400 V |
| **Voltage Range** | ~280 V to 403 V | ~300 V to 455 V |
| **EPA Range (Eco)** | ~207 mi | ~264 mi |
| **EPA Range (Plus)**| ~191 mi | ~243 mi |

### Construction
- **Samsung SDI Pack**: Configured with 96 series groups of 2 parallel cells (96S2P), resulting in 192 cells total.
- **CATL Pack**: Configured as 108 series cells in a 108S1P configuration, taking advantage of a higher voltage operating window.
- Structural floor-mounted pack, bolted to body via ~30 M12 fasteners.
- Liquid cooling plates between module layers (glycol/water EV coolant).
- Internal **Battery Junction Box (BJB)** houses main +/− contactors, pre-charge contactor & resistor, current shunt, MSD.
- **BMS Master** (battery management system controller) — typically located on top of pack — supervises the cell-monitoring slave boards.
- **Isolation Monitoring Device (IMD)** continuously measures HV-to-chassis leakage resistance; trip threshold ~100 Ω/V.

### Electrical (CATL Pack Specs)
| Parameter | Value |
|-----------|-------|
| Gross capacity | ~92 kWh |
| Usable capacity | ~87.7 kWh |
| Nominal voltage | ~400 V |
| Max charge voltage | ~455 V |
| Min discharge voltage | ~300 V |
| Continuous discharge | ~450 A |
| Peak discharge (10 s) | ~700 A |
| Max DC charge current | ~400 A |

### Thermal Management
- Two independent low-temperature coolant loops (battery loop / power-electronics loop), bridged through a 4-way valve to enable:
  - Battery-only cooling
  - Battery-only heating (via heat pump + PTC)
  - Battery preconditioning before DC fast-charge (driver-selectable in nav)
  - Cabin/battery serial cooling under high load
- A/C system: R-1234yf with electric scroll compressor; integrated heat-pump on 2024 MY

### Manual Service Disconnect (MSD)
- Located under a service cover on the pack (left of center, accessed from underbody)
- Pulling the MSD opens the HV string mid-pack, dropping bus voltage at the contactors to ≤ 60 V
- **Always wait ≥ 5 min** after MSD removal for capacitors to discharge through bleed resistors before opening HV connectors. Verify 0 V with a CAT III meter.

## Observed BMS / HV DTCs from Autel Scan

An Autel MaxiCOM MK900-BT full-system report from a 2024 VF 8, run under Autel's VF e34 profile, logged 11 BMS DTC rows. The current BMS rows were `P180000`, `P124100`, `P183401`, `P124003`, `P0A9500`, and `U014687`; history rows were `U110116`, `P18D000`, `U110117`, `P0ABF86`, and `U012587`. The exact scan is archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md).

Do not treat these as official VinFast definitions. The solid takeaway is that the pack reported active high-voltage/fuse/contactor-related BMS codes and network communication codes during the same scan that also showed missing airbag/restraint messages in other modules. Before any READY attempt, verify physical HV integrity, HVIL closure, 12 V stability, and insulation resistance with proper EV-rated equipment.

## Drive Modes

| Mode | Behavior |
|------|----------|
| Eco | Reduced throttle map, max regen, cabin HVAC capped |
| Normal | Default torque map |
| Sport | Full motor torque, stiffer steering, rear-biased torque split |
| Snow | Reduced torque, gentler regen, looser TCS thresholds |
| Off-Road (where enabled) | Increased ground-clearance behavior (no air suspension), ABS retuned |
| Custom | Driver-defined |

## Regenerative Braking

- 3 selectable levels (Low / Standard / High) via touchscreen
- Not full one-pedal stop — vehicle creeps from low speed
- Blended regen + hydraulic via the eBooster brake system

