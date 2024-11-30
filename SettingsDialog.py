from PyQt6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QTabWidget, QDialogButtonBox, 
    QWidget, QGroupBox, QLabel, QCheckBox, QSpinBox
)
from PyQt6.QtCore import QSettings

from ModernWidgets import ModernComboBox, ModernLineEdit  # Assuming these are custom widgets

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        # Load saved settings
        self.settings = QSettings("FileOrganizer", "Preferences")
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_appearance_tab(), "Appearance")
        tabs.addTab(self.create_automation_tab(), "Automation")
        tabs.addTab(self.create_organization_tab(), "Organization")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = ModernComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText(
            self.settings.value("theme", "System")
        )
        
        theme_layout.addWidget(QLabel("Color Theme:"))
        theme_layout.addWidget(self.theme_combo)
        
        # Accent color
        self.accent_combo = ModernComboBox()
        self.accent_combo.addItems(["Blue", "Purple", "Green", "Orange"])
        self.accent_combo.setCurrentText(
            self.settings.value("accent_color", "Blue")
        )
        
        theme_layout.addWidget(QLabel("Accent Color:"))
        theme_layout.addWidget(self.accent_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Interface options
        interface_group = QGroupBox("Interface")
        interface_layout = QVBoxLayout()
        
        self.minimize_tray = QCheckBox("Minimize to system tray")
        self.minimize_tray.setChecked(
            self.settings.value("minimize_tray", False, type=bool)
        )
        
        self.show_tooltips = QCheckBox("Show detailed tooltips")
        self.show_tooltips.setChecked(
            self.settings.value("show_tooltips", True, type=bool)
        )
        
        interface_layout.addWidget(self.minimize_tray)
        interface_layout.addWidget(self.show_tooltips)
        
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        layout.addStretch()
        return widget

    def create_automation_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Auto-start options
        autostart_group = QGroupBox("Startup")
        autostart_layout = QVBoxLayout()
        
        self.autostart = QCheckBox("Start with system")
        self.autostart.setChecked(
            self.settings.value("autostart", False, type=bool)
        )
        
        autostart_layout.addWidget(self.autostart)
        autostart_group.setLayout(autostart_layout)
        layout.addWidget(autostart_group)
        
        # Folder watching
        watch_group = QGroupBox("Folder Watching")
        watch_layout = QVBoxLayout()
        
        self.watch_enabled = QCheckBox("Enable folder watching")
        self.watch_enabled.setChecked(
            self.settings.value("watch_enabled", False, type=bool)
        )
        
        self.watch_delay = QSpinBox()
        self.watch_delay.setRange(1, 60)
        self.watch_delay.setValue(
            self.settings.value("watch_delay", 5, type=int)
        )
        self.watch_delay.setSuffix(" seconds")
        
        watch_layout.addWidget(self.watch_enabled)
        watch_layout.addWidget(QLabel("Delay before organizing:"))
        watch_layout.addWidget(self.watch_delay)
        
        watch_group.setLayout(watch_layout)
        layout.addWidget(watch_group)
        
        layout.addStretch()
        return widget

    def create_organization_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Organization rules
        rules_group = QGroupBox("Organization Rules")
        rules_layout = QVBoxLayout()
        
        self.create_backup = QCheckBox("Create backup before organizing")
        self.create_backup.setChecked(
            self.settings.value("create_backup", True, type=bool)
        )
        
        self.keep_structure = QCheckBox("Preserve folder structure")
        self.keep_structure.setChecked(
            self.settings.value("keep_structure", False, type=bool)
        )
        
        rules_layout.addWidget(self.create_backup)
        rules_layout.addWidget(self.keep_structure)
        
        # File exclusions
        self.excluded_types = ModernLineEdit()
        self.excluded_types.setPlaceholderText("e.g. .tmp, .log")
        self.excluded_types.setText(
            self.settings.value("excluded_types", "")
        )
        
        rules_layout.addWidget(QLabel("Excluded file types:"))
        rules_layout.addWidget(self.excluded_types)
        
        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)
        
        layout.addStretch()
        return widget

    def save_settings(self):
        # Save appearance settings
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("accent_color", self.accent_combo.currentText())
        self.settings.setValue("minimize_tray", self.minimize_tray.isChecked())
        self.settings.setValue("show_tooltips", self.show_tooltips.isChecked())
        
        # Save automation settings
        self.settings.setValue("autostart", self.autostart.isChecked())
        self.settings.setValue("watch_enabled", self.watch_enabled.isChecked())
        self.settings.setValue("watch_delay", self.watch_delay.value())
        
        # Save organization settings
        self.settings.setValue("create_backup", self.create_backup.isChecked())
        self.settings.setValue("keep_structure", self.keep_structure.isChecked())
        self.settings.setValue("excluded_types", self.excluded_types.text())
        
        self.accept()