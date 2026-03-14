"""
15_carreras.py
Genera un ranking de las 20 carreras con mayor volumen de inscriptos atribuidos
(solo cruces exactos Match_Tipo = Exacto).

SALIDA (output_dir = outputs/General/Reporte_Carreras/):
  - Reporte_Carreras_Ranking.pdf   -> Informe visual con gráfico y tabla
  - Reporte_Carreras_Datos.xlsx    -> Datos del ranking (todas las carreras)
  - Reporte_Carreras.md            -> Documentación textual del ranking
  - memoria_tecnica.md             -> Metadata del proceso
  - ranking_carreras.png           -> Gráfico PNG embebido en el PDF
"""
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "General", "Reporte_Carreras")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")

# CSV consolidado (sin segmento): contiene todas las carreras juntas
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Generando Ranking de Carreras...")

# ============================================================
# HELPER: FECHA MÁXIMA DE INSCRIPTOS
# ============================================================
# Se usa para el titulo del reporte (ej: "al 17 de febrero de 2026")
meses_es = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio",
            7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}

def get_max_date_from_inscriptos():
    """Lee la fecha máxima de pago del CSV de inscriptos (filtrando fechas futuras)."""
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
            parsed = parsed[parsed <= hoy]   # excluir fechas futuras (Fecha Aplicación)
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
print(f"Fecha maxima de inscriptos: {max_date_str}")

# ============================================================
# CARGA DE DATOS
# ============================================================
# Usamos solo las columnas necesarias para evitar cargar el CSV completo en memoria
cols_read = ['Match_Tipo', 'Insc_Carrera', 'Carrera']
available_cols = pd.read_csv(inscriptos_csv, nrows=1).columns.tolist()
use = [c for c in cols_read if c in available_cols]
df_insc = pd.read_csv(inscriptos_csv, usecols=use, low_memory=False)

# Detectar nombre real de la columna de carrera (varía entre versiones del CSV)
carrera_col = 'Insc_Carrera' if 'Insc_Carrera' in df_insc.columns else (
    'Carrera' if 'Carrera' in df_insc.columns else None)

if not carrera_col:
    print("No se encontro la columna de carrera.")
    exit()

# ============================================================
# FILTRADO Y RANKING
# ============================================================
# Solo Match Exacto: garantiza que el inscripto tuvo un lead rastreable
df_exactos = df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Exacto')].copy()
df_exactos[carrera_col] = df_exactos[carrera_col].astype(str).str.strip().str.upper()
# Eliminar valores nulos o vacíos que no aportan al ranking
df_exactos = df_exactos[~df_exactos[carrera_col].isin(['NAN', 'NONE', ''])]

# Agrupar por carrera y ordenar de mayor a menor
ranking = df_exactos.groupby(carrera_col).size().reset_index(name='Cantidad_Inscriptos')
ranking = ranking.sort_values('Cantidad_Inscriptos', ascending=False).reset_index(drop=True)
ranking.index = ranking.index + 1  # ranking 1-based para el informe
top_carreras = ranking.head(20)

print(f"Total carreras con inscriptos exactos: {len(ranking)}")
print(f"Top 3: {top_carreras.head(3)[carrera_col].tolist()}")

# ============================================================
# GRÁFICO PNG
# ============================================================
plt.figure(figsize=(12, 8))
sns.barplot(data=top_carreras, y=carrera_col, x='Cantidad_Inscriptos', palette='viridis')
plt.title(f'Top 20 Carreras con Mayor Volumen de Inscriptos Atribuidos (al {max_date_str})')
plt.xlabel('Cantidad de Inscriptos (Cruce Exacto)')
plt.ylabel('Carrera')
# Etiquetas de valor al lado de cada barra
for p in plt.gca().patches:
    width = p.get_width()
    plt.text(width + 1, p.get_y() + p.get_height() / 2. + 0.2, f'{int(width):,}', ha="left")
plt.tight_layout()
chart_path = os.path.join(output_dir, 'ranking_carreras.png')
plt.savefig(chart_path, bbox_inches='tight')
plt.close()
print(f"-> PNG generado: {chart_path}")

# ============================================================
# EXCEL: RANKING COMPLETO
# ============================================================
xlsx_path = os.path.join(output_dir, 'Reporte_Carreras_Datos.xlsx')
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    # Hoja 1: Top 20 (la que se muestra en el PDF)
    top_carreras.reset_index(drop=True).to_excel(writer, sheet_name='Top20_Carreras', index=False)
    # Hoja 2: Ranking completo de todas las carreras
    ranking.reset_index(drop=True).to_excel(writer, sheet_name='Ranking_Completo', index=False)
print(f"-> Excel generado: {xlsx_path}")

# ============================================================
# PDF: INFORME VISUAL
# ============================================================
pdf = FPDF()
pdf.add_page()

# Encabezado
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Ranking de Inscriptos por Carrera', ln=True, align="C")
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 10, 'Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.', ln=True, align="C")
pdf.cell(0, 8, f'Datos actualizados al {max_date_str}', ln=True, align="C")
pdf.ln(5)

# Descripcion metodológica
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6,
    "El siguiente informe analiza las carreras que lograron mayor volumen de matriculacion de estudiantes "
    "a los que se les pudo comprobar de forma fehaciente (Match_Tipo = Exacto) que interactuaron de forma "
    "previa con las campanas publicitarias (Paid Ads) o los canales organicos registrados.")
pdf.ln(5)

# Gráfico Top 20
pdf.image(chart_path, x=10, w=190)
pdf.ln(10)

# Tabla: listado completo del ranking
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, "Listado Completo (Ranking Descendente):", ln=True)
pdf.set_font('Helvetica', '', 9)
for _, r in ranking.iterrows():
    pdf.cell(0, 5, f" - {r[carrera_col]}: {r['Cantidad_Inscriptos']:,} inscriptos", ln=True)

pdf_path = os.path.join(output_dir, 'Reporte_Carreras_Ranking.pdf')
pdf.output(pdf_path)
print(f"-> PDF generado: {pdf_path}")

# ============================================================
# MARKDOWN: DOCUMENTACIÓN DEL RANKING
# ============================================================
md_path = os.path.join(output_dir, 'Reporte_Carreras.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"# Ranking de Inscriptos por Carrera\n\n")
    f.write(f"**Actualizado al:** {max_date_str}  \n")
    f.write(f"**Criterio:** Solo inscriptos con Match_Tipo = Exacto (cruce confirmado con lead)  \n")
    f.write(f"**Total carreras con inscriptos exactos:** {len(ranking)}  \n\n")
    f.write("## Top 20 Carreras\n\n")
    f.write(top_carreras[[carrera_col, 'Cantidad_Inscriptos']].to_markdown(index=False))
    f.write("\n\n## Ranking Completo\n\n")
    f.write(ranking[[carrera_col, 'Cantidad_Inscriptos']].to_markdown(index=False))
print(f"-> MD generado: {md_path}")

# ============================================================
# MEMORIA TÉCNICA
# ============================================================
memoria = f"""# Memoria Tecnica: Ranking de Carreras

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Script:** `15_carreras.py`

## Fuentes de Datos
- Inscriptos: `{inscriptos_csv}`

## Metodologia
- Solo se consideran registros con `Match_Tipo` que contenga 'Exacto'
- La columna de carrera usada es: `{carrera_col}`
- Valores nulos/vacíos en carrera son excluidos del ranking

## Volúmenes
| Metrica | Valor |
|---|---|
| Total inscriptos exactos | {len(df_exactos):,} |
| Total carreras con inscriptos | {len(ranking)} |
| Top carrera | {top_carreras.iloc[0][carrera_col]} ({int(top_carreras.iloc[0]['Cantidad_Inscriptos']):,} insc.) |

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `Reporte_Carreras_Ranking.pdf` | Informe visual con grafico y tabla |
| `Reporte_Carreras_Datos.xlsx` | Ranking completo en Excel (2 hojas) |
| `Reporte_Carreras.md` | Documentacion textual del ranking |
| `ranking_carreras.png` | Grafico PNG embebido en PDF |
| `memoria_tecnica.md` | Este archivo |
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria)
print(f"-> Memoria tecnica generada en: {output_dir}")
print("Proceso finalizado.")
