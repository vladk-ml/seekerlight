import ee
import os
import json
from datetime import datetime

class AOIManager:
    def __init__(self, aoi_file='custom_aois_master.py'):
        self.aoi_file = aoi_file
        self.aois = self.read_existing_aois()
    
    def read_existing_aois(self):
        """Read existing AOIs from file"""
        if not os.path.exists(self.aoi_file):
            return {}
        try:
            namespace = {'ee': ee}
            with open(self.aoi_file) as f:
                exec(f.read(), namespace)
            return namespace.get('CUSTOM_AOIS', {})
        except Exception as e:
            print(f"Error reading AOIs: {str(e)}")
            return {}
    
    def save_aoi(self, name, coords, description="", area_km2=None):
        """Save a new AOI or update existing one"""
        if area_km2 is None:
            # Calculate area if not provided
            geometry = ee.Geometry.Polygon([coords])
            area_km2 = geometry.area().getInfo() / 1_000_000
        
        self.aois[name] = {
            'coords': coords,
            'description': description,
            'area_km2': area_km2,
            'geometry': ee.Geometry.Polygon([coords])
        }
        
        self.write_aois_file()
        return name
    
    def delete_aoi(self, name):
        """Delete an AOI by name"""
        if name in self.aois:
            del self.aois[name]
            self.write_aois_file()
            return True
        return False
    
    def write_aois_file(self):
        """Write AOIs to file"""
        content = [
            'import ee\n',
            '# Master file for custom AOIs\n',
            'CUSTOM_AOIS = {\n'
        ]
        
        for name, aoi_info in sorted(self.aois.items()):
            coords_str = str(aoi_info['coords']).replace('], [', '],\n            [')
            content.extend([
                f"    '{name}': {{\n",
                f"        'coords': {coords_str},\n",
                f"        'description': '{aoi_info.get('description', '')}',\n",
                f"        'area_km2': {aoi_info.get('area_km2', 0):.2f}\n",
                "    },\n"
            ])
        
        content.extend([
            "}\n\n",
            "# Create ee.Geometry objects for each AOI\n",
            "for name, aoi_info in CUSTOM_AOIS.items():\n",
            "    aoi_info['geometry'] = ee.Geometry.Polygon([aoi_info['coords']])\n"
        ])
        
        with open(self.aoi_file, 'w') as f:
            f.writelines(content)
    
    def export_aois(self, output_file):
        """Export AOIs to a JSON file"""
        export_data = {}
        for name, aoi_info in self.aois.items():
            export_data[name] = {
                'coords': aoi_info['coords'],
                'description': aoi_info.get('description', ''),
                'area_km2': aoi_info.get('area_km2', 0)
            }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_aois(self, input_file, overwrite=False):
        """Import AOIs from a JSON file"""
        with open(input_file, 'r') as f:
            import_data = json.load(f)
        
        for name, aoi_info in import_data.items():
            if name not in self.aois or overwrite:
                self.save_aoi(
                    name,
                    aoi_info['coords'],
                    aoi_info.get('description', ''),
                    aoi_info.get('area_km2')
                )
    
    def get_aoi_names(self):
        """Get list of AOI names"""
        return sorted(self.aois.keys())
    
    def get_aoi(self, name):
        """Get AOI by name"""
        return self.aois.get(name)
    
    def merge_aois(self, names, new_name, description=""):
        """Merge multiple AOIs into a new one"""
        if len(names) < 2:
            raise ValueError("Need at least 2 AOIs to merge")
            
        geometries = [self.aois[name]['geometry'] for name in names]
        merged = ee.Geometry.MultiPolygon([g.coordinates().getInfo() for g in geometries]).dissolve()
        coords = merged.coordinates().getInfo()[0]
        
        return self.save_aoi(new_name, coords, description)
    
    def split_aoi(self, name, split_geometry):
        """Split an AOI using another geometry"""
        if name not in self.aois:
            raise ValueError(f"AOI {name} not found")
            
        original = self.aois[name]['geometry']
        
        # Create two new geometries by intersection and difference
        part1 = original.intersection(split_geometry)
        part2 = original.difference(split_geometry)
        
        # Save new AOIs
        name1 = f"{name}_part1"
        name2 = f"{name}_part2"
        
        self.save_aoi(name1, part1.coordinates().getInfo()[0], f"Part 1 of {name}")
        self.save_aoi(name2, part2.coordinates().getInfo()[0], f"Part 2 of {name}")
        
        # Delete original
        self.delete_aoi(name)
        
        return name1, name2
