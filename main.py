import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                           QProgressBar, QFileDialog, QMessageBox, QComboBox,
                           QFrame, QSpacerItem, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QLinearGradient, QPainter
from PrivacyDialog import PrivacyDialog
import configparser

from file_organizer import ClaudeFileOrganizer
from ModernWidgets import ModernButton, ModernLineEdit, ModernComboBox, ModernProgressBar
from SettingsDialog import SettingsDialog


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in bundle
        bundle_dir = sys._MEIPASS
    else:
        # Running in dev mode
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(bundle_dir, relative_path)

icon_path = resource_path("assets/icon.ico")


class OrganizerWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    file_processed = pyqtSignal(str)

    def __init__(self, organizer):
        super().__init__()
        self.organizer = organizer
        self.is_paused = False
        self.is_cancelled = False

    def run(self):
        try:
            self.organizer.organize_files(
                progress_callback=self.progress.emit,
                file_callback=self.file_processed.emit,
                pause_check=lambda: self.is_paused,
                cancel_check=lambda: self.is_cancelled
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# Custom styled widgets

class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E5EA;
            }
        """)
        self.setContentsMargins(20, 20, 20, 20)

class PrivacyNoticeFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: #F0F9FF;
                border: 1px solid #BAE3FF;
                border-radius: 8px;
            }
            QLabel {
                color: #0A66C2;
            }
        """)
        self.setContentsMargins(15, 15, 15, 15)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Shield/Lock icon label (you can replace this with an actual icon)
        icon_label = QLabel("🔒")
        icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon_label)
        
        # Privacy message
        message = QLabel(
            "Privacy Notice: This app only looks at file names and metadata for organization. "
            "The contents of your files are never sent to any AI service or external servers."
        )
        message.setWordWrap(True)
        message.setStyleSheet("""
            font-size: 13px;
            line-height: 1.4;
        """)
        layout.addWidget(message, stretch=1)

        learn_more_btn = ModernButton("Learn More", is_primary=False)
        learn_more_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #0A66C2;
                border: none;
                padding: 4px 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        learn_more_btn.clicked.connect(self.show_privacy_info)
        layout.addWidget(learn_more_btn)
        
    def show_privacy_info(self):
        dialog = PrivacyDialog(self)
        dialog.exec()

class FileOrganizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window icon
        icon_path = resource_path("assets/icon.png")  # Can use PNG for window icon
        self.setWindowIcon(QIcon(icon_path))

        self.init_ui()
        self.load_config()
        self.worker = None
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: #F5F5F7;
            }
            QLabel {
                font-size: 14px;
                color: #1D1D1F;
            }
        """)

    def init_ui(self):
        self.setWindowTitle('File Organizer')
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel('File Organizer')
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1D1D1F;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title_label)

        # Settings card
        settings_card = CardFrame()
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setSpacing(15)

        # Provider selection
        provider_layout = QHBoxLayout()
        provider_label = QLabel('Choose AI Provider:')
        provider_label.setStyleSheet("font-weight: 500; font-size: 16px; padding-right: 10px;")
        self.provider_combo = ModernComboBox()
        self.provider_combo.addItems(["Claude (Anthropic)", "GPT-4 (OpenAI)", "Llama (Groq)"])
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        settings_layout.addLayout(provider_layout)

        # API Key section
        api_layout = QHBoxLayout()
        api_label = QLabel('API Key:')
        api_label.setStyleSheet("font-weight: 500; font-size: 16px; padding-right: 10px;")
        self.api_key_input = ModernLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText('Enter API Key')
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_key_input)
        settings_layout.addLayout(api_layout)

        # Directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel('Directory:')
        dir_label.setStyleSheet("font-weight: 500; font-size: 16px; padding-right: 10px;")
        self.dir_input = ModernLineEdit()
        self.dir_input.setPlaceholderText('Select Directory')
        self.browse_btn = ModernButton('Browse')
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.browse_btn)
        settings_layout.addLayout(dir_layout)

        main_layout.addWidget(settings_card)

        # Progress card
        progress_card = CardFrame()
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setSpacing(15)

        self.progress_bar = ModernProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel('Ready')
        self.status_label.setStyleSheet("color: #8E8E93; font-size: 14px; font-weight: 500;")
        progress_layout.addWidget(self.status_label)

        main_layout.addWidget(progress_card)

        # Control buttons
        btn_layout = QHBoxLayout()
        self.start_btn = ModernButton('Start Organization', is_primary=True)
        self.start_btn.clicked.connect(self.start_organization)
        self.pause_btn = ModernButton('Pause')
        self.pause_btn.clicked.connect(self.pause_organization)
        self.pause_btn.setEnabled(False)
        self.cancel_btn = ModernButton('Cancel')
        self.cancel_btn.clicked.connect(self.cancel_organization)
        self.cancel_btn.setEnabled(False)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.start_btn)

        # Privacy notice
        privacy_notice = PrivacyNoticeFrame()
        main_layout.addWidget(privacy_notice)

        # Add settings button
        # self.settings_btn = ModernButton('Settings')
        # self.settings_btn.setIcon(QIcon(resource_path("assets/settings.png")))
        # self.settings_btn.clicked.connect(self.show_settings)
        # btn_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        main_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def load_config(self):
        config = configparser.ConfigParser()
        config_file = Path.home() / '.file_organizer.ini'
        
        if config_file.exists():
            config.read(config_file)
            if 'Settings' in config:
                self.api_key_input.setText(config['Settings'].get('api_key', ''))
                self.dir_input.setText(config['Settings'].get('last_directory', ''))
                provider_index = config['Settings'].get('provider_index', '0')
                self.provider_combo.setCurrentIndex(int(provider_index))

    def save_config(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'api_key': self.api_key_input.text(),
            'last_directory': self.dir_input.text(),
            'provider_index': str(self.provider_combo.currentIndex())
        }
        
        config_file = Path.home() / '.file_organizer.ini'
        with open(config_file, 'w') as f:
            config.write(f)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_input.setText(directory)

    def start_organization(self):
        if not self.api_key_input.text() or not self.dir_input.text():
            QMessageBox.warning(self, 'Error', 'Please enter both API key and directory')
            return

        try:
            # Get selected provider
            provider_map = {
                0: "claude",
                1: "openai",
                2: "groq"
            }
            provider_type = provider_map[self.provider_combo.currentIndex()]
            
            self.organizer = ClaudeFileOrganizer(
                api_key=self.api_key_input.text(),
                source_dir=Path(self.dir_input.text()),
                provider_type=provider_type
            )
            
            self.worker = OrganizerWorker(self.organizer)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.organization_finished)
            self.worker.error.connect(self.show_error)
            self.worker.file_processed.connect(self.update_status)
            
            self.worker.start()
            self.save_config()
            
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to initialize organizer: {str(e)}')

    def pause_organization(self):
        if self.worker:
            self.worker.is_paused = not self.worker.is_paused
            self.pause_btn.setText('Resume' if self.worker.is_paused else 'Pause')
            self.status_label.setText('Paused' if self.worker.is_paused else 'Running')

    def cancel_organization(self):
        if self.worker:
            self.worker.is_cancelled = True
            self.worker.wait()
            self.reset_ui()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, filename):
        self.status_label.setText(f'Processing: {filename}')

    def organization_finished(self):
        self.reset_ui()
        QMessageBox.information(self, 'Success', 'File organization completed!')

    def show_error(self, error_msg):
        self.reset_ui()
        QMessageBox.critical(self, 'Error', f'An error occurred: {error_msg}')

    def reset_ui(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.pause_btn.setText('Pause')
        self.status_label.setText('Ready')
        self.progress_bar.setValue(0)
    
    def apply_settings(self):
        settings = QSettings("FileOrganizer", "Preferences")
        
        # Apply theme
        theme = settings.value("theme", "System")
        if theme != "System":
            self.set_theme(theme)
        
        # Apply accent color
        accent = settings.value("accent_color", "Blue")
        self.set_accent_color(accent)
        
        # Update UI based on other settings
        self.setup_tray_icon() if settings.value("minimize_tray", False, type=bool) else None

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_settings()

def main():
    app = QApplication(sys.argv)
    window = FileOrganizerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()