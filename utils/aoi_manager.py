"""
Area of Interest (AOI) management utilities.
"""
import ee
import json
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime

class AOIManager:
    def __init__(self):
        self.aoi_file = os.path.join(os.path.dirname(__file__), '../data/aois.json')
        self.aois: Dict[str, Dict[str, Any]] = self._load_aois()
        
    def _load_aois(self) -> Dict[str, Dict[str, Any]]:
        """Load AOIs from file or create default if not exists."""
        if os.path.exists(self.aoi_file):
            try:
                with open(self.aoi_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._get_default_aois()
        else:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.aoi_file), exist_ok=True)
            aois = self._get_default_aois()
            self._save_aois(aois)
            return aois
            
    def _get_default_aois(self) -> Dict[str, Dict[str, Any]]:
        """Get default AOI dictionary."""
        return {
            'Rostov Oblast': {
                'coords': [
                    [39.7015, 47.2357],
                    [39.7015, 47.5000],
                    [40.0000, 47.5000],
                    [40.0000, 47.2357],
                    [39.7015, 47.2357]
                ],
                'created_at': datetime.now().isoformat(),
                'area_km2': 0.0  # Will be calculated on first access
            },
            'Custom': {
                'coords': [],
                'created_at': datetime.now().isoformat(),
                'area_km2': 0.0
            }
        }
        
    def _save_aois(self, aois: Dict[str, Dict[str, Any]] = None) -> None:
        """Save AOIs to file."""
        if aois is None:
            aois = self.aois
        with open(self.aoi_file, 'w') as f:
            json.dump(aois, f, indent=2)
            
    def get_aoi_names(self) -> List[str]:
        """Get list of available AOI names."""
        return list(self.aois.keys())
        
    def get_aoi_geometry(self, name: str) -> ee.Geometry:
        """Get Earth Engine geometry for specified AOI."""
        if name not in self.aois:
            raise ValueError(f"AOI '{name}' not found")
            
        coords = self.aois[name]['coords']
        if not coords:
            raise ValueError(f"AOI '{name}' has no coordinates defined")
            
        return ee.Geometry.Polygon([coords])
        
    def get_area_km2(self, name: str) -> float:
        """Get area of AOI in square kilometers."""
        if name not in self.aois:
            raise ValueError(f"AOI '{name}' not found")
            
        # Calculate area if not already calculated
        if self.aois[name]['area_km2'] == 0.0 and self.aois[name]['coords']:
            geometry = self.get_aoi_geometry(name)
            area = geometry.area().getInfo()
            self.aois[name]['area_km2'] = area / 1_000_000  # Convert m² to km²
            self._save_aois()
            
        return self.aois[name]['area_km2']
        
    def add_aoi(self, name: str, coords: List[List[float]], overwrite: bool = False) -> Tuple[bool, str]:
        """Add new AOI with specified coordinates.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if name in self.aois and not overwrite:
            return False, f"AOI '{name}' already exists"
            
        self.aois[name] = {
            'coords': coords,
            'created_at': datetime.now().isoformat(),
            'area_km2': 0.0  # Will be calculated on first access
        }
        
        self._save_aois()
        return True, f"AOI '{name}' added successfully"
        
    def remove_aoi(self, name: str) -> Tuple[bool, str]:
        """Remove specified AOI.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if name not in self.aois:
            return False, f"AOI '{name}' not found"
            
        if name == 'Custom':
            return False, "Cannot remove the Custom AOI"
            
        del self.aois[name]
        self._save_aois()
        return True, f"AOI '{name}' removed successfully"
        
    def update_custom_aoi(self, coords: List[List[float]]) -> None:
        """Update coordinates for the Custom AOI."""
        self.aois['Custom']['coords'] = coords
        self.aois['Custom']['area_km2'] = 0.0  # Reset area to trigger recalculation
        self._save_aois()
        
    def get_aoi_info(self, name: str) -> Dict[str, Any]:
        """Get full information about an AOI."""
        if name not in self.aois:
            raise ValueError(f"AOI '{name}' not found")
            
        info = self.aois[name].copy()
        info['area_km2'] = self.get_area_km2(name)  # Ensure area is calculated
        return info
