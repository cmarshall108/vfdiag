"""
Minimal ctypes binding for the SAE J2534-1 (04.04) Pass-Thru API.

Only the subset needed for ISO 15765-4 OBD-II read/clear DTC is implemented:

    PassThruOpen, PassThruClose,
    PassThruConnect, PassThruDisconnect,
    PassThruStartMsgFilter, PassThruStopMsgFilter,
    PassThruReadMsgs, PassThruWriteMsgs,
    PassThruIoctl,
    PassThruReadVersion, PassThruGetLastError.

Reference: SAE J2534-1 (2004), "Recommended Practice for Pass-Thru Vehicle
Programming."  Constants below come from that specification.

Windows-only.  Designed against MVCI32.dll (Toyota Mini-VCI clone) but should
work with any J2534-1 04.04 compliant DLL.
"""

from __future__ import annotations

import ctypes
import os
import sys
import winreg  # type: ignore[import-not-found]   # Windows-only
from ctypes import (
    POINTER,
    Structure,
    byref,
    c_char,
    c_long,
    c_ubyte,
    c_ulong,
    c_void_p,
    create_string_buffer,
    sizeof,
)
from typing import Iterable, List, Optional, Tuple

# --- J2534-1 04.04 constants ---------------------------------------------------

# Protocol IDs (PassThruConnect)
J1850VPW = 1
J1850PWM = 2
ISO9141 = 3
ISO14230 = 4
CAN = 5
ISO15765 = 6
SCI_A_ENGINE = 7
SCI_A_TRANS = 8
SCI_B_ENGINE = 9
SCI_B_TRANS = 10

# Connect flags
CAN_29BIT_ID = 0x00000100
ISO9141_NO_CHECKSUM = 0x00000200
CAN_ID_BOTH = 0x00000800
ISO9141_K_LINE_ONLY = 0x00001000

# TxFlags
ISO15765_FRAME_PAD = 0x00000040
ISO15765_ADDR_TYPE = 0x00000080   # 0=physical, 1=functional
CAN_29BIT_TX = 0x00000100

# Filter types
PASS_FILTER = 1
BLOCK_FILTER = 2
FLOW_CONTROL_FILTER = 3

# Ioctl IDs
GET_CONFIG = 0x01
SET_CONFIG = 0x02
READ_VBATT = 0x03
FIVE_BAUD_INIT = 0x04
FAST_INIT = 0x05
CLEAR_TX_BUFFER = 0x07
CLEAR_RX_BUFFER = 0x08
CLEAR_PERIODIC_MSGS = 0x09
CLEAR_MSG_FILTERS = 0x0A
CLEAR_FUNCT_MSG_LOOKUP_TABLE = 0x0B

# SCONFIG parameter IDs (subset)
DATA_RATE = 0x01
LOOPBACK = 0x03
NODE_ADDRESS = 0x04
NETWORK_LINE = 0x05
P1_MIN = 0x06
P1_MAX = 0x07
ISO15765_BS = 0x1E
ISO15765_STMIN = 0x1F

# Error codes (PassThruGetLastError returns a string; numeric returns below)
STATUS_NOERROR = 0x00
ERR_NOT_SUPPORTED = 0x01
ERR_INVALID_CHANNEL_ID = 0x02
ERR_INVALID_PROTOCOL_ID = 0x03
ERR_NULL_PARAMETER = 0x04
ERR_INVALID_IOCTL_VALUE = 0x05
ERR_INVALID_FLAGS = 0x06
ERR_FAILED = 0x07
ERR_DEVICE_NOT_CONNECTED = 0x08
ERR_TIMEOUT = 0x09
ERR_INVALID_MSG = 0x0A
ERR_INVALID_TIME_INTERVAL = 0x0B
ERR_EXCEEDED_LIMIT = 0x0C
ERR_INVALID_MSG_ID = 0x0D
ERR_DEVICE_IN_USE = 0x0E
ERR_INVALID_IOCTL_ID = 0x0F
ERR_BUFFER_EMPTY = 0x10
ERR_BUFFER_FULL = 0x11
ERR_BUFFER_OVERFLOW = 0x12
ERR_PIN_INVALID = 0x13
ERR_CHANNEL_IN_USE = 0x14
ERR_MSG_PROTOCOL_ID = 0x15
ERR_INVALID_FILTER_ID = 0x16
ERR_NO_FLOW_CONTROL = 0x17
ERR_NOT_UNIQUE = 0x18
ERR_INVALID_BAUDRATE = 0x19
ERR_INVALID_DEVICE_ID = 0x1A

# Message payload size (per J2534-1: 4128 bytes max)
_MSG_DATA_SIZE = 4128


class PASSTHRU_MSG(Structure):
    _fields_ = [
        ("ProtocolID", c_ulong),
        ("RxStatus", c_ulong),
        ("TxFlags", c_ulong),
        ("Timestamp", c_ulong),
        ("DataSize", c_ulong),
        ("ExtraDataIndex", c_ulong),
        ("Data", c_ubyte * _MSG_DATA_SIZE),
    ]


class SCONFIG(Structure):
    _fields_ = [("Parameter", c_ulong), ("Value", c_ulong)]


class SCONFIG_LIST(Structure):
    _fields_ = [("NumOfParams", c_ulong), ("ConfigPtr", POINTER(SCONFIG))]


class J2534Error(RuntimeError):
    def __init__(self, message: str, code: int, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{message} (code=0x{code:02X}){': ' + detail if detail else ''}")


# --- DLL discovery -------------------------------------------------------------

_PASSTHRU_REGISTRY_ROOTS = (
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\PassThruSupport.04.04"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\PassThruSupport.04.04"),
)


def discover_j2534_devices() -> List[Tuple[str, str]]:
    """Enumerate installed J2534 devices via the standard registry path.

    Returns a list of ``(Name, FunctionLibrary)`` tuples.
    """
    found: List[Tuple[str, str]] = []
    for root, path in _PASSTHRU_REGISTRY_ROOTS:
        try:
            with winreg.OpenKey(root, path) as key:
                i = 0
                while True:
                    try:
                        subname = winreg.EnumKey(key, i)
                    except OSError:
                        break
                    i += 1
                    try:
                        with winreg.OpenKey(key, subname) as sub:
                            name = _read_reg_value(sub, "Name") or subname
                            lib = _read_reg_value(sub, "FunctionLibrary")
                            if lib:
                                found.append((name, lib))
                    except OSError:
                        continue
        except OSError:
            continue
    return found


def _read_reg_value(key, name: str) -> Optional[str]:
    try:
        value, _ = winreg.QueryValueEx(key, name)
        return str(value) if value else None
    except OSError:
        return None


def find_default_dll() -> Optional[str]:
    """Best-effort DLL discovery for the Mini-VCI / MVCI driver.

    1. First J2534 registry entry whose name mentions MVCI / Mini-VCI / Toyota.
    2. Any J2534 registry entry.
    3. Common hard-coded install paths.
    """
    candidates = discover_j2534_devices()
    preferred = [lib for name, lib in candidates if _looks_like_mvci(name)]
    if preferred:
        return preferred[0]
    if candidates:
        return candidates[0][1]
    for path in _HARDCODED_DLL_PATHS:
        if os.path.isfile(path):
            return path
    return None


def _looks_like_mvci(name: str) -> bool:
    lowered = name.lower()
    return any(s in lowered for s in ("mvci", "mini vci", "mini-vci", "xhorse", "toyota"))


_HARDCODED_DLL_PATHS = (
    r"C:\Program Files (x86)\XHorse Electronics\MVCI Driver for TOYOTA TIS\MVCI32.dll",
    r"C:\Program Files\XHorse Electronics\MVCI Driver for TOYOTA TIS\MVCI32.dll",
    r"C:\Program Files (x86)\Toyota\MVCI\MVCI32.dll",
    r"C:\Program Files\Toyota\MVCI\MVCI32.dll",
)


# --- Thin wrapper class --------------------------------------------------------

class J2534:
    """Thin wrapper over a J2534-1 DLL.

    Lifecycle:
        j = J2534(dll_path)
        j.open()
        channel = j.connect(ISO15765, baud=500000)
        ...
        j.disconnect(channel)
        j.close()
    """

    def __init__(self, dll_path: str) -> None:
        if sys.platform != "win32":
            raise RuntimeError(
                "J2534 DLLs are Windows-only. This module cannot run on this platform."
            )
        if not os.path.isfile(dll_path):
            raise FileNotFoundError(dll_path)
        try:
            self._dll = ctypes.WinDLL(dll_path)
        except OSError as exc:
            # WinError 193 = "%1 is not a valid Win32 application" -> bitness mismatch
            raise RuntimeError(
                f"Failed to load {dll_path}.  If this is WinError 193, the DLL is "
                f"32-bit and you are running 64-bit Python.  Use 32-bit Python "
                f"(py -3-32) instead."
            ) from exc
        self.dll_path = dll_path
        self._device_id: Optional[c_ulong] = None
        self._bind_functions()

    # -- function binding ------------------------------------------------------

    def _bind_functions(self) -> None:
        d = self._dll

        d.PassThruOpen.argtypes = [c_void_p, POINTER(c_ulong)]
        d.PassThruOpen.restype = c_long

        d.PassThruClose.argtypes = [c_ulong]
        d.PassThruClose.restype = c_long

        d.PassThruConnect.argtypes = [
            c_ulong, c_ulong, c_ulong, c_ulong, POINTER(c_ulong)
        ]
        d.PassThruConnect.restype = c_long

        d.PassThruDisconnect.argtypes = [c_ulong]
        d.PassThruDisconnect.restype = c_long

        d.PassThruReadMsgs.argtypes = [
            c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong
        ]
        d.PassThruReadMsgs.restype = c_long

        d.PassThruWriteMsgs.argtypes = [
            c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong
        ]
        d.PassThruWriteMsgs.restype = c_long

        d.PassThruStartMsgFilter.argtypes = [
            c_ulong, c_ulong,
            POINTER(PASSTHRU_MSG), POINTER(PASSTHRU_MSG), POINTER(PASSTHRU_MSG),
            POINTER(c_ulong),
        ]
        d.PassThruStartMsgFilter.restype = c_long

        d.PassThruStopMsgFilter.argtypes = [c_ulong, c_ulong]
        d.PassThruStopMsgFilter.restype = c_long

        d.PassThruIoctl.argtypes = [c_ulong, c_ulong, c_void_p, c_void_p]
        d.PassThruIoctl.restype = c_long

        d.PassThruReadVersion.argtypes = [
            c_ulong, c_char * 80, c_char * 80, c_char * 80
        ]
        d.PassThruReadVersion.restype = c_long

        d.PassThruGetLastError.argtypes = [c_char * 80]
        d.PassThruGetLastError.restype = c_long

    # -- error helper ----------------------------------------------------------

    def _check(self, rc: int, op: str) -> None:
        if rc == STATUS_NOERROR:
            return
        buf = create_string_buffer(80)
        try:
            self._dll.PassThruGetLastError(buf)
            detail = buf.value.decode("ascii", errors="replace").strip()
        except Exception:
            detail = ""
        raise J2534Error(op, rc, detail)

    # -- high-level API --------------------------------------------------------

    def open(self) -> None:
        dev = c_ulong(0)
        rc = self._dll.PassThruOpen(None, byref(dev))
        self._check(rc, "PassThruOpen")
        self._device_id = dev

    def close(self) -> None:
        if self._device_id is None:
            return
        rc = self._dll.PassThruClose(self._device_id)
        self._device_id = None
        self._check(rc, "PassThruClose")

    def read_version(self) -> Tuple[str, str, str]:
        if self._device_id is None:
            raise RuntimeError("Device not open")
        firmware = create_string_buffer(80)
        dll_ver = create_string_buffer(80)
        api_ver = create_string_buffer(80)
        rc = self._dll.PassThruReadVersion(self._device_id, firmware, dll_ver, api_ver)
        self._check(rc, "PassThruReadVersion")
        return (
            firmware.value.decode("ascii", errors="replace"),
            dll_ver.value.decode("ascii", errors="replace"),
            api_ver.value.decode("ascii", errors="replace"),
        )

    def read_vbatt_mv(self) -> int:
        """Return battery voltage at OBD port in millivolts."""
        if self._device_id is None:
            raise RuntimeError("Device not open")
        mv = c_ulong(0)
        rc = self._dll.PassThruIoctl(self._device_id, READ_VBATT, None, byref(mv))
        self._check(rc, "PassThruIoctl(READ_VBATT)")
        return int(mv.value)

    def connect(self, protocol: int, flags: int = 0, baud: int = 500000) -> int:
        if self._device_id is None:
            raise RuntimeError("Device not open")
        ch = c_ulong(0)
        rc = self._dll.PassThruConnect(
            self._device_id, protocol, flags, baud, byref(ch)
        )
        self._check(rc, "PassThruConnect")
        return int(ch.value)

    def disconnect(self, channel_id: int) -> None:
        rc = self._dll.PassThruDisconnect(channel_id)
        self._check(rc, "PassThruDisconnect")

    def ioctl_clear_msg_filters(self, channel_id: int) -> None:
        rc = self._dll.PassThruIoctl(channel_id, CLEAR_MSG_FILTERS, None, None)
        self._check(rc, "PassThruIoctl(CLEAR_MSG_FILTERS)")

    def ioctl_clear_rx_buffer(self, channel_id: int) -> None:
        rc = self._dll.PassThruIoctl(channel_id, CLEAR_RX_BUFFER, None, None)
        self._check(rc, "PassThruIoctl(CLEAR_RX_BUFFER)")

    def start_flow_control_filter(
        self,
        channel_id: int,
        mask: bytes,
        pattern: bytes,
        flow_control: bytes,
        protocol: int = ISO15765,
        tx_flags: int = ISO15765_FRAME_PAD,
    ) -> int:
        """Install an ISO 15765 flow-control filter.

        mask / pattern apply to the CAN arbitration ID of incoming responses.
        flow_control contains the CAN arbitration ID we will transmit flow-control
        frames on (i.e. the *request* address for this responder).

        All three byte strings must be 4 bytes (big-endian CAN ID), per J2534-1.
        """
        if not (len(mask) == len(pattern) == len(flow_control) == 4):
            raise ValueError("mask/pattern/flow_control must each be 4 bytes")

        def _mk(data: bytes) -> PASSTHRU_MSG:
            m = PASSTHRU_MSG()
            m.ProtocolID = protocol
            m.TxFlags = tx_flags
            m.DataSize = 4
            for i, b in enumerate(data):
                m.Data[i] = b
            return m

        mask_m = _mk(mask)
        pat_m = _mk(pattern)
        flow_m = _mk(flow_control)
        fid = c_ulong(0)
        rc = self._dll.PassThruStartMsgFilter(
            channel_id, FLOW_CONTROL_FILTER,
            byref(mask_m), byref(pat_m), byref(flow_m),
            byref(fid),
        )
        self._check(rc, "PassThruStartMsgFilter")
        return int(fid.value)

    def start_pass_filter(
        self,
        channel_id: int,
        mask: bytes,
        pattern: bytes,
        protocol: int = ISO15765,
        tx_flags: int = ISO15765_FRAME_PAD,
    ) -> int:
        """Install an ISO 15765 or CAN pass filter.

        All frames matching mask and pattern are placed in the receive buffer.
        mask/pattern must be 4 bytes.
        """
        if not (len(mask) == len(pattern) == 4):
            raise ValueError("mask/pattern must each be 4 bytes")

        def _mk(data: bytes) -> PASSTHRU_MSG:
            m = PASSTHRU_MSG()
            m.ProtocolID = protocol
            m.TxFlags = tx_flags
            m.DataSize = 4
            for i, b in enumerate(data):
                m.Data[i] = b
            return m

        mask_m = _mk(mask)
        pat_m = _mk(pattern)
        fid = c_ulong(0)
        rc = self._dll.PassThruStartMsgFilter(
            channel_id, PASS_FILTER,
            byref(mask_m), byref(pat_m), None,
            byref(fid),
        )
        self._check(rc, "PassThruStartMsgFilter(PASS_FILTER)")
        return int(fid.value)

    def write(
        self,
        channel_id: int,
        can_id: int,
        payload: bytes,
        protocol: int = ISO15765,
        tx_flags: int = ISO15765_FRAME_PAD,
        timeout_ms: int = 1000,
    ) -> None:
        msg = PASSTHRU_MSG()
        msg.ProtocolID = protocol
        msg.TxFlags = tx_flags
        # 4-byte big-endian CAN ID prefix per J2534-1
        prefix = can_id.to_bytes(4, "big")
        data = prefix + payload
        if len(data) > _MSG_DATA_SIZE:
            raise ValueError("payload too large")
        msg.DataSize = len(data)
        for i, b in enumerate(data):
            msg.Data[i] = b
        n = c_ulong(1)
        rc = self._dll.PassThruWriteMsgs(channel_id, byref(msg), byref(n), timeout_ms)
        self._check(rc, "PassThruWriteMsgs")

    def read(
        self,
        channel_id: int,
        max_msgs: int = 8,
        timeout_ms: int = 1000,
    ) -> List[Tuple[int, bytes, int]]:
        """Read up to ``max_msgs`` messages.

        Returns a list of ``(can_id, payload, rx_status)`` tuples. ``payload``
        excludes the leading 4-byte CAN ID.  An empty list means the buffer was
        empty within the timeout (ERR_BUFFER_EMPTY / ERR_TIMEOUT are swallowed).
        """
        msgs = (PASSTHRU_MSG * max_msgs)()
        n = c_ulong(max_msgs)
        rc = self._dll.PassThruReadMsgs(channel_id, msgs, byref(n), timeout_ms)
        if rc in (ERR_BUFFER_EMPTY, ERR_TIMEOUT):
            # Return whatever (if any) was placed in the buffer before the timeout.
            count = int(n.value)
        elif rc != STATUS_NOERROR:
            self._check(rc, "PassThruReadMsgs")
            return []
        else:
            count = int(n.value)

        out: List[Tuple[int, bytes, int]] = []
        for i in range(count):
            m = msgs[i]
            size = int(m.DataSize)
            if size < 4:
                continue
            raw = bytes(bytearray(m.Data[:size]))
            cid = int.from_bytes(raw[:4], "big")
            out.append((cid, raw[4:], int(m.RxStatus)))
        return out

    # -- context manager -------------------------------------------------------

    def __enter__(self) -> "J2534":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.close()
        except Exception:
            pass


__all__ = [
    "ISO15765",
    "ISO15765_FRAME_PAD",
    "ISO15765_ADDR_TYPE",
    "CAN_ID_BOTH",
    "J2534",
    "J2534Error",
    "PASSTHRU_MSG",
    "discover_j2534_devices",
    "find_default_dll",
]
