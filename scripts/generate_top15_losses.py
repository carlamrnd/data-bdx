import csv
import json

data = []
# On lit le fichier dernier graph.csv
with open('dernier graph.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # User mapping: BO (67th column, index 66), BJ (62nd column, index 61), BL (64th column, index 63)
    # 0: Code BV
    # 61: TOTAL GAUCHE T1 (BJ)
    # 63: Voix 2 (BL)
    # 66: NOMBRE DE VOIX PERDUES (BO)
    
    for row in reader:
        if not row or len(row) < 67: continue
        
        try:
            bureau = row[0].strip()
            # NOMBRE DE VOIX PERDUES (BO)
            perte_val = row[66].replace(',', '.').replace(' ', '').strip()
            perte = abs(float(perte_val))
            
            # TOTAL GAUCHE T1 (BJ)
            t1_val = row[61].replace(',', '.').replace(' ', '').strip()
            t1 = float(t1_val)
            
            # Voix 2 (BL)
            t2_val = row[63].replace(',', '.').replace(' ', '').strip()
            t2 = float(t2_val)
            
            # Report % (Using index 65: % Voix/exprimés 2 as a proxy if needed)
            report = row[65].strip()
            
            data.append({
                'b': bureau,
                'perte': perte,
                't1': int(t1),
                't2': int(t2),
                'rep': report
            })
        except Exception as e:
            # print(f"Error at bureau {row[0]}: {e}")
            continue

# Tri décroissant par perte
data_sorted = sorted(data, key=lambda x: x['perte'], reverse=True)[:15]

html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Top 15 Pertes - Bordeaux</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: white; padding: 20px; }}
        .chart-container {{ height: 600px; width: 100%; max-width: 850px; margin: auto; }}
        h2 {{ text-align: center; font-size: 18px; color: #333; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="chart-container">
        <h2>Top 15 : Bureaux où la gauche a perdu le plus de voix au 2nd tour</h2>
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
                    label: 'Voix perdues',
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
                                    'Voix perdues : ' + d[i].perte,
                                    'Potentiel Gauche T1 (BJ) : ' + d[i].t1,
                                    'Score Hurmic T2 (BL) : ' + d[i].t2,
                                    'Taux de report : ' + d[i].rep
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ 
                        grid: {{ display: true, color: '#f0f0f0' }}, 
                        title: {{ display: true, text: 'Nombre de voix perdues' }} 
                    }},
                    y: {{ 
                        grid: {{ display: false }}, 
                        ticks: {{ font: {{ weight: 'bold' }} }} 
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
