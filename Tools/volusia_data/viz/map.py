#!/usr/bin/env python3
"""
Project Volusia — Map Generator
Generate choropleth maps of Volusia County by census tract or zip code.

Usage:
    python Tools/volusia_data/viz/map.py --input data.geojson --column median_income --output map.html
"""

import argparse
import json
import sys
from pathlib import Path


def generate_choropleth(geojson_path, column, output_path, title=None):
    """Generate a choropleth map as HTML using Leaflet."""
    
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)
    
    # Extract values for color scaling
    values = []
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        try:
            val = float(props.get(column, 0))
            values.append(val)
        except (ValueError, TypeError):
            pass
    
    if not values:
        print(f"ERROR: No numeric values found for column '{column}'", file=sys.stderr)
        return False
    
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val != min_val else 1
    
    # Color scale (blue to red)
    def get_color(value):
        ratio = (value - min_val) / range_val
        r = int(255 * ratio)
        b = int(255 * (1 - ratio))
        return f"rgb({r}, 50, {b})"
    
    # Build map HTML
    map_title = title or f"Volusia County - {column}"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{map_title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: system-ui, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        .legend {{
            background: white; padding: 10px; border-radius: 4px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2); line-height: 1.5;
        }}
        .legend i {{ width: 18px; height: 18px; display: inline-block; margin-right: 8px; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([29.0, -81.0], 10);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        var geojson = {json.dumps(geojson)};
        
        function style(feature) {{
            var val = parseFloat(feature.properties['{column}']) || 0;
            var ratio = (val - {min_val}) / {range_val};
            var r = Math.floor(255 * ratio);
            var b = Math.floor(255 * (1 - ratio));
            return {{
                fillColor: 'rgb(' + r + ', 50, ' + b + ')',
                weight: 1,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.7
            }};
        }}
        
        function onEachFeature(feature, layer) {{
            var props = feature.properties;
            var popup = '<b>' + (props.NAME || props.name || 'Area') + '</b><br>';
            popup += '{column}: ' + (props['{column}'] || 'N/A');
            layer.bindPopup(popup);
        }}
        
        L.geoJSON(geojson, {{ style: style, onEachFeature: onEachFeature }}).addTo(map);
        
        // Legend
        var legend = L.control({{ position: 'bottomright' }});
        legend.onAdd = function(map) {{
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<b>{column}</b><br>';
            for (var i = 0; i <= 5; i++) {{
                var val = {min_val} + ({range_val} * i / 5);
                var ratio = i / 5;
                var r = Math.floor(255 * ratio);
                var b = Math.floor(255 * (1 - ratio));
                div.innerHTML += '<i style="background:rgb(' + r + ',50,' + b + ')"></i> ' + val.toFixed(1) + '<br>';
            }}
            return div;
        }};
        legend.addTo(map);
    </script>
</body>
</html>"""
    
    Path(output_path).write_text(html)
    print(f"Map saved to {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate choropleth map")
    parser.add_argument("--input", "-i", required=True, help="Input GeoJSON file")
    parser.add_argument("--column", "-c", required=True, help="Column to visualize")
    parser.add_argument("--output", "-o", required=True, help="Output HTML file")
    parser.add_argument("--title", "-t", help="Map title")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    success = generate_choropleth(args.input, args.column, args.output, args.title)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
