"""
Main entry point for the SeekerLight application.
"""
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from src.gee_handler import GEEHandler

def main():
    # Create Qt Application first
    app = QApplication(sys.argv)
    
    try:
        # Initialize Earth Engine
        gee_handler = GEEHandler()
        
        # Create and show main window
        window = MainWindow()
        
        # Start the event loop
        sys.exit(app.exec())
        
    except Exception as e:
        # Show error dialog
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("Failed to start application")
        error_dialog.setDetailedText(str(e))
        error_dialog.exec()
        sys.exit(1)

if __name__ == "__main__":
    main()
