"""
08_tabla_utm.py
Genera tabla de campañas UTM por segmento con volumen de leads, inscriptos y tasa
de conversión. Exporta PDF y Excel.

ENTRADA: outputs/Data_Base/<Segmento>/reporte_marketing_leads_completos.csv
SALIDA (outputs/<Segmento>/):
  - tabla_utm_campaigns.xlsx  -> Tabla de UTM Campaigns
  - Tabla_UTM_Campaigns.pdf   -> Versión PDF
"""
import pandas as pd
import os
from fpdf import FPDF

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento)
os.makedirs(output_dir, exist_ok=True)

base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")

print("Cargando datos...")
df = pd.read_csv(leads_csv, low_memory=False)

# Clasificar
def classify(v):
    s = str(v)
    if 'Exacto' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

df['_mc'] = df['Match_Tipo'].apply(classify)
df_main = df[df['_mc'] != 'fuzzy'].copy()

# Limpiar UTM
for col in ['UtmSource', 'UtmCampaign', 'UtmMedium']:
    if col in df_main.columns:
        df_main[col] = df_main[col].astype(str).replace('nan', '').str.strip()

# Deduplicar por persona
df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

# REGLA DE NEGOCIO COHORTES (Muestra para Conversión)
if segmento == 'Grado_Pregrado':
    df_main['Fecha_Limpia'] = pd.to_datetime(df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_main_conv = df_main[df_main['Fecha_Limpia'] >= '2025-09-01'].copy()
else:
    df_main_conv = df_main.copy()

# Filtrar solo los que tienen UTM Campaign
df_utm = df_main[df_main['UtmCampaign'] != ''].copy()
df_utm_conv = df_main_conv[df_main_conv['UtmCampaign'] != ''].copy()

print(f"Leads con UTM Campaign: {len(df_utm):,}")

# ==========================================
# TABLA POR UTM CAMPAIGN (deduplicado por persona)
# ==========================================
df_utm_dedup = df_utm.drop_duplicates(subset='_pk')
df_utm_dedup_conv = df_utm_conv.drop_duplicates(subset='_pk')

tabla_vol = df_utm_dedup.groupby('UtmCampaign').agg(
    Personas_Unicas=('_pk', 'nunique')
).reset_index()

tabla_conv = df_utm_dedup_conv.groupby('UtmCampaign').agg(
    Personas_Muestra=('_pk', 'nunique'),
    Inscriptos_Exactos=('_mc', lambda x: (x == 'exacto').sum())
).reset_index()

tabla = pd.merge(tabla_vol, tabla_conv, on='UtmCampaign', how='outer').fillna(0)

# Consultas totales (sin deduplicar)
consultas = df_utm.groupby('UtmCampaign').size().reset_index(name='Total_Consultas')
tabla = tabla.merge(consultas, on='UtmCampaign', how='left')

# Tasa de conversion
tabla['Tasa_Conversion_%'] = (tabla['Inscriptos_Exactos'] / tabla['Personas_Muestra'] * 100).round(2)
tabla.loc[tabla['Personas_Muestra'] == 0, 'Tasa_Conversion_%'] = 0.0

# Ordenar por personas
tabla = tabla.sort_values('Personas_Unicas', ascending=False)

# Agregar UTM Source predominante para cada campaign
src = df_utm.groupby('UtmCampaign')['UtmSource'].agg(
    lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else ''
).reset_index(name='UtmSource_Principal')
tabla = tabla.merge(src, on='UtmCampaign', how='left')

# Agregar UTM Medium predominante
med = df_utm.groupby('UtmCampaign')['UtmMedium'].agg(
    lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else ''
).reset_index(name='UtmMedium_Principal')
tabla = tabla.merge(med, on='UtmCampaign', how='left')

# Reordenar columnas
tabla = tabla[['UtmCampaign', 'UtmSource_Principal', 'UtmMedium_Principal',
               'Total_Consultas', 'Personas_Unicas', 'Personas_Muestra', 'Inscriptos_Exactos', 'Tasa_Conversion_%']]

# Exportar Excel
xlsx_path = os.path.join(output_dir, "tabla_utm_campaigns.xlsx")
tabla.to_excel(xlsx_path, index=False, sheet_name='UTM Campaigns')
print(f"-> Tabla UTM guardada en: {xlsx_path}")
print(f"   {len(tabla)} campanas distintas")
print(f"   Top 10:")
print(tabla.head(10).to_string(index=False))

# ==========================================
# AGREGAR AL PDF COMPLETO
# ==========================================
print("\nAgregando tabla UTM al PDF completo...")

# Leer PDF existente y crear uno nuevo que incluya la tabla
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Tabla de UTM Campaigns - Detalle', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_text_color(0, 0, 0)
        self.ln(2)
    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, f'Pagina {self.page_no()}', new_x="LMARGIN", new_y="NEXT", align='C')

pdf = PDF('L')  # Landscape para que entre la tabla
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Titulo
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 12, 'Detalle de UTM Campaigns', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(3)
pdf.set_font('Helvetica', '', 9)
pdf.set_x(10)
pdf.multi_cell(260, 5,
    f'Se identificaron {len(tabla)} campanas UTM distintas con un total de {len(df_utm):,} consultas de leads.\n'
    f'Modelo: Deduplicado por persona (DNI). Match: Exacto (DNI/Email/Telefono/Celular). Any-Touch: ver Informe Analitico (04).')
if segmento == 'Grado_Pregrado':
    pdf.set_font('Helvetica', 'I', 8)
    pdf.multi_cell(260, 5, "Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads desde Septiembre 2024 (Personas_Muestra).")
    pdf.set_font('Helvetica', '', 9)
pdf.ln(5)

# Cabecera de tabla
col_widths = [72, 30, 25, 25, 25, 25, 25, 25]
headers = ['UTM Campaign', 'Source', 'Medium', 'Consultas', 'Pers.(Hist.)', 'Pers.(Mues.)', 'Inscrip.', 'Conv. %']

pdf.set_font('Helvetica', 'B', 7)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers):
    pdf.cell(col_widths[i], 7, h, border=1, fill=True, align='C')
pdf.ln()
pdf.set_text_color(0, 0, 0)

# Filas
pdf.set_font('Helvetica', '', 6)
for _, row in tabla.iterrows():
    # Alternar color de fondo
    if _ % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)
    
    campaign_name = str(row['UtmCampaign'])[:40]  # Truncar si es muy largo
    pdf.cell(col_widths[0], 6, campaign_name, border=1, fill=True)
    pdf.cell(col_widths[1], 6, str(row['UtmSource_Principal'])[:18], border=1, fill=True, align='C')
    pdf.cell(col_widths[2], 6, str(row['UtmMedium_Principal'])[:15], border=1, fill=True, align='C')
    pdf.cell(col_widths[3], 6, f"{int(row['Total_Consultas']):,}", border=1, fill=True, align='R')
    pdf.cell(col_widths[4], 6, f"{int(row['Personas_Unicas']):,}", border=1, fill=True, align='R')
    pdf.cell(col_widths[5], 6, f"{int(row.get('Personas_Muestra', 0)):,}", border=1, fill=True, align='R')
    pdf.cell(col_widths[6], 6, f"{int(row['Inscriptos_Exactos']):,}", border=1, fill=True, align='R')
    pdf.cell(col_widths[7], 6, f"{row['Tasa_Conversion_%']:.2f}%", border=1, fill=True, align='R')
    pdf.ln()

# Totales
pdf.set_font('Helvetica', 'B', 7)
pdf.set_fill_color(52, 73, 94)
pdf.set_text_color(255, 255, 255)
pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 7, 'TOTALES', border=1, fill=True, align='R')
pdf.cell(col_widths[3], 7, f"{int(tabla['Total_Consultas'].sum()):,}", border=1, fill=True, align='R')
pdf.cell(col_widths[4], 7, f"{int(tabla['Personas_Unicas'].sum()):,}", border=1, fill=True, align='R')
pdf.cell(col_widths[5], 7, f"{int(tabla.get('Personas_Muestra', pd.Series([0])).sum()):,}", border=1, fill=True, align='R')
pdf.cell(col_widths[6], 7, f"{int(tabla['Inscriptos_Exactos'].sum()):,}", border=1, fill=True, align='R')
tasa_total = (tabla['Inscriptos_Exactos'].sum() / tabla['Personas_Muestra'].sum() * 100) if tabla['Personas_Muestra'].sum() > 0 else 0
pdf.cell(col_widths[7], 7, f"{tasa_total:.2f}%", border=1, fill=True, align='R')
pdf.ln()

# Nota Metodologica
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Nota Metodologica', new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.set_font('Helvetica', '', 9)
pdf.multi_cell(260, 5,
    'Cruce de datos: Deduplicado por persona (DNI). Match exacto por DNI, Email, Telefono y Celular.\n'
    'Modelo Any-Touch: Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). '
    'Detalle en el Informe Analitico (04_reporte_final).\n'
    'Fuente: Consultas exportadas de Salesforce, inscriptos del sistema academico.')

pdf_path = os.path.join(output_dir, "Tabla_UTM_Campaigns.pdf")
pdf.output(pdf_path)
print(f"\n-> PDF de tabla UTM guardado en: {pdf_path}")
print("Listo!")
