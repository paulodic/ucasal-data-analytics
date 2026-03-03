import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "Reporte_Carreras")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")

inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Generando Ranking de Carreras...")

# Fechas maximas
meses_es = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio", 
            7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}

def get_max_date_from_inscriptos():
    try:
        cols_i = pd.read_csv(inscriptos_csv, nrows=1).columns.tolist()
        pago_candidates = [c for c in cols_i if 'fecha' in c.lower() and 'pago' in c.lower()]
        if not pago_candidates:
            d = datetime.now()
            return f"{d.day} de {meses_es[d.month]} de {d.year}"
        
        df_i = pd.read_csv(inscriptos_csv, usecols=pago_candidates, low_memory=False)
        max_date = pd.NaT
        for col in pago_candidates:
            parsed = pd.to_datetime(df_i[col], errors='coerce', dayfirst=True)
            hoy = pd.Timestamp.now()
            parsed = parsed[parsed <= hoy]
            col_max = parsed.max()
            if pd.notna(col_max):
                if pd.isna(max_date) or col_max > max_date:
                    max_date = col_max
        if pd.notna(max_date):
            return f"{max_date.day} de {meses_es[max_date.month]} de {max_date.year}"
    except Exception:
        pass
    d = datetime.now()
    return f"{d.day} de {meses_es[d.month]} de {d.year}"

max_date_str = get_max_date_from_inscriptos()
print(f"Fecha máxima de inscriptos: {max_date_str}")

# Leer Base
cols_read = ['Match_Tipo', 'Insc_Carrera', 'Carrera']
available_cols = pd.read_csv(inscriptos_csv, nrows=1).columns.tolist()
use = [c for c in cols_read if c in available_cols]
df_insc = pd.read_csv(inscriptos_csv, usecols=use, low_memory=False)

carrera_col = 'Insc_Carrera' if 'Insc_Carrera' in df_insc.columns else ('Carrera' if 'Carrera' in df_insc.columns else None)

if not carrera_col:
    print("No se encontró la columna de carrera.")
    exit()

# Filtrar a solo exactos para la calidad del reporte
df_exactos = df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Exacto')].copy()
df_exactos[carrera_col] = df_exactos[carrera_col].astype(str).str.strip().str.upper()
df_exactos = df_exactos[~df_exactos[carrera_col].isin(['NAN', 'NONE', ''])]

# Agrupar y rankear
ranking = df_exactos.groupby(carrera_col).size().reset_index(name='Cantidad_Inscriptos')
ranking = ranking.sort_values('Cantidad_Inscriptos', ascending=False)
top_carreras = ranking.head(20)

# Graficar
plt.figure(figsize=(12, 8))
sns.barplot(data=top_carreras, y=carrera_col, x='Cantidad_Inscriptos', palette='viridis')
plt.title(f'Top 20 Carreras con Mayor Volumen de Inscriptos Atribuidos (al {max_date_str})')
plt.xlabel('Cantidad de Inscriptos (Cruce Exacto)')
plt.ylabel('Carrera')
for p in plt.gca().patches:
    width = p.get_width()
    plt.text(width + 1, p.get_y() + p.get_height()/2. + 0.2, f'{int(width):,}', ha="left")

plt.tight_layout()
chart_path = os.path.join(output_dir, 'ranking_carreras.png')
plt.savefig(chart_path, bbox_inches='tight')
plt.close()

# Generar PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Ranking de Inscriptos por Carrera', ln=True, align="C")
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 10, f'Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.', ln=True, align="C")
pdf.cell(0, 8, f'Datos actualizados al {max_date_str}', ln=True, align="C")
pdf.ln(5)

pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, "El siguiente informe analiza las carreras que lograron mayor volumen de matriculación de estudiantes a los "
                     "que se les pudo comprobar de forma fehaciente (Match_Tipo = Exacto) que interactuaron de forma previa con "
                     "las campañas publicitarias (Paid Ads) o los canales orgánicos registrados.")
pdf.ln(5)

pdf.image(chart_path, x=10, w=190)
pdf.ln(10)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, "Listado Completo (Ranking Descendente):", ln=True)
pdf.set_font('Helvetica', '', 9)

# Imprimir tabla top
for _, r in ranking.iterrows():
    pdf.cell(0, 5, f" - {r[carrera_col]}: {r['Cantidad_Inscriptos']:,} inscriptos", ln=True)

pdf_path = os.path.join(output_dir, 'Reporte_Carreras_Ranking.pdf')
pdf.output(pdf_path)

print(f"Ranking exportado exitosamente a: {pdf_path}")
