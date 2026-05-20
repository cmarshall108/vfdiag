# vf-obd — Generic OBD-II reader for VinFast Vehicles (VF 8 / VF 9)

A small, **honest-about-its-limits** Python tool that talks to your VinFast VF 8 / VF 9 through a
**Mini-VCI J2534** cable (Amazon ASIN B0DXB8N5KH) on **Windows**, and supports:

- Reading the VIN (OBD-II Mode 09 PID 02)
- Reading stored DTCs (**Mode 03**)
- Reading pending DTCs (**Mode 07**)
- Reading permanent DTCs (**Mode 0A**)
- Clearing DTCs and freeze-frame data (**Mode 04**)
- Scanning responsive ECU names & calibration IDs/software versions (**Mode 09 PIDs 0A & 04**)
- Monitoring standard OBD live parameters (like control module voltage, SoC %, and ambient temp) (**Mode 01**)
- Passively sniffing/monitoring raw CAN traffic on pins 6/14 (with CSV logging) — useful for observing diagnostics during a service session
- Utility script to derive Engineering Mode Dynamic TOTP credentials using standard dynamic HMAC-SHA256 derivation over custom private seeds
That's it. No module coding, no SecOC authentication bypassing, no direct command-based clearing of crash flags.
You asked for "DTCs from each module + clear" — see the **honest scope** section before you
use this.

---

## ⚠️ Honest scope — read this first

This tool talks to the **emissions-legislated OBD-II bus only** (ISO 15765-4 CAN @ 500 kbps,
broadcast on functional address `0x7DF`, responders `0x7E8–0x7EF`).

On the VF 8 / VF 9, that bus is the legally mandated CAN segment that exits the OBD-II J1962
connector at pins 6/14. Anything more interesting (BMS cell data, MCU phase currents,
ADAS calibration, ABS module DTCs, ECU coding) sits **behind the VinFast Central Gateway**,
which enforces **SecOC** authentication. We cannot reach those modules with a Mini-VCI
and no credentials. Period. Anyone telling you otherwise is selling you something.

What this means in practice:

- On a **healthy** BEV, this tool will probably tell you **"no DTCs stored"** and that
  will be correct — the emissions-bus side of an EV is very sparse.
- If the dash shows an "EV system check" warning but this tool reports nothing, that's
  expected. The fault is set in a gateway-protected module (BMS/MCU/ABS/etc.) and
  is not visible on the legislated bus.
- For full per-module scanning you need either (a) a VinFast dealer scan tool, or
  (b) a raw-CAN device (CANable Pro / Macchina M2) and a UDS scanner — both outside
  the scope of this tool.

See [../../docs/08-diagnostics-obd.md](../../docs/08-diagnostics-obd.md) for the full
picture of what's reachable on this car.
For the consolidated programming/security-access boundary, see
[../../docs/19-diagnostic-programming-notes.md](../../docs/19-diagnostic-programming-notes.md).

---

## ⚠️ Hardware honesty — the Mini-VCI cable

The Amazon listing for this cable is keyword-stuffed. The actual product is a clone of
the **Toyota MVCI (Mongoose) J2534 pass-thru cable**. Key facts:

- It is **NOT an ELM327** and exposes no serial AT-command interface.
- It is a **J2534-1 pass-thru device** — software talks to it by loading a vendor DLL
  (`MVCI32.dll`) and calling the SAE J2534 API.
- **Windows only** (XP/7/10/11). Does not work on macOS or Linux.
- The **included CD has been reported to contain malware** by an Amazon reviewer.
  **Do not run the included CD.** Get the MVCI driver from a clean source — see below.
- The cable's *electrical* interface (CAN-H pin 6, CAN-L pin 14, +12V pin 16,
  GND pins 4/5) and chipset *do* support ISO 15765-4 CAN at 500 kbps, so it will
  physically work on the VF 8 & VF 9 OBD bus.

---

## Requirements

- A **Windows** machine (this will not run on macOS/Linux — the J2534 DLL is Windows-only).
- **Python 3.9 or newer**, 32-bit, x86. Yes, 32-bit — the Toyota MVCI driver ships
  `MVCI32.dll` only. A 64-bit Python cannot load a 32-bit DLL.
  - Download: https://www.python.org/downloads/windows/ → "Windows installer (32-bit)".
- The **Toyota MVCI driver** installed (provides `MVCI32.dll`).
  - Cleanest source: install **Toyota Techstream** from a known-good source; it bundles
    the MVCI driver as a separate MSI (`MVCI Driver for TOYOTA.msi`).
  - Typical install path:
    `C:\Program Files (x86)\XHorse Electronics\MVCI Driver for TOYOTA TIS\MVCI32.dll`
    or
    `C:\Program Files (x86)\Toyota\MVCI\MVCI32.dll`
- For CLI usage, zero Python package dependencies are required (pure standard library).
- To launch the graphical user interface, the `PyQt5` framework is required.

---

## Setup

1. Plug the Mini-VCI into a USB port. Windows should enumerate it as a serial /
   USB device. If a yellow bang appears in Device Manager, install the FTDI / MVCI
   driver from the Toyota MSI (not from the included CD).
2. Merge the J2534 registry settings to automate driver auto-discovery. You can do this easily by double-clicking the raw registry file [tools/vf_obd/register_mvci32.reg](register_mvci32.reg) included in this directory. 
   - Note: If your `MVCI32.dll` driver is installed at a non-standard path, open that `.reg` file in a text editor like Notepad, adjust the `"FunctionLibrary"` fields to match your physical folder structure, save, and then execute it.
3. Install PyQt5 package if using the dealer GUI replacement tool:
   ```cmd
   pip install PyQt5
   ```
4. Plug the cable's OBD-II end into the vehicle's J1962 port (driver-side dash, left of
   steering column).
5. **Wake the car**: press the brake pedal once, or open the driver door. Most modules require a wake event before they will reply on the OBD bus.
6. From a Windows command prompt:

   - **For GUI Launcher (Recommended - Dark Mode Dealer Tool Replacement)**:
     ```cmd
     cd path\to\vf-obd
     py -3-32 vf_gui.py
     ```
   
   - **For CLI Launcher**:
     ```cmd
     cd path\to\vf-obd
     py -3-32 vf_obd.py doctor
     ```

   This locates the DLL, opens the device, and prints firmware/version info. Run this
   before anything else.

---

## Usage

All commands accept `--dll PATH` to override DLL auto-discovery.

```cmd
py -3-32 vf_obd.py doctor                      # verify driver & cable, no car needed
py -3-32 vf_obd.py vin                         # read VIN
py -3-32 vf_obd.py scan                        # read stored + pending + permanent DTCs
py -3-32 vf_obd.py scan --mode 03              # stored only
py -3-32 vf_obd.py scan --mode 07              # pending only
py -3-32 vf_obd.py scan --mode 0A              # permanent only
py -3-32 vf_obd.py clear                       # clear functional broadcast (Mode 04) - prompts for confirmation
py -3-32 vf_obd.py clear --yes                 # skip functional clear prompt
py -3-32 vf_obd.py clear-physical              # sequentially target physical clear to individual modules (0x7E0..0x7E7)
py -3-32 vf_obd.py clear-physical --yes        # skip physical clear prompt
py -3-32 vf_obd.py ecu                         # scan responsive ECU Names & Calibration IDs/Versions
py -3-32 vf_obd.py info                        # query deep module parameters (VIN, Name, CALID, CVN, Serials)
py -3-32 vf_obd.py hvil                        # start live 12V/HV battery and pre-charge stability monitor
py -3-32 vf_obd.py uds-discover                # scan for open physical UDS Sessions and Security Access (Seed requests)
py -3-32 vf_obd.py can-watch 0x7E8             # track a single CAN ID payload in-place, highlighting any byte changes (*)
py -3-32 vf_obd.py live                        # monitor standard live sensor parameters in real-time
py -3-32 vf_obd.py live --once                 # take a single live snapshot of sensor data and exit
py -3-32 vf_obd.py monitor                     # start passive CAN sniffer (wildcard filter on pins 6/14)
py -3-32 vf_obd.py monitor --id 0x7E8          # display ONLY target messages (e.g. from ECU 0x7E8)
py -3-32 vf_obd.py monitor --exclude-id 0x100  # suppress generic high-frequency background traffic
py -3-32 vf_obd.py monitor --out log.csv       # sniff and save all received traffic to a CSV log
```

### Automatic Session Logging

Every subcommand execution automatically generates a comprehensive date-stamped session log recording standard output, errors, full diagnostic events, and J2534 traffic details to help independent rebuilders and mechanics trace vehicle status step-by-step.

Logs are written dynamically to the [tools/vf_obd/logs/](tools/vf_obd/logs) directory in the workspace:

- File format: `session_YYYYMMDD_HHMMSS_<command>.log`
- Contains details such as connection metadata, timestamps, exact bytes sent and received, and any warning indicators.

### Dynamic TOTP Password Generation

We've provided a helper utility to calculate the dynamic engineering passcode targeting the customizable variables:

```cmd
py -3-32 totp.py --vin LFGXXXXXXXXXXXXXX --secret <your_hex_or_ascii_seed>
```

Add `--step <seconds>` to override target time windows (default is 3600), or `--digits 8` if your software generation targets 8-digit validation layers.

Optional flags:

- `--dll C:\path\to\MVCI32.dll` — explicit DLL path
- `--timeout-ms 2000` — per-message read timeout (default 2000)
- `-v` / `--verbose` — print raw J2534 traffic for debugging

---

## What the tool reports

For each DTC found, the tool prints:

```
P0A0D  [stored]   raw bytes: 0A 0D
```

A short description is shown for codes that are defined in **SAE J2012** or in the
local VinFast-specific dictionary built from observed scan evidence and working notes.
For manufacturer-specific codes not in the local dictionary, the tool prints no
description rather than inventing one.

Autel-style 7-character DTCs such as `U110887` should be read as base DTC plus a
2-character symptom byte: `U1108` + suffix `87`. The current Python decoder maps the
5-character base code; keep the suffix in your scan notes because it can change the
fault subtype.

A nominally healthy VF 8 will typically print:

```
Mode 03 (stored)    : no DTCs
Mode 07 (pending)   : no DTCs
Mode 0A (permanent) : no DTCs
```

That is a real, useful result. It tells you the emissions-legislated bus has nothing
to report. If a fault light is on and this tool says "no DTCs", the fault lives
behind the gateway and you need a real OEM-coverage scan tool.

---

## Safety notes

- **Clearing DTCs** with Mode 04 erases stored codes, freeze-frame data, and
  emissions-monitor readiness on whatever module(s) respond to functional `0x7DF`.
  On a BEV that's typically the VCU / motor controller side of the gateway. It will
  **not** touch BMS-internal data, HV-pack history, or ADAS calibration (those are
  on the gated bus). Still — clear only when you know why.
- Do not leave the Mini-VCI plugged in continuously when not in use. The cable keeps
  the OBD port and gateway awake and **will drain the 12 V battery over a few days**.
- This tool sends nothing more than the four request modes documented above.
  No coding, no security access, no writes other than Mode 04.

---

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| `doctor` fails with `WinError 193` or `not a valid Win32 application` | You're running 64-bit Python; install **32-bit Python**. |
| `doctor` fails with `FileNotFoundError: MVCI32.dll` | MVCI driver not installed, or in a non-standard path; pass `--dll`. |
| `doctor` opens device but `scan` times out on every read | Car not awake. Press brake pedal or open driver door, retry. |
| `scan` returns nothing but car has a fault light | Expected — fault is behind the gateway and not visible on legislated OBD bus. |
| Random `ERR_TIMEOUT` mid-scan | Cable connection flaky (it's a $33 clone). Re-seat the J1962 plug. |
| Antivirus quarantines the included CD | Believe your antivirus. Do not run that CD. |

---

## Files

- `vf8_obd.py` — CLI entry point
- `j2534.py` — minimal `ctypes` binding for the SAE J2534-1 API subset we use
- `dtc.py` — DTC byte → SAE-J2012 code-string decoder and generic-code dictionary
