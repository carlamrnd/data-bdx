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
            perte_val = row[85].replace(',', '.').replace(' ', '').strip()
            perte = float(perte_val)
            
            # On ne garde que les pertes (valeurs négatives)
            if perte >= 0: continue
            
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

# Tri par perte (la plus forte perte en premier : -37, -35, ..., -12)
data_sorted = sorted(data, key=lambda x: x['perte'])[:15]

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
                    label: 'Perte de voix',
                    data: d.map(x => x.perte),
                    backgroundColor: '#FF0000', // Rouge pour la perte
                    borderRadius: 4,
                    barThickness: 20
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
                                    'Perte de voix (CH) : ' + d[i].perte,
                                    'Potentiel T1 (Somme BJ+BK) : ' + d[i].t1,
                                    'Hurmic T2 (CF) : ' + d[i].t2,
                                    'Taux de report : ' + d[i].rep
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ 
                        grid: {{ display: true, color: '#f0f0f0' }}, 
                        title: {{ display: true, text: 'Points de perte' }},
                        min: -40,
                        max: 0,
                        ticks: {{ stepSize: 5 }}
                    }},
                    y: {{ 
                        grid: {{ display: false }}, 
                        ticks: {{ font: {{ weight: 'bold' }}, color: '#333' }},
                        position: 'right' // Place les noms à droite pour qu'ils ne soient pas écrasés par les barres négatives
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('index_graph_pertes.html', 'w', encoding='utf-8') as f:
    f.write(html)
