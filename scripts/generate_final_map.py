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
        if num_bur in ['1062', '5001', '5003']: cat = "Bastion démobilisé"
        elif 'exemplaire' in cat_raw or 'mobilisé' in cat_raw: cat = "Bastion mobilisé"
        else: cat = "Bastion historique"
        bastions_data[num_bur] = {
            'name': nom_bur, 'cat': cat,
            'hurmic_t1': row[4].strip(), 'raymond_t1': row[6].strip(), 'poutou_t1': row[8].strip(),
            'score_t2': row[10].strip()
        }

# 2. Extraire le GeoJSON
with open('sources/source_map.html', 'r', encoding='utf-8') as f:
    content = f.read()
    match = re.search(r'const GEOJSON = (\{.*?\});', content, re.DOTALL)
    if match: full_geojson = json.loads(match.group(1))
    else: raise Exception("GeoJSON non trouvé")

# 3. Filtrer et enrichir
filtered_features = []
for feature in full_geojson['features']:
    code = str(feature['properties']['code'])
    if code in bastions_data:
        data = bastions_data[code]
        feature['properties'].update(data)
        if data['cat'] == "Bastion démobilisé": feature['properties']['color'] = '#FF69B4'
        elif data['cat'] == "Bastion mobilisé": feature['properties']['color'] = '#FFA500'
        else: feature['properties']['color'] = '#FF0000'
        filtered_features.append(feature)
full_geojson['features'] = filtered_features

# 4. Générer le HTML Responsive
html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Bastions de Gauche - Bordeaux 2026</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; }}
        #map {{ height: 100%; width: 100%; background: #f8f9fa; }}
        .custom-tooltip {{
            background: white; border: 1px solid #ccc; border-radius: 8px;
            padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-size: 13px; min-width: 180px; max-width: 250px;
        }}
        .tooltip-title {{ font-weight: bold; font-size: 14px; margin-bottom: 2px; display: block; }}
        .tooltip-cat {{ font-style: italic; color: #666; margin-bottom: 8px; display: block; font-size: 11px; }}
        .score-section {{ margin-bottom: 5px; border-top: 1px solid #eee; padding-top: 5px; }}
        .score-row {{ display: flex; justify-content: space-between; margin-bottom: 2px; }}
        .score-label {{ color: #555; font-size: 11px; }}
        .score-val {{ font-weight: bold; color: #333; font-size: 11px; }}
        .t2-section {{ border-top: 2px solid #eee; margin-top: 5px; padding-top: 5px; }}
        .t2-label {{ font-weight: bold; color: #111; font-size: 11px; }}
        
        /* Ajustements mobiles */
        @media (max-width: 600px) {{
            .custom-tooltip {{ min-width: 150px; padding: 8px; }}
            .tooltip-title {{ font-size: 12px; }}
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map', {{ 
            zoomControl: true,
            scrollWheelZoom: false, // Désactivé pour faciliter le scroll de la page WordPress
            touchZoom: true
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
                '<div class="score-section">' +
                    '<div class="score-row"><span class="score-label">Hurmic (T1) :</span><span class="score-val">' + p.hurmic_t1 + '</span></div>' +
                    '<div class="score-row"><span class="score-label">Raymond (T1) :</span><span class="score-val">' + p.raymond_t1 + '</span></div>' +
                    '<div class="score-row"><span class="score-label">Poutou (T1) :</span><span class="score-val">' + p.poutou_t1 + '</span></div>' +
                '</div>' +
                '<div class="score-section t2-section">' +
                    '<div class="score-row"><span class="t2-label">Gauche Hurmic (T2) :</span><span class="score-val">' + p.score_t2 + '</span></div>' +
                '</div>' +
                '</div>';
            
            // Sur mobile, on préfère le clic pour ouvrir, sur ordi le survol
            if (window.innerWidth < 600) {{
                layer.bindPopup(content);
            }} else {{
                layer.bindTooltip(content, {{ sticky: true, opacity: 1, direction: 'top' }});
            }}
            
            layer.setStyle({{
                fillColor: p.color, weight: 1.5, opacity: 1, color: 'white', fillOpacity: 0.7
            }});

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

        var geojsonLayer = L.geoJSON(data, {{ onEachFeature: onEachFeature }}).addTo(map);
        if (geojsonLayer.getBounds().isValid()) {{
            map.fitBounds(geojsonLayer.getBounds(), {{ padding: [20, 20] }});
        }}
    </script>
</body>
</html>
"""
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
