import csv
import json

# Charger les données du top 15.csv
data = []
with open('top 15.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row: continue
        
        # On extrait : Bureau (0), DIFF GAUCHE (86), T1 (Somme BJ+BK), T2 (CF=83), Quartier
        try:
            bureau = row[0].strip()
            diff = float(row[86].replace(',', '.'))
            t1 = float(row[59]) + float(row[60]) # TOTAL GAUCHE + TOTAL EXT GAUCHE
            t2 = float(row[83]) # Voix 2nd tour Hurmic
            report = row[89].strip() # REPORT GAUCHE
            quartier = "Bordeaux" # Valeur par défaut si non trouvé
            
            data.append({
                'b': bureau,
                'q': quartier,
                'diff': abs(diff), # On prend la valeur absolue car on parle de "perte"
                't1': int(t1),
                't2': int(t2),
                'rep': report
            })
        except:
            continue

# Trier par perte décroissante
data_sorted = sorted(data, key=lambda x: x['diff'], reverse=True)[:15]

html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top 15 - Pertes de voix de gauche</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: white; padding: 20px; }}
        .chart-container {{ height: 600px; width: 100%; max-width: 900px; margin: auto; }}
        h2 {{ text-align: center; font-size: 18px; margin-bottom: 30px; color: #333; }}
    </style>
</head>
<body>
    <div class="chart-container">
        <h2>Top 15 : Bureaux de vote où la gauche a perdu le plus de voix au 2nd tour</h2>
        <canvas id="top15Chart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('top15Chart').getContext('2d');
        const d = {json.dumps(data_sorted)};
        
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: d.map(x => x.b),
                datasets: [{{
                    label: 'Voix manquantes',
                    data: d.map(x => x.diff),
                    backgroundColor: '#FF0000', // Rouge pour la perte
                    borderRadius: 4,
                    barThickness: 20
                }}]
            }},
            options: {{
                indexAxis: 'y', // Barres horizontales
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: 'white',
                        titleColor: '#333',
                        bodyColor: '#555',
                        borderColor: '#ccc',
                        borderWidth: 1,
                        padding: 15,
                        displayColors: false,
                        callbacks: {{
                            label: function(ctx) {{
                                const i = ctx.dataIndex;
                                return [
                                    'Voix manquantes : ' + d[i].diff,
                                    'Potentiel T1 (Somme BJ+BK) : ' + d[i].t1,
                                    'Hurmic T2 (CF) : ' + d[i].t2,
                                    'Taux de report : ' + d[i].rep
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, title: {{ display: true, text: 'Nombre de voix' }} }},
                    y: {{ grid: {{ display: false }}, ticks: {{ font: {{ weight: 'bold' }} }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('index_graph_pertes.html', 'w', encoding='utf-8') as f:
    f.write(html)
