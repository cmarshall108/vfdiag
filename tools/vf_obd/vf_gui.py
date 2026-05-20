import os
import sys
import time
import threading
from typing import Optional, List

# Ensure we are in the correct folder to run
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import pyqtSignal, QObject, QThread
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QCheckBox, QPlainTextEdit, QGroupBox,
        QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
        QProgressBar, QSplitter, QFileDialog, QComboBox
    )
except ImportError:
    # We will guide the user to install PyQt5 if it is missing
    print("PyQt5 is not installed. To run the GUI, please install it using: pip install PyQt5")
    # Define placeholder classes so code passes syntax check
    class QMainWindow: pass
    class QWidget: pass
    class QObject: pass
    class QThread: pass

import j2534
import vf_obd


class TextRedirector(QObject):
    """Signals written text to be printed in the GUI log window."""
    text_written = pyqtSignal(str)

    def write(self, text: str) -> None:
        self.text_written.emit(text)

    def flush(self) -> None:
        pass


class CommandWorker(QThread):
    """Background thread to execute OBD commands without freezing the Qt Main GUI thread."""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, command_name: str, args_dict: dict):
        super().__init__()
        self.command_name = command_name
        self.args_dict = args_dict
        self._stop_event = threading.Event()

    def run(self):
        # Build mock namespace matching argparse output
        class MockArgs:
            def __init__(self, d):
                for k, v in d.items():
                    setattr(self, k, v)
        
        args = MockArgs(self.args_dict)
        
        # Override argv for the automatic session logger inside main
        original_argv = sys.argv
        sys.argv = ["vf_obd_gui.py", self.command_name]
        
        # Retrieve subcommand handler from vf_obd
        handler = {
            "doctor": vf_obd.cmd_doctor,
            "vin": vf_obd.cmd_vin,
            "scan": vf_obd.cmd_scan,
            "clear": vf_obd.cmd_clear,
            "clear-physical": vf_obd.cmd_clear_physical,
            "ecu": vf_obd.cmd_ecu,
            "info": vf_obd.cmd_info,
            "hvil": vf_obd.cmd_hvil,
            "uds-discover": vf_obd.cmd_uds_discover,
            "can-watch": vf_obd.cmd_can_watch,
            "live": vf_obd.cmd_live,
            "monitor": vf_obd.cmd_monitor,
        }.get(self.command_name)

        if not handler:
            self.output_signal.emit(f"Unknown subcommand tool: {self.command_name}\n")
            self.finished_signal.emit(-1)
            sys.argv = original_argv
            return

        exit_code = -1
        try:
            # We call the main wrapper of vf_obd to take advantage of TeeWriter and file-logging setup automatically.
            # However, since we want background execution, we will call the handler directly.
            # To preserve session files, we wrap the handler call in the same setup as main.
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(script_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_filename = f"session_{timestamp}_{self.command_name}_gui.log"
            log_filepath = os.path.join(log_dir, log_filename)

            log_file = None
            original_stdout = sys.stdout
            original_stderr = sys.stderr

            try:
                log_file = open(log_filepath, "w", encoding="utf-8")
                log_file.write(f"=== GUI DIAGNOSTIC SESSION START: {time.asctime()} ===\n")
                log_file.write(f"Command run: {self.command_name}\n")
                log_file.write(f"================================================\n\n")
                log_file.flush()

                # Redirect output so print statements go to BOTH the file and our custom GUI redirector
                class DoubleWriter:
                    def __init__(self, f_log, gui_emitter):
                        self.f_log = f_log
                        self.gui_emitter = gui_emitter
                    def write(self, s):
                        if self.f_log:
                            try:
                                self.f_log.write(s)
                                self.f_log.flush()
                            except Exception:
                                pass
                        self.gui_emitter.emit(s)
                    def flush(self):
                        pass

                sys.stdout = DoubleWriter(log_file, self.output_signal)
                sys.stderr = DoubleWriter(log_file, self.output_signal)
            except Exception as exc:
                self.output_signal.emit(f"Warning: could not open dynamic GUI session file: {exc}\n")

            exit_code = handler(args)

        except Exception as exc:
            self.output_signal.emit(f"\nExecution error: {exc}\n")
            exit_code = -1
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if log_file:
                try:
                    log_file.write(f"\n================================================\n")
                    log_file.write(f"=== GUI DIAGNOSTIC SESSION END: {time.asctime()} ===\n")
                    log_file.close()
                except Exception:
                    pass
                self.output_signal.emit(f"\nSession log captured: tools/vf_obd/logs/{log_filename}\n")
            sys.argv = original_argv
            self.finished_signal.emit(exit_code)


class VinFastDiagGUI(QMainWindow):
    """The masterclass VinFast VF 8/VF 9 pyqt5 OEM replacement suite."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VinFast OEM Diagnostic Replacement Tool (VF 8 & VF 9)")
        self.resize(1100, 750)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e24;
                color: #f0f0f2;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QGroupBox {
                border: 2px solid #3a3a45;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #0088cc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
            QPushButton:pressed {
                background-color: #005999;
            }
            QPushButton:disabled {
                background-color: #4a4a50;
                color: #8a8a90;
            }
            QPushButton#clear_btn {
                background-color: #cc3333;
            }
            QPushButton#clear_btn:hover {
                background-color: #ff4444;
            }
            QLineEdit, QComboBox {
                background-color: #2d2d37;
                border: 1px solid #4a4a58;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a45;
                background-color: #1e1e24;
            }
            QTabBar::tab {
                background-color: #2b2b35;
                border: 1px solid #3a3a45;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e24;
                border-bottom-color: #1e1e24;
                color: #0088cc;
                font-weight: bold;
            }
            QPlainTextEdit {
                background-color: #0c0c10;
                color: #00ff66;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 1px solid #2d2d37;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #3a3a45;
                border-radius: 4px;
                text-align: center;
                background-color: #0c0c10;
            }
            QProgressBar::chunk {
                background-color: #00ff66;
            }
            QTableWidget {
                gridline-color: #383842;
                background-color: #1a1a20;
                alternate-background-color: #22222a;
            }
            QHeaderView::section {
                background-color: #2d2d37;
                color: #0088cc;
                padding: 4px;
                border: 1px solid #383842;
                font-weight: bold;
            }
        """)

        self.current_worker: Optional[CommandWorker] = None
        self._init_ui()
        self._discover_devices()

    def _init_ui(self):
        # Main layout splitter (top tabs & control, bottom console log output)
        main_splitter = QSplitter(QtCore.Qt.Vertical)
        
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(8, 8, 8, 8)
        
        # J2534 Hardware config header
        config_group = QGroupBox("J2534 Diagnostic Interface Hardware Setup")
        cfg_layout = QFormLayout(config_group)
        
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        cfg_layout.addRow("Select Cable/Driver:", self.device_combo)
        
        dll_row = QHBoxLayout()
        self.dll_path_edit = QLineEdit()
        self.browse_dll_btn = QPushButton("Browse DLL...")
        self.browse_dll_btn.clicked.connect(self._browse_dll)
        dll_row.addWidget(self.dll_path_edit)
        dll_row.addWidget(self.browse_dll_btn)
        cfg_layout.addRow("Manual DLL Path:", dll_row)

        opts_row = QHBoxLayout()
        self.timeout_spin = QLineEdit("2000")
        self.verbose_check = QCheckBox("Enable Verbose Multi-Frame Logging")
        opts_row.addWidget(QLabel("Timeout (ms):"))
        opts_row.addWidget(self.timeout_spin)
        opts_row.addWidget(self.verbose_check)
        cfg_layout.addRow("Communication Tweaks:", opts_row)
        
        top_layout.addWidget(config_group)

        # Main diagnostic action tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_doctor_tab(), "Cable Diagnostic (Doctor)")
        self.tabs.addTab(self._create_info_tab(), "Vehicle Identity")
        self.tabs.addTab(self._create_dtc_tab(), "DTC Fault Center")
        self.tabs.addTab(self._create_live_tab(), "Parameters & HVIL")
        self.tabs.addTab(self._create_uds_tab(), "UDS Developer Tools")
        top_layout.addWidget(self.tabs)
        
        main_splitter.addWidget(top_widget)

        # Bottom real-time console logger output
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(8, 0, 8, 8)
        
        hdr_row = QHBoxLayout()
        hdr_row.addWidget(QLabel("<b>Real-Time Live Diagnostic Monitor Logs</b>"))
        self.clear_logs_btn = QPushButton("Clear Output Pane")
        self.clear_logs_btn.clicked.connect(self._clear_logs)
        self.clear_logs_btn.setStyleSheet("background-color: #3a3a45;")
        hdr_row.addSpacer(1)
        hdr_row.addWidget(self.clear_logs_btn)
        console_layout.addLayout(hdr_row)
        
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        
        main_splitter.addWidget(console_widget)
        
        # Allocate initial sizes (70% top, 30% bottom console log)
        main_splitter.setSizes([500, 250])
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(main_splitter)
        self.setCentralWidget(container)

        self.statusBar().showMessage("VinFast Multi-ECU Diagnostic Suite Loaded. Choose your driver above.")

    def _create_doctor_tab(self) -> QWidget:
        tbl = QWidget()
        layout = QVBoxLayout(tbl)
        
        lbl = QLabel(
            "<h3>Verify hardware loop status and FTDI chip parameters</h3>"
            "This will parse local Windows configurations, attempt loading the native 32-bit Mini-VCI DLL,<br>"
            "and establish an initial handshake with the vehicle's functional CAN pins 6 & 14.<br>"
            "If communication errors or disconnected loops are identified, step-by-step diagnostic paths will be shown."
        )
        layout.addWidget(lbl)
        
        self.btn_run_doctor = QPushButton("🚀 Run Master Hardware Doctor Diagnostic")
        self.btn_run_doctor.setMinimumHeight(45)
        self.btn_run_doctor.setStyleSheet("font-size: 15px;")
        self.btn_run_doctor.clicked.connect(lambda: self._execute_command("doctor"))
        layout.addWidget(self.btn_run_doctor)
        layout.addStretch()
        return tbl

    def _create_info_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("<h3>Vehicle Deep Parameter Metadata Retrieval (Mode 09)</h3>"))
        
        row = QHBoxLayout()
        self.btn_get_vin = QPushButton("🚗 Read VIN (PID 02)")
        self.btn_get_vin.clicked.connect(lambda: self._execute_command("vin"))
        
        self.btn_get_ecu = QPushButton("🔍 Scan Online ECUs (PIDs 0A & 04)")
        self.btn_get_ecu.clicked.connect(lambda: self._execute_command("ecu"))
        
        self.btn_get_info = QPushButton("📋 Get Deep Info (Serials/CALID/CVN)")
        self.btn_get_info.clicked.connect(lambda: self._execute_command("info"))
        
        row.addWidget(self.btn_get_vin)
        row.addWidget(self.btn_get_ecu)
        row.addWidget(self.btn_get_info)
        layout.addLayout(row)
        
        info_label = QLabel(
            "<b>Explanation:</b><br>"
            "  - <b>VIN:</b> Queries module-specific VIN entries from OBD nodes.<br>"
            "  - <b>Scan ECUs:</b> Enumerate responsive controllers, custom boot parameters, and firmware version identifiers.<br>"
            "  - <b>Deep Info:</b> Gathers official calibration IDs, validation checksums (CVN), and controller physical serial numbers."
        )
        layout.addWidget(info_label)
        layout.addStretch()
        return tab

    def _create_dtc_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("<h3>Diagnostic Trouble Code (DTC) Diagnostics Center</h3>"))
        
        grp_scan = QGroupBox("A. Read Diagnostic Fault Codes")
        scan_lay = QVBoxLayout(grp_scan)
        
        chks = QHBoxLayout()
        self.chk_stored = QCheckBox("Mode 03 (Stored Codes)")
        self.chk_stored.setChecked(True)
        self.chk_pending = QCheckBox("Mode 07 (Pending/Intermittent)")
        self.chk_pending.setChecked(True)
        self.chk_permanent = QCheckBox("Mode 0A (Permanent Codes)")
        self.chk_permanent.setChecked(True)
        chks.addWidget(self.chk_stored)
        chks.addWidget(self.chk_pending)
        chks.addWidget(self.chk_permanent)
        scan_lay.addLayout(chks)
        
        self.btn_scan_dtcs = QPushButton("🔍 Fetch DTCs From Online Nodes")
        self.btn_scan_dtcs.clicked.connect(self._run_scan_dtcs)
        scan_lay.addWidget(self.btn_scan_dtcs)
        
        layout.addWidget(grp_scan)

        grp_clear = QGroupBox("B. Secure Reset & Memory Clearing Commands")
        clear_lay = QHBoxLayout(grp_clear)
        
        self.btn_clear_functional = QPushButton("⚠️ Broad Functional Broadcast Clear (Mode 04)")
        self.btn_clear_functional.setObjectName("clear_btn")
        self.btn_clear_functional.clicked.connect(lambda: self._run_clear(physical=False))
        
        self.btn_clear_physical = QPushButton("⚡ Force Sequential Physical Clear (per ECU)")
        self.btn_clear_physical.setObjectName("clear_btn")
        self.btn_clear_physical.clicked.connect(lambda: self._run_clear(physical=True))
        
        clear_lay.addWidget(self.btn_clear_functional)
        clear_lay.addWidget(self.btn_clear_physical)
        layout.addWidget(grp_clear)

        explanation = QLabel(
            "<b>Physical Sequential Clears</b> bypass security routing layers. Use them if central gateways "
            "are ignoring functional clears due to residual crash signals or collision locks."
        )
        layout.addWidget(explanation)
        layout.addStretch()
        return tab

    def _create_live_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("<h3>Live Parameter Logging & HVIL System Diagnostics</h3>"))
        
        row_btns = QHBoxLayout()
        self.btn_live_once = QPushButton("📊 Single Live Data Snapshot")
        self.btn_live_once.clicked.connect(lambda: self._execute_command("live", {"once": True}))
        
        self.btn_live_loop = QPushButton("🔄 Start Live Monitoring Loop")
        self.btn_live_loop.clicked.connect(lambda: self._execute_command("live", {"once": False}))
        
        self.btn_hvil_loop = QPushButton("🔋 Start Fast HVIL & Pre-Charge Monitor")
        self.btn_hvil_loop.clicked.connect(lambda: self._execute_command("hvil"))
        
        row_btns.addWidget(self.btn_live_once)
        row_btns.addWidget(self.btn_live_loop)
        row_btns.addWidget(self.btn_hvil_loop)
        layout.addLayout(row_btns)
        
        self.stop_loop_btn = QPushButton("⏹️ STOP Continuous Monitor Loop")
        self.stop_loop_btn.setStyleSheet("background-color: #5a5a65;")
        self.stop_loop_btn.setEnabled(False)
        self.stop_loop_btn.clicked.connect(self._stop_active_loop)
        layout.addWidget(self.stop_loop_btn)
        
        layout.addWidget(QLabel(
            "<b>Parameters Logged:</b><br>"
            "  - 12S Supply Battery, Ambient Temp, ECU Run Timer, HV Pack State of Charge (SoC), Vehicle Speed.<br>"
            "  - <b>HVIL Monitor (High Voltage Interlock Loop):</b> Continuously loops and warns you if the "
            "auxiliary battery drops under critical 11.5V or if contactors refuse to pre-charge."
        ))
        layout.addStretch()
        return tab

    def _create_uds_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("<h3>UDS Developer Scan Tools (ISO 14229)</h3>"))
        
        row_actions = QHBoxLayout()
        self.btn_uds_discover = QPushButton("📡 Query UDS Sessions & Security Seeds (0x7E0..0x7E7)")
        self.btn_uds_discover.clicked.connect(lambda: self._execute_command("uds-discover"))
        row_actions.addWidget(self.btn_uds_discover)
        
        layout.addLayout(row_actions)

        # Passive sniffer logs
        grp_sniff = QGroupBox("Raw CAN Bus Passive Logger / Delta Watcher")
        sniff_lay = QVBoxLayout(grp_sniff)
        
        form = QFormLayout()
        self.txt_watch_id = QLineEdit("0x7E8")
        form.addRow("ID to Delta-Watch (e.g. 0x7E8):", self.txt_watch_id)
        
        self.txt_out_csv = QLineEdit("")
        self.btn_browse_csv = QPushButton("Browse...")
        self.btn_browse_csv.clicked.connect(self._browse_csv)
        csv_row = QHBoxLayout()
        csv_row.addWidget(self.txt_out_csv)
        csv_row.addWidget(self.btn_browse_csv)
        form.addRow("Passive Trace Out CSV File (Optional):", csv_row)
        
        self.txt_include_ids = QLineEdit("")
        form.addRow("Filter IDs to Include only (comma-sep, e.g. 0x7E8,0x7E9):", self.txt_include_ids)
        self.txt_exclude_ids = QLineEdit("")
        form.addRow("Filter IDs to Ignore (comma-sep):", self.txt_exclude_ids)
        
        sniff_lay.addLayout(form)
        
        row_sniff_btns = QHBoxLayout()
        self.btn_start_watch = QPushButton("📊 Start Live Byte Delta-Watch (can-watch)")
        self.btn_start_watch.clicked.connect(self._run_can_watch)
        
        self.btn_start_sniffer = QPushButton("📁 Start Raw Passive Sniffer (monitor)")
        self.btn_start_sniffer.clicked.connect(self._run_sniffer)
        
        row_sniff_btns.addWidget(self.btn_start_watch)
        row_sniff_btns.addWidget(self.btn_start_sniffer)
        sniff_lay.addLayout(row_sniff_btns)
        
        layout.addWidget(grp_sniff)
        layout.addStretch()
        return tab

    def _discover_devices(self):
        self.device_combo.clear()
        devs = j2534.discover_j2534_devices()
        if not devs:
            self.device_combo.addItem("No J2534 drivers found in Windows registry", "")
            return
        
        for name, path in devs:
            self.device_combo.addItem(f"{name} ({path})", path)
            
        # Try auto-locating standard DLL
        default_dll = j2534.find_default_dll()
        if default_dll:
            self.dll_path_edit.setText(default_dll)
            # Match item in index
            for idx in range(self.device_combo.count()):
                if self.device_combo.itemData(idx) == default_dll:
                    self.device_combo.setCurrentIndex(idx)
                    break

    def _on_device_selected(self, idx):
        path = self.device_combo.itemData(idx)
        if path:
            self.dll_path_edit.setText(path)

    def _browse_dll(self):
        f, _ = QFileDialog.getOpenFileName(self, "Load J2534 passthru DLL module", "C:\\", "Dynamic Link Library (*.dll)")
        if f:
            self.dll_path_edit.setText(f)

    def _browse_csv(self):
        f, _ = QFileDialog.getSaveFileName(self, "Select sniffer export target CSV", "C:\\", "CSV files (*.csv)")
        if f:
            self.txt_out_csv.setText(f)

    def _clear_logs(self):
        self.console_output.clear()

    def _get_base_args(self) -> dict:
        return {
            "dll": self.dll_path_edit.text().strip() or None,
            "timeout_ms": int(self.timeout_spin.text().strip() or "2000"),
            "verbose": self.verbose_check.isChecked(),
        }

    def _execute_command(self, command_name: str, subcommand_opts: Optional[dict] = None):
        if self.current_worker and self.current_worker.isRunning():
            QMessageBox.warning(self, "Worker busy", "A diagnostic command is currently running in the background. Please stop it or wait for completion.")
            return

        self._clear_logs()
        self.statusBar().showMessage(f"Running command: {command_name}...")
        
        args = self._get_base_args()
        if subcommand_opts:
            args.update(subcommand_opts)
            
        # UI controls update
        self.stop_loop_btn.setEnabled(command_name in ("hvil", "live", "can-watch", "monitor") and not args.get("once", False))
        self._toggle_buttons(False)

        self.current_worker = CommandWorker(command_name, args)
        self.current_worker.output_signal.connect(self._append_console_output)
        self.current_worker.finished_signal.connect(self._on_worker_finished)
        self.current_worker.start()

    def _toggle_buttons(self, enabled: bool):
        self.btn_run_doctor.setEnabled(enabled)
        self.btn_get_vin.setEnabled(enabled)
        self.btn_get_ecu.setEnabled(enabled)
        self.btn_get_info.setEnabled(enabled)
        self.btn_scan_dtcs.setEnabled(enabled)
        self.btn_clear_functional.setEnabled(enabled)
        self.btn_clear_physical.setEnabled(enabled)
        self.btn_live_once.setEnabled(enabled)
        self.btn_live_loop.setEnabled(enabled)
        self.btn_hvil_loop.setEnabled(enabled)
        self.btn_uds_discover.setEnabled(enabled)
        self.btn_start_watch.setEnabled(enabled)
        self.btn_start_sniffer.setEnabled(enabled)

    def _append_console_output(self, text: str):
        # Keeps cursor at the bottom automatically
        self.console_output.insertPlainText(text)
        self.console_output.ensureCursorVisible()

    def _on_worker_finished(self, exit_code: int):
        self.statusBar().showMessage(f"Command execution completed. (Exit code: {exit_code})", 6000)
        self._toggle_buttons(True)
        self.stop_loop_btn.setEnabled(False)
        self.current_worker = None

    def _stop_active_loop(self):
        if self.current_worker and self.current_worker.isRunning():
            self._append_console_output("\n[GUI] Requesting cancellation of background thread...\n")
            # Because reading raw ctypes blocks, we can try to interrupt it.
            # KeyboardInterrupt is captured inside the runs of CommandWorker automatically.
            # To trigger this, we can raise a keyboard interrupt in the thread if python lets us, or we just rely on standard loop exits.
            # A cleaner approach is simulating driver disconnect if J2534 blocks, or using thread terminations of Python ctypes.
            # Alternatively, we can force-terminate the QThread to avoid un-killable J2534 blocks.
            self.current_worker.terminate()
            self.current_worker.wait()
            self._append_console_output("\n⚠️ Background diagnostic thread forcefully stopped.\n")
            self._on_worker_finished(130)

    # Subcommand Helpers with custom options
    def _run_scan_dtcs(self):
        modes = []
        if self.chk_stored.isChecked():
            modes.append(0x03)
        if self.chk_pending.isChecked():
            modes.append(0x07)
        if self.chk_permanent.isChecked():
            modes.append(0x0A)
            
        if not modes:
            QMessageBox.critical(self, "Invalid Selection", "At least one DTC Mode must be checked!")
            return
            
        self._execute_command("scan", {"modes": modes})

    def _run_clear(self, physical: bool):
        desc = (
            "This will issue a sequential, physical OBD-II Mode 04 direct command mapping separate addresses 0x7E0..0x7E7 instead of a single functional group address.\n\nUse this to bypass secure central gateway routing filters."
            if physical else
            "This will broadcast standard OBD-II Mode 04 commands to the functional address 0x7DF.\n\nAll compliant powertrain and backup auxiliary modules will reset fault thresholds."
        )
        ans = QMessageBox.warning(
            self,
            "Confirm Diagnostic Memory Reset",
            f"⚠️ <b>WARNING:</b> You are about to clear diagnostic troubles codes & emissions checklists.\n\n{desc}\n\nAre you sure you want to proceed?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if ans == QMessageBox.Yes:
            command = "clear-physical" if physical else "clear"
            self._execute_command(command, {"yes": True})

    def _run_can_watch(self):
        t_id = self.txt_watch_id.text().strip()
        if not t_id:
            QMessageBox.critical(self, "Invalid ID", "Please target a valid CAN ID for byte monitoring.")
            return
        self._execute_command("can-watch", {"target_id": t_id})

    def _run_sniffer(self):
        csv_file = self.txt_out_csv.text().strip() or None
        
        # Parse include IDs
        include_list = None
        inc_str = self.txt_include_ids.text().strip()
        if inc_str:
            include_list = [x.strip() for x in inc_str.split(",") if x.strip()]
            
        exclude_list = None
        exc_str = self.txt_exclude_ids.text().strip()
        if exc_str:
            exclude_list = [x.strip() for x in exc_str.split(",") if x.strip()]
            
        self._execute_command("monitor", {
            "out": csv_file,
            "id": include_list,
            "exclude_id": exclude_list
        })


def main():
    if sys.platform != "win32":
        print("This application requires Windows OS environment configs.")
        return 1
        
    app = QApplication(sys.argv)
    window = VinFastDiagGUI()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
