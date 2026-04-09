import csv
import json

def to_float(val):
    try:
        return float(val.replace(',', '.').replace('%', '').strip())
    except:
        return 0.0

# Mapping Quartiers based on knowledge of Bordeaux (Menuts, André Meunier are in Bordeaux Sud)
quartier_mapping = {
    "1062": "Bordeaux Sud (St Michel)",
    "5001": "Bordeaux Sud (St Michel)",
    "5003": "Bordeaux Sud (St Michel)"
}

data = []
with open('bâtons démobilisés.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) < 100: continue
        
        code_bv = row[0]
        bureau = row[1]
        voix_t1 = to_float(row[86]) # TOTAL GAUCHE T1
        voix_t2 = to_float(row[83]) # Hurmic T2
        
        part_t1 = row[4] # % Votants T1
        part_t2 = row[66] # % Votants T2
        report = row[90] # REPORT GAUCHE
        perc_t2 = row[85] # % Voix/exprimés 2
        
        voix_manquantes = max(0, voix_t1 - voix_t2)
        
        data.append({
            "Bureau": f"{bureau}",
            "Code": code_bv,
            "Quartier": quartier_mapping.get(code_bv, "Bordeaux Sud"),
            "Gauche_T1": int(voix_t1),
            "Hurmic_T2": int(voix_t2),
            "Voix_manquantes": int(voix_manquantes),
            "Report": report,
            "Part_T1": part_t1,
            "Part_T2": part_t2,
            "Perc_T2": perc_t2
        })

# Sort by potential
data.sort(key=lambda x: x['Gauche_T1'], reverse=True)

labels = [d['Bureau'] for d in data]
gauche_t1 = [d['Gauche_T1'] for d in data]
hurmic_t2 = [d['Hurmic_T2'] for d in data]
custom_data = [[d['Quartier'], d['Part_T1'], d['Part_T2'], d['Voix_manquantes'], d['Report'], d['Perc_T2'], d['Code']] for d in data]

html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Bastions Démobilisés - Bordeaux 2026</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 40px auto; 
            max-width: 900px;
            background-color: #ffffff; 
            color: #333;
        }}
        #chart-container {{ 
            background: white; 
            padding: 30px; 
            border: 1px solid #eee;
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); 
        }}
        .header {{ margin-bottom: 30px; border-left: 4px solid #27ae60; padding-left: 20px; }}
        h2 {{ margin: 0; font-size: 24px; color: #1a1a1a; }}
        p.subtitle {{ margin: 5px 0 0; color: #666; font-style: italic; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #999; text-align: right; }}
    </style>
</head>
<body>
    <div id="chart-container">
        <div class="header">
            <h2>Potentiel de gauche vs Réalité des urnes</h2>
            <p class="subtitle">Analyse de la démobilisation dans les bastions historiques (Bordeaux Sud)</p>
        </div>
        <div id="chart"></div>
        <div class="footer">Source : Résultats officiels par bureau de vote - Traitement journalistique</div>
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
                '<b>%{{x}} (Bureau %{{customdata[6]}})</b><br>' +
                'Quartier : %{{customdata[0]}}<br><br>' +
                '<b>Potentiel Gauche (T1) : %{{y}} voix</b><br>' +
                'Participation T1 : %{{customdata[1]}}<br>' +
                '<extra></extra>'
        }};

        const trace2 = {{
            x: labels,
            y: data_t2,
            name: 'Score Pierre Hurmic (T2)',
            type: 'bar',
            marker: {{ color: '#27ae60' }},
            customdata: custom,
            hovertemplate: 
                '<b>%{{x}} (Bureau %{{customdata[6]}})</b><br>' +
                'Quartier : %{{customdata[0]}}<br><br>' +
                '<b>Score Hurmic (T2) : %{{y}} voix (%{{customdata[5]}})</b><br>' +
                'Voix manquantes : %{{customdata[3]}}<br>' +
                'Taux de report : %{{customdata[4]}}<br>' +
                'Participation T2 : %{{customdata[2]}}<br>' +
                '<extra></extra>'
        }};

        const data = [trace1, trace2];

        const layout = {{
            barmode: 'group',
            bargap: 0.15,
            bargroupgap: 0.1,
            xaxis: {{
                tickfont: {{ size: 13, color: '#444' }},
                automargin: true,
                fixedrange: true
            }},
            yaxis: {{
                title: 'Nombre de voix',
                gridcolor: '#f0f0f0',
                fixedrange: true
            }},
            margin: {{ t: 20, b: 60, l: 60, r: 20 }},
            legend: {{ 
                orientation: 'h', 
                y: -0.2, 
                x: 0.5, 
                xanchor: 'center',
                font: {{ size: 12 }}
            }},
            hoverlabel: {{
                bgcolor: '#FFF',
                font: {{ family: 'sans-serif', size: 13 }},
                bordercolor: '#CCC'
            }},
            hovermode: 'x unified',
            template: 'plotly_white'
        }};

        const config = {{ 
            responsive: true, 
            displayModeBar: false 
        }};

        Plotly.newPlot('chart', data, layout, config);
    </script>
</body>
</html>
"""

with open('graphique_interactif_hurmic.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
