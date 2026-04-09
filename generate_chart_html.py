import csv
import json

def to_float(val):
    try:
        return float(val.replace(',', '.').replace('%', '').strip())
    except:
        return 0.0

# Mapping Quartiers
quartier_mapping = {"1062": "Bordeaux Sud (St Michel)", "5001": "Bordeaux Sud (St Michel)", "5003": "Bordeaux Sud (St Michel)"}

data = []
with open('bâtons démobilisés.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # Header
    for row in reader:
        if len(row) < 100: continue
        code_bv = row[0]
        voix_t1 = to_float(row[86]) # TOTAL GAUCHE T1
        voix_t2 = to_float(row[83]) # Hurmic T2
        
        data.append({
            "Bureau": row[1],
            "Code": code_bv,
            "Quartier": quartier_mapping.get(code_bv, "Bordeaux Sud"),
            "Gauche_T1": int(voix_t1),
            "Hurmic_T2": int(voix_t2),
            "Voix_manquantes": int(max(0, voix_t1 - voix_t2)),
            "Taux_report": row[90] # TAUX DE REPORT
        })

# Sort by Gauche_T1
data.sort(key=lambda x: x['Gauche_T1'], reverse=True)

labels = [d['Bureau'] for d in data]
gauche_t1 = [d['Gauche_T1'] for d in data]
hurmic_t2 = [d['Hurmic_T2'] for d in data]
# Custom data alignée sur le modèle demandé : Bureau, Quartier, Voix T1, Voix T2, Voix manquantes, Report
custom_data = [[d['Bureau'], d['Quartier'], d['Gauche_T1'], d['Hurmic_T2'], d['Voix_manquantes'], d['Taux_report']] for d in data]

html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Potentiel Gauche vs Hurmic T2 - Bordeaux</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 40px auto; 
            max-width: 900px;
        }}
        #chart-container {{ 
            background: white; 
            padding: 30px; 
            border: 1px solid #eee;
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); 
        }}
        .header {{ margin-bottom: 30px; border-left: 4px solid #FF69B4; padding-left: 20px; }}
        h2 {{ margin: 0; font-size: 24px; color: #1a1a1a; }}
    </style>
</head>
<body>
    <div id="chart-container">
        <div class="header">
            <h2>Potentiel Gauche (T1) vs Réel Hurmic (T2)</h2>
        </div>
        <div id="chart"></div>
    </div>

    <script>
        const labels = {json.dumps(labels)};
        const data_t1 = {json.dumps(gauche_t1)};
        const data_t2 = {json.dumps(hurmic_t2)};
        const custom = {json.dumps(custom_data)};

        const trace1 = {{
            x: labels,
            y: data_t1,
            name: 'Potentiel Gauche (T1)',
            type: 'bar',
            marker: {{ color: '#E0E0E0' }},
            customdata: custom,
            hovertemplate: 
                '<b>Bureau : %{{customdata[0]}}</b><br>' +
                'Quartier : %{{customdata[1]}}<br>' +
                'Gauche_T1_voix : %{{customdata[2]}}<br>' +
                'Hurmic_T2_voix : %{{customdata[3]}}<br>' +
                'Voix_manquantes : %{{customdata[4]}}<br>' +
                'Taux_report : %{{customdata[5]}}<br>' +
                '<extra></extra>'
        }};

        const trace2 = {{
            x: labels,
            y: data_t2,
            name: 'Score Pierre Hurmic (T2)',
            type: 'bar',
            marker: {{ color: '#FF69B4' }},
            customdata: custom,
            hovertemplate: 
                '<b>Bureau : %{{customdata[0]}}</b><br>' +
                'Quartier : %{{customdata[1]}}<br>' +
                'Gauche_T1_voix : %{{customdata[2]}}<br>' +
                'Hurmic_T2_voix : %{{customdata[3]}}<br>' +
                'Voix_manquantes : %{{customdata[4]}}<br>' +
                'Taux_report : %{{customdata[5]}}<br>' +
                '<extra></extra>'
        }};

        const data = [trace1, trace2];

        const layout = {{
            barmode: 'group',
            xaxis: {{ tickangle: -45, automargin: true }},
            yaxis: {{ title: 'Nombre de voix' }},
            margin: {{ t: 20, b: 100, l: 60, r: 20 }},
            legend: {{ orientation: 'h', y: -0.3, x: 0.5, xanchor: 'center' }},
            hovermode: 'x unified',
            template: 'plotly_white'
        }};

        Plotly.newPlot('chart', data, layout, {{ responsive: true, displayModeBar: false }});
    </script>
</body>
</html>
"""

with open('graphique_interactif_hurmic.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
