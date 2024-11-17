#!/usr/bin/env python3
"""
SeekerLight - Satellite Imagery Analysis Application
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("SeekerLight")
    app.setApplicationDisplayName("SeekerLight - Satellite Imagery Analysis")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
