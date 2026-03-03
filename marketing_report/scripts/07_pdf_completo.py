import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
# ==========================================
import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

# CONFIGURACIÓN
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Informe_Analitico")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)

leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Cargando datos para resumen...")
df = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

# Clasificar
def classify(v):
    s = str(v)
    if 'Si (Lead -> Inscripto Exacto)' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

df['_mc'] = df['Match_Tipo'].apply(classify)
df_main = df[df['_mc'] != 'fuzzy'].copy()
df_fuzzy = df[df['_mc'] == 'fuzzy'].copy()

# Deduplicar por persona (Histórico de leads para no perder volumen)
df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

personas = df_main.drop_duplicates(subset='_pk')
total_personas = len(personas)

# REGLA DE NEGOCIO COHORTES (Filtro para Conversión)
if segmento == 'Grado_Pregrado':
    df_main['Fecha_Limpia'] = pd.to_datetime(df_main['Consulta: Fecha de creación'], errors='coerce')
    df_main_conv = df_main[df_main['Fecha_Limpia'] >= '2024-09-01'].copy()
    personas_conv_base = df_main_conv.drop_duplicates(subset='_pk')
else:
    personas_conv_base = personas.copy()

total_personas_conv = len(personas_conv_base)
personas_conv = len(personas_conv_base[personas_conv_base['_mc'] == 'exacto'])
tasa_dedup = (personas_conv / total_personas_conv * 100) if total_personas_conv > 0 else 0

# Totales
total_registros = len(df_main)
total_exactos = len(personas_conv_base[personas_conv_base['_mc'] == 'exacto']) # basados en la muestra
total_fuzzy = len(df_fuzzy)

# Bot
df_main['_fl'] = df_main['FuenteLead'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
df_bot = df_main[df_main['_fl'] == '907']
bot_leads = len(df_bot)

personas_conv_base['_fl'] = personas_conv_base['FuenteLead'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
df_bot_conv = personas_conv_base[personas_conv_base['_fl'] == '907']
bot_leads_conv = len(df_bot_conv)
bot_insc = len(df_bot_conv[df_bot_conv['_mc'] == 'exacto'])
bot_tasa = (bot_insc / bot_leads_conv * 100) if bot_leads_conv > 0 else 0

# Inscriptos
insc_exactos = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Exacto')])
insc_directos = len(df_insc[df_insc['Match_Tipo'] == 'No (Solo Inscripto Directo)'])

# UTM
for col in ['UtmSource', 'UtmCampaign', 'UtmMedium']:
    if col in df_main.columns:
        df_main[col] = df_main[col].astype(str).replace('nan', '').str.strip()
con_utm = len(df_main[(df_main['UtmSource'] != '') | (df_main['UtmCampaign'] != '') | (df_main['UtmMedium'] != '')])
sin_utm = total_registros - con_utm

print(f"Personas: {total_personas:,} | Conv: {personas_conv:,} ({tasa_dedup:.2f}%)")
print(f"Bot: {bot_leads:,} -> {bot_insc:,} ({bot_tasa:.2f}%)")

def get_max_date(df_i):
    meses = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio", 
             7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}
    for col in ['Insc_Fecha Pago', 'Insc_Fecha Aplicación', 'Fecha Pago', 'Fecha Aplicación']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], errors='coerce', dayfirst=True)
            if not dates.isna().all():
                d = dates.max()
                return f"{d.day} de {meses[d.month]} de {d.year}"
    d = datetime.now()
    return f"{d.day} de {meses[d.month]} de {d.year}"

max_date_str = get_max_date(df_insc)
print(f"Fecha maxima de inscriptos: {max_date_str}")

# ==========================================
# EXPORTAR TEXTOS A MARKDOWN
# ==========================================
md_path = os.path.join(output_dir, "Informe_Analitico_Marketing_Completo.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"# Informe Analitico de Marketing - Completo\n\n**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.**\n\n*(Datos actualizados al {max_date_str})*\n\n")
    f.write("## Resumen Ejecutivo\n")
    if segmento == 'Grado_Pregrado':
        f.write("*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2024, coincidiendo con la inscripcion a la primera cohorte. En mayo se abren a la segunda.)*\n\n")
    f.write(f"- Total Registros de Leads (Historico): {total_registros:,}\n")
    f.write(f"- Personas Unicas (Muestra para conversion): {total_personas_conv:,}\n")
    f.write(f"- Tasa de Conversion Global (deduplicada): {tasa_dedup:.2f}%\n")
    f.write(f"- Inscriptos Atribuidos a Paid Ads (exacto): {insc_exactos:,}\n")
    f.write(f"- Inscriptos sin trazabilidad (sin lead previo): {insc_directos:,}\n")
    f.write(f"- Bot - Leads captados (historico): {bot_leads:,}\n")
    f.write(f"- Bot - Inscriptos confirmados (muestra): {bot_insc:,}\n")
    f.write(f"- Bot - Tasa de conversion: {bot_tasa:.2f}%\n")
    f.write(f"- Leads con UTM: {con_utm:,} ({(con_utm/total_registros)*100:.1f}%)\n")
    f.write(f"- Leads sin UTM: {sin_utm:,} ({(sin_utm/total_registros)*100:.1f}%)\n")
    f.write(f"- Registros Fuzzy Complementarios: {total_fuzzy:,}\n\n")
    f.write("## Conclusiones y Recomendaciones\n")
    f.write("### 1. Atribucion de Marketing\n")
    f.write(f"Se logro trazar el origen exacto de {insc_exactos:,} inscriptos. La tasa de conversion real (deduplicada por persona) es de {tasa_dedup:.2f}%.\n\n")
    f.write("### 2. Rendimiento del Chatbot (907)\n")
    comp = "superior" if bot_tasa > tasa_dedup else "inferior"
    f.write(f"El Bot presenta una tasa de conversion de {bot_tasa:.2f}%, {comp} al promedio general de {tasa_dedup:.2f}%. Capto {bot_leads:,} leads de los cuales {bot_insc:,} se inscribieron.\n\n")
    f.write("### 3. Campanas Digitales (UTM)\n")
    f.write(f"{con_utm:,} leads ({(con_utm/total_registros)*100:.1f}%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El {(sin_utm/total_registros)*100:.1f}% restante no tiene UTM asociado.\n\n")
    f.write("### 4. Calidad de Datos\n")
    f.write(f"{total_fuzzy:,} registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.\n\n")
    f.write("### 5. Recomendaciones\n")
    f.write("- Implementar UTMs en todas las campanas para mejorar la trazabilidad.\n")
    f.write("- Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.\n")
print(f"-> Textos exportados a MD: {md_path}\n")

# ==========================================
# GENERAR PDF COMPLETO
# ==========================================
print("Generando PDF completo con todos los graficos y resumenes...")

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Informe Analitico de Marketing - UCASAL', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_text_color(0, 0, 0)
        self.ln(2)
    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, f'Pagina {self.page_no()}/{{nb}}', new_x="LMARGIN", new_y="NEXT", align='C')

pdf = PDF('L')
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)

# ============================
# PORTADA
# ============================
pdf.add_page()
pdf.set_font('Helvetica', 'B', 28)
pdf.ln(50)
pdf.cell(0, 15, f'Informe Analitico ({segmento.replace("_", " ")})', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.cell(0, 15, 'de Marketing', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(5)
pdf.set_font('Helvetica', 'B', 12)
pdf.set_text_color(255, 0, 0) # Red color for draft notice
pdf.cell(0, 10, 'Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.set_text_color(0, 0, 0)
pdf.ln(5)
pdf.ln(10)
pdf.set_font('Helvetica', '', 14)
pdf.cell(0, 10, f'Trazabilidad de Leads e Inscriptos (al {max_date_str})', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(5)
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 8, '(Solo cruces exactos - Fuzzy en informe complementario)', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(20)

# ============================
# RESUMEN EJECUTIVO
# ============================
pdf.add_page()
pdf.set_font('Helvetica', 'B', 18)
pdf.cell(0, 12, 'Resumen Ejecutivo', new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

# Tabla principal
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
pdf.cell(180, 9, '  Metrica', border=1, fill=True)
pdf.cell(80, 9, '  Valor', border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.set_font('Helvetica', '', 9)

def table_row(label, val, bold=False):
    if bold:
        pdf.set_font('Helvetica', 'B', 9)
    else:
        pdf.set_font('Helvetica', '', 9)
    pdf.cell(180, 7, f'  {label}', border=1)
    pdf.cell(80, 7, f'  {val}', border=1, new_x="LMARGIN", new_y="NEXT")

table_row('Total Registros de Leads', f'{total_registros:,}')
table_row('Personas Unicas (Muestra Evaluada)', f'{total_personas_conv:,}')
table_row('Leads Convertidos a Inscripto (exacto en muestra)', f'{total_exactos:,}')
table_row('Personas Convertidas (deduplicado)', f'{personas_conv:,}')
table_row('TASA DE CONVERSION REAL (deduplicada)', f'{tasa_dedup:.2f}%', bold=True)

pdf.ln(3)
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(46, 204, 113)
pdf.set_text_color(255, 255, 255)
pdf.cell(180, 9, '  Inscriptos', border=1, fill=True)
pdf.cell(80, 9, '  Valor', border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

table_row('Inscriptos Atribuidos a Paid Ads (exacto)', f'{insc_exactos:,}')
table_row('Inscriptos sin trazabilidad (sin lead previo)', f'{insc_directos:,}')
table_row('Coincidencias Fuzzy (informe complementario)', f'{total_fuzzy:,}')

pdf.ln(3)
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(155, 89, 182)
pdf.set_text_color(255, 255, 255)
pdf.cell(180, 9, '  Chatbot (Origen 907)', border=1, fill=True)
pdf.cell(80, 9, '  Valor', border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

table_row('Bot - Leads captados', f'{bot_leads:,}')
table_row('Bot - Inscriptos confirmados', f'{bot_insc:,}')
table_row('Bot - Tasa de conversion', f'{bot_tasa:.2f}%', bold=True)

pdf.ln(3)
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(230, 126, 34)
pdf.set_text_color(255, 255, 255)
pdf.cell(180, 9, '  Campanas (UTM)', border=1, fill=True)
pdf.cell(80, 9, '  Valor', border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

table_row('Leads con UTM', f'{con_utm:,} ({con_utm/total_registros*100:.1f}%)')
table_row('Leads sin UTM', f'{sin_utm:,} ({sin_utm/total_registros*100:.1f}%)')

# ============================
# TODOS LOS GRAFICOS
# ============================
sections = [
    # (titulo de seccion, lista de (archivo, titulo grafico))
    ('Analisis de Conversion General', [
        ('chart_1_conversion_leads.png', 'Conversion General de Leads'),
        ('chart_2_composicion_inscriptos.png', 'Composicion de Inscriptos (Atribuidos vs Sin trazabilidad)'),
        ('chart_5_leads_pagos_vs_otros.png', 'Distribucion de Leads Totales: Pagados vs Otros'),
        ('chart_7_inscriptos_pagos_vs_otros.png', 'Distribucion de Inscriptos (Atribuidos): Pagados vs Otros'),
        ('chart_8_tiempos_resolucion.png', 'Tiempos de Resolucion (Pagados vs Otros)'),
    ]),
    ('Analisis por Formulario de Origen', [
        ('chart_4_top10_origenes.png', 'Top 10 Formularios de Origen por Volumen'),
        ('chart_7_conversion_origenes.png', 'Tasa de Conversion por Origen (min. 100 leads)'),
    ]),
    ('Analisis por Modalidad', [
        ('chart_5_distribucion_modalidad.png', 'Distribucion de Leads por Modalidad'),
        ('chart_6_conversion_modalidad.png', 'Tasa de Conversion por Modalidad'),
    ]),
    ('Journey del Estudiante', [
        ('chart_9_consultas_por_dia.png', 'Volumen de Consultas (Leads) a traves del Tiempo (Diario)'),
        ('chart_9b_consultas_por_mes.png', 'Volumen de Consultas (Leads) Agrupadas por Mes'),
        ('chart_3_top_fuentes.png', 'Top 10 Fuentes Iniciales de Inscriptos (1er Touch)'),
        ('chart_6_inscripciones_por_dia.png', 'Curva de Inscripciones Confirmadas por Dia'),
    ]),
    ('Diagramas Sankey - Flujos Visuales', [
        ('diagrama_sankey_agrupado.png', 'Flujo General: Origen -> Modalidad -> Resultado'),
        ('sankey_A_inscriptos_origen_modo.png', 'Solo Inscriptos Exactos: Origen -> Modalidad'),
        ('sankey_B_consultas_inscripcion.png', 'Cantidad de Consultas -> Inscripcion'),
        ('sankey_C_bot_cross_origin.png', 'Bot: Otros Origenes Consultados'),
        ('sankey_D_flujo_oportunidades.png', 'Flujo Oportunidades: Modalidades de los Inscriptos'),
        ('sankey_E_flujo_bot.png', 'Modalidades de Inscriptos desde el Bot'),
    ]),
    ('Analisis de UTM (Campanas Digitales)', [
        ('chart_utm_source.png', 'Top 10 UTM Source'),
        ('chart_utm_campaign.png', 'Top 15 UTM Campaign'),
        ('chart_utm_medium.png', 'Top 10 UTM Medium'),
        ('chart_utm_conversion.png', 'Conversion por UTM Source (deduplicado)'),
    ]),
]

for section_title, charts in sections:
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_fill_color(52, 73, 94)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, f'  {section_title}', new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    for fname, chart_title in charts:
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, chart_title, new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(3)
            
            pdf.image(fpath, x='C', w=260, h=160, keep_aspect_ratio=True)
            pdf.ln(8)

# ============================
# CONCLUSIONES
# ============================
pdf.add_page()
pdf.set_font('Helvetica', 'B', 16)
pdf.set_fill_color(52, 73, 94)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 12, '  Conclusiones y Recomendaciones', new_x="LMARGIN", new_y="NEXT", fill=True)
pdf.set_text_color(0, 0, 0)
pdf.ln(8)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, '1. Atribucion de Marketing', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f'Se logro trazar el origen exacto de {insc_exactos:,} inscriptos. La tasa de conversion real (deduplicada por persona) es de {tasa_dedup:.2f}%.')
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, '2. Rendimiento del Chatbot (907)', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 10)
comp = "superior" if bot_tasa > tasa_dedup else "inferior"
pdf.multi_cell(0, 6, f'El Bot presenta una tasa de conversion de {bot_tasa:.2f}%, {comp} al promedio general de {tasa_dedup:.2f}%. Capto {bot_leads:,} leads de los cuales {bot_insc:,} se inscribieron.')
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, '3. Campanas Digitales (UTM)', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f'{con_utm:,} leads ({con_utm/total_registros*100:.1f}%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El {sin_utm/total_registros*100:.1f}% restante no tiene UTM asociado.')
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, '4. Calidad de Datos', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f'{total_fuzzy:,} registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.')
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, '5. Recomendaciones', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 10)
pdf.set_x(10)
pdf.set_x(10)
pdf.multi_cell(180, 6, '* Implementar UTMs en todas las campanas para mejorar la trazabilidad.')
pdf.set_x(10)
pdf.multi_cell(180, 6, '* Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.')
pdf.ln(6)

# Pie de informe
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(128, 128, 128)
pdf.multi_cell(0, 5, 'Nota: Los archivos detallados en Excel (.xlsx y .csv) se encuentran en la carpeta outputs/ del proyecto. El informe complementario de coincidencias fuzzy requiere verificacion humana antes de ser incorporado.')

# Guardar
pdf_path = os.path.join(output_dir, "Informe_Analitico_Marketing_Completo.pdf")
pdf.output(pdf_path)
print(f"\n-> PDF COMPLETO guardado en: {pdf_path}")
print(f"   Paginas: {pdf.page_no()}")
print("   Incluye: Portada + Resumen Ejecutivo + 16 graficos + Conclusiones")
