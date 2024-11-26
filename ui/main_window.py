"""
Main application window using PyQt6.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QDateEdit,
    QDockWidget, QStatusBar, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
import sys
import datetime

from .map_widget import MapWidget
from src.aoi_manager import AOIManager
from src.gee_handler import GEEHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SeekerLight - Satellite Imagery Analysis")
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self.gee_handler = GEEHandler()
        self.aoi_manager = AOIManager()
        
        # Initialize SAR data variables
        self.current_polarization = 'VH'
        self.current_orbit = 'BOTH'
        self.current_vis_params = {
            'min': -25,
            'max': 0,
            'palette': ['black', 'white']
        }
        
        # Initialize UI components
        self.init_ui()
        
        # Show the window
        self.show()

    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget (will hold the map)
        self.map_widget = MapWidget()
        self.setCentralWidget(self.map_widget)
        
        # Create control panel dock widget
        control_dock = QDockWidget("Controls", self)
        control_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                   Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Create widget to hold controls
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        
        # SAR Data Controls
        sar_group = QGroupBox("SAR Data Controls")
        sar_layout = QVBoxLayout()
        
        # Date controls
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        sar_layout.addLayout(date_layout)
        
        # Polarization control
        pol_layout = QHBoxLayout()
        pol_layout.addWidget(QLabel("Polarization:"))
        self.pol_combo = QComboBox()
        self.pol_combo.addItems(['VH', 'VV'])
        pol_layout.addWidget(self.pol_combo)
        sar_layout.addLayout(pol_layout)
        
        # Orbit control
        orbit_layout = QHBoxLayout()
        orbit_layout.addWidget(QLabel("Orbit:"))
        self.orbit_combo = QComboBox()
        self.orbit_combo.addItems(['BOTH', 'ASCENDING', 'DESCENDING'])
        orbit_layout.addWidget(self.orbit_combo)
        sar_layout.addLayout(orbit_layout)
        
        # Visualization mode
        vis_layout = QHBoxLayout()
        vis_layout.addWidget(QLabel("Visualization:"))
        self.vis_combo = QComboBox()
        self.vis_combo.addItems(['Single', 'Temporal'])
        vis_layout.addWidget(self.vis_combo)
        sar_layout.addLayout(vis_layout)
        
        # Update button
        update_btn = QPushButton("Update SAR Data")
        update_btn.clicked.connect(self.update_sar_data)
        sar_layout.addWidget(update_btn)
        
        sar_group.setLayout(sar_layout)
        control_layout.addWidget(sar_group)
        
        # AOI Controls
        aoi_group = QGroupBox("AOI Controls")
        aoi_layout = QVBoxLayout()
        
        # AOI list
        aoi_layout.addWidget(QLabel("Available AOIs:"))
        self.aoi_combo = QComboBox()
        self.update_aoi_list()
        aoi_layout.addWidget(self.aoi_combo)
        
        # AOI buttons
        aoi_btn_layout = QHBoxLayout()
        save_aoi_btn = QPushButton("Save Current")
        save_aoi_btn.clicked.connect(self.save_current_aoi)
        aoi_btn_layout.addWidget(save_aoi_btn)
        
        delete_aoi_btn = QPushButton("Delete")
        delete_aoi_btn.clicked.connect(self.delete_aoi)
        aoi_btn_layout.addWidget(delete_aoi_btn)
        aoi_layout.addLayout(aoi_btn_layout)
        
        # Export/Import buttons
        exp_imp_layout = QHBoxLayout()
        export_btn = QPushButton("Export AOIs")
        export_btn.clicked.connect(self.export_aois)
        exp_imp_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import AOIs")
        import_btn.clicked.connect(self.import_aois)
        exp_imp_layout.addWidget(import_btn)
        aoi_layout.addLayout(exp_imp_layout)
        
        aoi_group.setLayout(aoi_layout)
        control_layout.addWidget(aoi_group)
        
        # Add stretch to push controls to top
        control_layout.addStretch()
        
        # Set the layout for the control widget
        control_widget.setLayout(control_layout)
        control_dock.setWidget(control_widget)
        
        # Add the dock widget to the main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, control_dock)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def update_sar_data(self):
        """Update SAR data display based on current settings."""
        try:
            # Get current map bounds if no AOI selected
            bounds = self.map_widget.get_bounds()
            geometry = self.gee_handler.get_map_bounds(bounds)
            
            # Get selected AOI if any
            selected_aoi = self.aoi_combo.currentText()
            if selected_aoi:
                aoi = self.aoi_manager.get_aoi(selected_aoi)
                if aoi:
                    geometry = aoi['geometry']
            
            # Get dates
            start_date = self.start_date.date().toString(Qt.DateFormat.ISODate)
            end_date = self.end_date.date().toString(Qt.DateFormat.ISODate)
            
            # Get collection
            collection = self.gee_handler.get_sentinel1_collection(
                start_date=start_date,
                end_date=end_date,
                geometry=geometry,
                polarization=self.pol_combo.currentText(),
                orbit=self.orbit_combo.currentText()
            )
            
            # Create composite based on visualization mode
            if self.vis_combo.currentText() == 'Temporal':
                composite = self.gee_handler.create_temporal_composite(
                    collection,
                    band=self.pol_combo.currentText()
                )
                vis_params = self.gee_handler.get_vis_params('temporal')
            else:
                composite = self.gee_handler.create_composite(collection)
                vis_params = self.gee_handler.get_vis_params('single')
            
            # Update map
            self.map_widget.update_sar_layer(composite, vis_params)
            self.statusBar.showMessage("SAR data updated successfully", 5000)
            
        except Exception as e:
            self.statusBar.showMessage(f"Error updating SAR data: {str(e)}", 5000)

    def save_current_aoi(self):
        """Save the current map selection as an AOI."""
        geometry = self.map_widget.get_selection()
        if not geometry:
            self.statusBar.showMessage("No area selected", 5000)
            return
            
        # Get name from user (you'll need to implement this dialog)
        name = "New AOI"  # Placeholder
        
        try:
            self.aoi_manager.add_aoi(name, geometry)
            self.update_aoi_list()
            self.statusBar.showMessage(f"AOI '{name}' saved successfully", 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error saving AOI: {str(e)}", 5000)

    def delete_aoi(self):
        """Delete the selected AOI."""
        name = self.aoi_combo.currentText()
        if not name:
            return
            
        if self.aoi_manager.remove_aoi(name):
            self.update_aoi_list()
            self.statusBar.showMessage(f"AOI '{name}' deleted", 5000)
        else:
            self.statusBar.showMessage(f"Error deleting AOI '{name}'", 5000)

    def update_aoi_list(self):
        """Update the AOI combo box with current AOIs."""
        current = self.aoi_combo.currentText()
        self.aoi_combo.clear()
        self.aoi_combo.addItems(self.aoi_manager.list_aois())
        
        # Restore previous selection if it still exists
        index = self.aoi_combo.findText(current)
        if index >= 0:
            self.aoi_combo.setCurrentIndex(index)

    def export_aois(self):
        """Export all AOIs to a file."""
        try:
            self.aoi_manager.export_aois("aois_export.geojson")
            self.statusBar.showMessage("AOIs exported successfully", 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error exporting AOIs: {str(e)}", 5000)

    def import_aois(self):
        """Import AOIs from a file."""
        try:
            imported, skipped = self.aoi_manager.import_aois("aois_import.geojson")
            self.update_aoi_list()
            msg = f"Imported {imported} AOIs"
            if skipped:
                msg += f" ({len(skipped)} skipped)"
            self.statusBar.showMessage(msg, 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error importing AOIs: {str(e)}", 5000)
