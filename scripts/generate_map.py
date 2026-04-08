import csv
import json

# 1. Charger les données des 20 bastions
bastions = []
with open('20 bastions.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or len(row) < 11: continue
        
        def clean_score(val):
            try:
                return float(val.replace(',', '.').replace('%', '').strip())
            except:
                return 0.0
        
        # Scores T1 : Hurmic, Raymond, Poutou
        hurmic_t1 = clean_score(row[4])
        raymond_t1 = clean_score(row[6])
        poutou_t1 = clean_score(row[8])
        gauche_t1 = hurmic_t1 + raymond_t1 + poutou_t1
        
        # Score T2 : Hurmic
        gauche_t2 = clean_score(row[10])
        
        bastions.append({
            'id': row[0],
            'name': row[1],
            'cat': row[2],
            'score_t1': f"{gauche_t1:.2f}%",
            'score_t2': f"{gauche_t2:.2f}%"
        })

# 2. Charger les tracés GeoJSON
try:
    with open('bordeaux_bureaux.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    bastions_ids = [b['id'] for b in bastions]
    filtered_features = []
    
    for feature in geojson_data.get('features', []):
        props = feature.get('properties', {})
        num_bur = str(props.get('num_bureau', props.get('num_bur', '')))
        
        if num_bur in bastions_ids:
            data = next(b for b in bastions if b['id'] == num_bur)
            props['name'] = data['name']
            props['cat'] = data['cat']
            props['score_t1'] = data['score_t1']
            props['score_t2'] = data['score_t2']
            props['num_bureau'] = num_bur
            
            # Définir la couleur
            if 'démobilisé' in props['cat']:
                props['color'] = '#FF69B4' # Rose
            elif 'exemplaire' in props['cat']:
                props['color'] = '#FFA500' # Orange
            else:
                props['color'] = '#FF0000' # Rouge
                
            filtered_features.append(feature)
            
    geojson_data['features'] = filtered_features
    
    # 3. Générer le HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bastions de Gauche - Bordeaux 2026</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        #map {{ height: 800px; width: 100%; background: #f0f0f0; border-radius: 10px; }}
        .leaflet-tooltip {{ font-size: 14px; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h4 {{ margin: 0 0 5px; color: #333; }}
        body {{ font-family: sans-serif; margin: 20px; }}
    </style>
</head>
<body>
    <h1>Carte des 20 Bastions de Gauche - Bordeaux</h1>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([44.837789, -0.57918], 14);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        var geojsonData = {json.dumps(geojson_data)};

        function onEachFeature(feature, layer) {{
            if (feature.properties) {{
                var popupContent = "<h4>" + feature.properties.name + " (" + feature.properties.num_bureau + ")</h4>" +
                                 "<i>" + feature.properties.cat + "</i><br><br>" +
                                 "<b>Score Gauche T1 :</b> " + feature.properties.score_t1 + "<br>" +
                                 "<b>Score Hurmic T2 :</b> " + feature.properties.score_t2;
                layer.bindTooltip(popupContent, {{ sticky: true }});
            }}
            
            layer.setStyle({{
                fillColor: feature.properties.color,
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7
            }});

            layer.on({{
                mouseover: function(e) {{
                    var layer = e.target;
                    layer.setStyle({{
                        weight: 4,
                        color: '#333',
                        dashArray: '',
                        fillOpacity: 0.9
                    }});
                }},
                mouseout: function(e) {{
                    geojsonLayer.resetStyle(e.target);
                }}
            }});
        }}

        var geojsonLayer = L.geoJSON(geojsonData, {{
            onEachFeature: onEachFeature
        }}).addTo(map);
        
        if (geojsonLayer.getBounds().isValid()) {{
            map.fitBounds(geojsonLayer.getBounds());
        }}
    </script>
</body>
</html>
"""
    with open('carte_bastions_bordeaux.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Carte générée avec succès : carte_bastions_bordeaux.html")

except Exception as e:
    print(f"Erreur : {{e}}")
