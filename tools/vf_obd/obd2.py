"""
SAE J1979 / SAE J1979-2 / ISO 15031-5 — Generic OBD-II definitions.

All values in this module come directly from publicly published standards:
  * SAE J1979_202202  "E/E Diagnostic Test Modes"
  * SAE J1979-2_202103 "E/E Diagnostic Test Modes — ZEV/Electrified Vehicle Data"
  * ISO 15031-5:2015  (corresponding international standard)
  * SAE J2012_202203  "Diagnostic Trouble Code Definitions"

No vendor-specific or speculative identifiers are included. PIDs whose only
public definition is in the spec are listed; manufacturer-specific PIDs and
PIDs requiring scaling tables that exceed the simple A/B/C/D byte formulas
defined in the standard are not synthesized.
"""

# =============================================================================
# OBD-II Mode (Service) Identifiers -- SAE J1979 §6.1
# =============================================================================
MODE_01_CURRENT_DATA                    = 0x01
MODE_02_FREEZE_FRAME                    = 0x02
MODE_03_STORED_DTCS                     = 0x03
MODE_04_CLEAR_DTCS                      = 0x04
MODE_05_O2_MONITOR_RESULTS              = 0x05
MODE_06_ON_BOARD_MONITORING_RESULTS     = 0x06
MODE_07_PENDING_DTCS                    = 0x07
MODE_08_CONTROL_OPERATION               = 0x08
MODE_09_VEHICLE_INFORMATION             = 0x09
MODE_0A_PERMANENT_DTCS                  = 0x0A


# =============================================================================
# Mode 01 / Mode 02 Standard PIDs -- SAE J1979 Table A1
# Only standardised PIDs are listed. Each entry: (pid, name, length_in_bytes,
# formula_string). Formula uses A,B,C,D for response data bytes per J1979.
# =============================================================================
PID_01_SUPPORTED_01_20                  = 0x00
PID_01_MONITOR_STATUS_SINCE_DTC_CLEARED = 0x01
PID_01_FREEZE_DTC                       = 0x02
PID_01_FUEL_SYSTEM_STATUS               = 0x03
PID_01_CALCULATED_ENGINE_LOAD           = 0x04
PID_01_ENGINE_COOLANT_TEMPERATURE       = 0x05
PID_01_SHORT_TERM_FUEL_TRIM_BANK_1      = 0x06
PID_01_LONG_TERM_FUEL_TRIM_BANK_1       = 0x07
PID_01_SHORT_TERM_FUEL_TRIM_BANK_2      = 0x08
PID_01_LONG_TERM_FUEL_TRIM_BANK_2       = 0x09
PID_01_FUEL_PRESSURE                    = 0x0A
PID_01_INTAKE_MANIFOLD_ABSOLUTE_PRESSURE= 0x0B
PID_01_ENGINE_RPM                       = 0x0C
PID_01_VEHICLE_SPEED                    = 0x0D
PID_01_TIMING_ADVANCE                   = 0x0E
PID_01_INTAKE_AIR_TEMPERATURE           = 0x0F
PID_01_MAF_AIR_FLOW_RATE                = 0x10
PID_01_THROTTLE_POSITION                = 0x11
PID_01_COMMANDED_SECONDARY_AIR_STATUS   = 0x12
PID_01_O2_SENSORS_PRESENT_2_BANKS       = 0x13
PID_01_OBD_STANDARDS                    = 0x1C
PID_01_RUN_TIME_SINCE_ENGINE_START      = 0x1F
PID_01_SUPPORTED_21_40                  = 0x20
PID_01_DISTANCE_WITH_MIL_ON             = 0x21
PID_01_FUEL_RAIL_PRESSURE_VS_VAC        = 0x22
PID_01_FUEL_RAIL_PRESSURE_DIESEL        = 0x23
PID_01_COMMANDED_EGR                    = 0x2C
PID_01_EGR_ERROR                        = 0x2D
PID_01_COMMANDED_EVAP_PURGE             = 0x2E
PID_01_FUEL_TANK_LEVEL_INPUT            = 0x2F
PID_01_WARM_UPS_SINCE_CODES_CLEARED     = 0x30
PID_01_DISTANCE_SINCE_CODES_CLEARED     = 0x31
PID_01_BAROMETRIC_PRESSURE              = 0x33
PID_01_CONTROL_MODULE_VOLTAGE           = 0x42
PID_01_ABSOLUTE_LOAD_VALUE              = 0x43
PID_01_COMMANDED_AIR_FUEL_EQUIV_RATIO   = 0x44
PID_01_RELATIVE_THROTTLE_POSITION       = 0x45
PID_01_AMBIENT_AIR_TEMPERATURE          = 0x46
PID_01_ABSOLUTE_THROTTLE_POSITION_B     = 0x47
PID_01_ABSOLUTE_THROTTLE_POSITION_C     = 0x48
PID_01_ACCELERATOR_PEDAL_POSITION_D     = 0x49
PID_01_ACCELERATOR_PEDAL_POSITION_E     = 0x4A
PID_01_ACCELERATOR_PEDAL_POSITION_F     = 0x4B
PID_01_COMMANDED_THROTTLE_ACTUATOR      = 0x4C
PID_01_TIME_RUN_WITH_MIL_ON             = 0x4D
PID_01_TIME_SINCE_TROUBLE_CODES_CLEARED = 0x4E
PID_01_SUPPORTED_41_60                  = 0x40
PID_01_SUPPORTED_61_80                  = 0x60
PID_01_SUPPORTED_81_A0                  = 0x80
PID_01_SUPPORTED_A1_C0                  = 0xA0
PID_01_SUPPORTED_C1_E0                  = 0xC0
PID_01_HYBRID_BATTERY_PACK_REMAINING    = 0x5B
PID_01_ENGINE_OIL_TEMPERATURE           = 0x5C
PID_01_FUEL_INJECTION_TIMING            = 0x5D
PID_01_ENGINE_FUEL_RATE                 = 0x5E
PID_01_DRIVERS_DEMAND_ENGINE_TORQUE_PCT = 0x61
PID_01_ACTUAL_ENGINE_TORQUE_PCT         = 0x62
PID_01_ENGINE_REFERENCE_TORQUE          = 0x63

# SAE J1979-2 (ZEV / Electrified-vehicle) PIDs.  These are publicly defined in
# the 2021 ZEVDTC supplement / J1979-2.  Only the few that appear in the
# published spec are listed here.
PID_01_ODOMETER_FOUR_BYTE               = 0xA6   # J1979-2:2021, 32-bit km*0.1


# =============================================================================
# Mode 09 (Vehicle information) InfoTypes -- SAE J1979 §A2.5
# =============================================================================
INFO_09_SUPPORTED_01_20                 = 0x00
INFO_09_VIN_MESSAGE_COUNT               = 0x01
INFO_09_VIN                             = 0x02
INFO_09_CALIBRATION_ID_MESSAGE_COUNT    = 0x03
INFO_09_CALIBRATION_ID                  = 0x04
INFO_09_CVN_MESSAGE_COUNT               = 0x05
INFO_09_CVN                             = 0x06
INFO_09_IN_USE_PERFORMANCE_TRACKING     = 0x08   # spark ignition
INFO_09_ECU_NAME_MESSAGE_COUNT          = 0x09
INFO_09_ECU_NAME                        = 0x0A
INFO_09_IN_USE_PERFORMANCE_TRACKING_CI  = 0x0B   # compression ignition
INFO_09_ESN                             = 0x0D   # engine serial number


# =============================================================================
# Mode 01 PID 01 — Monitor status byte definitions -- SAE J1979 §5.1.2.1
# Byte A: MIL status + DTC count
#   bit7 = MIL on/off, bits6..0 = DTC count
# Byte B: continuous monitors (supported in bits7..5, ready in bits3..1)
#   bit0 = misfire monitoring supported
#   bit1 = fuel system monitoring supported
#   bit2 = comprehensive components supported
#   bit4 = misfire monitor ready
#   bit5 = fuel system monitor ready
#   bit6 = comprehensive components monitor ready
# Bytes C, D: non-continuous monitor supported/ready bits
# =============================================================================
MIL_STATUS_MASK                         = 0x80
DTC_COUNT_MASK                          = 0x7F

CONTINUOUS_MONITOR_BITS = {
    "misfire":              (0x01, 0x10),
    "fuel_system":          (0x02, 0x20),
    "comprehensive_comp":   (0x04, 0x40),
}

# Non-continuous monitors (Spark Ignition).  Byte C = supported, Byte D = ready.
NONCONTINUOUS_MONITORS_SI = {
    "catalyst":            0x01,
    "heated_catalyst":     0x02,
    "evap_system":         0x04,
    "secondary_air":       0x08,
    "ac_refrigerant":      0x10,
    "o2_sensor":           0x20,
    "o2_sensor_heater":    0x40,
    "egr_system":          0x80,
}

# Non-continuous monitors (Compression Ignition / Diesel)
NONCONTINUOUS_MONITORS_CI = {
    "nmhc_catalyst":       0x01,
    "nox_aftertreatment":  0x02,
    "boost_pressure":      0x08,
    "exhaust_gas_sensor":  0x20,
    "pm_filter":           0x40,
    "egr_vvt":             0x80,
}


# =============================================================================
# Convenience formula helpers from SAE J1979 Table A1
# All formulas take the response data bytes (A, B, C, D...).
# =============================================================================
def pid_engine_load(A: int) -> float:        # PID 04
    return (100.0 / 255.0) * A

def pid_coolant_temp_c(A: int) -> int:       # PID 05
    return A - 40

def pid_engine_rpm(A: int, B: int) -> float: # PID 0C
    return ((A * 256) + B) / 4.0

def pid_vehicle_speed_kph(A: int) -> int:    # PID 0D
    return A

def pid_intake_air_temp_c(A: int) -> int:    # PID 0F
    return A - 40

def pid_throttle_pct(A: int) -> float:       # PID 11
    return (100.0 / 255.0) * A

def pid_run_time_seconds(A: int, B: int) -> int:  # PID 1F
    return A * 256 + B

def pid_fuel_level_pct(A: int) -> float:     # PID 2F
    return (100.0 / 255.0) * A

def pid_module_voltage(A: int, B: int) -> float:  # PID 42
    return ((A * 256) + B) / 1000.0

def pid_ambient_air_temp_c(A: int) -> int:   # PID 46
    return A - 40

def pid_hybrid_battery_remaining(A: int) -> float:  # PID 5B
    return (100.0 / 255.0) * A

def pid_engine_oil_temp_c(A: int) -> int:    # PID 5C
    return A - 40

def pid_engine_fuel_rate_lph(A: int, B: int) -> float:  # PID 5E
    return ((A * 256) + B) * 0.05

def pid_odometer_km(A: int, B: int, C: int, D: int) -> float:  # PID A6 (J1979-2)
    return ((A << 24) | (B << 16) | (C << 8) | D) * 0.1
