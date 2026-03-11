"""
14_bot_deep_dive.py
Informe exclusivo para leads originados por Bot/Chatbot.
Genera reportes (MD, Excel, PDF) en outputs/Bot_Deep_Dive/
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from fpdf import FPDF
from datetime import datetime

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Bot_Deep_Dive")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

meses_es = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio",
            7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}

def get_max_date():
    """Obtiene la fecha máxima de PAGO de inscriptos para el encabezado del informe.
    
    IMPORTANTE: Solo usa columnas 'Fecha Pago' / 'Insc_Fecha Pago'.
    NUNCA usa 'Fecha Aplicación' porque contiene fechas FUTURAS (inicio de cursado).
    Además filtra <= hoy para evitar cualquier dato corrupto.
    
    Returns:
        str: Fecha formateada en español, ej: '17 de febrero de 2026'
    """
    try:
        # Leer solo headers para detectar columnas disponibles (rápido)
        cols_i = pd.read_csv(inscriptos_csv, nrows=1).columns.tolist()
        # Filtrar SOLO columnas de pago (contienen 'fecha' Y 'pago')
        pago_cols = [c for c in cols_i if 'fecha' in c.lower() and 'pago' in c.lower()]
        if pago_cols:
            # Cargar solo las columnas de fecha de pago (optimización de memoria)
            df_i = pd.read_csv(inscriptos_csv, usecols=pago_cols, low_memory=False)
            max_d = pd.NaT
            hoy = pd.Timestamp.now()
            for col in pago_cols:
                parsed = pd.to_datetime(df_i[col], format='mixed', dayfirst=True, errors='coerce')
                # Filtrar fechas futuras por seguridad
                parsed = parsed[parsed <= hoy]
                col_max = parsed.max()
                if pd.notna(col_max) and (pd.isna(max_d) or col_max > max_d):
                    max_d = col_max
            if pd.notna(max_d):
                return f"{max_d.day} de {meses_es[max_d.month]} de {max_d.year}"
    except Exception:
        pass
    # Fallback: fecha actual si no se pudo leer el CSV
    d = datetime.now()
    return f"{d.day} de {meses_es[d.month]} de {d.year}"

print("Obteniendo fecha de corte...")
max_date_str = get_max_date()
print(f"Fecha máxima: {max_date_str}")

# ======================================================
# CARGA DE DATOS (optimizada con usecols)
# ======================================================
# El CSV pesa cientos de MB. Solo cargamos las columnas necesarias para este análisis.
# Primero leemos los headers (nrows=1) para verificar qué columnas existen.
print("Cargando datos de leads...")
try:
    usecols = ['Id. candidato/contacto', 'Correo', 'Match_Tipo', 'ColaNombre', 'PrimeraCola',
               'FuenteLead', 'UtmSource', 'UtmCampaign', 'Carrera', 'Sede Nombre',
               'Consulta: Fecha de creación', 'Estado']
    cols_avail = pd.read_csv(leads_csv, nrows=1).columns.tolist()
    usecols = [c for c in usecols if c in cols_avail]  # Solo pedir las que existen
    df = pd.read_csv(leads_csv, usecols=usecols, low_memory=False)
except Exception:
    # Fallback: cargar todo (lento, puede agotar RAM)
    df = pd.read_csv(leads_csv, low_memory=False)

# ======================================================
# FILTRO DE CATEGORÍAS (BOT VS META VS GOOGLE VS OTROS)
# ======================================================
df['FuenteLead_Num'] = pd.to_numeric(df['FuenteLead'], errors='coerce')
df['UtmSource_Clean'] = df['UtmSource'].astype(str).str.lower().str.strip()

# Máscaras Históricas (Volumen)
bot_mask = df['FuenteLead_Num'] == 907

meta_keywords = ['fb', 'facebook', 'ig', 'instagram', 'meta']
mask_meta = df['UtmSource_Clean'].str.contains('|'.join(meta_keywords), na=False) | (df['FuenteLead_Num'] == 18)

google_keywords = ['google', 'gads']
mask_google = df['UtmSource_Clean'].str.contains('|'.join(google_keywords), na=False)

# Evitar superposiciones (prevalecen las definiciones nativas)
mask_meta = mask_meta & ~bot_mask
mask_google = mask_google & ~bot_mask & ~mask_meta

mask_otros = ~(bot_mask | mask_meta | mask_google)

df_bot = df[bot_mask].copy()
df_meta = df[mask_meta].copy()
df_google = df[mask_google].copy()
df_otros = df[mask_otros].copy()
df_nobot = df[~bot_mask].copy()

total_leads = len(df)
total_bot = len(df_bot)
total_meta = len(df_meta)
total_google = len(df_google)
total_otros = len(df_otros)
total_nobot = len(df_nobot)

pct_bot = (total_bot / total_leads * 100) if total_leads > 0 else 0

print(f"Leads -> Bot: {total_bot:,} | Meta: {total_meta:,} | Google: {total_google:,} | Otros: {total_otros:,}")

# REGLA DE NEGOCIO COHORTES (Muestra para Conversión)
if segmento == 'Grado_Pregrado':
    df['Fecha_Limpia'] = pd.to_datetime(df['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_conv = df[df['Fecha_Limpia'] >= '2025-09-01'].copy()
else:
    df_conv = df.copy()

bot_mask_conv = df_conv['FuenteLead_Num'] == 907
mask_meta_conv = df_conv['UtmSource_Clean'].str.contains('|'.join(meta_keywords), na=False) | (df_conv['FuenteLead_Num'] == 18)
mask_google_conv = df_conv['UtmSource_Clean'].str.contains('|'.join(google_keywords), na=False)

mask_meta_conv = mask_meta_conv & ~bot_mask_conv
mask_google_conv = mask_google_conv & ~bot_mask_conv & ~mask_meta_conv
mask_otros_conv = ~(bot_mask_conv | mask_meta_conv | mask_google_conv)

df_bot_conv = df_conv[bot_mask_conv].copy()
df_meta_conv = df_conv[mask_meta_conv].copy()
df_google_conv = df_conv[mask_google_conv].copy()
df_otros_conv = df_conv[mask_otros_conv].copy()
df_nobot_conv = df_conv[~bot_mask_conv].copy()

total_bot_conv = len(df_bot_conv)
total_meta_conv = len(df_meta_conv)
total_google_conv = len(df_google_conv)
total_otros_conv = len(df_otros_conv)
total_nobot_conv = len(df_nobot_conv)

# Clasificar match
df_conv['Es_Exacto'] = df_conv['Match_Tipo'].astype(str).str.contains('Exacto', case=False, na=False).astype(int)

df_bot_conv['Es_Exacto'] = df_conv['Es_Exacto'][bot_mask_conv].copy()
df_meta_conv['Es_Exacto'] = df_conv['Es_Exacto'][mask_meta_conv].copy()
df_google_conv['Es_Exacto'] = df_conv['Es_Exacto'][mask_google_conv].copy()
df_otros_conv['Es_Exacto'] = df_conv['Es_Exacto'][mask_otros_conv].copy()
df_nobot_conv['Es_Exacto'] = df_conv['Es_Exacto'][~bot_mask_conv].copy()

tasa_bot = (df_bot_conv['Es_Exacto'].sum() / total_bot_conv * 100) if total_bot_conv > 0 else 0
tasa_meta = (df_meta_conv['Es_Exacto'].sum() / total_meta_conv * 100) if total_meta_conv > 0 else 0
tasa_google = (df_google_conv['Es_Exacto'].sum() / total_google_conv * 100) if total_google_conv > 0 else 0
tasa_otros = (df_otros_conv['Es_Exacto'].sum() / total_otros_conv * 100) if total_otros_conv > 0 else 0
tasa_nobot = (df_nobot_conv['Es_Exacto'].sum() / total_nobot_conv * 100) if total_nobot_conv > 0 else 0

# ============ MARKDOWN ============
md = f"# Análisis de Leads Originados por Bot/Chatbot\n\n"
md += f"**Datos actualizados al {max_date_str}**\n\n"
if segmento == 'Grado_Pregrado':
    md += "*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2024, coincidiendo con la inscripcion a la primera cohorte. En mayo se abren a la segunda.)*\n\n"

# Resumen
total_bot_insc = df_bot_conv['Es_Exacto'].sum()
total_nobot_insc = df_nobot_conv['Es_Exacto'].sum()
total_insc = df_conv['Es_Exacto'].sum()

md += "## 1. Volumen y Proporción\n\n"
md += f"| Métrica | Bot/Chatbot | Meta Ads | Google Ads | Otros Canales | Total |\n"
md += f"|---------|------------|----------|------------|---------------|-------|\n"
md += f"| Leads (Histórico) | {total_bot:,} | {total_meta:,} | {total_google:,} | {total_otros:,} | {total_leads:,} |\n"
md += f"| Leads (Muestra Conv.) | {total_bot_conv:,} | {total_meta_conv:,} | {total_google_conv:,} | {total_otros_conv:,} | {len(df_conv):,} |\n"
md += f"| Inscriptos Confirmados | {total_bot_insc:,} | {df_meta_conv['Es_Exacto'].sum():,} | {df_google_conv['Es_Exacto'].sum():,} | {df_otros_conv['Es_Exacto'].sum():,} | {total_insc:,} |\n"
md += f"| Conversión (Muestra) | {tasa_bot:.2f}% | {tasa_meta:.2f}% | {tasa_google:.2f}% | {tasa_otros:.2f}% | {(total_insc/len(df_conv)*100) if len(df_conv)>0 else 0:.2f}% |\n\n"

# Pie chart
plt.figure(figsize=(8, 8))
colors = ['#9b59b6', '#3b5998', '#ea4335', '#95a5a6']
labels_p = [f'Bot\n({total_bot:,})', f'Meta Ads\n({total_meta:,})', f'Google Ads\n({total_google:,})', f'Otros\n({total_otros:,})']
plt.pie([total_bot, total_meta, total_google, total_otros], labels=labels_p, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 10})
plt.title('Proporción de Leads: Naturaleza del Contacto', fontsize=14)
plt.savefig(os.path.join(output_dir, 'pie_bot_leads.png'), bbox_inches='tight')
plt.close()

# Conversión
md += "## 2. Tasa de Conversión (Inscripción)\n\n"
plt.figure(figsize=(8, 5))
bars = plt.bar(['Bot/Chatbot', 'Meta Ads', 'Google Ads'], [tasa_bot, tasa_meta, tasa_google], color=['#9b59b6', '#3b5998', '#ea4335'])
for bar, val in zip(bars, [tasa_bot, tasa_meta, tasa_google]):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{val:.2f}%', ha='center', fontsize=12)
plt.ylabel('Tasa de Inscripción (%)')
plt.title('Tasa de Conversión Real (Inscriptos / Consultas de la Fuente)')
plt.grid(axis='y', alpha=0.3)
plt.savefig(os.path.join(output_dir, 'conversion_bot.png'), bbox_inches='tight')
plt.close()

# Desglose de Metodología de Match
matched_bot = df_bot_conv[df_bot_conv['Es_Exacto'] == 1]
md += "## 3. Metodología de Atribución (Tipo de Match)\n\n"
md += "Desglose algorítmico de cómo se vincularon los leads del bot con inscripciones concretadas:\n\n"

if not matched_bot.empty:
    match_breakdown = matched_bot['Match_Tipo'].value_counts().reset_index()
    match_breakdown.columns = ['Metodología de Cruce (Lead -> Inscripto)', 'Inscriptos Confirmados']
    match_breakdown['%'] = (match_breakdown['Inscriptos Confirmados'] / match_breakdown['Inscriptos Confirmados'].sum() * 100).round(1)
    md += match_breakdown.to_markdown(index=False) + "\n\n"
else:
    md += "No hay inscriptos confirmados para generar desglose.\n\n"

# Top Carreras Bot (Por Inscriptos)
if 'Carrera' in df_bot_conv.columns:
    md += "## 4. Top 10 Carreras Inscriptas vía Bot\n\n"
    carreras_insc = df_bot_conv.groupby('Carrera')['Es_Exacto'].sum().reset_index()
    carreras_insc = carreras_insc.sort_values(by='Es_Exacto', ascending=False).head(10)
    carreras_insc.columns = ['Carrera', 'Inscriptos (Muestra)']
    
    carrera_match = []
    for _, row in carreras_insc.iterrows():
        c = row['Carrera']
        leads_c = len(df_bot_conv[df_bot_conv['Carrera'] == c])
        insc_c = row['Inscriptos (Muestra)']
        tasa = round(insc_c / leads_c * 100, 2) if leads_c > 0 else 0
        carrera_match.append({'Carrera': c, 'Inscriptos (Muestra)': insc_c, 'Consultas (Muestra)': leads_c, 'Tasa_%': tasa})
        
    df_carreras = pd.DataFrame(carrera_match)
    md += df_carreras.to_markdown(index=False) + "\n\n"

    plt.figure(figsize=(10, 6))
    plt.barh(df_carreras['Carrera'][::-1], df_carreras['Inscriptos (Muestra)'][::-1], color='#2ecc71')
    plt.xlabel('Cantidad de Inscriptos (Muestra)')
    plt.title('Top 10 Carreras Inscriptas vía Bot')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_carreras_bot.png'), bbox_inches='tight')
    plt.close()

# Sedes Bot
if 'Sede Nombre' in df_bot.columns:
    md += "## 4. Distribución por Sede\n\n"
    sedes = df_bot['Sede Nombre'].value_counts().head(10).reset_index()
    sedes.columns = ['Sede', 'Leads']
    md += sedes.to_markdown(index=False) + "\n\n"

# ColaNombre / canal de origen
if 'ColaNombre' in df_bot.columns:
    md += "## 5. Canales de Origen (ColaNombre)\n\n"
    colas = df_bot['ColaNombre'].value_counts().head(10).reset_index()
    colas.columns = ['Cola', 'Leads']
    md += colas.to_markdown(index=False) + "\n\n"

# Estado de leads
if 'Estado' in df_bot.columns:
    md += "## 6. Estado de los Leads de Bot\n\n"
    estados = df_bot['Estado'].value_counts().reset_index()
    estados.columns = ['Estado', 'Cantidad']
    estados['%'] = (estados['Cantidad'] / estados['Cantidad'].sum() * 100).round(1)
    md += estados.to_markdown(index=False) + "\n\n"

# ============ GUARDAR ============
print("Guardando archivos...")
with open(os.path.join(output_dir, 'Bot_Deep_Dive.md'), 'w', encoding='utf-8') as f:
    f.write(md)

# Exportar CSV de bot con todos los datos
print("Exportando CSV completo de Bot...")
try:
    df_full = pd.read_csv(leads_csv, low_memory=False)
    df_full['FuenteLead_Num'] = pd.to_numeric(df_full['FuenteLead'], errors='coerce')
    df_full_bot_export = df_full[df_full['FuenteLead_Num'] == 907].copy()
    
    if 'FuenteLead_Num' in df_full_bot_export.columns:
        df_full_bot_export = df_full_bot_export.drop(columns=['FuenteLead_Num'])
        
    csv_bot_path = os.path.join(output_dir, 'Bot_Data_Completa.csv')
    df_full_bot_export.to_csv(csv_bot_path, index=False, encoding='utf-8-sig')
    print("CSV Exportado con éxito.")
except Exception as e:
    print(f"Error al generar CSV completo del bot: {e}")

with pd.ExcelWriter(os.path.join(output_dir, 'datos_bot_deep_dive.xlsx')) as writer:
    if 'df_carreras' in dir():
        df_carreras.to_excel(writer, sheet_name='Top_Carreras', index=False)
    if 'sedes' in dir():
        sedes.to_excel(writer, sheet_name='Sedes', index=False)
    if 'estados' in dir():
        estados.to_excel(writer, sheet_name='Estados', index=False)

# ======================================================
# GENERACIÓN DE PDF (formato horizontal / landscape)
# ======================================================
# Se usa Helvetica (no Arial) para evitar DeprecationWarning de fpdf2.
# 'L' = Landscape (horizontal) para mejor visualización de gráficos.
class PDFBot(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "Análisis de Leads: Bot/Chatbot", ln=True, align="C")
        self.set_font("Helvetica", 'I', 10)
        self.cell(0, 6, f"Datos actualizados al {max_date_str}", ln=True, align="C")
        if segmento == 'Grado_Pregrado':
            self.set_font("Helvetica", 'I', 8)
            self.cell(0, 6, "Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads desde Septiembre 2024.", ln=True, align="C")
        self.ln(8)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

pdf = PDFBot('L')  # 'L' = Landscape
pdf.add_page()

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "1. Proporción de Leads y Tasa de Conversión Comparativa", ln=True)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, f"Consultas Originadas (Histórico) -> Bot: {total_bot:,} | Meta: {total_meta:,} | Google: {total_google:,} | Otros: {total_otros:,}\n"
                     f"Consultas (Muestra) -> Bot: {total_bot_conv:,} | Meta: {total_meta_conv:,} | Google: {total_google_conv:,} | Otros: {total_otros_conv:,}\n"
                     f"Inscriptos Ratificados -> Bot: {df_bot_conv['Es_Exacto'].sum():,} | Meta: {df_meta_conv['Es_Exacto'].sum():,} | Google: {df_google_conv['Es_Exacto'].sum():,} | Otros: {df_otros_conv['Es_Exacto'].sum():,}\n"
                     f"Tasa Modulada de Inscripción -> Bot: {tasa_bot:.2f}% | Meta: {tasa_meta:.2f}% | Google: {tasa_google:.2f}% | Otros: {tasa_otros:.2f}%")
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'pie_bot_leads.png'), w=130)
except Exception: pass

pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "2. Tasa de Conversión", ln=True)
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'conversion_bot.png'), w=200)
except Exception: pass

# Breakdown Match
if not matched_bot.empty:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3. Metodología de Atribución (Match)", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)
    for _, row in match_breakdown.iterrows():
        pdf.cell(0, 6, f"- {row['Metodología de Cruce (Lead -> Inscripto)']}: {row['Inscriptos Confirmados']} inscriptos ({row['%']}%)", ln=True)

if os.path.exists(os.path.join(output_dir, 'top_carreras_bot.png')):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "4. Top Carreras Inscriptas via Bot", ln=True)
    pdf.ln(5)
    try:
        pdf.image(os.path.join(output_dir, 'top_carreras_bot.png'), w=230)
    except Exception: pass

pdf.output(os.path.join(output_dir, 'Bot_Deep_Dive_Reporte.pdf'))

print("Proceso Finalizado. Archivos guardados en outputs/Bot_Deep_Dive/")

# Memoria Técnica
memoria_bot = """# Memoria Técnica: Cálculos de Bot/Chatbot

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión:** A nivel de base de datos (`reporte_marketing_leads_completos`), el origen Bot es aislado estrictamente rastreando la identificación codificada universal `FuenteLead_Num` que sea matemáticamente igual a `907`.
- **Match Exacto (Conversión):** Durante el cruce de Leads versus Inscriptos (ventas concretadas formales), solo se contabiliza un retorno sobre la inversión efectivo si el identificador secundario de `Match_Tipo` dictamina `"Exacto"`.
- **Proporción y Tasa de Conversión:** La proporción global se calcula versus todo el tráfico histórico registrado, mientras que la Tasa de Conversión aísla la masa de originados por IA (`907`) y la divide por aquellos Leads que lograron inscribir exitosamente.
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria_bot)

