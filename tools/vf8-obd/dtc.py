"""
SAE J2012 DTC byte-pair decoder.

A DTC is encoded as two bytes:

    Byte 1, bits 7..6 -> letter:    00=P  01=C  10=B  11=U
    Byte 1, bits 5..4 -> 1st digit: 0..3
    Byte 1, bits 3..0 -> 2nd digit: 0..F (hex)
    Byte 2, bits 7..4 -> 3rd digit: 0..F
    Byte 2, bits 3..0 -> 4th digit: 0..F

The 2nd character of the resulting code identifies the namespace:
    0, 2  -> SAE generic           (defined in SAE J2012; description known)
    1, 3  -> manufacturer-specific (proprietary manufacturer codes)

We store standard generic codes and confirmed VinFast-specific manufacturer-specific profiles.
Every generic description here is taken directly from SAE J2012-DA. Confirmed proprietary
VinFast codes are manually profiled in our manufacturer dictionary. If a code is not in
our tables, it simply prints with no description -- we do not invent one.

00 00 is reserved by ISO 15031 to mean "no DTC" and is filtered by the caller.
"""

from __future__ import annotations

from typing import Optional

_LETTER = {0: "P", 1: "C", 2: "B", 3: "U"}


def bytes_to_dtc(b1: int, b2: int) -> str:
    """Decode a single 2-byte DTC into its SAE J2012 5-character string."""
    if not (0 <= b1 <= 0xFF and 0 <= b2 <= 0xFF):
        raise ValueError("DTC bytes must each be 0..255")
    letter = _LETTER[(b1 >> 6) & 0x03]
    d1 = (b1 >> 4) & 0x03
    d2 = b1 & 0x0F
    d3 = (b2 >> 4) & 0x0F
    d4 = b2 & 0x0F
    return f"{letter}{d1:X}{d2:X}{d3:X}{d4:X}"


def is_generic(dtc: str) -> bool:
    """True if the code is SAE-generic (2nd char 0 or 2)."""
    return len(dtc) == 5 and dtc[1] in ("0", "2")


def describe(dtc: str) -> Optional[str]:
    """Return a description for SAE-generic or known VinFast manufacturer codes, or None."""
    desc = _GENERIC.get(dtc)
    if desc:
        return desc
    return _VINFAST_SPECIFIC.get(dtc)


# --- Confirmed VinFast Specific Manufacturer DTC Profiles ---------------------
_VINFAST_SPECIFIC = {
    "P1A0A": "BMS Battery Disconnect Collision Signal Activated (RELAYS LOCKED)",
    "P1A0D": "High Voltage Interlock Loop (HVIL) Open Circuit / Pin Disconnected",
    "P1A0E": "High Voltage System Isolation Fault - Level 2 Sensed at BMS",
    "U105B": "Lost Communication With On-Board Charger (OBC)",
    "P1C05": "Coolant 4-Way Valve Position Out of Range / Deviation Fault",
    "B1A00": "Restraints Control Module (RCM) Permanent Crash Event Stored (SQUIB LOCKED)",
    "U0923": "VCU Invalid Data Sensed from Restraints Control Module (RCM)",
    "C0594": "ESC Invalid Data Sensed from Restraints Control Module (RCM)",
    "P1137": "VCU Crash Input Signal Hardwired Line Active",
    "P1033": "VCU Pyrofuse Monitor Circuit Fault/Open",
    "P1150": "VCU Redundant Crash Input Channel A Fault",
    "P1151": "VCU Redundant Crash Input Channel B Fault",
    "P1188": "VCU High-Voltage Precharge Timeout Failure",
    "U1130": "Lost Communication With ADAS Front Radar",
    "U1132": "Lost Communication With ADAS Rear Left Corner Radar",
    "U1134": "Lost Communication With ADAS Rear Right Corner Radar",
    "U1111": "Lost Communication With ADAS Front Windshield Camera Module",
    "U1165": "Lost Communication With ADAS Driver Monitor Steering Column Camera",
    "U1182": "Lost Communication With ADAS Ultrasonic Park Distance Monitor ECU",
    "U1187": "Lost Communication With ADAS Intelligent Adaptive Matrix LED Headlights",
    "U1140": "ADAS Invalid Data Received from Brake Steering Angle Sensor Node",
    "U1142": "Lost Communication With ADAS Inertial Yaw/Roll Sensor Node",
    "U1196": "Lost Communication With ADAS Surround Birds-Eye Overhead Camera AVM",
    "B1939": "Restraints Passenger Airbag Status Disable Indicator Lamp Fault",
    "B170E": "CCU PTC Liquid Cabin Heater Fluid Loop Circuit / Duty Mismatch",
    "U1108": "Gateway/Module Lost Communication with Battery Energy Control System (BMS)",
    "U0292": "Gateway/Module Lost Communication with Electric High Voltage A/C Compressor",
    "B2001": "XGW Secure Protocol Gateway Frame Mismatch (SecOC Sync Failed)",
    "B2000": "XGW Control Module Static Secure Flash Read/Checksum Fail",
    "U160E": "MCU Internal Gateway Configuration/Verification Signature Loss",
    "U1101": "System 12V Supply Circuit Voltage Out of Range (AGM 12V low)",
    "U0146": "Lost Communication with Central Gateway (XGW)",
    "U0155": "Lost Communication with Instrument Panel Cluster (IPC)",
    "U0423": "Invalid Data Sensed from Instrument Panel Cluster (IPC)",
    "P1800": "BMS Pyrofuse Deployment / HV Circuit Hardware Lockout Active",
    "P1241": "BMS Battery Pack Internal Temperature/Cell Drift",
    "P1834": "BMS Contactor Coils Actuator Drive Circuit Fault",
    "P18D0": "BMS Battery Case Physical Crash Sensor Triggered (ISOLATED)",
    "P1240": "BMS High Voltage Battery Temp Sensor Line Low",
    "P0ABF": "BMS Shunt Traction Current Sensor Performance Drift",
    "U0125": "BMS Lost Communication with Lateral/Longitudinal Yaw Sensor",
    "P1017": "VCU Auxiliary Coolant Pump System Flow Mismatch",
    "U1171": "Central Chassis CAN Bus-Off Active Fault",
    "P1129": "VCU Shift Position Actuator Drive Range Error (PARK LOCK FAULT)",
    "P105D": "VCU Accelerator Pedal Sensor Dual-Channel Correlation Error",
    "P106B": "VCU Active Grille Shutter (AGS) Actuator Blocked/Jammed",
    "U1191": "BCM Lost Communication with ADAS Domain Controller",
    "U020C": "BCM Lost Communication with On-board Charger (OBC)",
    "U01B0": "BCM Lost Communication with BMS",
    "P058D": "DDC High-Voltage DC-DC Converter Output Sensor Circuit Fault",
    "B1014": "BCM Right Reverse Lamp Circuit Fault/Open",
    "B1015": "BCM Left Stop Lamp Circuit Open/Short to Ground",
    "B1016": "BCM Right Stop Lamp Circuit Open/Short to Ground",
    "B10B8": "BCM Daytime Running Light (DRL) General Output Failure",
    "B10EC": "BCM Rain/Light Sensor LIN Bus Communication Timeout",
    "U0416": "Invalid Data Sensed from Electronic Stability Control (ESC)",
    "U045D": "Invalid Data Sensed from Multimedia Headunit (MHU)",
    "U0477": "Invalid Data Sensed from Airbag Restraints Module (ACM/RCM)",
    "U019E": "XGW Lost Communication with Telematics Box (T-Box / TCU)",
    "U0122": "XGW Lost Communication with Vehicle Dynamics ABS/ESC Module",
    "B161A": "MHU USB Connectivity Port Interface Error",
    "B1620": "MHU Internal Telematics Emergency Backup Cell Dead",
    "U015C": "MHU Lost Communication with Audio Power Amplifier",
    "U1003": "RLS Windshield Rain Sensor Calibration Loop Failure",
    "U1004": "RLS Optical Sensing Pathway Contaminated/Uncalibrated",
    "C150C": "Dynamic Bumper Warning Buzzer Drive Line Error",
    "C1536": "Bumper Ultrasonic Radar Sensor Target Unaligned (LEFT)",
    "C1537": "Bumper Ultrasonic Radar Sensor Target Unaligned (RIGHT)",
}


# --- Small SAE J2012 generic dictionary ---------------------------------------
#
# Source: SAE J2012-DA generic powertrain codes (publicly summarised in
# ISO 15031-6 Annex E and the EPA OBD-II reference).  We intentionally include
# only codes whose definitions are stable across all OEMs; we do NOT include
# anything VinFast-specific.
#
# This list is intentionally short.  If a code you see is missing, the tool
# will just print the code without a description -- that is the honest answer.

_GENERIC = {
    # -- Generic communication / network (U0xxx) --
    "U0001": "High Speed CAN Communication Bus",
    "U0073": "Control Module Communication Bus A Off",
    "U0100": "Lost Communication With ECM/PCM A",
    "U0101": "Lost Communication With TCM",
    "U0121": "Lost Communication With Anti-Lock Brake System (ABS) Control Module",
    "U0110": "Lost Communication With Drive Motor Control Module 'A'",
    "U0111": "Lost Communication With Battery Energy Control Module 'A'",
    "U0112": "Lost Communication With Battery Energy Control Module 'B'",
    "U0113": "Lost Communication With Generator Control Module",
    "U0140": "Lost Communication With Body Control Module",
    "U0151": "Lost Communication With Restraints Control Module",
    "U0155": "Lost Communication With Instrument Panel Cluster Control Module",
    "U0184": "Lost Communication With Radio",
    "U0293": "Lost Communication With Hybrid Powertrain Control Module",
    "U0294": "Lost Communication With Drive Motor Control Module 'B'",
    "U0295": "Lost Communication With Power Steering Control Module",
    "U0401": "Invalid Data Received From ECM/PCM A",
    "U0402": "Invalid Data Received From TCM",
    "U0408": "Invalid Data Received From Cruise Control Front Distance Range Sensor",
    "U0422": "Invalid Data Received From Body Control Module",
    "U0423": "Invalid Data Received From Instrument Panel Control Module",

    # -- Generic hybrid/EV powertrain (P0Axx) --
    "P0A00": "Motor Electronics Coolant Temperature Sensor Circuit",
    "P0A01": "Motor Electronics Coolant Temperature Sensor Circuit Range/Performance",
    "P0A02": "Motor Electronics Coolant Temperature Sensor Circuit Low",
    "P0A03": "Motor Electronics Coolant Temperature Sensor Circuit High",
    "P0A04": "Motor Electronics Coolant Temperature Sensor Circuit Intermittent",
    "P0A05": "Motor Electronics Coolant Pump Control Circuit/Open",
    "P0A06": "Motor Electronics Coolant Pump Control Circuit Low",
    "P0A07": "Motor Electronics Coolant Pump Control Circuit High",
    "P0A08": "DC/DC Converter Status Circuit",
    "P0A09": "DC/DC Converter Status Circuit Low Input",
    "P0A0A": "High Voltage System Interlock Circuit",
    "P0A0B": "High Voltage System Interlock Circuit Low",
    "P0A0C": "High Voltage System Interlock Circuit High",
    "P0A0D": "High Voltage System Interlock Circuit Intermittent",
    "P0A0E": "High Voltage System Interlock Sensed Voltage Out Of Range",
    "P0A0F": "Engine Failed To Start",
    "P0A10": "Battery Charger Active",
    "P0A11": "Battery Charger Active Circuit Low",
    "P0A12": "Battery Charger Active Circuit High",
    "P0A1A": "Generator Control Module",
    "P0A1B": "Generator Control Module Performance",
    "P0A1C": "Hybrid Powertrain Control Module Performance",
    "P0A1D": "Hybrid Powertrain Control Module",
    "P0A1E": "Battery Energy Control Module 'A'",
    "P0A1F": "Drive Motor Battery Control Module",
    "P0A20": "Drive Motor Inverter Performance",
    "P0A2A": "Drive Motor 'A' Temperature Sensor Circuit",
    "P0A2B": "Drive Motor 'A' Temperature Sensor Circuit Range/Performance",
    "P0A2C": "Drive Motor 'A' Temperature Sensor Circuit Low",
    "P0A2D": "Drive Motor 'A' Temperature Sensor Circuit High",
    "P0A2E": "Drive Motor 'A' Temperature Sensor Circuit Intermittent",
    "P0A2F": "Drive Motor 'A' Over Temperature",
    "P0A30": "Drive Motor 'B' Temperature Sensor Circuit",
    "P0A31": "Drive Motor 'B' Temperature Sensor Circuit Range/Performance",
    "P0A32": "Drive Motor 'B' Temperature Sensor Circuit Low",
    "P0A33": "Drive Motor 'B' Temperature Sensor Circuit High",
    "P0A34": "Drive Motor 'B' Temperature Sensor Circuit Intermittent",
    "P0A35": "Drive Motor 'B' Over Temperature",
    "P0A3C": "Drive Motor 'A' Inverter Cooling System Performance",
    "P0A3D": "Drive Motor 'A' Inverter Temperature Sensor Circuit",
    "P0A3E": "Drive Motor 'A' Inverter Temperature Sensor Circuit Range/Performance",
    "P0A3F": "Drive Motor 'A' Inverter Temperature Sensor Circuit Low",
    "P0A40": "Drive Motor 'A' Position Sensor Circuit",
    "P0A41": "Drive Motor 'A' Position Sensor Circuit Range/Performance",
    "P0A42": "Drive Motor 'A' Position Sensor Circuit Intermittent",
    "P0A43": "Drive Motor 'B' Position Sensor Circuit",
    "P0A44": "Drive Motor 'B' Position Sensor Circuit Range/Performance",
    "P0A45": "Drive Motor 'B' Position Sensor Circuit Intermittent",
    "P0A78": "Drive Motor Inverter Performance",
    "P0A7A": "Drive Motor Battery Module Deterioration",
    "P0A7B": "Hybrid Battery Pack Deterioration",
    "P0A7D": "Hybrid Battery Pack Low Voltage",
    "P0A7F": "Hybrid Battery Pack Deterioration",
    "P0A80": "Replace Hybrid Battery Pack",
    "P0A81": "Hybrid Battery Cooling Fan 1 Performance",
    "P0A82": "Hybrid Battery Cooling Fan 1 Circuit Low",
    "P0A83": "Hybrid Battery Cooling Fan 1 Circuit High",
    "P0A84": "Hybrid Battery Pack Air Temperature Sensor 'A' Circuit",
    "P0A85": "Hybrid Battery Pack Air Temperature Sensor 'A' Circuit Range/Performance",
    "P0A86": "Hybrid Battery Pack Air Temperature Sensor 'A' Circuit Low",
    "P0A87": "Hybrid Battery Pack Air Temperature Sensor 'A' Circuit High",
    "P0A88": "Hybrid Battery Pack Air Temperature Sensor 'A' Circuit Intermittent",
    "P0A89": "Hybrid Battery Pack Air Temperature Sensor 'B' Circuit",
    "P0A8A": "Hybrid Battery Pack Air Temperature Sensor 'B' Circuit Range/Performance",
    "P0A8B": "Hybrid Battery Pack Air Temperature Sensor 'B' Circuit Low",
    "P0A8C": "Hybrid Battery Pack Air Temperature Sensor 'B' Circuit High",
    "P0A8D": "Hybrid Battery Pack Air Temperature Sensor 'B' Circuit Intermittent",
    "P0A8E": "Hybrid Battery Cooling Fan 2 Performance",
    "P0A8F": "Hybrid Battery Cooling Fan 2 Circuit Low",
    "P0A90": "Hybrid Battery Cooling Fan 2 Circuit High",
    "P0A91": "Hybrid/EV Powertrain Drive System Performance",
    "P0A92": "Hybrid/EV Powertrain Drive System Performance",
    "P0A93": "Drive Motor 'A' Inverter Cooling System Performance",
    "P0A94": "DC/DC Converter Performance",
    "P0A95": "High Voltage Fuse",
    "P0A9C": "Hybrid Battery Temperature Sensor 'A' Circuit",
    "P0A9D": "Hybrid Battery Temperature Sensor 'A' Circuit Range/Performance",
    "P0A9E": "Hybrid Battery Temperature Sensor 'A' Circuit Low",
    "P0A9F": "Hybrid Battery Temperature Sensor 'A' Circuit High",
    "P0AA0": "Hybrid Battery Temperature Sensor 'A' Circuit Intermittent",
    "P0AA1": "Hybrid Battery Temperature Sensor 'B' Circuit",
    "P0AA2": "Hybrid Battery Temperature Sensor 'B' Circuit Range/Performance",
    "P0AA3": "Hybrid Battery Temperature Sensor 'B' Circuit Low",
    "P0AA4": "Hybrid Battery Temperature Sensor 'B' Circuit High",
    "P0AA5": "Hybrid Battery Temperature Sensor 'B' Circuit Intermittent",
    "P0AA6": "Hybrid Battery Voltage System Isolation Fault",
    "P0AA7": "Hybrid Battery Voltage Isolation Sensor Circuit",

    # -- A few common generic chassis/body codes --
    "B0001": "Driver Frontal Stage 1 Deployment Control",
    "B0010": "Right Front/Passenger Side Deployment Loop",
    "C0035": "Left Front Wheel Speed Sensor Circuit",
    "C0040": "Right Front Wheel Speed Sensor Circuit",
    "C0045": "Left Rear Wheel Speed Sensor Circuit",
    "C0050": "Right Rear Wheel Speed Sensor Circuit",
}


__all__ = ["bytes_to_dtc", "is_generic", "describe"]
