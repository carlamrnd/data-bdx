import csv
import json

labels = []
pertes_data = []

with open('data/20 bastions.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if not row or len(row) < 11: continue
        
        def clean(v): return float(v.replace(',','.').replace('%','').strip())
        
        t1_total_gauche = clean(row[4]) + clean(row[6]) + clean(row[8])
        t2_hurmic = clean(row[10])
        
        # Calcul de la différence (si négatif = perte)
        diff = t2_hurmic - t1_total_gauche
        
        # On ne garde que les bureaux où il y a une stagnation ou une perte relative
        # ou ceux marqués comme "démobilisé"
        if diff < 5 or "démobilisé" in row[2].lower():
            labels.append(row[1].replace('BORDEAUX ', '').replace('ANDRE ', ''))
            pertes_data.append(round(diff, 2))

# Trier par perte la plus importante
sorted_data = sorted(zip(labels, pertes_data), key=lambda x: x[1])
labels_s, values_s = zip(*sorted_data)

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Analyse des Pertes / Démobilisation</title>
    <meta charset="utf-8" />
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: white; padding: 20px; margin: 0; }}
        .chart-container {{ position: relative; height: 500px; width: 100%; }}
        h2 {{ text-align: center; font-size: 18px; color: #333; margin-bottom: 5px; }}
        p {{ text-align: center; font-size: 14px; color: #666; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h2>Indice de Report de Voix (Écart T2 - T1)</h2>
    <p>Différence entre le score de Hurmic (T2) et le total de la gauche (T1)</p>
    <div class="chart-container">
        <canvas id="pertesChart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('pertesChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels_s)},
                datasets: [{{
                    label: 'Écart de points (T2 vs Réservoir T1)',
                    data: {json.dumps(values_s)},
                    backgroundColor: {json.dumps(['#FF69B4' if v < 0 else '#FF0000' for v in values_s])},
                    borderWidth: 1
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) label += ' : ';
                                label += context.parsed.x + ' pts';
                                return label;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ 
                        grid: {{ drawOnChartArea: true }},
                        title: {{ display: true, text: 'Points de différence (%)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('index_graph_pertes.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
