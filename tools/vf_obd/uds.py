"""
ISO 14229-1:2020 — Unified Diagnostic Services (UDS) constants.

All values in this module are taken directly from the published standard:
  * ISO 14229-1:2020 (UDS protocol)
  * ISO 14229-3:2022 (UDS on CAN, UDSonCAN)
  * ISO 15765-3 (Diagnostic communication over CAN-2.0B)
  * SAE J2012 / ISO 15031-6 (DTC numbering format)

No vendor-specific or speculative identifiers are included here. Where a range
is reserved for "vehicleManufacturerSpecific" use, that fact is noted but the
specific values in that range are NOT defined here.

Sources are cited at each section header with the section number from the
referenced specification.
"""

# =============================================================================
# Service Identifiers (SIDs)  -- ISO 14229-1:2020 Table 2
# =============================================================================

# Diagnostic and Communication Management
SID_DIAGNOSTIC_SESSION_CONTROL          = 0x10
SID_ECU_RESET                           = 0x11
SID_SECURITY_ACCESS                     = 0x27
SID_COMMUNICATION_CONTROL               = 0x28
SID_TESTER_PRESENT                      = 0x3E
SID_ACCESS_TIMING_PARAMETER             = 0x83
SID_SECURED_DATA_TRANSMISSION           = 0x84
SID_CONTROL_DTC_SETTING                 = 0x85
SID_RESPONSE_ON_EVENT                   = 0x86
SID_LINK_CONTROL                        = 0x87
SID_AUTHENTICATION                      = 0x29  # ISO 14229-1:2020 (formerly proprietary)

# Data Transmission
SID_READ_DATA_BY_IDENTIFIER             = 0x22
SID_READ_MEMORY_BY_ADDRESS              = 0x23
SID_READ_SCALING_DATA_BY_IDENTIFIER     = 0x24
SID_READ_DATA_BY_PERIODIC_IDENTIFIER    = 0x2A
SID_DYNAMICALLY_DEFINE_DATA_IDENTIFIER  = 0x2C
SID_WRITE_DATA_BY_IDENTIFIER            = 0x2E   # WRITE — disabled in this tool
SID_WRITE_MEMORY_BY_ADDRESS             = 0x3D   # WRITE — disabled in this tool

# Stored Data Transmission
SID_CLEAR_DIAGNOSTIC_INFORMATION        = 0x14
SID_READ_DTC_INFORMATION                = 0x19

# InputOutput Control
SID_IO_CONTROL_BY_IDENTIFIER            = 0x2F

# Remote Activation of Routine
SID_ROUTINE_CONTROL                     = 0x31

# Upload / Download (FLASH — all four disabled in this tool)
SID_REQUEST_DOWNLOAD                    = 0x34
SID_REQUEST_UPLOAD                      = 0x35
SID_TRANSFER_DATA                       = 0x36
SID_REQUEST_TRANSFER_EXIT               = 0x37
SID_REQUEST_FILE_TRANSFER               = 0x38   # ISO 14229-1:2020 §12.1

# Positive response SID = request SID + 0x40
POSITIVE_RESPONSE_OFFSET                = 0x40
NEGATIVE_RESPONSE_SID                   = 0x7F

# Services this tool refuses to send (anti-brick policy)
WRITE_SERVICES_DISABLED = frozenset({
    SID_WRITE_DATA_BY_IDENTIFIER,
    SID_WRITE_MEMORY_BY_ADDRESS,
    SID_REQUEST_DOWNLOAD,
    SID_REQUEST_UPLOAD,
    SID_TRANSFER_DATA,
    SID_REQUEST_TRANSFER_EXIT,
    SID_REQUEST_FILE_TRANSFER,
})


# =============================================================================
# DiagnosticSessionControl (0x10) sub-functions -- ISO 14229-1:2020 §9.2.2
# =============================================================================
SESSION_DEFAULT                         = 0x01
SESSION_PROGRAMMING                     = 0x02
SESSION_EXTENDED_DIAGNOSTIC             = 0x03
SESSION_SAFETY_SYSTEM_DIAGNOSTIC        = 0x04
# 0x05-0x3F        ISOSAEReserved
# 0x40-0x5F        vehicleManufacturerSpecific
# 0x60-0x7E        systemSupplierSpecific
# 0x7F             ISOSAEReserved


# =============================================================================
# ECUReset (0x11) sub-functions -- ISO 14229-1:2020 §9.3.2
# =============================================================================
RESET_HARD                              = 0x01
RESET_KEY_OFF_ON                        = 0x02
RESET_SOFT                              = 0x03
RESET_ENABLE_RAPID_POWER_SHUTDOWN       = 0x04
RESET_DISABLE_RAPID_POWER_SHUTDOWN      = 0x05


# =============================================================================
# SecurityAccess (0x27) sub-functions -- ISO 14229-1:2020 §9.4.2
# Odd value = requestSeed at security level N
# Even value (Odd+1) = sendKey at security level N
# 0x01/0x02 .. 0x41/0x42 are defined; 0x43-0x5E reserved; 0x5F-0x7E systemSupplierSpecific
# =============================================================================
SEC_REQ_SEED_LEVEL_1                    = 0x01
SEC_SEND_KEY_LEVEL_1                    = 0x02
SEC_REQ_SEED_LEVEL_3                    = 0x03
SEC_SEND_KEY_LEVEL_3                    = 0x04
SEC_REQ_SEED_LEVEL_5                    = 0x05
SEC_SEND_KEY_LEVEL_5                    = 0x06
# Ranges (per spec):
#   0x01–0x42  vehicleManufacturerSpecific seed/key pairs
#   0x5F–0x7E  systemSupplierSpecific seed/key pairs


# =============================================================================
# CommunicationControl (0x28) sub-functions -- ISO 14229-1:2020 §9.5.2
# =============================================================================
COMM_ENABLE_RX_AND_TX                   = 0x00
COMM_ENABLE_RX_DISABLE_TX               = 0x01
COMM_DISABLE_RX_ENABLE_TX               = 0x02
COMM_DISABLE_RX_AND_TX                  = 0x03
COMM_ENABLE_RX_DISABLE_TX_W_EAI         = 0x04
COMM_ENABLE_RX_TX_W_EAI                 = 0x05

# CommunicationType parameter (one byte alongside the sub-function)
COMM_TYPE_NORMAL                        = 0x01   # normalCommunicationMessages
COMM_TYPE_NETWORK_MGMT                  = 0x02   # networkManagementCommunicationMessages
COMM_TYPE_NORMAL_AND_NM                 = 0x03


# =============================================================================
# ControlDTCSetting (0x85) sub-functions -- ISO 14229-1:2020 §10.8.2
# =============================================================================
DTC_SETTING_ON                          = 0x01
DTC_SETTING_OFF                         = 0x02


# =============================================================================
# LinkControl (0x87) sub-functions -- ISO 14229-1:2020 §9.9.2
# =============================================================================
LINK_VERIFY_BAUD_FIXED                  = 0x01
LINK_VERIFY_BAUD_SPECIFIC               = 0x02
LINK_TRANSITION_BAUD                    = 0x03

# LinkControlBaudrateIdentifier (ISO 14229-1:2020 Annex C.1)
BAUD_PC9600                             = 0x01
BAUD_PC19200                            = 0x02
BAUD_PC38400                            = 0x03
BAUD_PC57600                            = 0x04
BAUD_PC115200                           = 0x05
BAUD_CAN125K                            = 0x10
BAUD_CAN250K                            = 0x11
BAUD_CAN500K                            = 0x12
BAUD_CAN1M                              = 0x13
BAUD_PROGRAMMING_SETUP                  = 0x20


# =============================================================================
# RoutineControl (0x31) sub-functions -- ISO 14229-1:2020 §11.5.2
# =============================================================================
ROUTINE_START                           = 0x01
ROUTINE_STOP                            = 0x02
ROUTINE_REQUEST_RESULTS                 = 0x03


# =============================================================================
# RoutineIdentifiers (RIDs) — ISO 14229-1:2020 Table C.4
# Only ISO-defined IDs are listed; everything else (0x0200-0xDFFF) is
# vehicleManufacturerSpecific and intentionally NOT enumerated here.
# =============================================================================
RID_ERASE_MEMORY                        = 0xFF00
RID_CHECK_PROGRAMMING_DEPENDENCIES      = 0xFF01
RID_ERASE_MIRROR_MEMORY_DTCS            = 0xFF02   # deprecated; kept for legacy interop
# RID ranges (from ISO 14229-1:2020 §11.5.4):
#   0x0000-0x00FF  ISOSAEReserved
#   0x0100-0x01FF  Tachograph (ISO 16844)
#   0x0200-0xDFFF  vehicleManufacturerSpecific
#   0xE000-0xE1FF  OBDII / SAE Reserved
#   0xE200-0xE2FF  safety system routine identifiers
#   0xE300-0xEFFF  reserved
#   0xF000-0xFEFF  systemSupplierSpecific
#   0xFF00-0xFFFF  ISOSAEReserved (the three above are the only defined values)


# =============================================================================
# IOControlByIdentifier (0x2F) inputOutputControlParameter
# -- ISO 14229-1:2020 §11.4.4.3
# =============================================================================
IOCP_RETURN_CONTROL_TO_ECU              = 0x00
IOCP_RESET_TO_DEFAULT                   = 0x01
IOCP_FREEZE_CURRENT_STATE               = 0x02
IOCP_SHORT_TERM_ADJUSTMENT              = 0x03


# =============================================================================
# ReadDTCInformation (0x19) sub-functions -- ISO 14229-1:2020 §10.4.2
# =============================================================================
RDTC_REPORT_NUMBER_OF_DTC_BY_STATUS_MASK              = 0x01
RDTC_REPORT_DTC_BY_STATUS_MASK                        = 0x02
RDTC_REPORT_DTC_SNAPSHOT_IDENTIFICATION               = 0x03
RDTC_REPORT_DTC_SNAPSHOT_RECORD_BY_DTC_NUMBER         = 0x04
RDTC_REPORT_DTC_STORED_DATA_BY_RECORD_NUMBER          = 0x05
RDTC_REPORT_DTC_EXT_DATA_RECORD_BY_DTC_NUMBER         = 0x06
RDTC_REPORT_NUMBER_OF_DTC_BY_SEVERITY_MASK_RECORD     = 0x07
RDTC_REPORT_DTC_BY_SEVERITY_MASK_RECORD               = 0x08
RDTC_REPORT_SEVERITY_INFORMATION_OF_DTC               = 0x09
RDTC_REPORT_SUPPORTED_DTC                             = 0x0A
RDTC_REPORT_FIRST_TEST_FAILED_DTC                     = 0x0B
RDTC_REPORT_FIRST_CONFIRMED_DTC                       = 0x0C
RDTC_REPORT_MOST_RECENT_TEST_FAILED_DTC               = 0x0D
RDTC_REPORT_MOST_RECENT_CONFIRMED_DTC                 = 0x0E
RDTC_REPORT_DTC_FAULT_DETECTION_COUNTER               = 0x14
RDTC_REPORT_DTC_WITH_PERMANENT_STATUS                 = 0x15
RDTC_REPORT_DTC_EXT_DATA_RECORD_BY_RECORD_NUMBER      = 0x16
RDTC_REPORT_USER_DEF_MEMORY_DTC_BY_STATUS_MASK        = 0x17
RDTC_REPORT_USER_DEF_MEMORY_DTC_SNAPSHOT_BY_DTC       = 0x18
RDTC_REPORT_USER_DEF_MEMORY_DTC_EXT_DATA_RECORD       = 0x19
RDTC_REPORT_WWHOBD_DTC_BY_MASK_RECORD                 = 0x42
RDTC_REPORT_WWHOBD_DTC_WITH_PERMANENT_STATUS          = 0x55


# =============================================================================
# DTCStatusMask bit definitions -- ISO 14229-1:2020 §D.2 Table D.2
# =============================================================================
DTC_STATUS_TEST_FAILED                        = 0x01
DTC_STATUS_TEST_FAILED_THIS_OPERATION_CYCLE   = 0x02
DTC_STATUS_PENDING_DTC                        = 0x04
DTC_STATUS_CONFIRMED_DTC                      = 0x08
DTC_STATUS_TEST_NOT_COMPLETED_SINCE_LAST_CLEAR= 0x10
DTC_STATUS_TEST_FAILED_SINCE_LAST_CLEAR       = 0x20
DTC_STATUS_TEST_NOT_COMPLETED_THIS_CYCLE      = 0x40
DTC_STATUS_WARNING_INDICATOR_REQUESTED        = 0x80


# =============================================================================
# DTCSeverity bit definitions -- ISO 14229-1:2020 §D.2 Table D.3
# =============================================================================
DTC_SEVERITY_MAINTENANCE_ONLY                 = 0x20
DTC_SEVERITY_CHECK_AT_NEXT_HALT               = 0x40
DTC_SEVERITY_CHECK_IMMEDIATELY                = 0x80


# =============================================================================
# Negative Response Codes (NRC) -- ISO 14229-1:2020 Annex A.1 Table A.1
# Identifiers and names taken verbatim from the standard.
# =============================================================================
NRC_GENERAL_REJECT                                       = 0x10
NRC_SERVICE_NOT_SUPPORTED                                = 0x11
NRC_SUB_FUNCTION_NOT_SUPPORTED                           = 0x12
NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT           = 0x13
NRC_RESPONSE_TOO_LONG                                    = 0x14
NRC_BUSY_REPEAT_REQUEST                                  = 0x21
NRC_CONDITIONS_NOT_CORRECT                               = 0x22
NRC_REQUEST_SEQUENCE_ERROR                               = 0x24
NRC_NO_RESPONSE_FROM_SUBNET_COMPONENT                    = 0x25
NRC_FAILURE_PREVENTS_EXECUTION_OF_REQUESTED_ACTION       = 0x26
NRC_REQUEST_OUT_OF_RANGE                                 = 0x31
NRC_SECURITY_ACCESS_DENIED                               = 0x33
NRC_AUTHENTICATION_REQUIRED                              = 0x34
NRC_INVALID_KEY                                          = 0x35
NRC_EXCEEDED_NUMBER_OF_ATTEMPTS                          = 0x36
NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED                      = 0x37
NRC_SECURE_DATA_TRANSMISSION_REQUIRED                    = 0x38
NRC_SECURE_DATA_TRANSMISSION_NOT_ALLOWED                 = 0x39
NRC_SECURE_DATA_VERIFICATION_FAILED                      = 0x3A
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_TIME_PERIOD  = 0x50
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_SIGNATURE    = 0x51
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_CHAIN_OF_TRUST = 0x52
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_TYPE         = 0x53
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_FORMAT       = 0x54
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_CONTENT      = 0x55
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_SCOPE        = 0x56
NRC_CERTIFICATE_VERIFICATION_FAILED_INVALID_CERTIFICATE  = 0x57
NRC_OWNERSHIP_VERIFICATION_FAILED                        = 0x58
NRC_CHALLENGE_CALCULATION_FAILED                         = 0x59
NRC_SETTING_ACCESS_RIGHTS_FAILED                         = 0x5A
NRC_SESSION_KEY_CREATION_OR_DERIVATION_FAILED            = 0x5B
NRC_CONFIGURATION_DATA_USAGE_FAILED                      = 0x5C
NRC_DEAUTHENTICATION_FAILED                              = 0x5D
NRC_UPLOAD_DOWNLOAD_NOT_ACCEPTED                         = 0x70
NRC_TRANSFER_DATA_SUSPENDED                              = 0x71
NRC_GENERAL_PROGRAMMING_FAILURE                          = 0x72
NRC_WRONG_BLOCK_SEQUENCE_COUNTER                         = 0x73
NRC_REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING          = 0x78
NRC_SUB_FUNCTION_NOT_SUPPORTED_IN_ACTIVE_SESSION         = 0x7E
NRC_SERVICE_NOT_SUPPORTED_IN_ACTIVE_SESSION              = 0x7F
NRC_RPM_TOO_HIGH                                         = 0x81
NRC_RPM_TOO_LOW                                          = 0x82
NRC_ENGINE_IS_RUNNING                                    = 0x83
NRC_ENGINE_IS_NOT_RUNNING                                = 0x84
NRC_ENGINE_RUN_TIME_TOO_LOW                              = 0x85
NRC_TEMPERATURE_TOO_HIGH                                 = 0x86
NRC_TEMPERATURE_TOO_LOW                                  = 0x87
NRC_VEHICLE_SPEED_TOO_HIGH                               = 0x88
NRC_VEHICLE_SPEED_TOO_LOW                                = 0x89
NRC_THROTTLE_PEDAL_TOO_HIGH                              = 0x8A
NRC_THROTTLE_PEDAL_TOO_LOW                               = 0x8B
NRC_TRANSMISSION_RANGE_NOT_IN_NEUTRAL                    = 0x8C
NRC_TRANSMISSION_RANGE_NOT_IN_GEAR                       = 0x8D
NRC_BRAKE_SWITCHES_NOT_CLOSED                            = 0x8F
NRC_SHIFTER_LEVER_NOT_IN_PARK                            = 0x90
NRC_TORQUE_CONVERTER_CLUTCH_LOCKED                       = 0x91
NRC_VOLTAGE_TOO_HIGH                                     = 0x92
NRC_VOLTAGE_TOO_LOW                                      = 0x93
NRC_RESOURCE_TEMPORARILY_NOT_AVAILABLE                   = 0x94

NRC_NAMES = {
    0x10: "generalReject",
    0x11: "serviceNotSupported",
    0x12: "subFunctionNotSupported",
    0x13: "incorrectMessageLengthOrInvalidFormat",
    0x14: "responseTooLong",
    0x21: "busyRepeatRequest",
    0x22: "conditionsNotCorrect",
    0x24: "requestSequenceError",
    0x25: "noResponseFromSubnetComponent",
    0x26: "failurePreventsExecutionOfRequestedAction",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x34: "authenticationRequired",
    0x35: "invalidKey",
    0x36: "exceededNumberOfAttempts",
    0x37: "requiredTimeDelayNotExpired",
    0x38: "secureDataTransmissionRequired",
    0x39: "secureDataTransmissionNotAllowed",
    0x3A: "secureDataVerificationFailed",
    0x70: "uploadDownloadNotAccepted",
    0x71: "transferDataSuspended",
    0x72: "generalProgrammingFailure",
    0x73: "wrongBlockSequenceCounter",
    0x78: "requestCorrectlyReceived-ResponsePending",
    0x7E: "subFunctionNotSupportedInActiveSession",
    0x7F: "serviceNotSupportedInActiveSession",
    0x81: "rpmTooHigh",
    0x82: "rpmTooLow",
    0x83: "engineIsRunning",
    0x84: "engineIsNotRunning",
    0x85: "engineRunTimeTooLow",
    0x86: "temperatureTooHigh",
    0x87: "temperatureTooLow",
    0x88: "vehicleSpeedTooHigh",
    0x89: "vehicleSpeedTooLow",
    0x8A: "throttle/PedalTooHigh",
    0x8B: "throttle/PedalTooLow",
    0x8C: "transmissionRangeNotInNeutral",
    0x8D: "transmissionRangeNotInGear",
    0x8F: "brakeSwitch(es)NotClosed",
    0x90: "shifterLeverNotInPark",
    0x91: "torqueConverterClutchLocked",
    0x92: "voltageTooHigh",
    0x93: "voltageTooLow",
    0x94: "resourceTemporarilyNotAvailable",
}


def decode_nrc(nrc: int) -> str:
    """Return the standardized name for a UDS NRC byte, or '<reserved>' if unknown."""
    return NRC_NAMES.get(nrc, f"<reserved 0x{nrc:02X}>")


# =============================================================================
# Standardised Data Identifiers (DIDs) -- ISO 14229-1:2020 Annex C Table C.1
# Only the ISO/SAE-defined identifiers are enumerated. Manufacturer-specific
# ranges are documented but not populated with assumed values.
# =============================================================================

# Vehicle / ECU identification data (range 0xF180-0xF1FF; ISO defines these
# individual identifiers and reserves the rest of the range for OEM use)
DID_BOOT_SOFTWARE_IDENTIFICATION                  = 0xF180
DID_APPLICATION_SOFTWARE_IDENTIFICATION           = 0xF181
DID_APPLICATION_DATA_IDENTIFICATION               = 0xF182
DID_BOOT_SOFTWARE_FINGERPRINT                     = 0xF183
DID_APPLICATION_SOFTWARE_FINGERPRINT              = 0xF184
DID_APPLICATION_DATA_FINGERPRINT                  = 0xF185
DID_ACTIVE_DIAGNOSTIC_SESSION                     = 0xF186
DID_VEHICLE_MANUFACTURER_SPARE_PART_NUMBER        = 0xF187
DID_VEHICLE_MANUFACTURER_ECU_SOFTWARE_NUMBER      = 0xF188
DID_VEHICLE_MANUFACTURER_ECU_SOFTWARE_VERSION     = 0xF189
DID_SYSTEM_SUPPLIER_IDENTIFIER                    = 0xF18A
DID_ECU_MANUFACTURING_DATE                        = 0xF18B
DID_ECU_SERIAL_NUMBER                             = 0xF18C
DID_SUPPORTED_FUNCTIONAL_UNITS                    = 0xF18D
DID_VEHICLE_MANUFACTURER_KIT_ASSEMBLY_PART_NUMBER = 0xF18E
DID_VIN                                           = 0xF190
DID_VEHICLE_MANUFACTURER_ECU_HARDWARE_NUMBER      = 0xF191
DID_SYSTEM_SUPPLIER_ECU_HARDWARE_NUMBER           = 0xF192
DID_SYSTEM_SUPPLIER_ECU_HARDWARE_VERSION          = 0xF193
DID_SYSTEM_SUPPLIER_ECU_SOFTWARE_NUMBER           = 0xF194
DID_SYSTEM_SUPPLIER_ECU_SOFTWARE_VERSION          = 0xF195
DID_EXHAUST_REGULATION_OR_TYPE_APPROVAL_NUMBER    = 0xF196
DID_SYSTEM_NAME_OR_ENGINE_TYPE                    = 0xF197
DID_REPAIR_SHOP_CODE_OR_TESTER_SERIAL_NUMBER      = 0xF198
DID_PROGRAMMING_DATE                              = 0xF199
DID_CALIBRATION_REPAIR_SHOP_CODE_OR_TESTER_SERIAL = 0xF19A
DID_CALIBRATION_EQUIPMENT_SOFTWARE_NUMBER         = 0xF19B
DID_ECU_INSTALLATION_DATE                         = 0xF19D
DID_ODX_FILE_IDENTIFIER                           = 0xF19E
DID_ENTITY                                        = 0xF19F

# DID range map (informative; from ISO 14229-1:2020 §10.2.4 Table 81)
DID_RANGE_MAP = (
    (0x0000, 0x00FF, "ISOSAEReserved"),
    (0x0100, 0xA5FF, "vehicleManufacturerSpecific"),
    (0xA600, 0xA7FF, "reservedForLegislativeUse"),
    (0xA800, 0xACFF, "vehicleManufacturerSpecific"),
    (0xAD00, 0xAFFF, "reservedForLegislativeUse"),
    (0xB000, 0xB1FF, "vehicleManufacturerSpecific"),
    (0xB200, 0xBFFF, "reservedForLegislativeUse"),
    (0xC000, 0xC2FF, "vehicleManufacturerSpecific"),
    (0xC300, 0xCEFF, "reservedForLegislativeUse"),
    (0xCF00, 0xEFFF, "vehicleManufacturerSpecific"),
    (0xF000, 0xF00F, "networkConfigurationDataForTractorTrailerApplication"),
    (0xF010, 0xF0FF, "vehicleManufacturerSpecific"),
    (0xF100, 0xF17F, "identificationOptionVehicleManufacturerSpecific"),
    (0xF180, 0xF19F, "identificationOptionVehicleManufacturerSpecific (ISO defined)"),
    (0xF1A0, 0xF1EF, "identificationOptionVehicleManufacturerSpecific"),
    (0xF1F0, 0xF1FF, "identificationOptionSystemSupplierSpecific"),
    (0xF200, 0xF2FF, "periodicDataIdentifier"),
    (0xF300, 0xF3FF, "dynamicallyDefinedDataIdentifier"),
    (0xF400, 0xF4FF, "OBD DataIdentifier"),
    (0xF500, 0xF5FF, "OBD DataIdentifier"),
    (0xF600, 0xF6FF, "OBDMonitorDataIdentifier"),
    (0xF700, 0xF7FF, "OBDMonitorDataIdentifier"),
    (0xF800, 0xF8FF, "OBDInfoTypeDataIdentifier"),
    (0xF900, 0xF9FF, "tachographDataIdentifier"),
    (0xFA00, 0xFA0F, "airbagDeploymentDataIdentifier"),
    (0xFA10, 0xFAFF, "safetySystemDataIdentifier"),
    (0xFB00, 0xFCFF, "reservedForLegislativeUse"),
    (0xFD00, 0xFEFF, "systemSupplierSpecific"),
    (0xFF00, 0xFFFF, "ISOSAEReserved"),
)


def classify_did(did: int) -> str:
    """Return the standardized range name for a Data Identifier value."""
    for lo, hi, name in DID_RANGE_MAP:
        if lo <= did <= hi:
            return name
    return "unknown"


# =============================================================================
# DTC formatting helpers -- SAE J2012 / ISO 15031-6
# =============================================================================
# First nibble of byte-0 selects the DTC system letter:
DTC_SYSTEM_LETTERS = {0: "P", 1: "P", 2: "P", 3: "P",   # Powertrain
                      4: "C", 5: "C", 6: "C", 7: "C",   # Chassis
                      8: "B", 9: "B", 0xA: "B", 0xB: "B",  # Body
                      0xC: "U", 0xD: "U", 0xE: "U", 0xF: "U"}  # Network


def decode_dtc(byte_hi: int, byte_lo: int) -> str:
    """Format a two-byte DTC into the canonical SAE J2012 string (e.g. P0301)."""
    letter = DTC_SYSTEM_LETTERS[(byte_hi >> 4) & 0xF]
    d1 = (byte_hi >> 4) & 0x3   # SAE/Manufacturer indicator (0=SAE, 1=Mfr, 2=SAE2, 3=Mfr2)
    d2 = byte_hi & 0xF
    d3 = (byte_lo >> 4) & 0xF
    d4 = byte_lo & 0xF
    return f"{letter}{d1}{d2:X}{d3:X}{d4:X}"


# =============================================================================
# ISO 15765-4 (UDS-on-CAN) physical addressing -- ISO 15765-4:2021 §6.3
# =============================================================================
OBD_FUNCTIONAL_REQUEST_ID_11BIT         = 0x7DF
OBD_PHYSICAL_REQUEST_ID_MIN_11BIT       = 0x7E0
OBD_PHYSICAL_REQUEST_ID_MAX_11BIT       = 0x7E7
OBD_PHYSICAL_RESPONSE_ID_MIN_11BIT      = 0x7E8
OBD_PHYSICAL_RESPONSE_ID_MAX_11BIT      = 0x7EF
OBD_FUNCTIONAL_REQUEST_ID_29BIT         = 0x18DB33F1
OBD_PHYSICAL_REQUEST_ID_BASE_29BIT      = 0x18DA00F1   # 0x00 = target ECU; tester ID = 0xF1
OBD_PHYSICAL_RESPONSE_ID_BASE_29BIT     = 0x18DAF100   # tester 0xF1 = destination

# Tester source address used in 29-bit addressing (ISO 15765-4 §6.3.2.3)
ISO_15765_TESTER_ADDRESS                = 0xF1


# =============================================================================
# ISO 15765-2 network-layer Protocol Control Information (PCI) -- §6.5
# Single-byte PCI nibble values when CAN frame is unsegmented (FS/Pad mode).
# =============================================================================
PCI_SINGLE_FRAME                        = 0x00   # 0x0_ low nibble = length
PCI_FIRST_FRAME                         = 0x10
PCI_CONSECUTIVE_FRAME                   = 0x20
PCI_FLOW_CONTROL                        = 0x30

# Flow Control sub-field FS values
FC_CONTINUE_TO_SEND                     = 0x00
FC_WAIT                                 = 0x01
FC_OVERFLOW                             = 0x02


# =============================================================================
# Authentication (0x29) sub-functions -- ISO 14229-1:2020 §9.6.2
# (Added in 2020 revision)
# =============================================================================
AUTH_DEAUTHENTICATE                                      = 0x00
AUTH_VERIFY_CERT_UNIDIRECTIONAL                          = 0x01
AUTH_VERIFY_CERT_BIDIRECTIONAL                           = 0x02
AUTH_PROOF_OF_OWNERSHIP                                  = 0x03
AUTH_TRANSMIT_CERT                                       = 0x04
AUTH_REQUEST_CHALLENGE_FOR_AUTH                          = 0x05
AUTH_VERIFY_PROOF_OF_OWNERSHIP_UNIDIRECTIONAL            = 0x06
AUTH_VERIFY_PROOF_OF_OWNERSHIP_BIDIRECTIONAL             = 0x07
AUTH_AUTHENTICATION_CONFIGURATION                        = 0x08
