from PyQt6.QtWidgets import QComboBox, QLineEdit, QPushButton, QProgressBar
from PyQt6.QtCore import Qt

class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 15px;
                background: #ffffff;
                min-width: 200px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                selection-background-color: #007AFF;
            }
        """)


class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 15px;
                background: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007AFF;
            }
        """)


class ModernButton(QPushButton):
    def __init__(self, text, is_primary=False, parent=None):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setStyleSheet(self._get_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _get_style(self):
        if self.is_primary:
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #0A84FF, stop:1 #007AFF);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #1D95FF, stop:1 #1A8CFF);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #0071E3, stop:1 #0077ED);
                }
                QPushButton:disabled {
                    background: #E5E5EA;
                    color: #AEAEB2;
                }
            """
        else:
            return """
                QPushButton {
                    background: #F2F2F7;
                    color: #007AFF;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #E5E5EA;
                }
                QPushButton:pressed {
                    background: #D1D1D6;
                }
                QPushButton:disabled {
                    color: #AEAEB2;
                }
            """


class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background: #F2F2F7;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #0A84FF, stop:1 #30B0C7);
                border-radius: 4px;
            }
        """)
