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
from utils.aoi_manager import AOIManager
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
        
        # Create control panel content
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        
        # Date Range Selection
        date_group = QGroupBox("Date Range")
        date_layout = QVBoxLayout()
        
        start_date_layout = QHBoxLayout()
        start_date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        start_date_layout.addWidget(self.start_date)
        
        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        end_date_layout.addWidget(self.end_date)
        
        date_layout.addLayout(start_date_layout)
        date_layout.addLayout(end_date_layout)
        date_group.setLayout(date_layout)
        control_layout.addWidget(date_group)
        
        # SAR Data Controls
        sar_group = QGroupBox("SAR Data")
        sar_layout = QVBoxLayout()
        
        # Polarization selection
        pol_layout = QHBoxLayout()
        pol_layout.addWidget(QLabel("Polarization:"))
        self.pol_combo = QComboBox()
        self.pol_combo.addItems(['VH', 'VV'])
        self.pol_combo.currentTextChanged.connect(self.update_sar_visualization)
        pol_layout.addWidget(self.pol_combo)
        sar_layout.addLayout(pol_layout)
        
        # Orbit selection
        orbit_layout = QHBoxLayout()
        orbit_layout.addWidget(QLabel("Orbit Pass:"))
        self.orbit_combo = QComboBox()
        self.orbit_combo.addItems(['BOTH', 'ASCENDING', 'DESCENDING'])
        self.orbit_combo.currentTextChanged.connect(self.update_sar_visualization)
        orbit_layout.addWidget(self.orbit_combo)
        sar_layout.addLayout(orbit_layout)
        
        # Layer visibility
        self.sar_visible = QCheckBox("Show SAR Layer")
        self.sar_visible.setChecked(True)
        self.sar_visible.stateChanged.connect(self.toggle_sar_layer)
        sar_layout.addWidget(self.sar_visible)
        
        sar_group.setLayout(sar_layout)
        control_layout.addWidget(sar_group)
        
        # AOI Selection
        aoi_group = QGroupBox("Area of Interest")
        aoi_layout = QVBoxLayout()
        
        # AOI dropdown
        aoi_combo_layout = QHBoxLayout()
        aoi_combo_layout.addWidget(QLabel("Select AOI:"))
        self.aoi_combo = QComboBox()
        self.update_aoi_list()
        aoi_combo_layout.addWidget(self.aoi_combo)
        aoi_layout.addLayout(aoi_combo_layout)
        
        # AOI buttons
        aoi_buttons = QHBoxLayout()
        self.draw_aoi_btn = QPushButton("Draw New")
        self.draw_aoi_btn.clicked.connect(self.start_drawing_aoi)
        self.save_aoi_btn = QPushButton("Save Current")
        self.save_aoi_btn.clicked.connect(self.save_current_aoi)
        aoi_buttons.addWidget(self.draw_aoi_btn)
        aoi_buttons.addWidget(self.save_aoi_btn)
        aoi_layout.addLayout(aoi_buttons)
        
        # AOI info
        self.aoi_info_label = QLabel()
        aoi_layout.addWidget(self.aoi_info_label)
        
        aoi_group.setLayout(aoi_layout)
        control_layout.addWidget(aoi_group)
        
        # Update button
        update_btn = QPushButton("Update View")
        update_btn.clicked.connect(self.update_view)
        control_layout.addWidget(update_btn)
        
        # Add stretch to push everything up
        control_layout.addStretch()
        
        # Set the layout for the control widget
        control_widget.setLayout(control_layout)
        control_dock.setWidget(control_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, control_dock)
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
    def update_sar_visualization(self):
        """Update SAR visualization based on current settings."""
        self.current_polarization = self.pol_combo.currentText()
        self.current_orbit = self.orbit_combo.currentText()
        self.update_view()
        
    def toggle_sar_layer(self, state):
        """Toggle SAR layer visibility."""
        if state:
            self.update_view()
        else:
            # TODO: Implement layer removal in MapWidget
            pass
            
    def update_view(self):
        """Update the map view with current settings."""
        try:
            if not self.sar_visible.isChecked():
                return
                
            # Get current AOI
            aoi_name = self.aoi_combo.currentText()
            if not aoi_name:
                self.statusBar.showMessage("Please select an Area of Interest")
                return
                
            aoi_geometry = self.aoi_manager.get_aoi_geometry(aoi_name)
            
            # Get date range
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            # Get SAR collection
            collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
                .filterBounds(aoi_geometry) \
                .filterDate(start_date, end_date)
            
            # Apply orbit filter if needed
            if self.current_orbit != 'BOTH':
                collection = collection.filter(ee.Filter.eq('orbitProperties_pass', self.current_orbit))
            
            # Create composite
            composite = collection \
                .select(self.current_polarization) \
                .mean() \
                .clip(aoi_geometry)
            
            # Update map
            self.map_widget.add_ee_layer(composite, self.current_vis_params, f'SAR_{self.current_polarization}')
            
            # Update status
            self.statusBar.showMessage("View updated successfully")
            
        except Exception as e:
            self.statusBar.showMessage(f"Error updating view: {str(e)}")
            
    def start_drawing_aoi(self):
        """Start AOI drawing mode."""
        # TODO: Implement drawing mode in MapWidget
        self.statusBar.showMessage("Drawing mode not implemented yet")
        
    def save_current_aoi(self):
        """Save the current AOI."""
        # TODO: Implement AOI saving
        self.statusBar.showMessage("AOI saving not implemented yet")
        
    def update_aoi_list(self):
        """Update the AOI dropdown with current AOIs."""
        self.aoi_combo.clear()
        aoi_names = self.aoi_manager.get_aoi_names()
        for name in aoi_names:
            area = self.aoi_manager.get_area_km2(name)
            self.aoi_combo.addItem(f"{name} ({area:.2f} km²)")
