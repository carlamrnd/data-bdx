import csv
import json

def to_float(val):
    try:
        return float(val.replace(',', '.').replace('%', '').strip())
    except:
        return 0.0

# Mapping Quartiers (Bordeaux Centre / Chartrons / etc. pour les bastions mobilisés)
# Je vais essayer d'extraire le quartier si possible ou utiliser une valeur générique par défaut
data = []
try:
    with open('bâtons mobilisés.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) < 100: continue
            code_bv = row[0]
            nom_bv = row[1]
            voix_t1 = to_float(row[87]) # TOTAL GAUCHE T1 (Indice 87 dans ce fichier)
            voix_t2 = to_float(row[84]) # Hurmic T2 (Indice 84 dans ce fichier)
            
            # Vérifier si c'est bien Hurmic (Nom candidat 2 à l'indice 83)
            if row[83].upper() != "HURMIC":
                # Chercher Hurmic dans le header si besoin, mais selon l'index 83/84 ça semble bon
                pass

            data.append({
                "bureau": nom_bv,
                "code": code_bv,
                "quartier": "Bordeaux", # Valeur par défaut
                "t1": int(voix_t1),
                "t2": int(voix_t2),
                "difference": int(voix_t2 - voix_t1),
                "report": row[90] # TAUX DE REPORT
            })
except Exception as e:
    print(f"Erreur lors de la lecture : {e}")

# Trier par score T2
data.sort(key=lambda x: x['t2'], reverse=True)

html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Bastions Mobilisés - Bordeaux 2026</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; padding: 20px; background: #fff; }}
        .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; border: 1px solid #eee; }}
        h2 {{ text-align: center; color: #111; font-size: 22px; margin-bottom: 5px; }}
        p {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 35px; }}
        .legend-custom {{ display: flex; justify-content: center; gap: 20px; font-size: 12px; margin-bottom: 20px; color: #444; }}
        .leg-item {{ display: flex; align-items: center; gap: 6px; }}
        .dot {{ width: 10px; height: 10px; border-radius: 2px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Bastions Mobilisés : Potentiel vs Réel</h2>
        <p>Comparaison entre le réservoir de voix de gauche (T1) et le score de Pierre Hurmic (T2) dans les bureaux mobilisés.</p>
        
        <div class="legend-custom">
            <div class="leg-item"><div class="dot" style="background:#9ca3af"></div> Potentiel Gauche (T1)</div>
            <div class="leg-item"><div class="dot" style="background:#f97316"></div> Réel Hurmic (T2)</div>
        </div>

        <canvas id="myChart"></canvas>
    </div>

    <script>
        const rawData = {json.dumps(data)};
        
        const ctx = document.getElementById('myChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: rawData.map(d => d.bureau),
                datasets: [
                    {{
                        label: 'Potentiel Gauche (T1)',
                        data: rawData.map(d => d.t1),
                        backgroundColor: '#9ca3af',
                        borderRadius: 2,
                        categoryPercentage: 0.8,
                        barPercentage: 0.9
                    }},
                    {{
                        label: 'Pierre Hurmic (T2)',
                        data: rawData.map(d => d.t2),
                        backgroundColor: '#f97316',
                        borderRadius: 2,
                        categoryPercentage: 0.8,
                        barPercentage: 0.9
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.85)',
                        padding: 12,
                        callbacks: {{
                            title: (items) => rawData[items[0].dataIndex].bureau + " (Bureau " + rawData[items[0].dataIndex].code + ")",
                            label: function(context) {{
                                const d = rawData[context.dataIndex];
                                if (context.datasetIndex === 0) return "Potentiel T1 : " + d.t1 + " voix";
                                return "Réel Hurmic T2 : " + d.t2 + " voix";
                            }},
                            afterBody: function(context) {{
                                const d = rawData[context[0].dataIndex];
                                const labelDiff = d.difference >= 0 ? "Voix gagnées : " : "Voix perdues : ";
                                return [
                                    '',
                                    labelDiff + Math.abs(d.difference),
                                    'Taux de report : ' + d.report,
                                    'Quartier : ' + d.quartier
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{ 
                        beginAtZero: true,
                        title: {{ display: true, text: 'Nombre de voix', font: {{ weight: 'bold' }} }},
                        grid: {{ color: '#f9f9f9' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ font: {{ size: 10 }} }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('graphique_bastions_mobilises.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
