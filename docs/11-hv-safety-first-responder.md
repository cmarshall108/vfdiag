# 11 — High-Voltage Safety & First-Responder Guide

> ☠️ The VinFast VF 8 carries a nominal ~355 V DC traction bus capable of delivering several hundred amperes. Contact with energized HV components can be **immediately lethal**. The procedures below summarize public information; always work to the **current VinFast Emergency Response Guide (ERG)** and follow your organization's lockout-tagout (LOTO) policy.

## HV Component Locations

```
                    ┌──────────────────────────────────────┐
                    │  ┌─Charge Port (driver-side rear)    │
                    │  │                                   │
        ┌───────────┼──┴──┐                  ┌─────────────┴─┐
        │  Front     │     │                  │   Rear         │
        │  motor +   │     │   ──CABIN──      │   motor +      │
        │  inverter  │     │                  │   inverter     │
        │  + DC-DC   │     │                  │   + AC compr.  │
        │  + OBC     │     │                  │                │
        │  (HV J-Box)│     │                  │                │
        └────────────┘     │                  └────────────────┘
                           ▼
              ┌────────── HV Battery Pack ──────────┐
              │           (under floor)             │
              │      MSD service plug — center      │
              │      HVIL daisy-chained             │
              └─────────────────────────────────────┘
```

- **Orange cabling** = energized HV (≥ 60 V). Never cut.
- **Blue connectors / shielding** = HV signal / interlock.
- **First responder cut-loops:** typically one under the hood (rearward of 12 V battery) and one in the trunk near the rear inverter. Cutting both disables HV by opening the HVIL.

## HV Disable Procedure (Service)

1. Park on level surface, shift to **P**, engage EPB, chock wheels.
2. Power off via touchscreen / brake-not-pressed key-out, exit, take key fob ≥ 5 m away.
3. Wait ≥ 2 minutes for buses to sleep.
4. Disconnect 12 V negative terminal at under-hood AGM. Tape or cover terminal.
5. Don **Class 0 (1000 V) HV gloves** with leather over-gloves, face shield, arc-rated PPE.
6. Locate the **Manual Service Disconnect (MSD)** on top/side of battery pack:
   - Lift safety latch, pull straight up to remove.
   - Pulling the MSD also opens the HVIL — main contactors will open.
7. Wait **≥ 5 minutes** for HV bus capacitors to bleed.
8. Using a **CAT III 1000 V** rated DMM, verify:
   - Battery + to battery − terminals (at vehicle HV J-box outputs): **≤ 5 V DC**
   - HV + to chassis: **≤ 5 V DC**
   - HV − to chassis: **≤ 5 V DC**
9. Apply LOTO tag. Service may now proceed.

## Re-Energization

1. Verify all HV connectors fully seated and HVIL loops closed.
2. Reinstall MSD, latch secured.
3. Reconnect 12 V negative — verify no sparking (indicates HV pre-charge anomaly or downstream short).
4. Wake vehicle; perform full scan; clear logistical DTCs (U-codes from cycling).
5. Drive cycle and re-scan.

### Post-Collision Diagnostic Hold Points

If a post-collision VF 8 reports active BMS, VCU, ESC, or gateway faults after pyrofuse or restraint work, treat the vehicle as not ready for re-energization until a qualified EV technician verifies the HV circuit. A supplied Autel scan from a 2024 VF 8 showed current faults in BMS, VCU, ESC, CCU, ADAS, RLS, BCM, and XGW after collision repair work; the exact codes are archived in [18-autel-dtc-scan-2026-03-30.md](18-autel-dtc-scan-2026-03-30.md).

Before attempting READY mode, verify at minimum: stable 12 V supply, no unresolved orange-cable damage, no open HVIL loop, no active restraints/airbag communication loss, and no active BMS high-voltage fuse/contactor/isolation fault. Do not use a DTC clear as proof that the HV system is safe.

## First-Responder Quick Reference

| Scenario | Action |
|----------|--------|
| Vehicle on its wheels, no fire | Chock, ignition off, key ≥ 5 m away. Treat as energized. Cut both ERG-marked HVIL loops if extrication required. |
| Fire involving HV battery | **Use copious water** — thermal runaway requires massive heat removal. Plan for >30,000 L over hours. Do not attempt to "smother" with foam alone. Expect re-ignition. |
| Submerged vehicle | Salt water = additional risk of pack short. Avoid contact with water near vehicle until HV verified de-energized by qualified responder. |
| Extrication | Avoid cutting through B-pillar (HV cable runs are routed there for some markets) — refer to color diagram in current ERG. Orange = no-cut zone. |
| Battery damaged / leaking | Establish 15 m perimeter. Vapor may be flammable + toxic (electrolyte → HF, CO). Use SCBA. |

## ERG Distribution

The official **VinFast VF 8 Emergency Response Guide** is published as a PDF to NHTSA and to NFPA-EVSAFE training partners. Download the current version from VinFast's owner portal under *Safety → Emergency Response Guide*.

