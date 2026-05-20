"""
vf8_obd.py -- generic OBD-II reader / clearer for the VinFast VF 8 via Mini-VCI.

Subcommands:
    doctor   verify J2534 DLL loads and the cable is talking to us
    vin      read VIN via OBD-II Mode 09 PID 02
    scan     read DTCs via Mode 03 (stored), 07 (pending), 0A (permanent)
    clear    clear DTCs via Mode 04 (prompts for confirmation)

Honest scope:
    Talks only to the emissions-legislated bus (ISO 15765-4 CAN @ 500 kbps,
    broadcast 0x7DF, responders 0x7E8..0x7EF).  Cannot reach modules behind
    the VinFast central gateway (BMS, MCU internals, ADAS, ABS, etc.).

Windows-only.  Requires 32-bit Python because the Toyota MVCI driver ships
MVCI32.dll only.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import dtc as dtc_mod
import j2534

# --- Address plan for ISO 15765-4 OBD-II (per SAE J1979 / ISO 15031-5) --------

OBD_FUNCTIONAL_REQ = 0x7DF                       # broadcast request
OBD_PHYSICAL_REQ_BASE = 0x7E0                    # physical req addrs 0x7E0..0x7E7
OBD_RESP_BASE = 0x7E8                            # resp addrs       0x7E8..0x7EF
OBD_RESP_RANGE = range(OBD_RESP_BASE, OBD_RESP_BASE + 8)

# Per-mode response SID (request SID + 0x40)
SID_RESP = {0x01: 0x41, 0x03: 0x43, 0x04: 0x44, 0x07: 0x47, 0x09: 0x49, 0x0A: 0x4A}


# --- Connection helpers --------------------------------------------------------

def _resolve_dll(arg_dll: Optional[str]) -> str:
    if arg_dll:
        if not os.path.isfile(arg_dll):
            sys.exit(f"DLL not found: {arg_dll}")
        return arg_dll
    env = os.environ.get("MVCI_DLL")
    if env:
        if not os.path.isfile(env):
            sys.exit(f"MVCI_DLL points to a missing file: {env}")
        return env
    found = j2534.find_default_dll()
    if not found:
        sys.exit(
            "Could not auto-locate a J2534 DLL.\n"
            "  - Install the Toyota MVCI driver (bundled with Techstream).\n"
            "  - Or pass --dll C:\\path\\to\\MVCI32.dll\n"
            "  - Or set the MVCI_DLL environment variable.\n"
            "Detected devices (from registry):\n"
            + "\n".join(f"  {n} -> {p}" for n, p in j2534.discover_j2534_devices())
        )
    return found


def _open_obd_channel(j: j2534.J2534, verbose: bool = False) -> int:
    """Connect ISO 15765 @ 500k and install flow-control filters for 0x7E8..0x7EF."""
    channel = j.connect(j2534.ISO15765, flags=0, baud=500000)
    if verbose:
        print(f"  channel={channel}, ISO15765 @ 500000 baud")
    j.ioctl_clear_msg_filters(channel)
    j.ioctl_clear_rx_buffer(channel)

    # One flow-control filter per responder; FC frames are sent on the
    # matching physical request address (0x7E8 -> FC on 0x7E0, etc.).
    mask = (0xFFFFFFFF).to_bytes(4, "big")
    for offset in range(8):
        resp = OBD_RESP_BASE + offset
        req = OBD_PHYSICAL_REQ_BASE + offset
        fid = j.start_flow_control_filter(
            channel,
            mask=mask,
            pattern=resp.to_bytes(4, "big"),
            flow_control=req.to_bytes(4, "big"),
        )
        if verbose:
            print(f"  filter[{fid}]: rx=0x{resp:03X}  fc-tx=0x{req:03X}")
    return channel


def _request_and_collect(
    j: j2534.J2534,
    channel: int,
    can_id: int,
    payload: bytes,
    expected_resp_sid: int,
    timeout_ms: int,
    verbose: bool,
) -> Dict[int, bytes]:
    """Send one OBD request, collect responses keyed by responder CAN ID.

    Reads until the bus goes quiet for one full timeout window.  Returns a dict
    mapping CAN response ID -> first valid response payload.
    """
    j.ioctl_clear_rx_buffer(channel)
    if verbose:
        print(f"  TX 0x{can_id:03X}: {payload.hex(' ').upper()}")
    j.write(channel, can_id, payload, timeout_ms=timeout_ms)

    responses: Dict[int, bytes] = {}
    deadline = time.monotonic() + (timeout_ms / 1000.0) * 1.5
    while time.monotonic() < deadline:
        msgs = j.read(channel, max_msgs=8, timeout_ms=timeout_ms)
        if not msgs:
            # nothing more arrived; if we already have any responses, stop early
            if responses:
                break
            continue
        for cid, data, rx_status in msgs:
            if verbose:
                print(f"  RX 0x{cid:03X} [{rx_status:08X}]: {data.hex(' ').upper()}")
            if cid not in OBD_RESP_RANGE:
                continue
            if not data or data[0] != expected_resp_sid:
                continue
            if cid not in responses:
                responses[cid] = data
        # short grace window for more responses from other ECUs
        deadline = max(deadline, time.monotonic() + 0.2)
    return responses


# --- OBD-II response parsing ---------------------------------------------------

def _parse_dtc_payload(payload: bytes, expected_sid_resp: int) -> List[Tuple[int, int]]:
    """Return list of (b1, b2) DTC byte pairs from a Mode 03/07/0A response."""
    if not payload or payload[0] != expected_sid_resp:
        return []
    rest = payload[1:]
    if not rest:
        return []

    # Modern (ISO 15031-5): first byte after SID is DTC count.
    count = rest[0]
    if count == 0 and len(rest) == 1:
        return []
    if 1 + count * 2 == len(rest):
        body = rest[1:]
    else:
        # Fallback: legacy SAE J1979 layout -- pairs immediately after SID.
        body = rest

    pairs: List[Tuple[int, int]] = []
    for i in range(0, len(body) - (len(body) % 2), 2):
        b1, b2 = body[i], body[i + 1]
        if b1 == 0 and b2 == 0:        # 00 00 = no-DTC padding
            continue
        pairs.append((b1, b2))
    return pairs


def _parse_vin_payload(payload: bytes) -> Optional[str]:
    """Extract a 17-character ASCII VIN from a Mode 09 PID 02 response."""
    # Response framing: 49 02 [count] <17 VIN bytes>  (modern)
    #              or:  49 02 <17 VIN bytes>          (legacy)
    if len(payload) < 3 or payload[0] != 0x49 or payload[1] != 0x02:
        return None
    body = payload[2:]
    # Skip optional 1-byte item count if present
    if len(body) == 18 and body[0] in (0x01, 0x02):
        body = body[1:]
    if len(body) < 17:
        return None
    vin_bytes = body[:17]
    try:
        vin = vin_bytes.decode("ascii")
    except UnicodeDecodeError:
        return None
    if not all(ch.isalnum() for ch in vin):
        return None
    return vin


def _parse_ecu_name_payload(payload: bytes) -> Optional[str]:
    """Extract ECU name (up to 20 ASCII chars) from a Mode 09 PID 0A response."""
    # Response framing: 49 0A <optional count-byte> <up to 20 ASCII bytes>
    if len(payload) < 3 or payload[0] != 0x49 or payload[1] != 0x0A:
        return None
    body = payload[2:]
    if len(body) > 0 and body[0] == 0x01:
        body = body[1:]
    chars = []
    for b in body:
        if 32 <= b <= 126:
            chars.append(chr(b))
        elif b == 0:
            break
    res = "".join(chars).strip()
    return res if res else None


def _parse_calid_payload(payload: bytes) -> List[str]:
    """Extract list of Calibration IDs from a Mode 09 PID 04 response."""
    # Response framing: 49 04 <count-byte> <16 bytes ASCII> ... (modern) or <16 bytes ASCII> (legacy)
    if len(payload) < 3 or payload[0] != 0x49 or payload[1] != 0x04:
        return []
    first_char = payload[2]
    if 32 <= first_char <= 126:
        body = payload[2:]
        count = 1
    else:
        body = payload[3:]
        count = first_char
    calids = []
    for idx in range(count):
        chunk = body[idx * 16 : (idx + 1) * 16]
        if not chunk:
            break
        chars = []
        for b in chunk:
            if 32 <= b <= 126 and b != 0:
                chars.append(chr(b))
        calid_str = "".join(chars).strip()
        if calid_str:
            calids.append(calid_str)
    return calids


# --- Subcommands ---------------------------------------------------------------

def cmd_doctor(args: argparse.Namespace) -> int:
    dll = _resolve_dll(args.dll)
    print(f"DLL              : {dll}")
    devs = j2534.discover_j2534_devices()
    if devs:
        print("Registered J2534 devices:")
        for n, p in devs:
            print(f"  - {n}  ->  {p}")
    else:
        print("Registered J2534 devices: (none found in registry)")
    print()

    try:
        d = j2534.J2534(dll)
    except Exception as exc:
        print(f"FAIL: could not load DLL: {exc}")
        return 2

    try:
        d.open()
    except j2534.J2534Error as exc:
        print(f"FAIL: PassThruOpen: {exc}")
        if exc.code == j2534.ERR_DEVICE_NOT_CONNECTED:
            print("\n💡 Diagnosing ERR_DEVICE_NOT_CONNECTED (0x08):")
            print("  - The J2534 DLL loaded, but it cannot detect the physical cable over USB.")
            print("  - Check 1: Is the Mini-VCI/XHorse hardware plugged securely into a USB port?")
            print("  - Check 2: Try a different USB port on your PC (prefer direct USB 2.0 physical ports instead of third-party hubs).")
            print("  - Check 3: If running inside a Virtual Machine (VMware, VirtualBox, Parallels), verify the USB device")
            print("             is passed through/connected to the Windows guest OS rather than the host macOS.")
            print("  - Check 4: Open Device Manager (devmgmt.msc). Is there a yellow exclamation triangle (⚠️) on a USB device?")
            print("             If so, download and install the official VCP driver from: https://ftdichip.com/drivers/vcp-drivers/")
        return 2
    except Exception as exc:
        print(f"FAIL: PassThruOpen: {exc}")
        return 2

    try:
        try:
            fw, dll_ver, api_ver = d.read_version()
            print(f"Firmware version : {fw}")
            print(f"DLL version      : {dll_ver}")
            print(f"API version      : {api_ver}")
        except j2534.J2534Error as exc:
            print(f"WARN: PassThruReadVersion failed: {exc}")
        try:
            mv = d.read_vbatt_mv()
            print(f"Battery at OBD   : {mv/1000:.2f} V")
            if mv < 11000:
                print("  (note: < 11 V -- car may not be awake, or cable not fully seated)")
        except j2534.J2534Error as exc:
            print(f"WARN: READ_VBATT failed: {exc}")
    finally:
        d.close()

    print("\nOK: device opened and closed cleanly.")
    return 0


def cmd_vin(args: argparse.Namespace) -> int:
    dll = _resolve_dll(args.dll)
    with j2534.J2534(dll) as d:
        channel = _open_obd_channel(d, verbose=args.verbose)
        try:
            responses = _request_and_collect(
                d, channel,
                can_id=OBD_FUNCTIONAL_REQ,
                payload=bytes([0x09, 0x02]),
                expected_resp_sid=SID_RESP[0x09],
                timeout_ms=args.timeout_ms,
                verbose=args.verbose,
            )
        finally:
            d.disconnect(channel)

    if not responses:
        print("No response to Mode 09 PID 02.")
        print("  - Is the car awake?  Press the brake pedal or open the driver door, then retry.")
        print("  - Is the cable fully seated in the OBD port?")
        return 1

    for cid, payload in sorted(responses.items()):
        vin = _parse_vin_payload(payload)
        if vin:
            print(f"VIN (from 0x{cid:03X}): {vin}")
        else:
            print(f"0x{cid:03X}: unexpected payload {payload.hex(' ').upper()}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    modes = args.modes if args.modes else [0x03, 0x07, 0x0A]
    dll = _resolve_dll(args.dll)
    total_dtcs = 0

    with j2534.J2534(dll) as d:
        channel = _open_obd_channel(d, verbose=args.verbose)
        try:
            for mode in modes:
                label = {0x03: "stored", 0x07: "pending", 0x0A: "permanent"}[mode]
                print(f"\nMode 0x{mode:02X} ({label}):")
                responses = _request_and_collect(
                    d, channel,
                    can_id=OBD_FUNCTIONAL_REQ,
                    payload=bytes([mode]),
                    expected_resp_sid=SID_RESP[mode],
                    timeout_ms=args.timeout_ms,
                    verbose=args.verbose,
                )
                if not responses:
                    print("  (no module responded)")
                    continue
                for cid, payload in sorted(responses.items()):
                    pairs = _parse_dtc_payload(payload, SID_RESP[mode])
                    if not pairs:
                        print(f"  0x{cid:03X}: no DTCs")
                        continue
                    print(f"  0x{cid:03X}: {len(pairs)} DTC(s)")
                    for b1, b2 in pairs:
                        code = dtc_mod.bytes_to_dtc(b1, b2)
                        desc = dtc_mod.describe(code)
                        if desc:
                            print(f"    {code}  -- {desc}  (raw {b1:02X} {b2:02X})")
                        elif dtc_mod.is_generic(code):
                            print(f"    {code}  (generic; description not in local table; raw {b1:02X} {b2:02X})")
                        else:
                            print(f"    {code}  (manufacturer-specific -- no public description; raw {b1:02X} {b2:02X})")
                        total_dtcs += 1
        finally:
            d.disconnect(channel)

    print(f"\nTotal DTCs found: {total_dtcs}")
    if total_dtcs == 0:
        print(
            "\nNote: a healthy BEV typically shows zero codes on the OBD-II legislated bus.\n"
            "If a warning is on in the car but this tool finds nothing, the fault lives\n"
            "behind the gateway and is not reachable with this hardware."
        )
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    if not args.yes:
        print("This will issue OBD-II Mode 04 to functional address 0x7DF.")
        print("All modules that listen on 0x7DF will clear stored DTCs,")
        print("freeze-frame data, and emissions-monitor readiness status.")
        print("It will NOT touch BMS, ADAS, or other gateway-protected data.")
        confirm = input('Type "YES" to proceed: ').strip()
        if confirm != "YES":
            print("Aborted.")
            return 1

    dll = _resolve_dll(args.dll)
    with j2534.J2534(dll) as d:
        channel = _open_obd_channel(d, verbose=args.verbose)
        try:
            responses = _request_and_collect(
                d, channel,
                can_id=OBD_FUNCTIONAL_REQ,
                payload=bytes([0x04]),
                expected_resp_sid=SID_RESP[0x04],
                timeout_ms=args.timeout_ms,
                verbose=args.verbose,
            )
        finally:
            d.disconnect(channel)

    if not responses:
        print("No module acknowledged Mode 04.")
        print("  - Is the car awake?  Press brake or open driver door, then retry.")
        return 1
    for cid in sorted(responses):
        print(f"  0x{cid:03X}: cleared (positive response 0x44)")
    return 0


def cmd_ecu(args: argparse.Namespace) -> int:
    dll = _resolve_dll(args.dll)
    print("Scanning for responsive modules (ECUs) & metadata...")
    print("Functional Broadcast to 0x7DF...")

    with j2534.J2534(dll) as d:
        channel = _open_obd_channel(d, verbose=args.verbose)
        try:
            # First, read ECU Names (Mode 09 PID 0A)
            print("\nQuerying Mode 09 PID 0A (ECU Names):")
            names_resp = _request_and_collect(
                d, channel,
                can_id=OBD_FUNCTIONAL_REQ,
                payload=bytes([0x09, 0x0A]),
                expected_resp_sid=SID_RESP[0x09],
                timeout_ms=args.timeout_ms,
                verbose=args.verbose,
            )
            ecu_names: Dict[int, str] = {}
            if not names_resp:
                print("  (no ECU names returned; optional PID)")
            else:
                for cid, payload in sorted(names_resp.items()):
                    name = _parse_ecu_name_payload(payload)
                    if name:
                        ecu_names[cid] = name
                        print(f"  0x{cid:03X} -> Name: {name}")
                    else:
                        print(f"  0x{cid:03X} -> Raw response (non-ASCII or unparsed): {payload.hex(' ').upper()}")

            # Second, read Calibration IDs (Mode 09 PID 04)
            print("\nQuerying Mode 09 PID 04 (Calibration IDs / Software Versions):")
            calid_resp = _request_and_collect(
                d, channel,
                can_id=OBD_FUNCTIONAL_REQ,
                payload=bytes([0x09, 0x04]),
                expected_resp_sid=SID_RESP[0x09],
                timeout_ms=args.timeout_ms,
                verbose=args.verbose,
            )
            if not calid_resp:
                print("  (no Calibration IDs returned)")
            else:
                for cid, payload in sorted(calid_resp.items()):
                    calids = _parse_calid_payload(payload)
                    name_str = f" [{ecu_names[cid]}]" if cid in ecu_names else ""
                    if calids:
                        print(f"  0x{cid:03X}{name_str}:")
                        for idx, cal in enumerate(calids):
                            print(f"    - CALID {idx+1}: {cal}")
                    else:
                        print(f"  0x{cid:03X}{name_str}: Raw response {payload.hex(' ').upper()}")

        finally:
            d.disconnect(channel)
    return 0


def cmd_live(args: argparse.Namespace) -> int:
    dll = _resolve_dll(args.dll)
    
    # We will poll these PIDs:
    # PID -> (length, lambda, name)
    pids_to_poll = {
        0x42: (4, lambda d: f"{(d[0]*256 + d[1])/1000:.2f} V", "Control Module Voltage (12V)"),
        0x46: (3, lambda d: f"{d[0] - 40} \u00b0C", "Ambient Air Temperature"),
        0x1F: (4, lambda d: f"{d[0]*256 + d[1]} sec", "ECU Run Time"),
        0x5B: (3, lambda d: f"{d[0]*100/255:.1f} %", "HV Battery Remaining Charge (SoC)"),
        0x0D: (3, lambda d: f"{d[0]} km/h", "Vehicle Speed"),
    }

    print("Starting Live OBD-II Parameter Monitor...")
    print("Queries are sent functional on 0x7DF. Press Ctrl+C to stop.\n")

    with j2534.J2534(dll) as d:
        channel = _open_obd_channel(d, verbose=args.verbose)
        try:
            while True:
                lines = []
                for pid, (min_len, parser, label) in pids_to_poll.items():
                    responses = _request_and_collect(
                        d, channel,
                        can_id=OBD_FUNCTIONAL_REQ,
                        payload=bytes([0x01, pid]),
                        expected_resp_sid=SID_RESP[0x01],
                        timeout_ms=args.timeout_ms,
                        verbose=args.verbose,
                    )
                    
                    if not responses:
                        continue
                    
                    for cid, payload in sorted(responses.items()):
                        if len(payload) >= min_len and payload[0] == 0x41 and payload[1] == pid:
                            data_bytes = payload[2:]
                            try:
                                val_str = parser(data_bytes)
                                lines.append(f"  0x{cid:03X} | {label:<35} | {val_str}")
                            except Exception:
                                pass
                
                if lines:
                    timestamp = time.strftime('%H:%M:%S')
                    print(f"--- Live Data Snapshot @ {timestamp} ---")
                    print("\n".join(lines))
                    print()
                else:
                    print("No parameters returned. Is the ignition on?")
                
                if args.once:
                    break
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nStopped monitor.")
        finally:
            d.disconnect(channel)
    return 0


def cmd_monitor(args: argparse.Namespace) -> int:
    dll = _resolve_dll(args.dll)
    
    out_file = None
    if args.out:
        try:
            out_file = open(args.out, "a", encoding="utf-8")
            print(f"Logging messages passively to: {args.out}")
        except Exception as exc:
            sys.exit(f"Failed to open log file: {exc}")

    print("Opening raw CAN monitoring channel at 500 kbps...")
    print("Passive sniffing mode. Wildcard filter installed. Press Ctrl+C to stop.\n")

    with j2534.J2534(dll) as d:
        # Connect raw CAN
        channel = d.connect(j2534.CAN, flags=0, baud=500000)
        d.ioctl_clear_msg_filters(channel)
        d.ioctl_clear_rx_buffer(channel)

        # Wildcard filter
        mask = bytes([0, 0, 0, 0])
        pattern = bytes([0, 0, 0, 0])
        fid = d.start_pass_filter(channel, mask, pattern, protocol=j2534.CAN, tx_flags=0)
        
        if args.verbose:
            print(f"Installed wildcard PASS_FILTER (id={fid})")

        try:
            while True:
                msgs = d.read(channel, max_msgs=32, timeout_ms=100)
                for cid, data, rx_status in msgs:
                    timestamp = time.time()
                    time_str = f"{timestamp:.6f}"
                    data_hex = data.hex(" ").upper()
                    char_repr = "".join(chr(b) if 32 <= b <= 126 else "." for b in data)
                    
                    line = f"[{time_str}] ID: 0x{cid:03X}  Len: {len(data)}  Data: {data_hex:<24} | ASCII: {char_repr}"
                    print(line)
                    
                    if out_file:
                        out_file.write(f"{time_str},0x{cid:03X},{len(data)},{data.hex().upper()}\n")
                        out_file.flush()
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
        finally:
            if out_file:
                out_file.close()
            d.disconnect(channel)
    return 0


# --- argparse plumbing ---------------------------------------------------------

def _mode_arg(s: str) -> int:
    v = int(s, 16)
    if v not in (0x03, 0x07, 0x0A):
        raise argparse.ArgumentTypeError("--mode must be 03, 07, or 0A")
    return v


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vf8_obd",
        description="Generic OBD-II reader/clearer for the VinFast VF 8 via Mini-VCI J2534.",
    )
    p.add_argument("--dll", help="Path to J2534 DLL (default: auto-discover; or set MVCI_DLL env var)")
    p.add_argument("--timeout-ms", type=int, default=2000, help="Per-message read timeout (default 2000)")
    p.add_argument("-v", "--verbose", action="store_true", help="Print raw J2534 traffic")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Verify DLL loads and device opens")
    sub.add_parser("vin", help="Read VIN via Mode 09 PID 02")

    sp_scan = sub.add_parser("scan", help="Read DTCs (default: modes 03, 07, 0A)")
    sp_scan.add_argument(
        "--mode", dest="modes", type=_mode_arg, action="append",
        help="Limit to a single mode (03/07/0A). May be repeated.",
    )

    sp_clear = sub.add_parser("clear", help="Clear DTCs via Mode 04")
    sp_clear.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    sub.add_parser("ecu", help="Read responsive ECU Names & Calibration IDs/Versions via Mode 09")

    sp_live = sub.add_parser("live", help="Monitor standard vehicle OBD live-data parameters")
    sp_live.add_argument("--once", action="store_true", help="Take a single snapshot and exit instead of loop")

    sp_monitor = sub.add_parser("monitor", help="Passive raw CAN bus logger (sniffer)")
    sp_monitor.add_argument("--out", help="Path to write log of received CAN frames")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    if sys.platform != "win32":
        sys.exit("vf8_obd requires Windows -- the J2534 DLL is Windows-only.")
    args = build_parser().parse_args(argv)
    handler = {
        "doctor": cmd_doctor,
        "vin": cmd_vin,
        "scan": cmd_scan,
        "clear": cmd_clear,
        "ecu": cmd_ecu,
        "live": cmd_live,
        "monitor": cmd_monitor,
    }[args.command]
    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except j2534.J2534Error as exc:
        print(f"J2534 error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
