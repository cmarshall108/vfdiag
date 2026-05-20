# 2024 VinFast VF 8 — Reference Documentation Set

A consolidated technical reference for the **2024 VinFast VF 8** battery-electric mid-size crossover (D-segment), assembled from manufacturer specifications, NHTSA data, third-party EV databases, and published reviews/teardowns.

> ⚠️ **Disclaimer.** This documentation is compiled from public sources for informational and reference use only. VinFast service procedures, torque specs, high-voltage interlock steps, and DTC interpretations should always be verified against the official VinFast Service Information (VSI) portal, the printed Owner's Manual delivered with the vehicle, and any current Service Bulletins / Recall notices before performing work. Working on a high-voltage EV without proper training and PPE can be fatal.

## Document Index

| # | Document | Scope |
|---|----------|-------|
| 01 | [01-overview.md](docs/01-overview.md) | Model history, trims, pricing, market positioning |
| 02 | [02-specifications.md](docs/02-specifications.md) | Full technical specs, dimensions, weights, capacities |
| 03 | [03-powertrain-battery.md](docs/03-powertrain-battery.md) | Motors, inverter, HV battery, BMS, thermal mgmt |
| 04 | [04-charging.md](docs/04-charging.md) | AC/DC charging, charge port, curve, network compatibility |
| 05 | [05-electrical-hv-system.md](docs/05-electrical-hv-system.md) | HV/LV architecture, ECUs, CAN bus, wiring topology |
| 06 | [06-chassis-suspension-brakes.md](docs/06-chassis-suspension-brakes.md) | Suspension, steering, brakes, wheels/tires |
| 07 | [07-adas-infotainment.md](docs/07-adas-infotainment.md) | ADAS sensors, Smart Services, OTA, infotainment |
| 08 | [08-diagnostics-obd.md](docs/08-diagnostics-obd.md) | OBD-II port, protocols, scan tools, diagnostic workflow |
| 09 | [09-dtc-codes.md](docs/09-dtc-codes.md) | DTC reference (generic SAE J2012 + EV-specific), interpretation guide |
| 10 | [10-maintenance-schedule.md](docs/10-maintenance-schedule.md) | Service intervals, fluids, consumables |
| 11 | [11-hv-safety-first-responder.md](docs/11-hv-safety-first-responder.md) | HV disable procedure, cut-loops, first-responder guide |
| 12 | [12-recalls-tsb-known-issues.md](docs/12-recalls-tsb-known-issues.md) | NHTSA recalls, investigations, common complaints |
| 13 | [13-warranty-support.md](docs/13-warranty-support.md) | Warranty terms, roadside, battery subscription/purchase |
| 14 | [14-wiring-diagrams.md](docs/14-wiring-diagrams.md) | System block diagrams (ASCII), connector pinouts overview |
| 15 | [15-worksheets.md](docs/15-worksheets.md) | Printable pre-delivery, service, and HV-disable worksheets |
| 16 | [16-sources.md](docs/16-sources.md) | Bibliography and source links |
| 17 | [17-engineering-menu-totp.md](docs/17-engineering-menu-totp.md) | Infotainment Engineering Menu, Android Developer Options, and Dynamic TOTP algorithm |
| 18 | [18-autel-dtc-scan-2026-03-30.md](docs/18-autel-dtc-scan-2026-03-30.md) | Exact Autel scan appendix for a 2024 VF 8 read under the VF e34 profile |
| 19 | [19-diagnostic-programming-notes.md](docs/19-diagnostic-programming-notes.md) | VinFast-specific diagnostic access, J2534 limits, programming status, and tool routing |

## Quick Facts

- **Class:** Mid-size crossover SUV (D-segment), 5-door, dual-motor AWD (US-spec)
- **Platform:** VinFast VMG-C/D (formerly known as VF e35 / VF 32 in dev)
- **Powertrain (US 2024):** Dual permanent-magnet AC synchronous motors, AWD
  - **Eco:** 348 hp (260 kW) / 368 lb-ft (499 N·m)
  - **Plus:** 402 hp (300 kW) / 457 lb-ft (620 N·m)
- **Battery:** ~87.7 kWh usable (90 kWh gross), Samsung SDI NMC, ~400 V architecture
- **Charging:** 11 kW AC (J1772), ~150 kW DC peak (CCS1 in NA)
- **Range (EPA, 2024 MY):** ~207 mi (Eco) / ~191 mi (Plus) — corrected EPA figures
- **0–60 mph:** ~5.5 s (Plus), ~5.8 s (Eco)
- **Designer:** Pininfarina (exterior); David Lyon (VinFast design dir.)
- **Assembly:** Hai Phong, Vietnam (Cát Hải plant)
- **Warranty:** 10-year / 125,000-mile limited vehicle warranty; 10-year battery warranty (US)


## Mini-VCI / J2534 Windows Setup

The Python diagnostic helper under [tools/vf_obd](tools/vf_obd) can talk through a Toyota Mini-VCI / XHorse-style J2534 cable, but that cable requires a Windows driver stack before `vf_obd.py` can load it.

### Install Requirements

- **Windows PC**: J2534 vendor DLLs are Windows-only.
- **32-bit Python 3.9+**: the Toyota/XHorse Mini-VCI driver exposes `MVCI32.dll`, which cannot be loaded by 64-bit Python. Use `py -3-32` when running the tool.
- **FTDI USB driver**: install the official FTDI VCP driver if Windows does not enumerate the cable cleanly in Device Manager.
- **Toyota MVCI / XHorse J2534 driver**: installs the PassThru DLL, usually named `MVCI32.dll`.

Common DLL locations:

```text
C:\Program Files (x86)\XHorse Electronics\MVCI Driver for TOYOTA TIS\MVCI32.dll
C:\Program Files\XHorse Electronics\MVCI Driver for TOYOTA TIS\MVCI32.dll
C:\Program Files (x86)\Toyota\MVCI\MVCI32.dll
C:\Program Files\Toyota\MVCI\MVCI32.dll
```

### Registry Discovery

For auto-discovery, the MVCI installer should register a J2534 entry under one of these keys:

```text
HKEY_LOCAL_MACHINE\SOFTWARE\PassThruSupport.04.04
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\PassThruSupport.04.04
```

The device entry should include a `FunctionLibrary` value pointing to `MVCI32.dll`. To automate this, you can merge our pre-configured registry script [tools/vf_obd/register_mvci32.reg](tools/vf_obd/register_mvci32.reg), which registers the standard drivers under BOTH WOW6432Node and standard hives.

Alternatively, you can manually add a registry entry like this, adjusting the path if needed:

```registry
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\PassThruSupport.04.04\XHorse - MVCI]
"Name"="XHorse - MVCI"
"FunctionLibrary"="C:\\Program Files (x86)\\XHorse Electronics\\MVCI Driver for TOYOTA TIS\\MVCI32.dll"
"Vendor"="XHorse Directive"
"ConfigApplication"=""
"CAN"=dword:00000001
"ISO15765"=dword:00000001
"ISO14230"=dword:00000001
"ISO9141"=dword:00000001
"J1850VPW"=dword:00000001
```

### Verify the Cable

From a Windows command prompt inside `tools\vf_obd`:

```cmd
py -3-32 vf_obd.py doctor
```

If the DLL is not auto-discovered, pass it explicitly:

```cmd
py -3-32 vf_obd.py doctor --dll "C:\Program Files (x86)\XHorse Electronics\MVCI Driver for TOYOTA TIS\MVCI32.dll"
```

Expected result: the tool loads the DLL, opens the device, prints firmware/API versions when available, and reports OBD battery voltage. A `WinError 193` or "not a valid Win32 application" error means 64-bit Python is being used with a 32-bit DLL.

### Driver Sources

- Avoid running bundled Mini-VCI CDs from unknown sellers; they are commonly flagged by antivirus tools.
- FTDI VCP driver: https://ftdichip.com/drivers/vcp-drivers/
- Bosch J2534 driver index: https://www.boschdiagnostics.com/J2534drivers