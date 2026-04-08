import csv
import json
import re

# 1. Charger les données des 20 bastions
bastions_data = {}
with open('20 bastions.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or len(row) < 11: continue
        
        num_bur = row[0].strip()
        nom_bur = row[1].strip()
        cat = row[2].strip()
        
        # Nettoyage des scores
        def clean_score(val):
            try:
                return float(val.replace(',', '.').replace('%', '').strip())
            except:
                return 0.0
        
        hurmic_t1 = clean_score(row[4])
        raymond_t1 = clean_score(row[6])
        poutou_t1 = clean_score(row[8])
        gauche_t1 = hurmic_t1 + raymond_t1 + poutou_t1
        
        gauche_t2 = clean_score(row[10])
        
        bastions_data[num_bur] = {
            'name': nom_bur,
            'cat': cat,
            'score_t1': f"{gauche_t1:.2f}%",
            'score_t2': f"{gauche_t2:.2f}%"
        }

# 2. Extraire le GeoJSON de source_map.html
with open('source_map.html', 'r', encoding='utf-8') as f:
    for line in f:
        if 'const GEOJSON =' in line:
            # Extraire la partie JSON
            match = re.search(r'const GEOJSON = (\{.*\});', line)
            if match:
                full_geojson = json.loads(match.group(1))
                break
    else:
        raise Exception("GeoJSON non trouvé dans source_map.html")

# 3. Filtrer et enrichir le GeoJSON
filtered_features = []
for feature in full_geojson['features']:
    code = str(feature['properties']['code'])
    if code in bastions_data:
        data = bastions_data[code]
        feature['properties']['name'] = data['name']
        feature['properties']['cat'] = data['cat']
        feature['properties']['score_t1'] = data['score_t1']
        feature['properties']['score_t2'] = data['score_t2']
        
        # Définir la couleur
        if 'démobilisé' in data['cat']:
            feature['properties']['color'] = '#FF69B4' # Rose
        elif 'exemplaire' in data['cat']:
            feature['properties']['color'] = '#FFA500' # Orange
        else:
            feature['properties']['color'] = '#FF0000' # Rouge
            
        filtered_features.append(feature)

full_geojson['features'] = filtered_features

# 4. Générer le fichier HTML final
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bastions de Gauche - Bordeaux 2026</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        #map {{ height: 100vh; width: 100vw; background: #f8f9fa; }}
        .custom-tooltip {{
            background: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-size: 13px;
            min-width: 200px;
        }}
        .tooltip-title {{ font-weight: bold; font-size: 15px; margin-bottom: 4px; display: block; }}
        .tooltip-cat {{ font-style: italic; color: #666; margin-bottom: 10px; display: block; }}
        .score-row {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
        .score-val {{ font-weight: bold; color: #333; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map', {{
            zoomControl: true,
            scrollWheelZoom: true
        }}).setView([44.837789, -0.57918], 13);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '© OpenStreetMap contributors © CARTO'
        }}).addTo(map);

        var data = {json.dumps(full_geojson)};

        function onEachFeature(feature, layer) {{
            var p = feature.properties;
            var content = '<div class="custom-tooltip">' +
                '<span class="tooltip-title">' + p.name + '</span>' +
                '<span class="tooltip-cat">' + p.cat + '</span>' +
                '<div class="score-row"><span>Gauche (T1) :</span><span class="score-val">' + p.score_t1 + '</span></div>' +
                '<div class="score-row"><span>Gauche Hurmic (T2) :</span><span class="score-val">' + p.score_t2 + '</span></div>' +
                '</div>';
            
            layer.bindTooltip(content, {{ sticky: true, className: 'leaflet-tooltip-own', opacity: 1, direction: 'top' }});
            
            layer.setStyle({{
                fillColor: p.color,
                weight: 1.5,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.7
            }});

            layer.on({{
                mouseover: function(e) {{
                    var l = e.target;
                    l.setStyle({{
                        weight: 3,
                        color: '#444',
                        fillOpacity: 0.85
                    }});
                    l.bringToFront();
                }},
                mouseout: function(e) {{
                    geojsonLayer.resetStyle(e.target);
                }}
            }});
        }}

        var geojsonLayer = L.geoJSON(data, {{
            onEachFeature: onEachFeature
        }}).addTo(map);

        if (geojsonLayer.getBounds().isValid()) {{
            map.fitBounds(geojsonLayer.getBounds(), {{ padding: [20, 20] }});
        }}
    </script>
</body>
</html>
"""

with open('carte_bastions_bordeaux.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Carte finale générée avec succès : carte_bastions_bordeaux.html")
