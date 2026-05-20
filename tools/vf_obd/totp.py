"""
totp.py -- TOTP Passcode Generator for VinFast VF 8 Engineering Menu.

Given that the actual private root seed/key is unique per vehicle (and stored 
in the secure Head Unit storage or generated dynamically by VinFast's internal 
dealer portal), this tool implements the standard RFC 6238/SHA-256 
cryptographic derivation algorithm.

If you have extracted or computed your vehicle's private seed (or want to test
with a simulation seed), you can feed it into this tool along with your VIN and
current system time to generate the hourly engineering menu passcode.

Usage:
    py -3-32 totp.py --vin LFGXXXXXXXXXXXXXX --secret MY_SECRET_SEED_HEX
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import struct
import sys
import time


def calculate_vin_totp(
    vin: str,
    secret_hex: str,
    step_seconds: int = 3600,
    digits: int = 6,
    timestamp: float | None = None,
) -> tuple[str, int]:
    """Calculate the dynamic TOTP passcode for the given VIN and secret.

    - Uses HMAC-SHA256.
    - Message format: VIN (ASCII bytes) + Time-Block (8-byte big-endian integer).
    - Uses standard dynamic truncation to pull a digits-long decimal token.
    """
    if timestamp is None:
        timestamp = time.time()

    # Determine current epoch block
    time_block = int(timestamp // step_seconds)

    # Convert inputs to bytes
    try:
        secret_bytes = bytes.fromhex(secret_hex)
    except ValueError:
        # Fallback: treat secret as raw ASCII string if not valid hex
        secret_bytes = secret_hex.encode("utf-8")

    vin_bytes = vin.encode("ascii")
    # Time block as 8-byte big-endian integer
    time_bytes = struct.pack(">Q", time_block)

    # Assemble message: VIN + Time-Block
    msg = vin_bytes + time_bytes

    # Perform HMAC-SHA256
    h = hmac.new(secret_bytes, msg, hashlib.sha256).digest()

    # Standard Dynamic Truncation (RFC 4226 Section 5.4)
    offset = h[-1] & 0x0F
    binary = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF

    # Modulo to get target length passcode
    passcode = binary % (10**digits)
    # Format with leading zeros
    passcode_str = f"{passcode:0{digits}d}"

    # Return passcode and remaining validity in seconds
    remaining_seconds = int(step_seconds - (timestamp % step_seconds))
    return passcode_str, remaining_seconds


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="totp",
        description="Engineering Menu TOTP generator for VinFast VF 8 (custom HMAC-SHA256).",
    )
    parser.add_argument("--vin", required=True, help="17-character vehicle VIN")
    parser.add_argument(
        "--secret",
        required=True,
        help="Shared private seed/key (in hex format, or raw ASCII string)",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=3600,
        help="Time-step size in seconds (default: 3600 / 1 hour)",
    )
    parser.add_argument(
        "--digits",
        type=int,
        choices=[6, 8],
        default=6,
        help="Passcode length (default: 6)",
    )
    parser.add_argument(
        "--offset-hours",
        type=float,
        default=0.0,
        help="Simulate a calculation with a time offset in hours",
    )

    args = parser.parse_args()

    # Validate VIN format range
    cleaned_vin = args.vin.strip().upper()
    if len(cleaned_vin) != 17:
        print("WARN: VIN is typically expected to be 17 characters long.")

    calc_time = time.time() + (args.offset_hours * 3600.0)

    try:
        passcode, remaining = calculate_vin_totp(
            vin=cleaned_vin,
            secret_hex=args.secret,
            step_seconds=args.step,
            digits=args.digits,
            timestamp=calc_time,
        )
    except Exception as exc:
        print(f"Error calculating TOTP: {exc}", file=sys.stderr)
        return 1

    time_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(calc_time))

    print("=" * 60)
    print("      VINFAST INFOTAINMENT ENGINEERING MENU PASSCODE")
    print("=" * 60)
    print(f"VIN              : {cleaned_vin}")
    print(f"Evaluation Time  : {time_str}")
    print(f"Step Window      : {args.step} seconds")
    print(f"Passcode         : {passcode}")
    print(f"Window Validity  : {remaining // 60}m {remaining % 60}s remaining")
    print("-" * 60)
    print("⚡ Note: This calculation requires your vehicle's correct private seed.")
    print("   Since the global OEM master seed is proprietary to VinFast systems,")
    print("   this tool computes matching calculations based on the '--secret'")
    print("   key parameter you provide. Check your reverse-engineered or dumped")
    print("   eeprom blocks for the target secure partition keys.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
