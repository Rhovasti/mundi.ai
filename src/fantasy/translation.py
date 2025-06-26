# Copyright (C) 2025 Bunting Labs, Inc.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ogr2osm
from typing import Dict, Any, Optional


class FantasyTranslation(ogr2osm.TranslationBase):
    """
    Custom translation class for converting GeoJSON properties 
    to fantasy-themed OSM tags for custom basemap generation.
    """

    def filter_tags(self, tags: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate GeoJSON properties to custom OSM tags for fantasy mapping.
        
        Args:
            tags: Dictionary of original GeoJSON properties
            
        Returns:
            Dictionary of OSM-compatible tags with fantasy namespacing
        """
        new_tags = {}
        
        # Fantasy-specific attribute mappings
        fantasy_mappings = {
            'kingdom': 'fantasy:kingdom',
            'realm': 'fantasy:realm',
            'magic_type': 'fantasy:magic',
            'magic_level': 'fantasy:magic_level',
            'creature_type': 'fantasy:creature',
            'race': 'fantasy:race',
            'alignment': 'fantasy:alignment',
            'danger_level': 'fantasy:danger',
            'resource_type': 'fantasy:resource',
            'artifact': 'fantasy:artifact',
            'guild': 'fantasy:guild',
            'deity': 'fantasy:deity'
        }
        
        # Apply fantasy mappings
        for original_key, fantasy_key in fantasy_mappings.items():
            if original_key in tags:
                new_tags[fantasy_key] = str(tags[original_key])
        
        # Building type mappings
        if 'building_type' in tags:
            building_type = tags['building_type'].lower()
            
            building_mappings = {
                'castle': {'building': 'castle', 'fantasy:type': 'castle'},
                'fortress': {'building': 'castle', 'fantasy:type': 'fortress'},
                'tower': {'building': 'tower', 'fantasy:type': 'wizard_tower'},
                'wizard_tower': {'building': 'tower', 'fantasy:type': 'wizard_tower'},
                'temple': {'building': 'temple', 'fantasy:type': 'divine_temple'},
                'shrine': {'building': 'shrine', 'fantasy:type': 'sacred_shrine'},
                'inn': {'building': 'inn', 'fantasy:type': 'tavern'},
                'tavern': {'building': 'inn', 'fantasy:type': 'tavern'},
                'shop': {'building': 'shop', 'fantasy:type': 'merchant'},
                'guild_hall': {'building': 'hall', 'fantasy:type': 'guild_hall'},
                'library': {'building': 'library', 'fantasy:type': 'magical_library'},
                'dungeon': {'building': 'ruins', 'fantasy:type': 'dungeon'},
                'ruins': {'building': 'ruins', 'fantasy:type': 'ancient_ruins'}
            }
            
            if building_type in building_mappings:
                new_tags.update(building_mappings[building_type])
            else:
                new_tags['building'] = 'yes'
                new_tags['fantasy:type'] = building_type
        
        # Landuse and natural feature mappings
        if 'landuse' in tags:
            landuse = tags['landuse'].lower()
            
            landuse_mappings = {
                'enchanted_forest': {'landuse': 'forest', 'fantasy:enchanted': 'yes'},
                'dark_forest': {'landuse': 'forest', 'fantasy:type': 'dark'},
                'sacred_grove': {'landuse': 'forest', 'fantasy:sacred': 'yes'},
                'farmland': {'landuse': 'farmland'},
                'village': {'landuse': 'residential', 'fantasy:settlement': 'village'},
                'city': {'landuse': 'residential', 'fantasy:settlement': 'city'},
                'battlefield': {'landuse': 'military', 'fantasy:type': 'battlefield'},
                'cemetery': {'landuse': 'cemetery', 'fantasy:haunted': 'unknown'}
            }
            
            if landuse in landuse_mappings:
                new_tags.update(landuse_mappings[landuse])
            else:
                new_tags['landuse'] = landuse
        
        # Natural feature mappings
        if 'natural' in tags:
            natural = tags['natural'].lower()
            
            natural_mappings = {
                'dragon_lair': {'natural': 'cave', 'fantasy:inhabitant': 'dragon'},
                'crystal_cave': {'natural': 'cave', 'fantasy:type': 'crystal'},
                'magic_spring': {'natural': 'spring', 'fantasy:magical': 'yes'},
                'cursed_swamp': {'natural': 'wetland', 'fantasy:cursed': 'yes'},
                'floating_island': {'natural': 'island', 'fantasy:floating': 'yes'},
                'volcano': {'natural': 'volcano'},
                'mountain': {'natural': 'peak'},
                'forest': {'natural': 'wood'},
                'lake': {'natural': 'water'},
                'river': {'waterway': 'river'}
            }
            
            if natural in natural_mappings:
                new_tags.update(natural_mappings[natural])
            else:
                new_tags['natural'] = natural
        
        # Transportation mappings
        if 'highway' in tags:
            highway = tags['highway'].lower()
            
            highway_mappings = {
                'kings_road': {'highway': 'primary', 'fantasy:type': 'royal_road'},
                'trade_route': {'highway': 'secondary', 'fantasy:type': 'trade_route'},
                'forest_path': {'highway': 'path', 'fantasy:type': 'forest_path'},
                'mountain_pass': {'highway': 'path', 'fantasy:type': 'mountain_pass'},
                'secret_passage': {'highway': 'path', 'fantasy:secret': 'yes'},
                'primary': {'highway': 'primary'},
                'secondary': {'highway': 'secondary'},
                'path': {'highway': 'path'},
                'track': {'highway': 'track'}
            }
            
            if highway in highway_mappings:
                new_tags.update(highway_mappings[highway])
            else:
                new_tags['highway'] = highway
        
        # Water features
        if 'waterway' in tags:
            waterway = tags['waterway'].lower()
            
            waterway_mappings = {
                'enchanted_river': {'waterway': 'river', 'fantasy:enchanted': 'yes'},
                'sacred_river': {'waterway': 'river', 'fantasy:sacred': 'yes'},
                'underground_river': {'waterway': 'river', 'fantasy:underground': 'yes'},
                'river': {'waterway': 'river'},
                'stream': {'waterway': 'stream'},
                'canal': {'waterway': 'canal'}
            }
            
            if waterway in waterway_mappings:
                new_tags.update(waterway_mappings[waterway])
            else:
                new_tags['waterway'] = waterway
        
        # Standard OSM tags (always preserve these)
        standard_tags = ['name', 'name:en', 'ref', 'ele', 'population', 
                        'admin_level', 'boundary', 'place']
        
        for tag in standard_tags:
            if tag in tags:
                new_tags[tag] = str(tags[tag])
        
        # Handle place types for settlements
        if 'place' in tags:
            place = tags['place'].lower()
            
            place_mappings = {
                'capital': {'place': 'city', 'fantasy:capital': 'yes'},
                'city': {'place': 'city'},
                'town': {'place': 'town'},
                'village': {'place': 'village'},
                'hamlet': {'place': 'hamlet'},
                'outpost': {'place': 'hamlet', 'fantasy:type': 'outpost'},
                'stronghold': {'place': 'town', 'fantasy:type': 'stronghold'}
            }
            
            if place in place_mappings:
                new_tags.update(place_mappings[place])
            else:
                new_tags['place'] = place
        
        # Add fantasy world identifier
        new_tags['source'] = 'fantasy_world'
        new_tags['fantasy:world'] = 'custom'
        
        return new_tags

    def filter_layer(self, layer):
        """
        Filter which layers to process.
        """
        # Process all layers by default
        return layer

    def filter_feature(self, ogrfeature, layer_fields, reproject):
        """
        Filter which features to include in the output.
        """
        # Include all features by default
        return ogrfeature

    def merge_tags(self, geometry_type, tags_list):
        """
        Merge tags when multiple features are combined.
        """
        if not tags_list:
            return {}
            
        # Use the first feature's tags as base
        merged_tags = tags_list[0].copy()
        
        # Merge fantasy-specific tags from other features
        for tags in tags_list[1:]:
            for key, value in tags.items():
                if key.startswith('fantasy:') and key not in merged_tags:
                    merged_tags[key] = value
        
        return merged_tags