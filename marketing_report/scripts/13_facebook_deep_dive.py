"""
13_facebook_deep_dive.py
Análisis profundo del tráfico Facebook/Meta por segmento.

Aísla leads del ecosistema Meta: FuenteLead=18 (Facebook Lead Ads) O UTM
conteniendo fb/facebook/ig/instagram/meta. Genera distribución por red social,
campañas top, y métricas de conversión.

ENTRADA:
  - outputs/Data_Base/<Segmento>/reporte_marketing_leads_completos.csv
  - outputs/Data_Base/<Segmento>/reporte_marketing_inscriptos_origenes.csv
SALIDA (outputs/<Segmento>/Facebook_Deep_Dive/):
  - reporte_especifico_facebook.xlsx     -> Tablas detalladas
  - Informe_Facebook_Deep_Dive.pdf       -> PDF con gráficos
  - Informe_Facebook_Deep_Dive.md        -> Versión markdown
  - distribucion_redes_meta.png          -> Gráfico pie
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from fpdf import FPDF
from datetime import datetime

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Facebook_Deep_Dive")
os.makedirs(output_dir, exist_ok=True)

base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Cargando bases de datos con columnas limitadas...")
usecols_leads = ['Id. candidato/contacto', 'UtmSource', 'UtmCampaign', 'UtmMedium', 'Match_Tipo', 'FuenteLead', 'Consulta: Fecha de creación']
df_leads = pd.read_csv(leads_csv, usecols=lambda c: c in usecols_leads, low_memory=False)

try:
    cols_insc = pd.read_csv(inscriptos_csv, nrows=1).columns.tolist()
    usecols_insc = [c for c in ['Inscripto_Tmp_ID', 'Insc_Fecha Pago', 'Insc_Fecha Aplicación'] if c in cols_insc]
    df_insc = pd.read_csv(inscriptos_csv, usecols=usecols_insc, low_memory=False)
except Exception:
    df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

def get_max_date(df_i):
    meses = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio", 
             7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}
    # SOLO columnas de PAGO (no Aplicación que puede ser futura)
    for col in ['Insc_Fecha Pago', 'Fecha Pago']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], errors='coerce', dayfirst=True)
            hoy = pd.Timestamp.now()
            dates = dates[dates <= hoy]
            if not dates.isna().all():
                d = dates.max()
                return f"{d.day} de {meses[d.month]} de {d.year}"
    d = datetime.now()
    return f"{d.day} de {meses[d.month]} de {d.year}"

max_date_str = get_max_date(df_insc)

# LIMPIEZA STRINGS UTM
df_leads['UtmSource'] = df_leads['UtmSource'].astype(str).str.lower().str.strip()
df_leads['UtmCampaign'] = df_leads['UtmCampaign'].astype(str).str.strip().replace('nan', 'Sin Campaña')
df_leads['UtmMedium'] = df_leads['UtmMedium'].astype(str).str.strip()

# AISLAR TRÁFICO META: UTM (Facebook, Instagram, Meta) + FuenteLead == 18 (Facebook Lead Ads)
meta_keywords = ['fb', 'facebook', 'ig', 'instagram', 'meta']
mask_utm = df_leads['UtmSource'].str.contains('|'.join(meta_keywords), na=False)

# FuenteLead 18 = Facebook Lead Ads (confirmado por usuario)
df_leads['FuenteLead_Num'] = pd.to_numeric(df_leads['FuenteLead'], errors='coerce')
mask_fuente = df_leads['FuenteLead_Num'] == 18

mask_meta = mask_utm | mask_fuente

df_meta = df_leads[mask_meta].copy()
df_meta['Match_Tipo'] = df_meta['Match_Tipo'].fillna('')

# Muestra para conversión
if segmento == 'Grado_Pregrado':
    df_meta['Fecha_Limpia'] = pd.to_datetime(df_meta['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_meta_conv = df_meta[df_meta['Fecha_Limpia'] >= '2025-09-01'].copy()
else:
    df_meta_conv = df_meta.copy()

total_meta_leads = len(df_meta)
total_meta_leads_conv = len(df_meta_conv)

if total_meta_leads == 0:
    print("No se encontraron leads procedentes del ecosistema Facebook/Meta.")
    exit()

exactos_meta = len(df_meta_conv[df_meta_conv['Match_Tipo'].str.contains('Exacto', case=False, na=False)])
insc_dni_meta = len(df_meta_conv[df_meta_conv['Match_Tipo'] == 'Exacto (DNI)'])
insc_email_meta = len(df_meta_conv[df_meta_conv['Match_Tipo'] == 'Exacto (Email)'])
insc_tel_meta = len(df_meta_conv[df_meta_conv['Match_Tipo'] == 'Exacto (Teléfono)'])
insc_cel_meta = len(df_meta_conv[df_meta_conv['Match_Tipo'] == 'Exacto (Celular)'])
conversion_meta = (exactos_meta / total_meta_leads_conv) * 100 if total_meta_leads_conv > 0 else 0

md_content = f"# Deep Dive: Facebook & Meta Ecosystem\n\n*(Datos actualizados al {max_date_str})*\n\n"
md_content += "Este informe analiza de forma exclusiva el volumen y rendimiento de los **Leads capturados a través de propiedades de Meta (Facebook, Instagram, Meta Ads)**.\n\n"
if segmento == 'Grado_Pregrado':
    md_content += "*(Nota Cohortes: Las tasas de conversión se calculan sobre leads desde Septiembre 2025, coincidiendo con la campaña de ingreso 2026.)*\n\n"
md_content += f"- **Volumen de Leads Totales Meta (Histórico):** {total_meta_leads:,}\n"
md_content += f"- **Volumen de Leads Meta (Muestra Conversión):** {total_meta_leads_conv:,}\n"
md_content += f"- **Inscriptos Confirmados Meta:** {exactos_meta:,}\n"
md_content += f"  - por DNI: {insc_dni_meta:,} | por Email: {insc_email_meta:,} | por Teléfono: {insc_tel_meta:,} | por Celular: {insc_cel_meta:,}\n"
md_content += f"- **Tasa de Conversión General Meta (Muestra):** {conversion_meta:.2f}%\n\n"

# --- 1. Distribución de Red (FB vs IG) ---
print("Analizando distribución de red...")
def clasificar_red(s):
    if 'ig' in s or 'instagram' in s: return 'Instagram'
    if 'fb' in s or 'facebook' in s: return 'Facebook'
    if 'meta' in s: return 'Meta (Genérico)'
    return 'Otro Meta'

df_meta_conv['Red_Primaria'] = df_meta_conv['UtmSource'].apply(clasificar_red)
red_gb = df_meta_conv.groupby('Red_Primaria').agg(
    Leads_Muestra=('Id. candidato/contacto', 'count'),
    Inscriptos=('Match_Tipo', lambda x: x.str.contains('Exacto', case=False, na=False).sum())
).reset_index()

red_gb['Conversión_%'] = (red_gb['Inscriptos'] / red_gb['Leads_Muestra'] * 100).round(2)
red_gb = red_gb.sort_values(by='Leads_Muestra', ascending=False)

md_content += "## 1. Distribución de Origen por Red Social (Muestra Conversión)\n\n"
md_content += red_gb.to_markdown(index=False) + "\n\n"

# Gráfico Redes (Volumen total)
df_meta['Red_Primaria'] = df_meta['UtmSource'].apply(clasificar_red)
red_gb_tot = df_meta.groupby('Red_Primaria').agg(
    Leads=('Id. candidato/contacto', 'count')
).reset_index()

plt.figure(figsize=(8, 8))
plt.pie(red_gb_tot['Leads'], labels=red_gb_tot['Red_Primaria'], autopct='%1.1f%%', colors=sns.color_palette('pastel'), startangle=140)
plt.title('Distribución de Leads por Red (Meta Histórico)')
plt.savefig(os.path.join(output_dir, 'distribucion_redes_meta.png'), bbox_inches='tight')
plt.close()

# --- 2. Top Campañas Meta ---
print("Analizando campañas...")
camp_gb = df_meta_conv[df_meta_conv['UtmCampaign'] != 'Sin Campaña'].groupby('UtmCampaign').agg(
    Leads_Muestra=('Id. candidato/contacto', 'count'),
    Inscriptos=('Match_Tipo', lambda x: x.str.contains('Exacto', case=False, na=False).sum())
).reset_index()

camp_gb['Conversión_%'] = (camp_gb['Inscriptos'] / camp_gb['Leads_Muestra'] * 100).round(2)

# Filtrar campañas basura (con menos de 5 leads en la muestra)
camp_gb = camp_gb[camp_gb['Leads_Muestra'] >= 5]

top_leads_camps = camp_gb.sort_values('Leads_Muestra', ascending=False).head(15)
top_conv_camps = camp_gb[camp_gb['Inscriptos'] > 0].sort_values('Conversión_%', ascending=False).head(15)

md_content += "## 2. Top 15 Campañas por Volumen de Leads (Muestra Conversión)\n\n"
md_content += top_leads_camps.to_markdown(index=False) + "\n\n"

plt.figure(figsize=(10, 8))
sns.barplot(x='Leads_Muestra', y='UtmCampaign', data=top_leads_camps, palette='Blues_r')
plt.title('Top 15 Campañas de Meta por Volumen de Leads (Muestra)')
plt.xlabel('Cantidad de Leads')
plt.ylabel('Campaña')
plt.grid(axis='x', alpha=0.3)
plt.savefig(os.path.join(output_dir, 'top_campanas_volumen.png'), bbox_inches='tight')
plt.close()

# Exportar a Excel
print("Generando Excel y Markdown...")
md_content += "\n## Nota Metodológica\n\n"
md_content += "- **Modelo de atribución:** Directa por canal (FuenteLead=18 o UTM de Meta). Deduplicado por lead.\n"
md_content += f"- **Match Exacto:** DNI ({insc_dni_meta:,}), Email ({insc_email_meta:,}), Teléfono ({insc_tel_meta:,}), Celular ({insc_cel_meta:,}). Total: {exactos_meta:,}.\n"
md_content += "- **Any-Touch:** Para ver cuántos inscriptos tuvieron *al menos un contacto* con Meta (aunque también consultaron por otros canales), referirse al Informe Analítico (04_reporte_final).\n"
if segmento == 'Grado_Pregrado':
    md_content += "- **Ventana de conversión:** Leads desde 01/09/2025 (campaña ingreso 2026).\n"
else:
    md_content += "- **Ventana de conversión:** Año calendario 2026.\n"

with open(os.path.join(output_dir, 'Informe_Facebook_Deep_Dive.md'), 'w', encoding='utf-8') as f:
    f.write(md_content)

with pd.ExcelWriter(os.path.join(output_dir, 'reporte_especifico_facebook.xlsx')) as writer:
    red_gb.to_excel(writer, sheet_name='Por_Red', index=False)
    camp_gb.sort_values('Leads_Muestra', ascending=False).to_excel(writer, sheet_name='Todas_Campañas', index=False)

# Generar PDF
print("Generando PDF de resultados...")
class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "Marketing Report - Facebook & Meta Deep Dive", ln=True, align="C")
        self.set_font("Helvetica", 'I', 10)
        self.cell(0, 6, f"Datos actualizados al {max_date_str}", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

pdf = PDFReport()
pdf.add_page()

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Resumen Global del Ecosistema Meta", ln=True)
pdf.set_font("Helvetica", size=11)
if segmento == 'Grado_Pregrado':
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 6, "Nota Cohortes: Las tasas de conversion se calculan sobre leads desde Septiembre 2025 (campaña ingreso 2026).", ln=True)
    pdf.set_font("Helvetica", size=11)

pdf.multi_cell(0, 6, f"Volumen total de Leads procedentes de Facebook o Instagram (Histórico): {total_meta_leads:,}\n" \
                     f"Volumen de Leads (Muestra Conversión): {total_meta_leads_conv:,}\n" \
                     f"(Incluye UTM de Meta + FuenteLead 18 de Facebook Lead Ads)\n" \
                     f"Inscriptos Exactos logrados en la muestra: {exactos_meta:,}\n" \
                     f"Tasa de Conversión (Muestra): {conversion_meta:.2f}%")
pdf.ln(10)

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Distribucion por Red Social", ln=True)
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'distribucion_redes_meta.png'), w=120)
except Exception as e:
    print(f"Error integrando imagen red: {e}")
pdf.ln(10)

pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Top Campañas por Volumen", ln=True)
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'top_campanas_volumen.png'), w=170)
except Exception as e:
    print(f"Error integrando imagen camp: {e}")

# Nota Metodológica
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Nota Metodológica", ln=True)
pdf.set_font("Helvetica", size=9)
nota_met = (
    f"Modelo de atribución: Directa por canal (FuenteLead=18 o UTM de Meta). Deduplicado por lead.\n"
    f"Match Exacto: DNI ({insc_dni_meta:,}), Email ({insc_email_meta:,}), Telefono ({insc_tel_meta:,}), Celular ({insc_cel_meta:,}). Total: {exactos_meta:,}.\n"
    f"Any-Touch: Para ver cuantos inscriptos tuvieron al menos un contacto con Meta (aunque tambien consultaron por otros canales), referirse al Informe Analitico (04_reporte_final).\n"
)
if segmento == 'Grado_Pregrado':
    nota_met += "Ventana de conversion: Leads desde 01/09/2025 (campana ingreso 2026).\n"
else:
    nota_met += "Ventana de conversion: Anio calendario 2026.\n"
pdf.multi_cell(0, 6, nota_met)

pdf.output(os.path.join(output_dir, 'Informe_Facebook_Deep_Dive.pdf'))

print("-> Deep Dive de Facebook generado en outputs/Facebook_Deep_Dive")

# Memoria Técnica
memoria_fb = """# Memoria Técnica: Cálculos de Facebook/Meta Ads Deep Dive

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión:** Se capturan a todos los Leads en los cuales el originador de fuente (`FuenteLead_Num`) coincida de manera estricta con el Id `18` (Facebook Lead Ads en el sistema local). Simultáneamente, se engloban aquellos prospectos con identificadores UTM pre-establecidos (`fb`, `facebook`, `ig`, `instagram`, `meta`) alojados dentro del rastreador en crudo `UtmSource`.
- **Match Exacto (Conversión):** En sincronía con el pipeline general, una conversión a 'Inscripto' solo es atribuida de existir el identificador de cruce numérico exacto proveniente del módulo madre (`02_cruce`).
- **Filtrado Dimensional Visual:** Por requerimientos funcionales y estéticos comerciales, el cruce y la presentación de volumen visual de Campañas suprime micro-campañas basura (consideradas aquellas de recolección de leads inferiores a 5). No obstante, para el cálculo base principal el acumulado toma el 100% de los datos orgánicos.
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria_fb)

