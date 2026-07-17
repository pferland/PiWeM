#!/usr/bin/env python3
import sys
import os
import urllib.parse
import urllib.request
import json

# Fallback support for PyQt6/PyQt5/PySide2 to ensure code runs on whichever is installed
try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                 QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                                 QFormLayout, QDialog, QMessageBox, QGroupBox, QCheckBox, QGridLayout, QHeaderView)
    from PyQt6.QtCore import QTimer, QSettings
    
    def qt_exec(obj):
        return obj.exec()
except ImportError:
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets
        from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                     QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                                     QFormLayout, QDialog, QMessageBox, QGroupBox, QCheckBox, QGridLayout, QHeaderView)
        from PyQt5.QtCore import QTimer, QSettings
        
        # Patch PyQt5 to support PyQt6-style enum classes
        QtCore.Qt.ItemDataRole = QtCore.Qt
        QtCore.Qt.CheckState = QtCore.Qt
        QLineEdit.EchoMode = QLineEdit
        QHeaderView.ResizeMode = QHeaderView
        QtWidgets.QAbstractItemView.SelectionBehavior = QtWidgets.QAbstractItemView
        QtWidgets.QAbstractItemView.SelectionMode = QtWidgets.QAbstractItemView
        QDialog.DialogCode = QDialog
        QSettings.Format = QSettings
        
        def qt_exec(obj):
            return obj.exec_()
    except ImportError:
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                     QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                                     QFormLayout, QDialog, QMessageBox, QGroupBox, QCheckBox, QGridLayout, QHeaderView)
        from PySide2.QtCore import QTimer, QSettings
        
        # Patch PySide2
        QtCore.Qt.ItemDataRole = QtCore.Qt
        QtCore.Qt.CheckState = QtCore.Qt
        QLineEdit.EchoMode = QLineEdit
        QHeaderView.ResizeMode = QHeaderView
        QtWidgets.QAbstractItemView.SelectionBehavior = QtWidgets.QAbstractItemView
        QtWidgets.QAbstractItemView.SelectionMode = QtWidgets.QAbstractItemView
        QDialog.DialogCode = QDialog
        QSettings.Format = QSettings
        
        def qt_exec(obj):
            return obj.exec_()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Connection")
        self.setMinimumWidth(400)
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
        self.settings = QSettings(settings_path, QSettings.Format.IniFormat)
        
        geom = self.settings.value("settings_dialog_geometry")
        if geom is not None:
            self.restoreGeometry(geom)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("http://your-server-ip/piwem")
        self.url_input.setText(self.settings.value("server_url", "http://localhost/piwem"))

        self.hash_input = QLineEdit()
        self.hash_input.setPlaceholderText("Client Hash (Desktop credentials)")
        self.hash_input.setText(self.settings.value("station_hash", ""))

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Client Key (Desktop credentials)")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText(self.settings.value("station_key", ""))

        form_layout.addRow(QLabel("Central Server URL:"), self.url_input)
        form_layout.addRow(QLabel("Client Hash:"), self.hash_input)
        form_layout.addRow(QLabel("Client Key:"), self.key_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def test_connection(self):
        server_url = self.url_input.text().strip()
        station_hash = self.hash_input.text().strip()
        station_key = self.key_input.text().strip()

        if not server_url or not station_hash or not station_key:
            QMessageBox.warning(self, "Validation Error", "All fields are required to test connection.")
            return

        api_url = f"{server_url.rstrip('/')}/api/api.php"
        params = {
            "station_hash": station_hash,
            "station_key": station_key,
            "mode": "liststations"
        }
        data = urllib.parse.urlencode(params).encode('utf-8')
        
        try:
            req = urllib.request.Request(api_url, data=data)
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                if "Invalid Station or Key" in res_data:
                    QMessageBox.critical(self, "Connection Failed", "Invalid Station Hash or Key.")
                else:
                    try:
                        json.loads(res_data)
                        QMessageBox.information(self, "Connection Success", "Connected to Central Server successfully!")
                    except json.JSONDecodeError:
                        QMessageBox.critical(self, "Parsing Error", f"Server returned unexpected non-JSON response.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {e}")

    def save_settings(self):
        self.settings.setValue("server_url", self.url_input.text().strip())
        self.settings.setValue("station_hash", self.hash_input.text().strip())
        self.settings.setValue("station_key", self.key_input.text().strip())
        self.settings.setValue("settings_dialog_geometry", self.saveGeometry())
        self.accept()

    def closeEvent(self, event):
        self.settings.setValue("settings_dialog_geometry", self.saveGeometry())
        super().closeEvent(event)


def calculate_moving_average(values, window=5):
    sma = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        sub_list = values[start : i + 1]
        sma.append(sum(sub_list) / len(sub_list))
    return sma


class QPainterChartWidget(QtWidgets.QWidget):
    def __init__(self, values, timestamps, title, field_name, unit, parent=None):
        super().__init__(parent)
        self.values = values
        self.timestamps = timestamps
        self.title = title
        self.field_name = field_name
        self.unit = unit
        self.setMinimumSize(600, 400)
        self.sma_values = calculate_moving_average(self.values, window=5)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        pad_left = 70
        pad_right = 30
        pad_top = 50
        pad_bottom = 50
        
        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom
        
        # Draw background
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#1e1e24")))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, w, h)
        
        # Draw grid
        min_val = min(self.values)
        max_val = max(self.values)
        val_range = max_val - min_val
        if val_range == 0:
            val_range = 1.0
            
        num_grid_lines = 4
        grid_pen = QtGui.QPen(QtGui.QColor("#2d2d3a"), 1, QtCore.Qt.PenStyle.DashLine)
        text_pen = QtGui.QPen(QtGui.QColor("#888898"))
        
        font = QtGui.QFont("Segoe UI", 9)
        painter.setFont(font)
        
        for i in range(num_grid_lines + 1):
            y_ratio = i / num_grid_lines
            y_coord = pad_top + chart_h - (y_ratio * chart_h)
            
            painter.setPen(grid_pen)
            painter.drawLine(pad_left, int(y_coord), pad_left + chart_w, int(y_coord))
            
            painter.setPen(text_pen)
            val = min_val + y_ratio * val_range
            painter.drawText(10, int(y_coord) - 10, pad_left - 20, 20, QtCore.Qt.AlignmentFlag.AlignRight, f"{val:.2f}")
            
        # Draw timestamps
        if self.timestamps:
            painter.setPen(text_pen)
            indices = [0, len(self.timestamps) // 2, len(self.timestamps) - 1]
            indices = sorted(list(set(indices)))
            for idx in indices:
                ts = str(self.timestamps[idx])
                if " " in ts:
                    ts = ts.split(" ")[1][:8]
                elif "T" in ts:
                    ts = ts.split("T")[1][:8]
                else:
                    ts = ts[:8]
                
                x_ratio = idx / (len(self.timestamps) - 1) if len(self.timestamps) > 1 else 0.5
                x_coord = pad_left + x_ratio * chart_w
                rect = QtCore.QRect(int(x_coord) - 40, h - pad_bottom + 10, 80, 20)
                painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, ts)

        # Plot Lines
        line_pen = QtGui.QPen(QtGui.QColor("#00bcd4"), 2)
        sma_pen = QtGui.QPen(QtGui.QColor("#eab308"), 2, QtCore.Qt.PenStyle.DashLine)
        
        points = []
        sma_points = []
        for idx, val in enumerate(self.values):
            x_ratio = idx / (len(self.values) - 1) if len(self.values) > 1 else 0.5
            x = pad_left + x_ratio * chart_w
            
            y_ratio = (val - min_val) / val_range
            y = pad_top + chart_h - (y_ratio * chart_h)
            points.append(QtCore.QPointF(x, y))
            
            sma_val = self.sma_values[idx]
            sma_y_ratio = (sma_val - min_val) / val_range
            sma_y = pad_top + chart_h - (sma_y_ratio * chart_h)
            sma_points.append(QtCore.QPointF(x, sma_y))
            
        path = QtGui.QPainterPath()
        if points:
            path.moveTo(points[0])
            for pt in points[1:]:
                path.lineTo(pt)
            painter.setPen(line_pen)
            painter.drawPath(path)
            
        sma_path = QtGui.QPainterPath()
        if sma_points:
            sma_path.moveTo(sma_points[0])
            for pt in sma_points[1:]:
                sma_path.lineTo(pt)
            painter.setPen(sma_pen)
            painter.drawPath(sma_path)

        # Draw Title
        title_pen = QtGui.QPen(QtGui.QColor("#ffffff"))
        painter.setPen(title_pen)
        title_font = QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(pad_left, 15, chart_w, 30, QtCore.Qt.AlignmentFlag.AlignCenter, f"{self.title} - {self.field_name} ({self.unit})")


class ChartDialog(QDialog):
    def __init__(self, values, timestamps, title, field_name, unit, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Historical Chart: {field_name}")
        self.setMinimumSize(650, 480)
        
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
        self.settings = QSettings(settings_path, QSettings.Format.IniFormat)
        
        geom = self.settings.value("chart_dialog_geometry")
        if geom is not None:
            self.restoreGeometry(geom)
            
        layout = QVBoxLayout()
        self.chart_widget = QPainterChartWidget(values, timestamps, title, field_name, unit, self)
        layout.addWidget(self.chart_widget)
        
        stats_group = QGroupBox("Chart Stats & Legend")
        stats_layout = QHBoxLayout()
        
        legend_lbl = QLabel(
            f"<b>Legend:</b> <font color='#00bcd4'>— Actual</font> &nbsp;&nbsp;&nbsp;&nbsp; "
            f"<font color='#eab308'>- - 5-Point SMA</font>"
        )
        legend_lbl.setStyleSheet("font-size: 12px;")
        stats_layout.addWidget(legend_lbl)
        
        stats_layout.addStretch()
        
        avg_val = sum(values) / len(values) if values else 0.0
        cur_val = values[-1] if values else 0.0
        min_val = min(values) if values else 0.0
        max_val = max(values) if values else 0.0
        
        stats_text = (
            f"Min: <b>{min_val:.2f}</b> | Max: <b>{max_val:.2f}</b> | "
            f"Current: <b>{cur_val:.2f}</b> | Avg: <b>{avg_val:.2f}</b>"
        )
        stats_lbl = QLabel(stats_text)
        stats_lbl.setStyleSheet("font-size: 12px; color: #e0e0e6;")
        stats_layout.addWidget(stats_lbl)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)

    def closeEvent(self, event):
        self.settings.setValue("chart_dialog_geometry", self.saveGeometry())
        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PiWeM Central Station Client")
        self.setMinimumSize(800, 500)
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
        self.settings = QSettings(settings_path, QSettings.Format.IniFormat)

        # Set style colors
        self.apply_theme()

        # Restore last state
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))

        # Setup Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_selected_station)

        self.init_ui()

    def apply_theme(self):
        # Premium dark mode stylesheet
        stylesheet = """
            QMainWindow {
                background-color: #1e1e24;
            }
            QWidget {
                color: #e0e0e6;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a4a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #252530;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #00bcd4;
            }
            QTableWidget {
                gridline-color: #3a3a4a;
                background-color: #252530;
                alternate-background-color: #2c2c3c;
                border: 1px solid #3a3a4a;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #313140;
                color: #00bcd4;
                padding: 6px;
                border: 1px solid #3a3a4a;
                font-weight: bold;
            }
            QPushButton {
                background-color: #00bcd4;
                color: #1e1e24;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #00acc1;
            }
            QPushButton:pressed {
                background-color: #00838f;
            }
            QPushButton:disabled {
                background-color: #555565;
                color: #888898;
            }
            QLineEdit {
                background-color: #2e2e3a;
                border: 1px solid #4a4a5a;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
            QLabel {
                font-weight: bold;
            }
            QStatusBar {
                background-color: #252530;
                color: #888898;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
        """
        self.setStyleSheet(stylesheet)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left panel: stations list
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Registered Stations:"))
        
        self.station_table = QTableWidget(0, 2)
        self.station_table.setHorizontalHeaderLabels(["Station Name", "Last Update"])
        self.station_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.station_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.station_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.station_table.itemSelectionChanged.connect(self.station_selected)
        left_layout.addWidget(self.station_table)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh List")
        self.refresh_btn.clicked.connect(self.load_stations)
        self.config_btn = QPushButton("Connection Config")
        self.config_btn.clicked.connect(self.open_settings)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.config_btn)
        left_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout, stretch=2)

        # Right panel: telemetry readout
        right_layout = QVBoxLayout()
        self.details_group = QGroupBox("Select a Station to View Telemetry")
        details_layout = QGridLayout()

        self.labels = {}
        fields = [
            ("Time", "timestamp"),
            ("Temperature (C)", "c_temp"),
            ("Temperature (F)", "f_temp"),
            ("Humidity", "humidity"),
            ("Pressure (Pa)", "pressure"),
            ("Altitude (m)", "altitude"),
            ("Light (Photolevel)", "photolevel"),
            ("Wind Speed (m/s)", "wind_mps"),
            ("Wind Direction (Deg)", "wind_direction"),
        ]

        row = 0
        for name, key in fields:
            lbl_name = QLabel(f"{name}:")
            lbl_val = QLabel("--")
            lbl_val.setStyleSheet("color: #ffffff; font-weight: normal; font-size: 14px;")
            details_layout.addWidget(lbl_name, row, 0)
            details_layout.addWidget(lbl_val, row, 1)
            self.labels[key] = lbl_val
            row += 1

        self.details_group.setLayout(details_layout)
        right_layout.addWidget(self.details_group)

        # Auto-refresh control
        refresh_layout = QHBoxLayout()
        self.refresh_cb = QCheckBox("Auto-Refresh (10s)")
        self.refresh_cb.stateChanged.connect(self.toggle_autorefresh)
        refresh_layout.addWidget(self.refresh_cb)
        right_layout.addLayout(refresh_layout)

        # Historical Charts control group
        self.charts_group = QGroupBox("Historical Telemetry Charts")
        charts_layout = QHBoxLayout()
        
        charts_layout.addWidget(QLabel("Field:"))
        self.field_combo = QtWidgets.QComboBox()
        self.field_combo.addItems([
            "Temperature (C)", "Temperature (F)", "Humidity", 
            "Pressure", "Altitude", "Light", "Wind Speed"
        ])
        charts_layout.addWidget(self.field_combo)
        
        charts_layout.addWidget(QLabel("Range:"))
        self.range_combo = QtWidgets.QComboBox()
        self.range_combo.addItems([
            "1 Hour", "12 Hours", "24 Hours", "7 Days", "30 Days"
        ])
        charts_layout.addWidget(self.range_combo)
        
        self.plot_btn = QPushButton("Plot Chart")
        self.plot_btn.clicked.connect(self.generate_chart)
        charts_layout.addWidget(self.plot_btn)
        
        self.charts_group.setLayout(charts_layout)
        right_layout.addWidget(self.charts_group)

        main_layout.addLayout(right_layout, stretch=3)

        self.statusBar().showMessage("Ready. Configure Connection settings to retrieve weather data.")
        
        # Load initial station list
        QTimer.singleShot(100, self.load_stations)

    def open_settings(self):
        dialog = SettingsDialog(self)
        if qt_exec(dialog) == QDialog.DialogCode.Accepted:
            self.load_stations()

    def make_api_request(self, mode, extra_params=None):
        server_url = self.settings.value("server_url", "http://localhost/piwem")
        station_hash = self.settings.value("station_hash", "")
        station_key = self.settings.value("station_key", "")

        if not server_url:
            raise Exception("Server URL not configured.")
        if not station_hash or not station_key:
            raise Exception("Station Hash/Key credentials missing.")

        api_url = f"{server_url.rstrip('/')}/api/api.php"
        params = {
            "station_hash": station_hash,
            "station_key": station_key,
            "mode": mode
        }
        if extra_params:
            params.update(extra_params)

        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(api_url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = response.read().decode('utf-8')
            if "Invalid Station or Key" in res_data:
                raise Exception("Authentication Failed: Invalid Station Hash/Key combination.")
            return json.loads(res_data)

    def load_stations(self):
        self.statusBar().showMessage("Retrieving registered stations...")
        try:
            stations = self.make_api_request("liststations")
            self.station_table.setRowCount(0)
            for station in stations:
                row_idx = self.station_table.rowCount()
                self.station_table.insertRow(row_idx)

                name_item = QTableWidgetItem(station.get("station_name", "Unknown"))
                name_item.setData(QtCore.Qt.ItemDataRole.UserRole, station.get("station_hash", ""))
                
                date_item = QTableWidgetItem(station.get("lastupdate", "--"))

                self.station_table.setItem(row_idx, 0, name_item)
                self.station_table.setItem(row_idx, 1, date_item)

            self.statusBar().showMessage(f"Retrieved {len(stations)} station(s) successfully.")
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load stations: {e}")

    def station_selected(self):
        selected_ranges = self.station_table.selectedRanges()
        if not selected_ranges:
            return

        row = selected_ranges[0].topRow()
        name_item = self.station_table.item(row, 0)
        station_hash = name_item.data(QtCore.Qt.ItemDataRole.UserRole)
        station_name = name_item.text()
        
        self.details_group.setTitle(f"Telemetry: {station_name}")
        self.refresh_selected_station(station_hash)

    def refresh_selected_station(self, target_hash=None):
        if not target_hash:
            selected_ranges = self.station_table.selectedRanges()
            if not selected_ranges:
                return
            row = selected_ranges[0].topRow()
            target_hash = self.station_table.item(row, 0).data(QtCore.Qt.ItemDataRole.UserRole)

        if not target_hash:
            return

        try:
            records = self.make_api_request("readdata", {"target_hash": target_hash, "limit": 1})
            if records and len(records) > 0:
                record = records[0]
                self.update_telemetry_ui(record)
                self.statusBar().showMessage("Telemetry updated successfully.")
            else:
                self.clear_telemetry_ui()
                self.statusBar().showMessage("No telemetry recorded for this station.")
        except Exception as e:
            self.statusBar().showMessage(f"Failed to update telemetry: {e}")

    def update_telemetry_ui(self, record):
        self.labels["timestamp"].setText(record.get("timestamp", "--"))
        self.labels["c_temp"].setText(f"{record.get('c_temp', 0.0):.1f} °C")
        self.labels["f_temp"].setText(f"{record.get('f_temp', 0.0):.1f} °F")
        self.labels["humidity"].setText(f"{record.get('humidity', 0.0):.1f} %")
        self.labels["pressure"].setText(f"{record.get('pressure', 0.0):.1f} Pa")
        self.labels["altitude"].setText(f"{record.get('altitude', 0.0):.1f} m")
        self.labels["photolevel"].setText(str(record.get("photolevel", "--")))
        self.labels["wind_mps"].setText(f"{record.get('wind_mps', 0.0):.1f} m/s")
        
        wind_dir = record.get("wind_direction", None)
        self.labels["wind_direction"].setText(f"{wind_dir} °" if wind_dir is not None else "--")

    def clear_telemetry_ui(self):
        for label in self.labels.values():
            label.setText("--")

    def toggle_autorefresh(self, state):
        if state == 2 or state == QtCore.Qt.CheckState.Checked:
            self.refresh_timer.start(10000) # 10 seconds
            self.statusBar().showMessage("Auto-Refresh enabled (10s interval).")
        else:
            self.refresh_timer.stop()
            self.statusBar().showMessage("Auto-Refresh disabled.")

    def generate_chart(self):
        selected_ranges = self.station_table.selectedRanges()
        if not selected_ranges:
            QMessageBox.warning(self, "No Station Selected", "Please select a weather station from the list first.")
            return

        row = selected_ranges[0].topRow()
        name_item = self.station_table.item(row, 0)
        station_hash = name_item.data(QtCore.Qt.ItemDataRole.UserRole)
        station_name = name_item.text()
        
        field_text = self.field_combo.currentText()
        range_text = self.range_combo.currentText()
        
        field_mappings = {
            "Temperature (C)": ("c_temp", "Temperature", "°C"),
            "Temperature (F)": ("f_temp", "Temperature", "°F"),
            "Humidity": ("humidity", "Humidity", "%"),
            "Pressure": ("pressure", "Pressure", "Pa"),
            "Altitude": ("altitude", "Altitude", "m"),
            "Light": ("photolevel", "Photo Level", "Photolevel"),
            "Wind Speed": ("wind_mps", "Wind Speed", "m/s")
        }
        
        range_mappings = {
            "1 Hour": "1 HOUR",
            "12 Hours": "12 HOUR",
            "24 Hours": "24 HOUR",
            "7 Days": "7 DAY",
            "30 Days": "30 DAY"
        }
        
        api_field, label, unit = field_mappings[field_text]
        limit = range_mappings[range_text]
        
        self.statusBar().showMessage(f"Fetching historical data for {label}...")
        try:
            records = self.make_api_request("readdata", {"target_hash": station_hash, "limit": limit})
            if not records:
                QMessageBox.information(self, "No Data", f"No telemetry recorded for field '{label}' in range '{range_text}'.")
                self.statusBar().showMessage("No data points found.")
                return
                
            records.reverse()
            
            values = []
            timestamps = []
            for r in records:
                val = r.get(api_field)
                if val is not None:
                    try:
                        values.append(float(val))
                        timestamps.append(r.get("timestamp", ""))
                    except ValueError:
                        pass
                        
            if not values:
                QMessageBox.information(self, "No Numeric Data", f"No numeric data found for field '{label}' in the retrieved range.")
                self.statusBar().showMessage("No valid data points found.")
                return
                
            dialog = ChartDialog(values, timestamps, station_name, label, unit, self)
            dialog.exec()
            self.statusBar().showMessage("Chart generated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Failed to Plot Chart", f"Error generating chart: {e}")
            self.statusBar().showMessage(f"Failed to generate chart: {e}")

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_exec(app))

if __name__ == '__main__':
    main()
