import csv
import json

# Charger les données des 20 bastions
labels = []
t1_data = []
t2_data = []

with open('data/20 bastions.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or len(row) < 11: continue
        
        # Nom court du bureau
        labels.append(row[1].replace('BORDEAUX ', '').replace('ANDRE ', ''))
        
        # Scores Hurmic T1 et T2
        t1_data.append(float(row[4].replace(',', '.').replace('%', '').strip()))
        t2_data.append(float(row[10].replace(',', '.').replace('%', '').strip()))

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Évolution Hurmic T1 vs T2</title>
    <meta charset="utf-8" />
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: white; padding: 10px; margin: 0; }}
        .chart-container {{ position: relative; height: 500px; width: 100%; }}
        h2 {{ text-align: center; font-size: 16px; color: #111; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <h2>Progression de Pierre Hurmic dans les 20 Bastions de Gauche</h2>
    <div class="chart-container">
        <canvas id="hurmicChart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('hurmicChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [
                    {{
                        label: 'Hurmic (1er Tour)',
                        data: {json.dumps(t1_data)},
                        backgroundColor: '#FF0000',
                        borderRadius: 4
                    }},
                    {{
                        label: 'Hurmic (2nd Tour)',
                        data: {json.dumps(t2_data)},
                        backgroundColor: '#FF69B4',
                        borderRadius: 4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ 
                        beginAtZero: true,
                        max: 100,
                        title: {{ display: true, text: 'Score (%)' }}
                    }},
                    x: {{
                        ticks: {{ font: {{ size: 10 }}, maxRotation: 45, minRotation: 45 }}
                    }}
                }},
                plugins: {{
                    legend: {{ position: 'bottom' }},
                    tooltip: {{ mode: 'index', intersect: false }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('graphique_interactif_hurmic.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
