#!/usr/bin/env python3
"""
SeekerLight launcher script - starts the PyQt application
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    try:
        print("Starting SeekerLight...")
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting SeekerLight: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
