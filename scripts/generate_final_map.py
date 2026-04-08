import csv
import json
import re

# 1. Charger les données des 20 bastions
bastions_data = {}
with open('data/20 bastions.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or len(row) < 11: continue
        
        num_bur = row[0].strip()
        nom_bur = row[1].strip()
        cat_raw = row[2].strip().lower()
        
        # Attribution stricte des catégories
        if num_bur in ['1062', '5001', '5003']:
            cat = "Bastion démobilisé"
        elif 'exemplaire' in cat_raw or 'mobilisé' in cat_raw:
            cat = "Bastion mobilisé"
        else:
            cat = "Bastion historique"
        
        # Scores
        hurmic_t1 = row[4].strip()
        raymond_t1 = row[6].strip()
        poutou_t1 = row[8].strip()
        gauche_t2 = row[10].strip()
        
        bastions_data[num_bur] = {
            'name': nom_bur,
            'cat': cat,
            'hurmic_t1': hurmic_t1,
            'raymond_t1': raymond_t1,
            'poutou_t1': poutou_t1,
            'score_t2': gauche_t2
        }

# 2. Extraire le GeoJSON de source_map.html
with open('sources/source_map.html', 'r', encoding='utf-8') as f:
    content = f.read()
    match = re.search(r'const GEOJSON = (\{.*?\});', content, re.DOTALL)
    if match:
        full_geojson = json.loads(match.group(1))
    else:
        raise Exception("GeoJSON non trouvé")

# 3. Filtrer et enrichir le GeoJSON
filtered_features = []
for feature in full_geojson['features']:
    code = str(feature['properties']['code'])
    if code in bastions_data:
        data = bastions_data[code]
        feature['properties'].update(data)
        
        # Définir la couleur persistante
        if data['cat'] == "Bastion démobilisé":
            feature['properties']['color'] = '#FF69B4' # Rose
        elif data['cat'] == "Bastion mobilisé":
            feature['properties']['color'] = '#FFA500' # Orange
        else:
            feature['properties']['color'] = '#FF0000' # Rouge
            
        filtered_features.append(feature)

full_geojson['features'] = filtered_features

# 4. Générer le fichier HTML final (avec balises anti-cache)
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bastions de Gauche - Bordeaux 2026</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Balises pour forcer le rafraîchissement du cache -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    
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
            min-width: 220px;
        }}
        .tooltip-title {{ font-weight: bold; font-size: 15px; margin-bottom: 2px; display: block; color: #111; }}
        .tooltip-cat {{ font-style: italic; color: #666; margin-bottom: 12px; display: block; font-size: 12px; }}
        .score-section {{ margin-bottom: 8px; border-top: 1px solid #eee; padding-top: 8px; }}
        .score-row {{ display: flex; justify-content: space-between; margin-bottom: 3px; }}
        .score-label {{ color: #555; }}
        .score-val {{ font-weight: bold; color: #333; }}
        .t2-section {{ border-top: 2px solid #eee; margin-top: 8px; padding-top: 8px; }}
        .t2-label {{ font-weight: bold; color: #111; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map', {{ zoomControl: true }}).setView([44.837789, -0.57918], 13);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '© OpenStreetMap contributors © CARTO'
        }}).addTo(map);

        var data = {json.dumps(full_geojson)};

        function getStyle(feature) {{
            return {{
                fillColor: feature.properties.color,
                weight: 1.5,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.7
            }};
        }}

        function onEachFeature(feature, layer) {{
            var p = feature.properties;
            var content = '<div class="custom-tooltip">' +
                '<span class="tooltip-title">' + p.name + '</span>' +
                '<span class="tooltip-cat">' + p.cat + '</span>' +
                '<div class="score-section">' +
                    '<div class="score-row"><span class="score-label">Hurmic (T1) :</span><span class="score-val">' + p.hurmic_t1 + '</span></div>' +
                    '<div class="score-row"><span class="score-label">Raymond (T1) :</span><span class="score-val">' + p.raymond_t1 + '</span></div>' +
                    '<div class="score-row"><span class="score-label">Poutou (T1) :</span><span class="score-val">' + p.poutou_t1 + '</span></div>' +
                '</div>' +
                '<div class="score-section t2-section">' +
                    '<div class="score-row"><span class="t2-label">Gauche Hurmic (T2) :</span><span class="score-val">' + p.score_t2 + '</span></div>' +
                '</div>' +
                '</div>';
            
            layer.bindTooltip(content, {{ sticky: true, opacity: 1, direction: 'top' }});
            
            layer.setStyle(getStyle(feature));

            layer.on({{
                mouseover: function(e) {{
                    var l = e.target;
                    l.setStyle({{ weight: 3, color: '#444', fillOpacity: 0.9 }});
                    l.bringToFront();
                }},
                mouseout: function(e) {{
                    geojsonLayer.resetStyle(e.target);
                }}
            }});
        }}

        var geojsonLayer = L.geoJSON(data, {{
            onEachFeature: onEachFeature,
            style: getStyle
        }}).addTo(map);

        if (geojsonLayer.getBounds().isValid()) {{
            map.fitBounds(geojsonLayer.getBounds(), {{ padding: [30, 30] }});
        }}
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Mise à jour terminée avec succès.")
