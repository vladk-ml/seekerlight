"""
Manages Areas of Interest (AOIs) including saving, loading, and manipulation.
"""
import json
import os
from typing import Dict, List, Optional, Tuple
import ee
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import unary_union

class AOIManager:
    def __init__(self, aoi_dir: str = "aois"):
        """Initialize AOI Manager with directory for storing AOI files."""
        self.aoi_dir = aoi_dir
        self.aois: Dict[str, Dict] = {}
        self._ensure_aoi_dir()
        self.load_all_aois()

    def _ensure_aoi_dir(self) -> None:
        """Ensure AOI directory exists."""
        if not os.path.exists(self.aoi_dir):
            os.makedirs(self.aoi_dir)

    def add_aoi(self, name: str, geometry: ee.Geometry, properties: Dict = None) -> None:
        """Add a new AOI."""
        if properties is None:
            properties = {}
            
        # Calculate area in square kilometers
        area_km2 = geometry.area().getInfo() / 1e6
        properties['area_km2'] = round(area_km2, 2)
        
        self.aois[name] = {
            'geometry': geometry,
            'properties': properties
        }
        self._save_aoi(name)

    def remove_aoi(self, name: str) -> bool:
        """Remove an AOI by name."""
        if name in self.aois:
            del self.aois[name]
            aoi_path = os.path.join(self.aoi_dir, f"{name}.json")
            if os.path.exists(aoi_path):
                os.remove(aoi_path)
            return True
        return False

    def get_aoi(self, name: str) -> Optional[Dict]:
        """Get an AOI by name."""
        return self.aois.get(name)

    def list_aois(self) -> List[str]:
        """List all available AOIs."""
        return list(self.aois.keys())

    def _save_aoi(self, name: str) -> None:
        """Save an AOI to file."""
        aoi = self.aois[name]
        aoi_dict = {
            'type': 'Feature',
            'geometry': mapping(shape(aoi['geometry'].getInfo())),
            'properties': aoi['properties']
        }
        
        with open(os.path.join(self.aoi_dir, f"{name}.json"), 'w') as f:
            json.dump(aoi_dict, f, indent=2)

    def load_all_aois(self) -> None:
        """Load all AOIs from files."""
        if not os.path.exists(self.aoi_dir):
            return
            
        for filename in os.listdir(self.aoi_dir):
            if filename.endswith('.json'):
                name = filename[:-5]  # Remove .json extension
                with open(os.path.join(self.aoi_dir, filename), 'r') as f:
                    aoi_dict = json.load(f)
                    
                geometry = ee.Geometry(aoi_dict['geometry'])
                self.aois[name] = {
                    'geometry': geometry,
                    'properties': aoi_dict['properties']
                }

    def merge_aois(self, aoi_names: List[str], new_name: str) -> bool:
        """Merge multiple AOIs into a new one."""
        if not all(name in self.aois for name in aoi_names):
            return False
            
        # Convert all geometries to shapely
        polygons = []
        for name in aoi_names:
            geom = shape(self.aois[name]['geometry'].getInfo())
            polygons.append(geom)
            
        # Merge polygons
        merged = unary_union(polygons)
        
        # Convert back to ee.Geometry and save
        merged_geojson = mapping(merged)
        merged_geometry = ee.Geometry(merged_geojson)
        
        # Calculate combined properties
        combined_properties = {
            'parent_aois': aoi_names,
            'operation': 'merge'
        }
        
        self.add_aoi(new_name, merged_geometry, combined_properties)
        return True

    def split_aoi(self, name: str, split_geometries: List[ee.Geometry], 
                 new_names: List[str]) -> bool:
        """Split an AOI into multiple new AOIs."""
        if name not in self.aois or len(split_geometries) != len(new_names):
            return False
            
        original_properties = self.aois[name]['properties']
        
        for geom, new_name in zip(split_geometries, new_names):
            split_properties = {
                'parent_aoi': name,
                'operation': 'split'
            }
            split_properties.update(original_properties)
            self.add_aoi(new_name, geom, split_properties)
            
        return True

    def export_aois(self, filename: str) -> None:
        """Export all AOIs to a single GeoJSON file."""
        features = []
        for name, aoi in self.aois.items():
            feature = {
                'type': 'Feature',
                'geometry': mapping(shape(aoi['geometry'].getInfo())),
                'properties': {
                    'name': name,
                    **aoi['properties']
                }
            }
            features.append(feature)
            
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        with open(filename, 'w') as f:
            json.dump(geojson, f, indent=2)

    def import_aois(self, filename: str, overwrite: bool = False) -> Tuple[int, List[str]]:
        """Import AOIs from a GeoJSON file."""
        with open(filename, 'r') as f:
            geojson = json.load(f)
            
        if geojson['type'] != 'FeatureCollection':
            raise ValueError("Invalid GeoJSON: must be a FeatureCollection")
            
        imported = 0
        skipped = []
        
        for feature in geojson['features']:
            name = feature['properties'].pop('name', None)
            if not name:
                continue
                
            if name in self.aois and not overwrite:
                skipped.append(name)
                continue
                
            geometry = ee.Geometry(feature['geometry'])
            self.add_aoi(name, geometry, feature['properties'])
            imported += 1
            
        return imported, skipped
