import csv
import json

data = []
# On lit le fichier top 15.csv
with open('top 15.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    for row in reader:
        if not row or len(row) < 86: continue
        
        try:
            bureau = row[0].strip()
            # La perte est dans la colonne CH (index 85)
            # On nettoie la valeur (parfois des espaces ou virgules)
            perte_val = row[85].replace(',', '.').replace(' ', '').strip()
            perte = abs(float(perte_val))
            
            # Données additionnelles pour le tooltip
            t1 = float(row[59]) + float(row[60]) # Potentiel T1
            t2 = float(row[83]) # Hurmic T2
            report = row[89].strip() # Taux de report
            
            data.append({
                'b': bureau,
                'perte': perte,
                't1': int(t1),
                't2': int(t2),
                'rep': report
            })
        except ValueError:
            continue

# Tri décroissant par perte
data_sorted = sorted(data, key=lambda x: x['perte'], reverse=True)[:15]

html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Top 15 Pertes de Voix - Bordeaux</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: white; padding: 20px; }}
        .chart-container {{ height: 600px; width: 100%; max-width: 850px; margin: auto; }}
        h2 {{ text-align: center; font-size: 18px; color: #333; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="chart-container">
        <h2>Top 15 des bureaux de vote où la gauche a perdu le plus de voix au 2nd tour</h2>
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
                    data: d.map(x => x.perte),
                    backgroundColor: '#FF0000',
                    borderRadius: 4,
                    barThickness: 22
                }}]
            }},
            options: {{
                indexAxis: 'y',
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
                                    'Voix manquantes : ' + d[i].perte,
                                    'Potentiel T1 (Somme BJ+BK) : ' + d[i].t1,
                                    'Hurmic T2 (CF) : ' + d[i].t2,
                                    'Taux de report : ' + d[i].rep
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ grid: {{ display: true, color: '#f0f0f0' }}, title: {{ display: true, text: 'Nombre de voix manquantes' }} }},
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
