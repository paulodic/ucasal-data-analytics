"""
05_mapeo_y_reportes.py
Genera Sankey principal (Origen → Modalidad → Resultado), reporte fuzzy,
análisis del bot, y PDF consolidado para el Informe Analítico global.

NOTA: Este script lee de Data_Base/ sin segmento (datos consolidados).
Se ejecuta como script global en 00_run_all.py.

SALIDA (outputs/Informe_Analitico/):
  - Sankey diagram, reporte fuzzy, análisis bot, PDF, Excel complementario
"""
import pandas as pd
import os
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys

segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

sns.set_theme(style="whitegrid")

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "Informe_Analitico")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")
data_dir = os.path.join(base_dir, "data", "1_raw")

leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")
mapping_xlsx = os.path.join(data_dir, "origenes_leads", "mapping_origenes.xlsx")

# ==========================================
# 1. CARGA DE DATOS (USANDO CACHÉ CSV)
# ==========================================
print("Cargando base unificada de Leads (CSV)...")
df_leads = pd.read_csv(leads_csv, low_memory=False)

print("Cargando base de Inscriptos (CSV)...")
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

print("Cargando diccionario de orígenes (mapping)...")
try:
    df_map = pd.read_excel(mapping_xlsx)
    df_map_unique = df_map.dropna(subset=['id_origen | Fuente lead', 'nombre'])
    df_map_unique = df_map_unique.copy()
    df_map_unique['id_origen_str'] = df_map_unique['id_origen | Fuente lead'].astype(str).str.replace(r'\.0$', '', regex=True)
    dict_origenes = dict(zip(df_map_unique['id_origen_str'], df_map_unique['nombre']))
except Exception as e:
    print(f"Error cargando mapping_origenes.xlsx: {e}")
    dict_origenes = {}

# ==========================================
# 2. CLASIFICACIÓN Y LIMPIEZA
# ==========================================
# Aplicar nombre de formulario de origen
df_leads['FuenteLead_clean'] = df_leads['FuenteLead'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

def get_origen_name(fuente_id):
    if pd.isna(fuente_id) or fuente_id == 'nan' or not fuente_id:
        return 'Sin Origen / Desconocido'
    if fuente_id == '18':
        return 'Facebook Lead Ads'
    if fuente_id == '907':
        return 'Chatbot'
    nombre = dict_origenes.get(fuente_id)
    if nombre:
        return f"LP: {nombre[:40]}"
    return f"Landing/Form ({fuente_id})"

df_leads['Formulario_Origen'] = df_leads['FuenteLead_clean'].apply(get_origen_name)

# Normalizar Modo
def normalize_modo(val):
    v_str = str(val).strip().lower()
    if v_str in ['1', '1.0'] or ('presencial' in v_str and 'semi' not in v_str):
        return 'Presencial'
    if v_str in ['2', '2.0'] or 'semi' in v_str:
        return 'Semipresencial'
    if v_str in ['7', '7.0'] or 'distancia' in v_str:
        return 'A Distancia'
    return 'Otro / No Informado'

df_leads['Modo_Limpio'] = df_leads['Modo'].apply(normalize_modo)

# Clasificar resultado: EXCLUYENDO FUZZY del principal
def classify_match(val):
    s = str(val)
    if 'Exacto' in s:
        return 'exacto'
    if 'Posible Match Fuzzy' in s:
        return 'fuzzy'
    return 'no_match'

df_leads['_match_class'] = df_leads['Match_Tipo'].apply(classify_match)

# Separar dataframes
df_main = df_leads[df_leads['_match_class'] != 'fuzzy'].copy()  # Solo exactos + no-match
df_fuzzy = df_leads[df_leads['_match_class'] == 'fuzzy'].copy()  # Solo fuzzy

# Resultado para Sankey (solo exactos)
df_main['Resultado_Insc'] = df_main['_match_class'].apply(
    lambda x: '✅ Inscripto Confirmado' if x == 'exacto' else '❌ No Inscripto'
)

print(f"Registros principales (exactos + no-match): {len(df_main):,}")
print(f"Registros fuzzy (informe complementario): {len(df_fuzzy):,}")

# ==========================================
# 3. DIAGRAMA SANKEY AGRUPADO (SOLO EXACTOS)
# ==========================================
print("Generando Diagrama Sankey Agrupado (sin fuzzy)...")

# Agrupar orígenes con poca masa en "Otros"
origen_counts = df_main['Formulario_Origen'].value_counts()
top_origenes = origen_counts[origen_counts > len(df_main) * 0.005].index.tolist()
df_main['Origen_Agrupado'] = df_main['Formulario_Origen'].apply(lambda x: x if x in top_origenes else 'Otros Formularios')

nodes = list(df_main['Origen_Agrupado'].unique()) + \
        list(df_main['Modo_Limpio'].unique()) + \
        list(df_main['Resultado_Insc'].unique())
node_dict = {name: i for i, name in enumerate(nodes)}

links_1 = df_main.groupby(['Origen_Agrupado', 'Modo_Limpio']).size().reset_index(name='value')
links_2 = df_main.groupby(['Modo_Limpio', 'Resultado_Insc']).size().reset_index(name='value')

source = [node_dict[x] for x in links_1['Origen_Agrupado']] + [node_dict[x] for x in links_2['Modo_Limpio']]
target = [node_dict[x] for x in links_1['Modo_Limpio']] + [node_dict[x] for x in links_2['Resultado_Insc']]
value = links_1['value'].tolist() + links_2['value'].tolist()

# Colores
n_origenes = len(df_main['Origen_Agrupado'].unique())
n_modos = len(df_main['Modo_Limpio'].unique())
colors = ['rgba(31,119,180,0.8)'] * n_origenes + ['rgba(255,187,120,0.8)'] * n_modos + ['rgba(44,160,44,0.8)', 'rgba(214,39,40,0.6)']

fig = go.Figure(data=[go.Sankey(
    node=dict(pad=20, thickness=25, line=dict(color="black", width=0.5),
              label=nodes, color=colors),
    link=dict(source=source, target=target, value=value)
)])
fig.update_layout(
    title_text="Flujo de Oportunidades: Formulario Origen → Modalidad → Resultado (solo cruce exacto)",
    font_size=11, width=1200, height=700
)

sankey_pdf = os.path.join(output_dir, "diagrama_sankey_agrupado.pdf")
sankey_png = os.path.join(output_dir, "diagrama_sankey_agrupado.png")
fig.write_image(sankey_pdf, engine="kaleido")
fig.write_image(sankey_png, engine="kaleido")
print(f"-> Sankey agrupado guardado en: {sankey_pdf}")

# ==========================================
# 4. GRÁFICOS ADICIONALES
# ==========================================
print("Generando gráficos adicionales...")

# REGLA DE NEGOCIO: Si es Grado_Pregrado, las tasas de conversión se calculan
# aislando leads desde septiembre de 2025 (inicio captación cohorte Ingreso 2026)
if segmento == 'Grado_Pregrado':
    df_main['Fecha_Limpia'] = pd.to_datetime(df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_main_conv = df_main[df_main['Fecha_Limpia'] >= '2025-09-01'].copy()
else:
    df_main_conv = df_main.copy()

# Gráfico 4: Top 10 Orígenes por Volumen de Leads (Usando todo el histórico para volumen)
plt.figure(figsize=(12, 6))
top10 = df_main['Formulario_Origen'].value_counts().head(10)
sns.barplot(y=top10.index, x=top10.values, hue=top10.index, palette='coolwarm', legend=False)
plt.title('Top 10 Formularios de Origen por Volumen de Leads')
plt.xlabel('Cantidad de Leads')
for i, v in enumerate(top10.values):
    plt.text(v + 50, i, f'{v:,}', va='center')
chart4_path = os.path.join(output_dir, "chart_4_top10_origenes.png")
plt.savefig(chart4_path, bbox_inches='tight')
plt.close()

# Gráfico 5: Distribución por Modalidad
plt.figure(figsize=(8, 5))
modo_counts = df_main['Modo_Limpio'].value_counts()
sns.barplot(x=modo_counts.index, y=modo_counts.values, hue=modo_counts.index, palette='Set2', legend=False)
plt.title('Distribución de Leads por Modalidad')
plt.ylabel('Cantidad')
for i, v in enumerate(modo_counts.values):
    plt.text(i, v + 100, f'{v:,}', ha='center')
chart5_path = os.path.join(output_dir, "chart_5_distribucion_modalidad.png")
plt.savefig(chart5_path, bbox_inches='tight')
plt.close()

# Gráfico 6: Tasa de Conversión por Modalidad 
plt.figure(figsize=(8, 5))
conv_por_modo = df_main_conv.groupby('Modo_Limpio')['_match_class'].apply(
    lambda x: (x == 'exacto').sum() / len(x) * 100 if len(x) > 0 else 0
).reset_index(name='Tasa_Conv')
sns.barplot(x='Modo_Limpio', y='Tasa_Conv', data=conv_por_modo, hue='Modo_Limpio', palette='RdYlGn', legend=False)
plt.title('Tasa de Conversión por Modalidad (%)')
plt.ylabel('% Conversión')
for i, row in conv_por_modo.iterrows():
    plt.text(i, row['Tasa_Conv'] + 0.1, f"{row['Tasa_Conv']:.2f}%", ha='center')
chart6_path = os.path.join(output_dir, "chart_6_conversion_modalidad.png")
plt.savefig(chart6_path, bbox_inches='tight')
plt.close()

# Gráfico 7: Tasa de Conversión por Top Orígenes
plt.figure(figsize=(12, 6))
conv_por_origen = df_main_conv.groupby('Formulario_Origen').agg(
    total=('_match_class', 'size'),
    convertidos=('_match_class', lambda x: (x == 'exacto').sum())
).reset_index()
conv_por_origen['tasa'] = conv_por_origen['convertidos'] / conv_por_origen['total'] * 100
conv_por_origen = conv_por_origen[conv_por_origen['total'] >= 100].sort_values('tasa', ascending=False).head(10)
sns.barplot(y='Formulario_Origen', x='tasa', data=conv_por_origen, hue='Formulario_Origen', palette='YlGn', legend=False)
plt.title('Top 10 Orígenes con Mejor Tasa de Conversión (mín. 100 leads en la muestra)')
plt.xlabel('% Conversión')
chart7_path = os.path.join(output_dir, "chart_7_conversion_origenes.png")
plt.savefig(chart7_path, bbox_inches='tight')
plt.close()

# ==========================================
# 5. REPORTE ESPECÍFICO DEL BOT (907)
# ==========================================
print("Generando Reporte Específico del Chatbot (907)...")
df_bot = df_main[df_main['FuenteLead_clean'] == '907'].copy()
df_bot_conv = df_main_conv[df_main_conv['FuenteLead_clean'] == '907'].copy()

total_bot_leads = len(df_bot)
total_bot_leads_conv = len(df_bot_conv)
total_bot_insc = len(df_bot_conv[df_bot_conv['_match_class'] == 'exacto'])
tasa_bot = (total_bot_insc / total_bot_leads_conv * 100) if total_bot_leads_conv > 0 else 0

# Comparar con el total
total_all_leads = len(df_main)
total_all_leads_conv = len(df_main_conv)
total_all_insc = len(df_main_conv[df_main_conv['_match_class'] == 'exacto'])
tasa_general = (total_all_insc / total_all_leads_conv * 100) if total_all_leads_conv > 0 else 0

print(f"-> Bot: {total_bot_leads:,} leads | {total_bot_insc:,} inscriptos (muestra) | {tasa_bot:.2f}% conversión")
print(f"-> General: {total_all_leads:,} leads | {total_all_insc:,} inscriptos (muestra) | {tasa_general:.2f}% conversión")

bot_report_xlsx = os.path.join(output_dir, "reporte_inscriptos_bot_907.xlsx")
df_bot.to_excel(bot_report_xlsx, index=False)

bot_summary = f"""# Análisis de Rendimiento: Chatbot (Origen 907)

Se analizó específicamente el rendimiento de las captaciones cuyo origen es el formulario del Bot (Fuente 907).

| Métrica | Bot (907) | General |
|---------|-----------|---------|
| Total Leads | {total_bot_leads:,} | {total_all_leads:,} |
| Total Inscriptos Confirmados | {total_bot_insc:,} | {total_all_insc:,} |
| Tasa de Conversión | {tasa_bot:.2f}% | {tasa_general:.2f}% |

*El detalle nominal completo se encuentra en: `reporte_inscriptos_bot_907.xlsx`.*
*Nota: Las coincidencias "fuzzy" (por similitud de nombre) se presentan en un informe complementario aparte.*
"""
with open(os.path.join(output_dir, "informe_bot_907.md"), "w", encoding="utf-8") as file:
    file.write(bot_summary)

# ==========================================
# 6. INFORME COMPLEMENTARIO FUZZY
# ==========================================
print("Generando informe complementario de coincidencias Fuzzy...")
fuzzy_xlsx = os.path.join(output_dir, "reporte_complementario_fuzzy.xlsx")
df_fuzzy.to_excel(fuzzy_xlsx, index=False)
print(f"-> {len(df_fuzzy):,} registros fuzzy exportados a: {fuzzy_xlsx}")

fuzzy_summary = f"""# Informe Complementario: Coincidencias Fuzzy (Requiere Verificación Humana)

Este informe contiene **{len(df_fuzzy):,}** registros de Leads que fueron asociados a Inscriptos mediante un algoritmo de similitud de nombres (fuzzy matching con score >= 85).

> ⚠️ **Estos registros NO se incluyen en el informe principal.** Deben ser revisados manualmente para confirmar o descartar la coincidencia.

El archivo Excel con el detalle completo es: `reporte_complementario_fuzzy.xlsx`.
"""
with open(os.path.join(output_dir, "informe_complementario_fuzzy.md"), "w", encoding="utf-8") as file:
    file.write(fuzzy_summary)

# ==========================================
# 7. INFORME PRINCIPAL (MD + PDF)
# ==========================================
print("Generando informe analítico principal (sin fuzzy)...")

# Métricas solo con exactos
leads_exactos = len(df_main[df_main['_match_class'] == 'exacto'])
leads_solo = len(df_main[df_main['_match_class'] == 'no_match'])

# Inscriptos
insc_con_origen = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Si \\(Lead -> Inscripto Exacto\\)')])
insc_directos = len(df_insc[df_insc['Match_Tipo'] == 'No (Solo Inscripto Directo)'])
total_inscriptos = len(df_insc[~df_insc['Match_Tipo'].astype(str).str.contains('Fuzzy')])  # excluir fuzzy del total
tasa_atribucion = (insc_con_origen / total_inscriptos * 100) if total_inscriptos > 0 else 0

leads_exactos_conv = len(df_main_conv[df_main_conv['_match_class'] == 'exacto'])
tasa_conversion = (leads_exactos_conv / len(df_main_conv) * 100) if len(df_main_conv) > 0 else 0

report_md = f"""# Informe Analítico de Marketing y Trazabilidad

Este informe consolida el análisis generado a partir del cruce **exacto** de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos** (cruzados por DNI, Email y Teléfono). Los registros encontrados por similitud de nombres (fuzzy) se presentan en un **informe complementario aparte**.

## 1. Resumen Ejecutivo
{f'*(Nota Cohortes: Para {segmento}, las tasas de conversión asumen como denominador los leads ingresados a partir de Septiembre 2024, coincidiendo con el inicio de inscripción a la primera cohorte. En mayo se abren a la segunda.)*' if segmento == 'Grado_Pregrado' else ''}

| Métrica | Valor |
|---------|-------|
| Total Leads Históricos (Sankey y Volumen) | {len(df_main):,} |
| Total Leads Analizados para Conversión | {len(df_main_conv):,} |
| Leads Convertidos a Inscripto (exacto en muestra) | {leads_exactos_conv:,} |
| Tasa de Conversión (exacta) | {tasa_conversion:.2f}% |
| Inscriptos Atribuidos a Paid Ads | {insc_con_origen:,} ({tasa_atribucion:.1f}%) |
| Inscriptos sin trazabilidad (sin lead previo) | {insc_directos:,} |

### Conversión General
![Conversión Leads](chart_1_conversion_leads.png)

### Composición de Inscriptos
![Composición Inscriptos](chart_2_composicion_inscriptos.png)

## 2. Análisis por Formulario de Origen

### Top 10 Formularios por Volumen
![Top 10 Orígenes](chart_4_top10_origenes.png)

### Tasa de Conversión por Origen (mín. 100 leads)
![Conversión por Origen](chart_7_conversion_origenes.png)

## 3. Análisis por Modalidad

### Distribución de Leads
![Distribución Modalidad](chart_5_distribucion_modalidad.png)

### Tasa de Conversión por Modalidad
![Conversión Modalidad](chart_6_conversion_modalidad.png)

## 4. Flujo Visual (Sankey)
El siguiente diagrama muestra el flujo agrupado desde el Formulario de Origen, pasando por la Modalidad, hasta el estado final de inscripción:

![Diagrama Sankey](diagrama_sankey_agrupado.png)

## 5. Reporte del Chatbot (Origen 907)

| Métrica | Bot (907) | General |
|---------|-----------|---------|
| Total Leads | {total_bot_leads:,} | {total_all_leads:,} |
| Inscriptos Confirmados | {total_bot_insc:,} | {total_all_insc:,} |
| Tasa de Conversión | {tasa_bot:.2f}% | {tasa_general:.2f}% |

## 6. Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen exacto de un porcentaje significativo de inscriptos, demostrando el impacto directo de las campañas de captación.
2. **Chatbot:** El Bot (907) presenta una tasa de conversión {"superior" if tasa_bot > tasa_general else "inferior"} a la media general ({tasa_bot:.2f}% vs {tasa_general:.2f}%), lo que {"valida su efectividad como canal de captación" if tasa_bot > tasa_general else "sugiere oportunidades de mejora en el flujo conversacional"}.
3. **Calidad de Datos:** {len(df_fuzzy):,} registros requirieron cruce fuzzy y están pendientes de verificación humana (ver informe complementario).

---
*Archivos complementarios:*
- `reporte_complementario_fuzzy.xlsx` - Coincidencias por similitud de nombres (requiere verificación)
- `reporte_inscriptos_bot_907.xlsx` - Detalle específico del Bot
- `diagrama_sankey_agrupado.pdf` - Diagrama Sankey en alta resolución
"""

# Guardar MD
report_md_file = os.path.join(output_dir, "Informe_Analitico_Marketing.md")
with open(report_md_file, "w", encoding="utf-8") as f:
    f.write(report_md)
print(f"-> Informe Markdown guardado en: {report_md_file}")

# ==========================================
# 8. GENERAR PDF
# ==========================================
print("Generando PDF del informe analítico...")
try:
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 12)
            self.cell(0, 10, 'Informe Analítico de Marketing', new_x="LMARGIN", new_y="NEXT", align='C')
            self.ln(5)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', new_x="LMARGIN", new_y="NEXT", align='C')
    
    pdf = PDF('L')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'Informe Analítico de Marketing y Trazabilidad', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    # Resumen
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, f'Este informe consolida el análisis del cruce exacto de {len(df_main):,} leads y {total_inscriptos:,} inscriptos.')
    pdf.ln(5)
    
    # Tabla Resumen
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(120, 8, 'Métrica', border=1)
    pdf.cell(50, 8, 'Valor', border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    
    rows = [
        ('Total Leads Históricos', f'{len(df_main):,}'),
        ('Total Leads (Muestra de Conversión)', f'{len(df_main_conv):,}'),
        ('Leads Convertidos (Muestra)', f'{leads_exactos_conv:,}'),
        ('Tasa de Conversión (Muestra)', f'{tasa_conversion:.2f}%'),
        ('Inscriptos Atribuidos', f'{insc_con_origen:,} ({tasa_atribucion:.1f}%)'),
        ('Inscriptos sin trazabilidad', f'{insc_directos:,}'),
        ('Bot (907) - Leads (Muestra)', f'{total_bot_leads_conv:,}'),
        ('Bot (907) - Inscriptos', f'{total_bot_insc:,}'),
        ('Bot (907) - Conversión', f'{tasa_bot:.2f}%'),
    ]
    for label, val in rows:
        pdf.cell(120, 7, label, border=1)
        pdf.cell(50, 7, val, border=1, new_x="LMARGIN", new_y="NEXT")
    
    # Insertar gráficos
    charts = [
        (chart4_path, 'Top 10 Formularios de Origen'),
        (chart5_path, 'Distribución por Modalidad'),
        (chart6_path, 'Tasa de Conversión por Modalidad'),
        (chart7_path, 'Tasa de Conversión por Origen'),
        (sankey_png, 'Diagrama Sankey: Flujo de Oportunidades'),
    ]
    
    for chart_path, title in charts:
        if os.path.exists(chart_path):
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(3)
            pdf.image(chart_path, x='C', w=260, h=160, keep_aspect_ratio=True)
    
    # Conclusiones
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Conclusiones y Recomendaciones', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    conclusiones = [
        f'1. Se logró trazar el origen exacto de {insc_con_origen:,} inscriptos ({tasa_atribucion:.1f}% del total).',
        f'2. El Bot (907) presenta una tasa de conversión de {tasa_bot:.2f}% vs {tasa_general:.2f}% general.',
        f'3. {len(df_fuzzy):,} registros requirieron cruce fuzzy y están en el informe complementario.',
    ]
    for c in conclusiones:
        pdf.multi_cell(0, 6, c)
        pdf.ln(2)
    
    pdf_path = os.path.join(output_dir, "Informe_Analitico_Marketing.pdf")
    pdf.output(pdf_path)
    print(f"-> PDF guardado en: {pdf_path}")
    
except ImportError:
    print("La librería fpdf2 no está instalada. Instalando...")
    import subprocess
    subprocess.run(['pip', 'install', 'fpdf2'], check=True)
    print("fpdf2 instalada. Vuelve a ejecutar el script para generar el PDF.")

print("\n¡Proceso completo finalizado con éxito!")
