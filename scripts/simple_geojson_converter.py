#!/usr/bin/env python3
"""
Simple GeoJSON to OSM XML converter for testing fantasy basemap conversion.
This demonstrates the concept without complex GDAL dependencies.
"""

import json
import sys
from xml.etree.ElementTree import Element, SubElement, tostring, indent

def geojson_to_osm_xml(geojson_file, osm_file):
    """Convert GeoJSON to simple OSM XML format."""
    
    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    # Create OSM root element
    osm = Element('osm', version='0.6', generator='simple_geojson_converter')
    
    node_id = -1
    way_id = -1
    
    for feature in geojson_data['features']:
        properties = feature['properties']
        geometry = feature['geometry']
        
        if geometry['type'] == 'Point':
            # Create node for point features (cities)
            lon, lat = geometry['coordinates'][:2]  # Ignore elevation
            
            node = SubElement(osm, 'node', id=str(node_id), lat=str(lat), lon=str(lon))
            
            # Add fantasy tags
            if 'Burg' in properties and properties['Burg']:
                SubElement(node, 'tag', k='name', v=str(properties['Burg']))
            
            if 'Capital' in properties and properties['Capital'] == 'capital':
                SubElement(node, 'tag', k='place', v='city')
                SubElement(node, 'tag', k='fantasy:capital', v='yes')
            else:
                SubElement(node, 'tag', k='place', v='town')
            
            if 'Culture' in properties and properties['Culture']:
                SubElement(node, 'tag', k='fantasy:culture', v=str(properties['Culture']))
            
            if 'Religion' in properties and properties['Religion']:
                if properties['Religion'] != 'No religion':
                    SubElement(node, 'tag', k='fantasy:religion', v=str(properties['Religion']))
            
            if 'State' in properties and properties['State']:
                SubElement(node, 'tag', k='fantasy:kingdom', v=str(properties['State']))
            
            if 'Population' in properties and properties['Population']:
                SubElement(node, 'tag', k='population', v=str(properties['Population']))
            
            # City features
            if 'Citadel' in properties and properties['Citadel'] == 'citadel':
                SubElement(node, 'tag', k='fantasy:citadel', v='yes')
            
            if 'Walls' in properties and properties['Walls'] == 'walls':
                SubElement(node, 'tag', k='fantasy:walls', v='yes')
            
            if 'Port' in properties and properties['Port'] == 'port':
                SubElement(node, 'tag', k='fantasy:port', v='yes')
            
            if 'Temple' in properties and properties['Temple'] == 'temple':
                SubElement(node, 'tag', k='fantasy:temple', v='yes')
            
            if 'Plaza' in properties and properties['Plaza'] == 'plaza':
                SubElement(node, 'tag', k='fantasy:plaza', v='yes')
            
            # Add fantasy world identifier
            SubElement(node, 'tag', k='source', v='fantasy_world')
            SubElement(node, 'tag', k='fantasy:world', v='eno')
            
            node_id -= 1
        
        elif geometry['type'] in ['LineString', 'Polygon']:
            # Create way for linear/area features
            way = SubElement(osm, 'way', id=str(way_id))
            
            coords = geometry['coordinates']
            if geometry['type'] == 'Polygon':
                coords = coords[0]  # Take outer ring
            
            # Create nodes for way coordinates
            for coord in coords:
                lon, lat = coord[:2]
                way_node = SubElement(osm, 'node', id=str(node_id), lat=str(lat), lon=str(lon))
                SubElement(way, 'nd', ref=str(node_id))
                node_id -= 1
            
            # Add basic tags based on feature properties
            if 'name' in properties:
                SubElement(way, 'tag', k='name', v=str(properties['name']))
            
            # Add source tag
            SubElement(way, 'tag', k='source', v='fantasy_world')
            SubElement(way, 'tag', k='fantasy:world', v='eno')
            
            way_id -= 1
    
    # Write XML file
    indent(osm, space="  ")
    xml_content = tostring(osm, encoding='unicode')
    
    with open(osm_file, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_content)
    
    print(f"Converted {len(geojson_data['features'])} features to {osm_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simple_geojson_converter.py input.geojson output.osm")
        sys.exit(1)
    
    geojson_to_osm_xml(sys.argv[1], sys.argv[2])