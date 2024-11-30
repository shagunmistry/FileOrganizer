from PyQt6.QtWidgets import QMessageBox

class PrivacyDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Privacy Information")
        self.setIcon(QMessageBox.Icon.Information)
        
        detailed_text = """
How This App Protects Your Privacy:

1. File Analysis
   • Only reads file names, creation dates, and file types
   • Never scans or reads the contents of your files
   • No file content is ever uploaded or transmitted

2. AI Integration
   • Only sends file metadata (names, types) to AI services
   • Uses this information to determine appropriate categories
   • File contents remain completely private on your device

3. Data Storage
   • All organization happens locally on your computer
   • No data is stored on external servers
   • Your API key is stored securely in local configuration

4. File Operations
   • Files are only moved between folders on your computer
   • No copies are created unless needed for duplicate handling
   • All operations are transparent and reversible
        """
        
        self.setText("Privacy is our top priority. Here's how we protect your data:")
        self.setDetailedText(detailed_text)
        
        # Style the dialog
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                font-size: 13px;
                min-width: 400px;
            }
            QPushButton {
                background: #F2F2F7;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #007AFF;
            }
            QPushButton:hover {
                background: #E5E5EA;
            }
        """)