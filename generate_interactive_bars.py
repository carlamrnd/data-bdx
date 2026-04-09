import pandas as pd
import plotly.graph_objects as go
import csv

def clean_percent(val):
    if isinstance(val, str):
        return val.replace(',', '.').replace('%', '').strip()
    return val

def to_float(val):
    try:
        return float(clean_percent(val))
    except:
        return 0.0

# Reading the CSV carefully with standard csv module to handle potential issues
data = []
with open('bâtons démobilisés.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) < 100: continue # Skip malformed rows
        
        # Mapping based on previous investigation
        # 0: Code BV
        # 1: Nom BV
        # 4: % Votants T1
        # 66: % Votants T2
        # 83: Voix 2 (Hurmic T2)
        # 84: % Voix/inscrits 2
        # 85: % Voix/exprimés 2
        # 86: TOTAL GAUCHE T1
        # 90: REPORT GAUCHE
        
        bureau = row[1]
        code_bv = row[0]
        voix_t1 = to_float(row[86])
        voix_t2 = to_float(row[83])
        
        # Tooltip data
        part_t1 = row[4]
        part_t2 = row[66]
        report = row[90]
        perc_t2 = row[85]
        
        voix_manquantes = voix_t1 - voix_t2
        
        data.append({
            "Bureau": f"{code_bv} - {bureau}",
            "Quartier": "Bordeaux", # Placeholder as not found
            "Gauche_T1": voix_t1,
            "Hurmic_T2": voix_t2,
            "Voix_manquantes": max(0, voix_manquantes),
            "Report": report,
            "Part_T1": part_t1,
            "Part_T2": part_t2,
            "Perc_T2": perc_t2
        })

df = pd.DataFrame(data)

# Sort by Gauche_T1 for better visualization
df = df.sort_values(by="Gauche_T1", ascending=False)

fig = go.Figure()

# Bar for Gauche T1 (Potentiel) - Light Gray
fig.add_trace(go.Bar(
    x=df["Bureau"],
    y=df["Gauche_T1"],
    name="Potentiel Gauche (T1)",
    marker_color="#D3D3D3",
    hovertemplate=(
        "<b>%{x}</b><br>" +
        "Quartier: %{customdata[0]}<br>" +
        "Voix T1 (Potentiel): %{y}<br>" +
        "Participation T1: %{customdata[1]}<br>" +
        "<extra></extra>"
    ),
    customdata=df[["Quartier", "Part_T1"]]
))

# Bar for Hurmic T2 (Réel) - Green
fig.add_trace(go.Bar(
    x=df["Bureau"],
    y=df["Hurmic_T2"],
    name="Score Hurmic (T2)",
    marker_color="#27ae60",
    hovertemplate=(
        "<b>%{x}</b><br>" +
        "Quartier: %{customdata[0]}<br>" +
        "Voix T2 (Réel): %{y} (%{customdata[1]})<br>" +
        "Voix manquantes: %{customdata[2]}<br>" +
        "Taux de report: %{customdata[3]}<br>" +
        "Participation T2: %{customdata[4]}<br>" +
        "<extra></extra>"
    ),
    customdata=df[["Quartier", "Perc_T2", "Voix_manquantes", "Report", "Part_T2"]]
))

fig.update_layout(
    title="Comparaison Potentiel Gauche T1 vs Score Hurmic T2 par Bureau",
    xaxis_title="Bureaux de vote",
    yaxis_title="Nombre de voix",
    barmode='group',
    legend_title="Scrutin",
    template="plotly_white",
    hovermode="x unified",
    xaxis={'tickangle': 45}
)

fig.write_html("graphique_interactif_hurmic.html")
print("Graphique généré avec succès : graphique_interactif_hurmic.html")
