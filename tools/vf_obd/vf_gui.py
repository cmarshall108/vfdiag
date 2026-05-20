import os
import sys
import time
import threading
from typing import Optional, List

# Ensure we are in the correct folder to run
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import pyqtSignal, QObject, QThread, QSettings, QSize
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QCheckBox, QPlainTextEdit, QGroupBox,
        QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
        QProgressBar, QSplitter, QFileDialog, QComboBox, QStyle, QToolBar,
        QAction, QActionGroup, QStatusBar, QToolButton
    )
except ImportError:
    # We will guide the user to install PyQt5 if it is missing
    print("PyQt5 is not installed. To run the GUI, please install it using: pip install PyQt5")
    # Define placeholder classes so code passes syntax check
    class QMainWindow: pass
    class QWidget: pass
    class QObject: pass
    class QThread: pass
    class QStyle: pass

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
            "ev-bleed": vf_obd.cmd_ev_bleed,
            "ev-airbag": vf_obd.cmd_ev_airbag,
            "ev-contactor": vf_obd.cmd_ev_contactor,
            "ev-neutral": vf_obd.cmd_ev_neutral,
            "ev-epb": vf_obd.cmd_ev_epb,
            "tpms": vf_obd.cmd_tpms,
            "battery-soh": vf_obd.cmd_battery_soh,
            "charge-unlock": vf_obd.cmd_charge_unlock,
            "freeze-frame": vf_obd.cmd_freeze_frame,
            "readiness": vf_obd.cmd_readiness,
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
        self.resize(1180, 800)

        # Persisted user settings (theme, last DLL, etc.)
        self._settings = QSettings("VFDiag", "VinFastDiag")
        self._theme_name = self._settings.value("theme", "dark", type=str)
        if self._theme_name not in ("dark", "light"):
            self._theme_name = "dark"

        self.current_worker: Optional[CommandWorker] = None
        self._init_ui()
        self._apply_theme(self._theme_name)
        self._discover_devices()

    # ------------------------------------------------------------------
    # Theme support
    # ------------------------------------------------------------------
    def _dark_stylesheet(self) -> str:
        return """
            QWidget {
                background-color: #1e1e24;
                color: #f0f0f2;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QMainWindow, QDialog { background-color: #1e1e24; }
            QMenuBar { background-color: #2b2b35; color: #f0f0f2; padding: 2px; }
            QMenuBar::item { background: transparent; padding: 4px 10px; }
            QMenuBar::item:selected { background: #0088cc; color: white; }
            QMenu { background-color: #2b2b35; color: #f0f0f2; border: 1px solid #3a3a45; }
            QMenu::item:selected { background-color: #0088cc; color: white; }
            QToolBar {
                background-color: #2b2b35;
                border-bottom: 1px solid #3a3a45;
                spacing: 6px;
                padding: 4px;
            }
            QToolButton {
                background-color: #2b2b35;
                color: #f0f0f2;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolButton:hover { background-color: #3a3a48; border-color: #0088cc; }
            QToolButton:checked { background-color: #0088cc; color: white; }
            QStatusBar { background-color: #2b2b35; color: #f0f0f2; border-top: 1px solid #3a3a45; }
            QGroupBox {
                border: 2px solid #3a3a45;
                border-radius: 6px;
                margin-top: 14px;
                font-weight: bold;
                padding: 10px 8px 8px 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #4dbcff;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover { background-color: #0099ff; }
            QPushButton:pressed { background-color: #005999; }
            QPushButton:disabled { background-color: #4a4a50; color: #8a8a90; }
            QPushButton#clear_btn { background-color: #cc3333; }
            QPushButton#clear_btn:hover { background-color: #ff4444; }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #2d2d37;
                border: 1px solid #4a4a58;
                border-radius: 4px;
                padding: 4px;
                color: #f0f0f2;
                selection-background-color: #0088cc;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2d2d37;
                color: #f0f0f2;
                selection-background-color: #0088cc;
            }
            QCheckBox { spacing: 6px; }
            QCheckBox::indicator { width: 14px; height: 14px; }
            QTabWidget::pane {
                border: 1px solid #3a3a45;
                background-color: #1e1e24;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #2b2b35;
                color: #c8c8d0;
                border: 1px solid #3a3a45;
                padding: 8px 14px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e24;
                border-bottom-color: #1e1e24;
                color: #4dbcff;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected { background-color: #353541; color: #f0f0f2; }
            QPlainTextEdit {
                background-color: #0c0c10;
                color: #5dff95;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 1px solid #2d2d37;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #3a3a45;
                border-radius: 4px;
                text-align: center;
                background-color: #0c0c10;
                color: #f0f0f2;
            }
            QProgressBar::chunk { background-color: #00cc66; }
            QTableWidget {
                gridline-color: #383842;
                background-color: #1a1a20;
                alternate-background-color: #22222a;
                color: #f0f0f2;
            }
            QHeaderView::section {
                background-color: #2d2d37;
                color: #4dbcff;
                padding: 4px;
                border: 1px solid #383842;
                font-weight: bold;
            }
            QScrollArea { background-color: #1e1e24; border: none; }
            QScrollBar:vertical {
                background: #1e1e24; width: 12px; margin: 0; border: none;
            }
            QScrollBar::handle:vertical {
                background: #3a3a48; min-height: 24px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #4a4a58; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QSplitter::handle { background-color: #3a3a45; }
            QSplitter::handle:horizontal { width: 4px; }
            QSplitter::handle:vertical { height: 4px; }
            QToolTip { background-color: #2b2b35; color: #f0f0f2; border: 1px solid #0088cc; padding: 4px; }
        """

    def _light_stylesheet(self) -> str:
        return """
            QWidget {
                background-color: #f5f6f8;
                color: #1c1c22;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QMainWindow, QDialog { background-color: #f5f6f8; }
            QMenuBar { background-color: #e8eaee; color: #1c1c22; padding: 2px; border-bottom: 1px solid #d0d3d8; }
            QMenuBar::item { background: transparent; padding: 4px 10px; }
            QMenuBar::item:selected { background: #0078d4; color: white; }
            QMenu { background-color: #ffffff; color: #1c1c22; border: 1px solid #d0d3d8; }
            QMenu::item:selected { background-color: #0078d4; color: white; }
            QToolBar {
                background-color: #e8eaee;
                border-bottom: 1px solid #d0d3d8;
                spacing: 6px;
                padding: 4px;
            }
            QToolButton {
                background-color: #e8eaee;
                color: #1c1c22;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolButton:hover { background-color: #d8dde4; border-color: #0078d4; }
            QToolButton:checked { background-color: #0078d4; color: white; }
            QStatusBar { background-color: #e8eaee; color: #1c1c22; border-top: 1px solid #d0d3d8; }
            QGroupBox {
                border: 1px solid #c8ccd2;
                border-radius: 6px;
                margin-top: 14px;
                font-weight: bold;
                padding: 10px 8px 8px 8px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0078d4;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #c8ccd2; color: #80848a; }
            QPushButton#clear_btn { background-color: #d13438; }
            QPushButton#clear_btn:hover { background-color: #b22a2e; }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #ffffff;
                border: 1px solid #c8ccd2;
                border-radius: 4px;
                padding: 4px;
                color: #1c1c22;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1c1c22;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QCheckBox { spacing: 6px; }
            QCheckBox::indicator { width: 14px; height: 14px; }
            QTabWidget::pane {
                border: 1px solid #c8ccd2;
                background-color: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #e8eaee;
                color: #4a4d52;
                border: 1px solid #c8ccd2;
                padding: 8px 14px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                color: #0078d4;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected { background-color: #d8dde4; color: #1c1c22; }
            QPlainTextEdit {
                background-color: #1e1e24;
                color: #5dff95;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 1px solid #c8ccd2;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #c8ccd2;
                border-radius: 4px;
                text-align: center;
                background-color: #ffffff;
                color: #1c1c22;
            }
            QProgressBar::chunk { background-color: #107c10; }
            QTableWidget {
                gridline-color: #d0d3d8;
                background-color: #ffffff;
                alternate-background-color: #f5f6f8;
                color: #1c1c22;
            }
            QHeaderView::section {
                background-color: #e8eaee;
                color: #0078d4;
                padding: 4px;
                border: 1px solid #d0d3d8;
                font-weight: bold;
            }
            QScrollArea { background-color: #f5f6f8; border: none; }
            QScrollBar:vertical {
                background: #f5f6f8; width: 12px; margin: 0; border: none;
            }
            QScrollBar::handle:vertical {
                background: #c8ccd2; min-height: 24px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #a8acb2; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QSplitter::handle { background-color: #d0d3d8; }
            QSplitter::handle:horizontal { width: 4px; }
            QSplitter::handle:vertical { height: 4px; }
            QToolTip { background-color: #ffffff; color: #1c1c22; border: 1px solid #0078d4; padding: 4px; }
        """

    def _apply_theme(self, name: str) -> None:
        name = "light" if name == "light" else "dark"
        self._theme_name = name
        self.setStyleSheet(self._dark_stylesheet() if name == "dark" else self._light_stylesheet())
        # Persist
        try:
            self._settings.setValue("theme", name)
        except Exception:
            pass
        # Keep menu/toolbar toggle in sync
        if hasattr(self, "act_dark") and hasattr(self, "act_light"):
            self.act_dark.setChecked(name == "dark")
            self.act_light.setChecked(name == "light")
        if hasattr(self, "tb_theme_btn"):
            self.tb_theme_btn.setText(" Light Mode" if name == "dark" else " Dark Mode")
            icon = self.style().standardIcon(
                QStyle.SP_DialogResetButton if name == "dark" else QStyle.SP_DialogYesButton
            )
            self.tb_theme_btn.setIcon(icon)

    def _toggle_theme(self) -> None:
        self._apply_theme("light" if self._theme_name == "dark" else "dark")

    def _init_ui(self):
        self._build_menu_bar()
        self._build_tool_bar()

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
        self.browse_dll_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.browse_dll_btn.clicked.connect(self._browse_dll)
        dll_row.addWidget(self.dll_path_edit)
        dll_row.addWidget(self.browse_dll_btn)
        cfg_layout.addRow("Manual DLL Path:", dll_row)

        opts_row = QHBoxLayout()
        self.timeout_spin = QLineEdit("2000")
        self.timeout_spin.setMaximumWidth(80)
        self.verbose_check = QCheckBox("Enable Verbose Multi-Frame Logging")
        opts_row.addWidget(QLabel("Timeout (ms):"))
        opts_row.addWidget(self.timeout_spin)
        opts_row.addSpacing(20)
        opts_row.addWidget(self.verbose_check)
        opts_row.addStretch()
        cfg_layout.addRow("Communication Tweaks:", opts_row)
        
        top_layout.addWidget(config_group)

        # Main diagnostic action tabs with icons for easier navigation
        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(18, 18))
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.tabs.setUsesScrollButtons(True)
        st = self.style()
        self.tabs.addTab(self._create_doctor_tab(), st.standardIcon(QStyle.SP_ComputerIcon), "Cable Doctor")
        self.tabs.addTab(self._create_info_tab(), st.standardIcon(QStyle.SP_FileDialogInfoView), "Vehicle Identity")
        self.tabs.addTab(self._create_dtc_tab(), st.standardIcon(QStyle.SP_MessageBoxWarning), "DTC Fault Center")
        self.tabs.addTab(self._create_live_tab(), st.standardIcon(QStyle.SP_MediaPlay), "Parameters & HVIL")
        self.tabs.addTab(self._create_ev_tab(), st.standardIcon(QStyle.SP_BrowserReload), "EV Service Procedures")
        self.tabs.addTab(self._create_uds_tab(), st.standardIcon(QStyle.SP_FileIcon), "UDS Developer Tools")
        self.tabs.addTab(self._create_totp_tab(), st.standardIcon(QStyle.SP_DialogApplyButton), "MHU Security (TOTP)")
        top_layout.addWidget(self.tabs)
        
        main_splitter.addWidget(top_widget)

        # Bottom real-time console logger output
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(8, 0, 8, 8)
        
        hdr_row = QHBoxLayout()
        hdr_row.addWidget(QLabel("<b>Real-Time Live Diagnostic Monitor Logs</b>"))
        hdr_row.addStretch()
        self.save_logs_btn = QPushButton(" Save Log...")
        self.save_logs_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_logs_btn.clicked.connect(self._save_logs)
        hdr_row.addWidget(self.save_logs_btn)
        self.clear_logs_btn = QPushButton(" Clear Output Pane")
        self.clear_logs_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        self.clear_logs_btn.clicked.connect(self._clear_logs)
        self.clear_logs_btn.setObjectName("clear_btn")
        hdr_row.addWidget(self.clear_logs_btn)
        console_layout.addLayout(hdr_row)
        
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        
        main_splitter.addWidget(console_widget)
        
        # Allocate initial sizes (70% top, 30% bottom console log)
        main_splitter.setSizes([560, 240])
        main_splitter.setCollapsible(0, False)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(main_splitter)
        self.setCentralWidget(container)

        # Status bar with persistent run indicator
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.status_indicator = QLabel("Idle")
        self.status_indicator.setStyleSheet("padding: 0 10px; font-weight: bold;")
        sb.addPermanentWidget(self.status_indicator)
        sb.showMessage("Ready.")

    def _build_menu_bar(self) -> None:
        mb = self.menuBar()
        # File menu
        m_file = mb.addMenu("&File")
        act_save = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "&Save Console Log...", self)
        act_save.setShortcut("Ctrl+S")
        act_save.triggered.connect(lambda: self._save_logs())
        m_file.addAction(act_save)
        act_clear = QAction(self.style().standardIcon(QStyle.SP_DialogResetButton), "&Clear Console", self)
        act_clear.setShortcut("Ctrl+L")
        act_clear.triggered.connect(self._clear_logs)
        m_file.addAction(act_clear)
        m_file.addSeparator()
        act_quit = QAction("E&xit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        # View menu (theme toggle)
        m_view = mb.addMenu("&View")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        self.act_dark = QAction("&Dark Theme", self, checkable=True)
        self.act_light = QAction("&Light Theme", self, checkable=True)
        self.act_dark.triggered.connect(lambda: self._apply_theme("dark"))
        self.act_light.triggered.connect(lambda: self._apply_theme("light"))
        theme_group.addAction(self.act_dark)
        theme_group.addAction(self.act_light)
        m_view.addAction(self.act_dark)
        m_view.addAction(self.act_light)
        m_view.addSeparator()
        act_toggle = QAction("&Toggle Theme", self)
        act_toggle.setShortcut("Ctrl+T")
        act_toggle.triggered.connect(self._toggle_theme)
        m_view.addAction(act_toggle)

        # Help menu
        m_help = mb.addMenu("&Help")
        act_about = QAction(self.style().standardIcon(QStyle.SP_MessageBoxInformation), "&About", self)
        act_about.triggered.connect(self._show_about)
        m_help.addAction(act_about)
        act_shortcuts = QAction("&Keyboard Shortcuts", self)
        act_shortcuts.triggered.connect(self._show_shortcuts)
        m_help.addAction(act_shortcuts)

    def _build_tool_bar(self) -> None:
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        tb.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.addToolBar(tb)

        # Quick navigation: jump to a tab
        def jump(idx: int):
            self.tabs.setCurrentIndex(idx)

        tab_meta = [
            (QStyle.SP_ComputerIcon, "Doctor", 0),
            (QStyle.SP_FileDialogInfoView, "Identity", 1),
            (QStyle.SP_MessageBoxWarning, "DTCs", 2),
            (QStyle.SP_MediaPlay, "Live", 3),
            (QStyle.SP_BrowserReload, "EV Service", 4),
            (QStyle.SP_FileIcon, "UDS", 5),
            (QStyle.SP_DialogApplyButton, "TOTP", 6),
        ]
        for icon_id, label, idx in tab_meta:
            act = QAction(self.style().standardIcon(icon_id), label, self)
            act.setToolTip(f"Jump to {label} tab")
            act.triggered.connect(lambda _checked=False, i=idx: jump(i))
            tb.addAction(act)

        tb.addSeparator()

        # Theme toggle button (visible quick switch)
        self.tb_theme_btn = QToolButton()
        self.tb_theme_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tb_theme_btn.setToolTip("Toggle between dark and light themes (Ctrl+T)")
        self.tb_theme_btn.clicked.connect(self._toggle_theme)
        # Spacer pushes theme button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        tb.addWidget(spacer)
        tb.addWidget(self.tb_theme_btn)

        # Ctrl+1..7 jump shortcuts (added as hidden actions on the main window)
        for i in range(7):
            sc = QAction(self)
            sc.setShortcut(f"Ctrl+{i+1}")
            sc.triggered.connect(lambda _checked=False, idx=i: self.tabs.setCurrentIndex(idx))
            self.addAction(sc)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About VinFast Diagnostic Tool",
            "<h3>VinFast OEM Diagnostic Replacement Tool</h3>"
            "<p>Supports VF 8 and VF 9 platforms.</p>"
            "<p>Read-only by design where possible; all write procedures restore default ECU control "
            "on disconnect. Does not implement UDS services 0x2E, 0x34, or 0x36, so module firmware "
            "and configuration cannot be modified by this tool.</p>"
            "<p>Uses J2534 PassThru over ISO 15765-4 CAN @ 500 kbps.</p>",
        )

    def _show_shortcuts(self) -> None:
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            "<b>Ctrl+S</b> &nbsp; Save console log to file<br>"
            "<b>Ctrl+L</b> &nbsp; Clear console output<br>"
            "<b>Ctrl+T</b> &nbsp; Toggle Dark/Light theme<br>"
            "<b>Ctrl+Q</b> &nbsp; Exit application<br>"
            "<b>Ctrl+1..7</b> &nbsp; Jump to tab 1..7",
        )

    def _save_logs(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Console Log", "vf_obd_console.log", "Log files (*.log *.txt);;All files (*.*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console_output.toPlainText())
            self.statusBar().showMessage(f"Saved console log: {path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not save log file:\n{e}")

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
        
        self.btn_run_doctor = QPushButton(" Run Master Hardware Doctor Diagnostic")
        self.btn_run_doctor.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
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
        self.btn_get_vin = QPushButton(" Read VIN (PID 02)")
        self.btn_get_vin.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
        self.btn_get_vin.clicked.connect(lambda: self._execute_command("vin"))
        
        self.btn_get_ecu = QPushButton(" Scan Online ECUs (PIDs 0A & 04)")
        self.btn_get_ecu.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_get_ecu.clicked.connect(lambda: self._execute_command("ecu"))
        
        self.btn_get_info = QPushButton(" Get Deep Info (Serials/CALID/CVN)")
        self.btn_get_info.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))
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
        
        self.btn_scan_dtcs = QPushButton(" Search / Fetch DTCs From Online Nodes")
        self.btn_scan_dtcs.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.btn_scan_dtcs.clicked.connect(self._run_scan_dtcs)
        scan_lay.addWidget(self.btn_scan_dtcs)
        
        layout.addWidget(grp_scan)

        grp_clear = QGroupBox("B. Secure Reset & Memory Clearing Commands")
        clear_lay = QHBoxLayout(grp_clear)
        
        self.btn_clear_functional = QPushButton(" Broad Functional Broadcast Clear (Mode 04)")
        self.btn_clear_functional.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
        self.btn_clear_functional.setObjectName("clear_btn")
        self.btn_clear_functional.clicked.connect(lambda: self._run_clear(physical=False))
        
        self.btn_clear_physical = QPushButton(" Force Sequential Physical Clear (per ECU)")
        self.btn_clear_physical.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
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
        self.btn_live_once = QPushButton(" Single Live Data Snapshot")
        self.btn_live_once.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.btn_live_once.clicked.connect(lambda: self._execute_command("live", {"once": True}))
        
        self.btn_live_loop = QPushButton(" Start Live Monitoring Loop")
        self.btn_live_loop.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_live_loop.clicked.connect(lambda: self._execute_command("live", {"once": False}))
        
        self.btn_hvil_loop = QPushButton(" Start Fast HVIL & Pre-Charge Monitor")
        self.btn_hvil_loop.setIcon(self.style().standardIcon(QStyle.SP_CommandLink))
        self.btn_hvil_loop.clicked.connect(lambda: self._execute_command("hvil"))
        
        row_btns.addWidget(self.btn_live_once)
        row_btns.addWidget(self.btn_live_loop)
        row_btns.addWidget(self.btn_hvil_loop)
        layout.addLayout(row_btns)
        
        self.stop_loop_btn = QPushButton(" STOP Continuous Monitor Loop")
        self.stop_loop_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
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
        self.btn_uds_discover = QPushButton(" Query UDS Sessions & Security Seeds (0x7E0..0x7E7)")
        self.btn_uds_discover.setIcon(self.style().standardIcon(QStyle.SP_CustomBase))
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
        self.btn_browse_csv.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
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
        self.btn_start_watch = QPushButton(" Start Live Byte Delta-Watch (can-watch)")
        self.btn_start_watch.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.btn_start_watch.clicked.connect(self._run_can_watch)
        
        self.btn_start_sniffer = QPushButton(" Start Raw Passive Sniffer (monitor)")
        self.btn_start_sniffer.setIcon(self.style().standardIcon(QStyle.SP_DriveFDIcon))
        self.btn_start_sniffer.clicked.connect(self._run_sniffer)
        
        row_sniff_btns.addWidget(self.btn_start_watch)
        row_sniff_btns.addWidget(self.btn_start_sniffer)
        sniff_lay.addLayout(row_sniff_btns)
        
        layout.addWidget(grp_sniff)
        layout.addStretch()
        return tab

    def _create_ev_tab(self) -> QWidget:
        tab = QWidget()
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        layout.addWidget(QLabel("<h2>Standard EV Service, Assembly Recovery & Diagnostic Routines</h2>"))
        layout.addWidget(QLabel(
            "<span style='color:#e67e22;'><b>IMPORTANT ADVISORY:</b> These routines interact directly with primary "
            "battery systems, cabin restraints, and fast-flowing cooling loops. Ensure exact compliance with high-voltage "
            "safety procedures before triggering executions.</span>"
        ))

        # Procedure 1: Pump Purge
        grp_bleed = QGroupBox("Procedure 1: HV Battery Coolant Purge & Air Bleeding")
        bleed_lay = QVBoxLayout(grp_bleed)
        bleed_lay.setSpacing(10)
        bleed_lay.addWidget(QLabel(
            "Forces dual pump controllers (Node 0x7E1 / 0x7E2) into active high-duty circulation mode to flush "
            "airlocks after coolant repairs. Gathers real-time 12V stability checks."
        ))
        self.chk_bleed_safe = QCheckBox("I confirm the glycol coolant reservoir is filled to MAX level to prevent pump cavitation.")
        self.chk_bleed_safe.setStyleSheet("padding: 4px 0;")
        bleed_lay.addWidget(self.chk_bleed_safe)
        
        self.btn_run_bleed = QPushButton(" Start Coolant Loop Active Bleeding")
        self.btn_run_bleed.setMinimumHeight(32)
        self.btn_run_bleed.setIcon(self.style().standardIcon(QStyle.SP_DialogYesButton))
        self.btn_run_bleed.clicked.connect(self._run_bleed)
        bleed_lay.addWidget(self.btn_run_bleed)
        layout.addWidget(grp_bleed)

        # Procedure 2: Airbag Check
        grp_airbag = QGroupBox("Procedure 2: Cabin Restraints & srs Crash Audit")
        airbag_lay = QVBoxLayout(grp_airbag)
        airbag_lay.setSpacing(10)
        airbag_lay.addWidget(QLabel(
            "Queries the central Airbag controller (Node 0x7E3) for collision squib firing events, "
            "crash indicators, and routing locks constrained by physical impacts."
        ))
        self.chk_airbag_safe = QCheckBox("I confirm the vehicle is stationary, unoccupied, and all harness lines are clear.")
        self.chk_airbag_safe.setStyleSheet("padding: 4px 0;")
        airbag_lay.addWidget(self.chk_airbag_safe)
        
        self.btn_run_airbag = QPushButton(" Start Airbag Firing & Crash Lock Audit")
        self.btn_run_airbag.setMinimumHeight(32)
        self.btn_run_airbag.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
        self.btn_run_airbag.clicked.connect(self._run_airbag)
        airbag_lay.addWidget(self.btn_run_airbag)
        layout.addWidget(grp_airbag)

        # Procedure 3: Contactor welds and isolation resistance
        grp_bms = QGroupBox("Procedure 3: BMS Main Contactor Welds & Isolation Resistance Audit")
        bms_lay = QVBoxLayout(grp_bms)
        bms_lay.setSpacing(10)
        bms_lay.addWidget(QLabel(
            "Queries Battery Management (Node 0x7E4) to compute structural isolation resistance (R_iso) "
            "and examine physical weld checkpoint parameters on primary battery contactors."
        ))
        self.chk_bms_safe = QCheckBox("I confirm the orange Manual Service Disconnect (MSD) is fully locked and orange HV wires are isolated.")
        self.chk_bms_safe.setStyleSheet("padding: 4px 0;")
        bms_lay.addWidget(self.chk_bms_safe)
        
        self.btn_run_contactor = QPushButton(" Start Contactor Weld & Leakage Scan")
        self.btn_run_contactor.setMinimumHeight(32)
        self.btn_run_contactor.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.btn_run_contactor.clicked.connect(self._run_contactor)
        bms_lay.addWidget(self.btn_run_contactor)
        layout.addWidget(grp_bms)

        # Procedure 4: Emergency Neutral Force
        grp_neutral = QGroupBox("Procedure 4: Shifter SCU/GSM Emergency Override to Neutral")
        neutral_lay = QVBoxLayout(grp_neutral)
        neutral_lay.setSpacing(10)
        neutral_lay.addWidget(QLabel(
            "Initiates electronic shifter bypass (Node 0x7E5) using UDS Service 0x2F and Service 0x31 "
            "routine controls to override park shift locks. Useful for recovery winching when vehicles are stuck."
        ))
        self.chk_neutral_safe = QCheckBox("I verify the vehicle's wheels are fully chocked to prevent immediate rollback!")
        self.chk_neutral_safe.setStyleSheet("padding: 4px 0;")
        neutral_lay.addWidget(self.chk_neutral_safe)
        
        self.btn_run_neutral = QPushButton(" Trigger Emergency Neutral Shift Lock Override")
        self.btn_run_neutral.setMinimumHeight(32)
        self.btn_run_neutral.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.btn_run_neutral.clicked.connect(self._run_neutral)
        neutral_lay.addWidget(self.btn_run_neutral)
        layout.addWidget(grp_neutral)

        # Procedure 5: EPB Service Mode
        grp_epb = QGroupBox("Procedure 5: Electronic Parking Brake Service Mode")
        epb_lay = QVBoxLayout(grp_epb)
        epb_lay.setSpacing(10)
        epb_lay.addWidget(QLabel(
            "Retracts EPB caliper pistons (Node 0x7E6) so rear brake pads/rotors can be safely replaced. "
            "Required service — pistons cannot be pushed back mechanically on VF 8/9. Cleanup automatically "
            "exits service mode and restores default session on disconnect."
        ))
        self.chk_epb_safe = QCheckBox("Vehicle is on a lift/jack stands with wheels secured; I will re-engage EPB after service.")
        self.chk_epb_safe.setStyleSheet("padding: 4px 0;")
        epb_lay.addWidget(self.chk_epb_safe)
        self.btn_run_epb = QPushButton(" Enter EPB Service Mode (Retract Calipers)")
        self.btn_run_epb.setMinimumHeight(32)
        self.btn_run_epb.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_run_epb.clicked.connect(self._run_epb)
        epb_lay.addWidget(self.btn_run_epb)
        layout.addWidget(grp_epb)

        # Read-only diagnostic block
        grp_diag = QGroupBox("Read-Only Vehicle Diagnostics")
        diag_lay = QVBoxLayout(grp_diag)
        diag_lay.setSpacing(8)
        diag_lay.addWidget(QLabel(
            "Safe, read-only commands that never write configuration. Useful for inspection, "
            "pre-purchase evaluation, and emissions/state inspection prep."
        ))

        self.btn_run_tpms = QPushButton(" Read TPMS Sensors (4 Tires)")
        self.btn_run_tpms.setMinimumHeight(32)
        self.btn_run_tpms.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.btn_run_tpms.clicked.connect(lambda: self._execute_command("tpms"))
        diag_lay.addWidget(self.btn_run_tpms)

        self.btn_run_soh = QPushButton(" Read HV Battery State-of-Health & Cell Spread")
        self.btn_run_soh.setMinimumHeight(32)
        self.btn_run_soh.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.btn_run_soh.clicked.connect(lambda: self._execute_command("battery-soh"))
        diag_lay.addWidget(self.btn_run_soh)

        self.btn_run_ff = QPushButton(" Read OBD-II Freeze-Frame DTC Snapshot")
        self.btn_run_ff.setMinimumHeight(32)
        self.btn_run_ff.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.btn_run_ff.clicked.connect(lambda: self._execute_command("freeze-frame"))
        diag_lay.addWidget(self.btn_run_ff)

        self.btn_run_readiness = QPushButton(" Read OBD-II Readiness Monitor Status")
        self.btn_run_readiness.setMinimumHeight(32)
        self.btn_run_readiness.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.btn_run_readiness.clicked.connect(lambda: self._execute_command("readiness"))
        diag_lay.addWidget(self.btn_run_readiness)

        layout.addWidget(grp_diag)

        # Procedure 6: Charge Port Lock Release
        grp_chg = QGroupBox("Procedure 6: Charge Port Lock Force-Release")
        chg_lay = QVBoxLayout(grp_chg)
        chg_lay.setSpacing(10)
        chg_lay.addWidget(QLabel(
            "Forces the charge port latch actuator (Nodes 0x7E1 / 0x7E6) to the unlocked position when "
            "a cable is mechanically trapped. Cleanup restores default control on disconnect."
        ))
        self.chk_chg_safe = QCheckBox("Charging session is terminated and the HV contactors are confirmed OPEN.")
        self.chk_chg_safe.setStyleSheet("padding: 4px 0;")
        chg_lay.addWidget(self.chk_chg_safe)
        self.btn_run_chg_unlock = QPushButton(" Force-Release Stuck Charge Port Lock")
        self.btn_run_chg_unlock.setMinimumHeight(32)
        self.btn_run_chg_unlock.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.btn_run_chg_unlock.clicked.connect(self._run_charge_unlock)
        chg_lay.addWidget(self.btn_run_chg_unlock)
        layout.addWidget(grp_chg)

        layout.addStretch()
        scroll.setWidget(content_widget)
        return scroll

    def _create_totp_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("<h3>MHU Infotainment Engineering Menu Security Generator</h3>"))
        layout.addWidget(QLabel(
            "VinFast infotainment Head Units (MHU) restrict Engineering / OS Developer Menu Access "
            "using hourly HMAC-SHA256 Time-Based One-Time Passwords (TOTP). Generates standard hourly rolling tokens."
        ))
        
        grp_totp = QGroupBox("Dynamic Hourly Passcode Calculator")
        totp_lay = QFormLayout(grp_totp)
        
        self.txt_totp_vin = QLineEdit("LFG")
        self.txt_totp_vin.setToolTip("Must be exactly 17 Characters alphanumeric ASCII Vin")
        totp_lay.addRow("Vehicle Identification Number (VIN):", self.txt_totp_vin)
        
        self.txt_totp_secret = QLineEdit("")
        self.txt_totp_secret.setEchoMode(QLineEdit.Password)
        self.txt_totp_secret.setPlaceholderText("Enter Hex private keys or fallback raw password ASCII seed")
        totp_lay.addRow("Private Root Key / Hex Seed:", self.txt_totp_secret)
        
        row_opts = QHBoxLayout()
        self.btn_calc_totp = QPushButton(" Generate Authorization Code")
        self.btn_calc_totp.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.btn_calc_totp.clicked.connect(self._run_calc_totp)
        row_opts.addWidget(self.btn_calc_totp)
        totp_lay.addRow("", row_opts)
        
        layout.addWidget(grp_totp)
        
        self.lbl_totp_result = QLabel("")
        self.lbl_totp_result.setStyleSheet("font-size: 16px; font-weight: bold; color: #55ff55; padding: 10px;")
        layout.addWidget(self.lbl_totp_result)
        
        layout.addStretch()
        return tab

    def _run_calc_totp(self):
        vin = self.txt_totp_vin.text().strip().upper()
        secret = self.txt_totp_secret.text().strip()
        if len(vin) != 17:
            QMessageBox.warning(self, "Invalid Inputs", "A valid VinFast vehicle chassis VIN must be exactly 17 characters.")
            return
        if not secret:
            QMessageBox.warning(self, "Missing Key Secret", "Provide the unique Hex or ASCII root secret associated with this Head Unit's trust chain.")
            return
            
        import totp
        try:
            code, sec_left = totp.calculate_vin_totp(vin, secret)
            m_left = sec_left // 60
            s_left = sec_left % 60
            self.lbl_totp_result.setText(
                f"Generated Passcode: {code}\n"
                f"Validation Window Remaining: {m_left:02d}m {s_left:02d}s (Hourly Epoch)"
            )
            self._append_console_output(f"\n[TOTP CALCULATOR] Success: VIN {vin} generated active passcode: {code}\n")
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Failed to compute HMAC sequence: {str(e)}")

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
        if hasattr(self, "status_indicator"):
            self.status_indicator.setText(f"● Running: {command_name}")
            self.status_indicator.setStyleSheet("padding: 0 10px; font-weight: bold; color: #ffaa00;")
        
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
        self.btn_run_bleed.setEnabled(enabled)
        self.btn_run_airbag.setEnabled(enabled)
        self.btn_run_contactor.setEnabled(enabled)
        self.btn_run_neutral.setEnabled(enabled)
        self.btn_run_epb.setEnabled(enabled)
        self.btn_run_tpms.setEnabled(enabled)
        self.btn_run_soh.setEnabled(enabled)
        self.btn_run_ff.setEnabled(enabled)
        self.btn_run_readiness.setEnabled(enabled)
        self.btn_run_chg_unlock.setEnabled(enabled)

    def _append_console_output(self, text: str):
        # Keeps cursor at the bottom automatically
        self.console_output.insertPlainText(text)
        self.console_output.ensureCursorVisible()

    def _on_worker_finished(self, exit_code: int):
        msg = f"Command execution completed. (Exit code: {exit_code})"
        self.statusBar().showMessage(msg, 6000)
        if hasattr(self, "status_indicator"):
            ok = (exit_code == 0)
            color = "#2ea043" if ok else "#d13438"
            self.status_indicator.setText("✓ Idle" if ok else "✗ Error")
            self.status_indicator.setStyleSheet(f"padding: 0 10px; font-weight: bold; color: {color};")
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

    def _run_bleed(self):
        if not self.chk_bleed_safe.isChecked():
            QMessageBox.critical(
                self,
                "Safety Check Incomplete",
                "⚠️ <b>Access Denied:</b> You must acknowledge and check the safety checkbox confirming "
                "that the glycol coolant reservoir is filled before launching pumps in order to prevent cavitation.",
                QMessageBox.Ok
            )
            return
            
        val = QMessageBox.warning(
            self,
            "Confirm Coolant Loop Air Bleed Sequence",
            "🛠️ <b>Active Procedure: Bleeding Coolant Loops</b><br><br>"
            "This will signal the pump control nodes (0x7E1 & 0x7E2) continuously for 10 cycles.<br>"
            "Ensure the transmission is in PARK, battery cooling lines are locked, and battery is charging/ignition READY.<br><br>"
            "Proceed with activation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if val == QMessageBox.Yes:
            self._execute_command("ev-bleed", {"yes": True})

    def _run_airbag(self):
        if not self.chk_airbag_safe.isChecked():
            QMessageBox.critical(
                self,
                "SRS Restraint Safety Warning",
                "⚠️ <b>Access Denied:</b> You must acknowledge and check the safety checkbox certifying "
                "that nobody is touching passenger cabin restraint devices or squib wiring harnesses.",
                QMessageBox.Ok
            )
            return
            
        val = QMessageBox.warning(
            self,
            "Authorise Cabin Restraints Calibration & Crash Audit",
            "🔴 <b>Active Procedure: SRS Crash Event Deployment Check</b><br><br>"
            "This will establish a diagnostic diagnostic session with the physical Airbag Restraints MCU (0x7E3).<br>"
            "Do NOT wiggle or disconnect physical SRS steering wheel or dash connectors while active!<br><br>"
            "Proceed with deployment check?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if val == QMessageBox.Yes:
            self._execute_command("ev-airbag", {"yes": True})

    def _run_contactor(self):
        if not self.chk_bms_safe.isChecked():
            QMessageBox.critical(
                self,
                "BMS Service Safety Check",
                "⚠️ <b>Access Denied:</b> You must acknowledge and check the safety checkbox confirming "
                "the orange MSD (Manual Service Disconnect) switch is locked and high-voltage leads are completely un-touched.",
                QMessageBox.Ok
            )
            return
            
        val = QMessageBox.warning(
            self,
            "BMS Contactor & Isolation Resistance Check",
            "☢️ <b>DANGER: High-Voltage Contactor Stress Diagnostic</b><br><br>"
            "This command initiates direct handshakes with Battery Management Node (0x7E4) to compute "
            "isolation leakage ($R_{iso}$) and assess relay weld-status checkpoints.<br>"
            "Ensure nobody is working on active components under the physical vehicle chassis.<br><br>"
            "Authorize BMS scan?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if val == QMessageBox.Yes:
            self._execute_command("ev-contactor", {"yes": True})

    def _run_neutral(self):
        if not self.chk_neutral_safe.isChecked():
            QMessageBox.critical(
                self,
                "Shift Lock Safety Advisory",
                "⚠️ <b>Access Denied:</b> You must confirm and check the safety box certifying that you "
                "have securely chocked the vehicle's wheels or hooked it to a flatbed winch before executing this park lock bypass.",
                QMessageBox.Ok
            )
            return
            
        val = QMessageBox.warning(
            self,
            "Confirm Emergency Neutral Gear Shift Force",
            "⚙️ <b>DANGER: Emergency Shifter Override Sequence</b><br><br>"
            "This command initiates UDS service handshakes with the Shifter Control Module / Gear Shift Unit (0x7E5).<br>"
            "We will issue Service 0x2F (InputOutputControl) and fallback routines to override transmission physical lock assemblies.<br>"
            "<b>The vehicle WILL roll freely after success!</b><br><br>"
            "Authorize Park lock bypass?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if val == QMessageBox.Yes:
            self._execute_command("ev-neutral", {"yes": True})

    def _run_epb(self):
        if not self.chk_epb_safe.isChecked():
            QMessageBox.critical(
                self,
                "EPB Safety Acknowledgement Required",
                "⚠️ <b>Access Denied:</b> You must confirm the vehicle is supported on a lift or jack stands "
                "with wheels secured before entering EPB service mode.",
                QMessageBox.Ok,
            )
            return
        val = QMessageBox.warning(
            self,
            "Confirm EPB Service Mode Entry",
            "🛠️ <b>Procedure: Electronic Parking Brake Service Mode</b><br><br>"
            "This issues UDS RoutineControl 0x31 01 BA01 to the rear EPB controller (0x7E6) to retract caliper pistons.<br>"
            "After brake service, RE-ENGAGE the parking brake (Procedure auto-calibrates and exits service mode on disconnect).<br><br>"
            "Proceed with caliper retraction?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if val == QMessageBox.Yes:
            self._execute_command("ev-epb", {"yes": True})

    def _run_charge_unlock(self):
        if not self.chk_chg_safe.isChecked():
            QMessageBox.critical(
                self,
                "Charge Port Safety Acknowledgement Required",
                "⚠️ <b>Access Denied:</b> Confirm the charging session is fully terminated and HV contactors "
                "are confirmed OPEN before forcing the latch.",
                QMessageBox.Ok,
            )
            return
        val = QMessageBox.warning(
            self,
            "Confirm Charge Port Force-Release",
            "🔌 <b>Procedure: Charge Port Lock Force-Release</b><br><br>"
            "This issues UDS IOControl 0x2F C101 to charge-port nodes (0x7E1, 0x7E6) to release the latch actuator.<br>"
            "Use ONLY when a charging cable is mechanically trapped.<br><br>"
            "Proceed with force-release?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if val == QMessageBox.Yes:
            self._execute_command("charge-unlock", {"yes": True})


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
