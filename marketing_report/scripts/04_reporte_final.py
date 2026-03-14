import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from causal_utils import compute_anytouch_causal, render_causal_md, make_pk
# ==========================================
import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Informe_Analitico")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)

leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")
journey_file = os.path.join(base_dir, "outputs", segmento, "Otros_Reportes", "reporte_journey_tiempos.xlsx")
# Fallback: si no está en Otros_Reportes, buscar en Data_Base
if not os.path.exists(journey_file):
    journey_file = os.path.join(base_output_dir, "reporte_journey_tiempos.xlsx")
report_md_file = os.path.join(output_dir, "Informe_Analitico_Marketing.md")

print("Generando informe analítico...")

# Leer datos
df_leads = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)
if os.path.exists(journey_file):
    print(f"Leyendo journey desde: {journey_file}")
    try:
        # Cargar solo columnas necesarias para optimizar memoria y tiempo
        df_journey = pd.read_excel(journey_file, usecols=['Total_Consultas', 'Dias_hasta_Inscripcion', 'Inscripto', 'Touch_1'])
    except Exception as e:
        print(f"Error optimizado ({e}). Intentando cargar todo...")
        df_journey = pd.read_excel(journey_file)
else:
    print("No se encontró archivo de journey.")
    df_journey = pd.DataFrame()

def get_max_date(df_i):
    """Retorna (Timestamp, string_formateado) de la última fecha de pago de inscriptos."""
    meses = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio",
             7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}
    # SOLO usar Fecha Pago — NUNCA Fecha Aplicación (puede ser fecha futura de cursado)
    for col in ['Insc_Fecha Pago', 'Fecha Pago']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], format='mixed', errors='coerce')
            valid = dates[dates <= pd.Timestamp.now()]
            if not valid.isna().all():
                d = valid.max()
                return (d, f"{d.day} de {meses[d.month]} de {d.year}")
    d = pd.Timestamp.now()
    return (d, f"{d.day} de {meses[d.month]} de {d.year}")

max_insc_ts, max_date_str = get_max_date(df_insc)

# Clave de persona para deduplicar conteos de inscriptos (DNI > Email > Tel > Cel)
df_leads['_pk'] = make_pk(df_leads)

# ==========================================
# CÁLCULO DE MÉTRICAS Y GRÁFICOS
# ==========================================
# Configurar estilo visual de Seaborn
sns.set_theme(style="whitegrid")

# =========================================================
# ANÁLISIS HERMÉTICO DE TASAS DE CONVERSIÓN (EXACTOS)
# =========================================================
# Las tasas de conversión se calculan estrictamente aislando 
# los registros "Fuzzy" para evitar sesgos positivos irreales.

# 1. Tasa General de Leads
# Calculada sobre TODO el universo de leads, contando solo los cruces seguros.
# REGLA DE NEGOCIO: Si el segmento es Grado_Pregrado, la tasa de conversión
# se calcula sobre los leads generados desde el 1 de septiembre de 2025 (inicio cohorte 2026).
# Denominador = leads dentro de [inicio_cohorte, max_fecha_inscripcion]
# Los leads posteriores a la última inscripción no tuvieron tiempo de convertirse.
df_leads['Fecha_Limpia_Consulta'] = pd.to_datetime(
    df_leads['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
if segmento == 'Grado_Pregrado':
    df_leads_conv = df_leads[
        (df_leads['Fecha_Limpia_Consulta'] >= '2025-09-01') &
        (df_leads['Fecha_Limpia_Consulta'] <= max_insc_ts)
    ].copy()
else:
    df_leads_conv = df_leads[df_leads['Fecha_Limpia_Consulta'] <= max_insc_ts].copy()

total_leads = len(df_leads)           # consultas únicas (por ID Consulta)
total_leads_conv = len(df_leads_conv)  # consultas en ventana de conversión
total_personas = df_leads['_pk'].nunique()          # personas únicas (todas)
total_personas_conv = df_leads_conv['_pk'].nunique()  # personas en ventana

# Deduplicar por persona para contar inscriptos (no filas de leads)
# Priorizar Exacto sobre otros match types al deduplicar
_prio_map = {'Exacto': 0, 'Fuzzy': 1, 'Sin_Match': 2}
df_leads_conv['_mc_label'] = df_leads_conv['Match_Tipo'].astype(str).apply(
    lambda v: 'Exacto' if 'Exacto' in v else ('Fuzzy' if 'Fuzzy' in v else 'Sin_Match'))
df_leads_conv['_mc_prio'] = df_leads_conv['_mc_label'].map(_prio_map)
df_leads_conv_dedup = df_leads_conv.sort_values('_mc_prio').drop_duplicates(subset='_pk', keep='first')

leads_convertidos_exact = len(df_leads_conv_dedup[df_leads_conv_dedup['_mc_label'] == 'Exacto'])
_fuzzy_prio = df_leads['Match_Tipo'].astype(str).apply(lambda v: 0 if 'Fuzzy' in v else 1)
leads_convertidos_fuzzy = len(df_leads.assign(_fz_prio=_fuzzy_prio).sort_values('_fz_prio').drop_duplicates(
    subset='_pk', keep='first').query('_fz_prio == 0'))
leads_no_convertidos = len(df_leads[df_leads['Match_Tipo'] == 'No (Solo Lead)'].drop_duplicates(subset='_pk'))
tasa_conversion_personas = (leads_convertidos_exact / total_personas_conv) * 100 if total_personas_conv > 0 else 0
tasa_conversion_consultas = (leads_convertidos_exact / total_leads_conv) * 100 if total_leads_conv > 0 else 0

# Clasificación por campaña (usa Campana_Lead de 02_cruce_datos.py)
# Se busca sobre TODOS los leads (df_leads), no solo los de la ventana de conversión,
# porque el propósito es identificar inscriptos cuyo lead vino de campaña anterior.
if 'Campana_Lead' in df_leads.columns:
    label_campana_actual = 'Ingreso 2026' if segmento == 'Grado_Pregrado' else '2026'
    # Deduplicar por persona: priorizar exacto, luego agrupar por campaña
    df_leads['_mc_label'] = df_leads['Match_Tipo'].astype(str).apply(
        lambda v: 'Exacto' if 'Exacto' in v else ('Fuzzy' if 'Fuzzy' in v else 'Sin_Match'))
    all_exact_dedup = df_leads[df_leads['_mc_label'] == 'Exacto'].drop_duplicates(subset='_pk', keep='first')
    insc_campana_actual = len(all_exact_dedup[all_exact_dedup['Campana_Lead'] == label_campana_actual])
    insc_campana_anterior = len(all_exact_dedup[all_exact_dedup['Campana_Lead'] == 'Campaña Anterior'])
else:
    label_campana_actual = ''
    insc_campana_actual = 0
    insc_campana_anterior = 0

# Limpiar UTM y FuenteLead para calcular Meta y Google
df_leads_conv['UtmSource_Clean'] = df_leads_conv['UtmSource'].astype(str).str.lower().str.strip()
df_leads_conv['UtmCampaign_Clean'] = df_leads_conv['UtmCampaign'].astype(str).str.strip().replace('nan', '')
df_leads_conv['FuenteLead_Num'] = pd.to_numeric(df_leads_conv['FuenteLead'], errors='coerce')

df_leads['UtmSource_Clean'] = df_leads['UtmSource'].astype(str).str.lower().str.strip()
df_leads['UtmCampaign_Clean'] = df_leads['UtmCampaign'].astype(str).str.strip().replace('nan', '')
df_leads['FuenteLead_Num'] = pd.to_numeric(df_leads['FuenteLead'], errors='coerce')

# 2. Tasa de Conversión Meta (Facebook/IG)
# Aislamos matemáticamente SOLO el universo de leads que vinieron por Meta
# (usando keywords en UTM o el ID 18 nativo de FB Lead Ads).
meta_keywords = ['fb', 'facebook', 'ig', 'instagram', 'meta']
mask_meta_conv = df_leads_conv['UtmSource_Clean'].str.contains('|'.join(meta_keywords), na=False) | (df_leads_conv['FuenteLead_Num'] == 18)
# Deduplicar por persona dentro del ecosistema Meta
df_meta_conv_dedup = df_leads_conv[mask_meta_conv].sort_values('_mc_prio').drop_duplicates(subset='_pk', keep='first')
total_meta_conv = len(df_meta_conv_dedup)            # personas únicas Meta
consultas_meta_conv = int(mask_meta_conv.sum())       # consultas Meta
meta_convertidos = len(df_meta_conv_dedup[df_meta_conv_dedup['_mc_label'] == 'Exacto'])
tasa_conversion_meta_personas = (meta_convertidos / total_meta_conv) * 100 if total_meta_conv > 0 else 0
tasa_conversion_meta_consultas = (meta_convertidos / consultas_meta_conv) * 100 if consultas_meta_conv > 0 else 0

# 3. Tasa de Conversión Google
# Aislamos matemáticamente SOLO el universo de leads que vinieron por Google.
google_keywords = ['google', 'gads']
mask_google_conv = df_leads_conv['UtmSource_Clean'].str.contains('|'.join(google_keywords), na=False)
# Deduplicar por persona dentro del ecosistema Google
df_google_conv_dedup = df_leads_conv[mask_google_conv].sort_values('_mc_prio').drop_duplicates(subset='_pk', keep='first')
total_google_conv = len(df_google_conv_dedup)          # personas únicas Google
consultas_google_conv = int(mask_google_conv.sum())     # consultas Google
google_convertidos = len(df_google_conv_dedup[df_google_conv_dedup['_mc_label'] == 'Exacto'])
tasa_conversion_google_personas = (google_convertidos / total_google_conv) * 100 if total_google_conv > 0 else 0
tasa_conversion_google_consultas = (google_convertidos / consultas_google_conv) * 100 if consultas_google_conv > 0 else 0

# =========================================================
# Plataformas Pagas (UTM Campaign o Meta Ads) vs Otros

# Se considera pago todo lo que tenga UTM Campaign válido O provenga explícitamente de FB Ads (FuenteLead 18)
mask_pago = (df_leads['UtmCampaign_Clean'] != '') | (df_leads['FuenteLead_Num'] == 18)
total_pago = len(df_leads[mask_pago])
total_otros = total_leads - total_pago

# Inscriptos
total_inscriptos = len(df_insc)
inscriptos_con_origen = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Exacto')])
inscriptos_con_origen_fuzzy = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Posible Match Fuzzy')])
inscriptos_directos = len(df_insc[df_insc['Match_Tipo'] == 'No (Solo Inscripto Directo)'])

tasa_atribucion = (inscriptos_con_origen / total_inscriptos) * 100 if total_inscriptos > 0 else 0
plt.figure(figsize=(8, 5))
data_conv = {'Tipo': ['Total Leads', 'Conv. Exactas', 'Conv. Fuzzy (Pendiente)'], 
             'Cantidad': [total_leads, leads_convertidos_exact, leads_convertidos_fuzzy]}
df_conv = pd.DataFrame(data_conv)
sns.barplot(x='Tipo', y='Cantidad', data=df_conv, palette='viridis')
plt.title('Conversión General de Leads')
plt.ylabel('Cantidad')
max_val = df_conv['Cantidad'].max()
for index, value in enumerate(df_conv['Cantidad'].tolist()):
    plt.text(index, value + (max_val * 0.01), f'{value:,}', ha='center')
chart1_path = os.path.join(output_dir, "chart_1_conversion_leads.png")
plt.savefig(chart1_path, bbox_inches='tight')
plt.close()

# Gráfico 2: Composición de Inscriptos por Canal — solo Campaña 2026
# Se filtran inscriptos cuyo lead matcheó exactamente Y pertenece a la campaña actual.
# Esto garantiza que el foco del informe sea exclusivamente la campaña vigente.
if 'Campana_Lead' in df_leads_conv.columns:
    df_insc_2026 = df_leads_conv[
        (df_leads_conv['_mc_label'] == 'Exacto') &
        (df_leads_conv['Campana_Lead'] == label_campana_actual)
    ].sort_values('_mc_prio').drop_duplicates(subset='_pk', keep='first').copy()
    titulo_pie = f'Origenes de Inscriptos - Campana {label_campana_actual}'
else:
    df_insc_2026 = df_leads_conv_dedup[df_leads_conv_dedup['_mc_label'] == 'Exacto'].copy()
    titulo_pie = 'Origenes de Inscriptos (Exacto)'

# Clasificar por canal — ANY-TOUCH: cada persona cuenta en TODOS sus canales.
# Usamos df_leads_conv (sin dedup) para encontrar todos los canales de cada persona,
# luego contamos personas únicas por canal.
_insc_pks_2026 = set(df_insc_2026['_pk'].unique())
if 'Campana_Lead' in df_leads_conv.columns:
    _df_canales = df_leads_conv[
        (df_leads_conv['_pk'].isin(_insc_pks_2026)) &
        (df_leads_conv['Campana_Lead'] == label_campana_actual)
    ].copy()
else:
    _df_canales = df_leads_conv[df_leads_conv['_pk'].isin(_insc_pks_2026)].copy()
_df_canales['_utm_pie'] = _df_canales['UtmSource'].astype(str).str.lower().str.strip()
_df_canales['_fl_pie'] = pd.to_numeric(_df_canales['FuenteLead'], errors='coerce')
meta_kw = ['fb', 'facebook', 'ig', 'instagram', 'meta']

# Para cada canal, contar personas únicas (any-touch)
_pks_google = set(_df_canales[_df_canales['_utm_pie'].str.contains('google', na=False)]['_pk'].unique())
_pks_meta = set(_df_canales[
    _df_canales['_utm_pie'].str.contains('|'.join(meta_kw), na=False) | (_df_canales['_fl_pie'] == 18)
]['_pk'].unique())
_pks_bot = set(_df_canales[_df_canales['_fl_pie'] == 907]['_pk'].unique())
_pks_otros = _insc_pks_2026 - _pks_google - _pks_meta - _pks_bot

pie_data = {
    'Google Ads': len(_pks_google),
    'Meta (FB/IG)': len(_pks_meta),
    'Bot (907)': len(_pks_bot),
    'Otros / Organico': len(_pks_otros),
}
# Agregar inscriptos sin lead (directos) como categoría separada
pie_data['Sin trazabilidad'] = inscriptos_directos
# Filtrar categorías con 0
pie_labels = [k for k, v in pie_data.items() if v > 0]
pie_sizes = [v for v in pie_data.values() if v > 0]

plt.figure(figsize=(7, 7))
colors_pie = ['#3498db', '#e74c3c', '#9b59b6', '#f39c12', '#95a5a6']
plt.pie(pie_sizes, labels=pie_labels, autopct=lambda p: f'{p:.1f}%\n({int(round(p*sum(pie_sizes)/100)):,})',
        startangle=140, colors=colors_pie[:len(pie_labels)])
plt.title(titulo_pie)
chart2_path = os.path.join(output_dir, "chart_2_composicion_inscriptos.png")
plt.savefig(chart2_path, bbox_inches='tight')
plt.close()

# Gráfico 2b: Comparativa Inscriptos por Canal — Campaña 2026 vs Anterior
# Solo se genera si existe la columna Campana_Lead y hay inscriptos de ambas campañas.
# Usa df_leads (todos los leads, no solo ventana) para ver ambas campañas.
if 'Campana_Lead' in df_leads.columns and insc_campana_anterior > 0:
    df_exact_all = df_leads[df_leads['_mc_label'] == 'Exacto'].drop_duplicates(subset='_pk', keep='first').copy()
    df_exact_all['_utm_cmp'] = df_exact_all['UtmSource'].astype(str).str.lower().str.strip()
    df_exact_all['_fl_cmp'] = pd.to_numeric(df_exact_all['FuenteLead'], errors='coerce')

    def classify_canal(row):
        utm = str(row['_utm_cmp'])
        fl = row['_fl_cmp']
        if 'google' in utm: return 'Google Ads'
        if any(k in utm for k in meta_kw) or fl == 18: return 'Meta (FB/IG)'
        if fl == 907: return 'Bot (907)'
        return 'Otros'

    df_exact_all['_canal'] = df_exact_all.apply(classify_canal, axis=1)
    cmp_table = df_exact_all.groupby(['Campana_Lead', '_canal']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    canales = ['Google Ads', 'Meta (FB/IG)', 'Bot (907)', 'Otros']
    canales_present = [c for c in canales if c in cmp_table.columns]
    x = np.arange(len(canales_present))
    width = 0.35

    vals_actual = [int(cmp_table.loc[label_campana_actual, c]) if label_campana_actual in cmp_table.index else 0 for c in canales_present]
    vals_anterior = [int(cmp_table.loc['Campaña Anterior', c]) if 'Campaña Anterior' in cmp_table.index else 0 for c in canales_present]

    bars1 = ax.bar(x - width/2, vals_actual, width, label=f'Campana {label_campana_actual}', color='#2ecc71')
    bars2 = ax.bar(x + width/2, vals_anterior, width, label='Campana Anterior', color='#e67e22')
    ax.set_xticks(x)
    ax.set_xticklabels(canales_present)
    ax.set_ylabel('Inscriptos (Exacto)')
    ax.set_title(f'Comparativa Inscriptos por Canal: {label_campana_actual} vs Anterior')
    ax.legend()
    ax.bar_label(bars1, fmt='%d', padding=3)
    ax.bar_label(bars2, fmt='%d', padding=3)
    plt.tight_layout()
    chart2b_path = os.path.join(output_dir, "chart_2b_campana_comparativa.png")
    plt.savefig(chart2b_path, bbox_inches='tight')
    plt.close()
else:
    chart2b_path = None

# Gráfico 5: Procedencia Pagado vs Otros
plt.figure(figsize=(6, 6))
labels_pago = ['Plataformas Pagas (Con UTM / Ads)', 'Sin trazabilidad']
sizes_pago = [total_pago, total_otros]
plt.pie(sizes_pago, labels=labels_pago, autopct='%1.1f%%', startangle=120, colors=['#ff9999','#66b3ff'])
plt.title('Distribución de Leads Totales: Pagados vs Otros')
chart5_path = os.path.join(output_dir, "chart_5_leads_pagos_vs_otros.png")
plt.savefig(chart5_path, bbox_inches='tight')
plt.close()

# Gráfico 7: Distribución Pagados vs Otros (Solo Inscriptos Exactos, dedup por persona)
df_exactos = df_leads[df_leads['_mc_label'] == 'Exacto'].drop_duplicates(subset='_pk', keep='first').copy()
mask_pago_exactos = (df_exactos['UtmCampaign_Clean'] != '') | (df_exactos['FuenteLead_Num'] == 18)
insc_pago = len(df_exactos[mask_pago_exactos])
insc_otros = len(df_exactos) - insc_pago

if len(df_exactos) > 0:
    plt.figure(figsize=(6, 6))
    labels_insc_pago = ['Inscripciones Pagas (Meta/UTM)', 'Inscripciones Orgánicas/Directas']
    sizes_insc_pago = [insc_pago, insc_otros]
    plt.pie(sizes_insc_pago, labels=labels_insc_pago, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#f1c40f'])
    plt.title('Distribución de Inscriptos (Matcheados): Pagados vs Otros')
    chart7_path = os.path.join(output_dir, "chart_7_inscriptos_pagos_vs_otros.png")
    plt.savefig(chart7_path, bbox_inches='tight')
    plt.close()

# Gráfico 8: Tiempos de Resolución (Pagados vs Otros)
df_exactos['Fecha_Consulta'] = pd.to_datetime(df_exactos['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
fecha_col_exactos = 'Insc_Fecha Pago' if 'Insc_Fecha Pago' in df_exactos.columns else 'Fecha Pago'
df_exactos['Fecha_Pago'] = pd.to_datetime(df_exactos[fecha_col_exactos], format='mixed', errors='coerce')

df_exactos['Dias_Resolucion'] = (df_exactos['Fecha_Pago'] - df_exactos['Fecha_Consulta']).dt.days
df_tiempos = df_exactos[(df_exactos['Dias_Resolucion'] >= 0) & (df_exactos['Dias_Resolucion'] <= 180)].copy()

report_tiempos = ""
if not df_tiempos.empty:
    df_tiempos['Origen_Agrupado'] = np.where(
        (df_tiempos['UtmCampaign_Clean'] != '') | (df_tiempos['FuenteLead_Num'] == 18), 
        'Pagados (Meta/UTM)', 
        'Orgánicos/Directos'
    )
    
    def my_mode(x):
        m = x.mode()
        return m.iloc[0] if not m.empty else np.nan
        
    tiempos_agrupados = df_tiempos.groupby('Origen_Agrupado')['Dias_Resolucion'].agg(
        Promedio='mean', 
        Mediana='median', 
        Moda=my_mode
    )
    
    plt.figure(figsize=(8, 5))
    metrics_melted = tiempos_agrupados.reset_index().melt(id_vars='Origen_Agrupado', var_name='Métrica', value_name='Días')
    sns.barplot(data=metrics_melted, x='Origen_Agrupado', y='Días', hue='Métrica', palette='Set2')
    plt.title('Tiempos de Resolución: Pagados vs Orgánicos')
    plt.ylabel('Cantidad de Días')
    plt.xlabel('Criterio de Origen')
    
    for container in plt.gca().containers:
        plt.gca().bar_label(container, fmt='%.1f', padding=3)
        
    chart8_path = os.path.join(output_dir, "chart_8_tiempos_resolucion.png")
    plt.savefig(chart8_path, bbox_inches='tight')
    plt.close()

    report_tiempos = f"### Análisis de Tiempos de Resolución (Inscriptos Exactos)\n"
    report_tiempos += f"Comparativa gráfica de cuánto demora en inscribirse un prospecto según su origen (filtrado de 0 a 180 días).\n\n"
    report_tiempos += tiempos_agrupados.round(1).to_markdown() + "\n\n"
    report_tiempos += "![Tiempos Resolucion](chart_8_tiempos_resolucion.png)\n"

# =========================================================
# ANÁLISIS MULTI-TOUCH PARA INSCRIPTOS
# =========================================================
# Para cada inscripto (matcheado exacto), identifica TODOS los leads (consultas)
# que esa persona generó a través de diferentes canales. Esto muestra el
# comportamiento real: una persona puede consultar primero por Google, luego
# por Bot, y finalmente inscribirse. El análisis multi-touch revela qué
# combinaciones de canales son más efectivas.

# Reusar _pk como clave de persona para multi-touch
df_leads['_pk_mt'] = df_leads['_pk']

# Identificar canal de cada lead
df_leads['_utm_mt'] = df_leads['UtmSource'].astype(str).str.lower().str.strip()
df_leads['_fl_mt'] = pd.to_numeric(df_leads['FuenteLead'], errors='coerce')

def canal_mt(row):
    utm = str(row['_utm_mt'])
    fl = row['_fl_mt']
    if 'google' in utm: return 'Google'
    if any(k in utm for k in ['fb', 'facebook', 'ig', 'instagram', 'meta']) or fl == 18: return 'Meta'
    if fl == 907: return 'Bot'
    return 'Otros'

df_leads['_canal_mt'] = df_leads.apply(canal_mt, axis=1)

# Identificar inscriptos exactos (todos) y asignarles su campaña
# Un inscripto se clasifica según la Campana_Lead de su lead matcheado.
df_exact_mt = df_leads[df_leads['Match_Tipo'].astype(str).str.contains('Exacto')].copy()
# Para cada persona, tomar la campaña del lead más reciente (prioridad actual)
if 'Campana_Lead' in df_exact_mt.columns and label_campana_actual:
    campana_por_pk = (df_exact_mt
        .sort_values('Fecha_Limpia_Consulta', ascending=False)
        .drop_duplicates(subset='_pk_mt', keep='first')
        [['_pk_mt', 'Campana_Lead']])
else:
    campana_por_pk = pd.DataFrame(columns=['_pk_mt', 'Campana_Lead'])

inscriptos_pks = set(df_exact_mt['_pk_mt'].unique())

# Para cada inscripto, obtener la lista de canales que consultó (sin repetir)
# y la cantidad total de consultas (leads) que generó.
df_insc_leads = df_leads[df_leads['_pk_mt'].isin(inscriptos_pks)].copy()
consultas_por_persona = df_insc_leads.groupby('_pk_mt').size().rename('n_consultas')
canales_por_persona = df_insc_leads.groupby('_pk_mt')['_canal_mt'].apply(lambda x: sorted(set(x))).reset_index()
canales_por_persona['n_canales'] = canales_por_persona['_canal_mt'].apply(len)
canales_por_persona['combinacion'] = canales_por_persona['_canal_mt'].apply(lambda x: ' + '.join(x))
canales_por_persona = canales_por_persona.merge(consultas_por_persona, on='_pk_mt', how='left')

# Mejor tipo de match por persona (prioridad: DNI > Email > Tel > Cel, deduplicado)
_mt_prio_map = {'Exacto (DNI)': 0, 'Exacto (Email)': 1, 'Exacto (Teléfono)': 2, 'Exacto (Celular)': 3}
df_exact_mt['_mt_prio'] = df_exact_mt['Match_Tipo'].map(_mt_prio_map).fillna(9)
_best_match = df_exact_mt.sort_values('_mt_prio').drop_duplicates(subset='_pk_mt', keep='first')[['_pk_mt', 'Match_Tipo']]
_best_match.rename(columns={'Match_Tipo': '_best_match'}, inplace=True)
canales_por_persona = canales_por_persona.merge(_best_match, on='_pk_mt', how='left')
canales_por_persona['_best_match'] = canales_por_persona['_best_match'].fillna('')

# Merge campaña a canales_por_persona
if not campana_por_pk.empty:
    canales_por_persona = canales_por_persona.merge(campana_por_pk, on='_pk_mt', how='left')
    canales_por_persona['Campana_Lead'] = canales_por_persona['Campana_Lead'].fillna('Campaña Anterior')
else:
    canales_por_persona['Campana_Lead'] = 'Total'

# =========================================================
# FUNCIÓN HELPER: calcular stats multi-touch + any-touch para un subset
# =========================================================
def calc_mt_at(df_sub, label):
    """Calcula estadísticas multi-touch y any-touch para un DataFrame de canales_por_persona."""
    total = len(df_sub)
    if total == 0:
        return {'total': 0, 'n_single': 0, 'n_multi': 0,
                'n_1consulta': 0, 'avg_consultas': 0,
                'top_combos': pd.Series(dtype='int64'),
                'mt_dist': pd.Series(dtype='int64'),
                'at': {'Bot': 0, 'Google': 0, 'Meta': 0, 'Otros': 0},
                'match_tipos': {'DNI': 0, 'Email': 0, 'Telefono': 0, 'Celular': 0}}
    n_s = int((df_sub['n_canales'] == 1).sum())
    n_m = int((df_sub['n_canales'] > 1).sum())
    # Consultas únicas: cuántas personas hicieron exactamente 1 consulta
    n_1c = int((df_sub['n_consultas'] == 1).sum())
    avg_c = float(df_sub['n_consultas'].mean())
    tc = df_sub['combinacion'].value_counts().head(10)
    md = df_sub['n_canales'].value_counts().sort_index()
    at = {
        'Bot':    int(df_sub['_canal_mt'].apply(lambda cs: 'Bot' in cs).sum()),
        'Google': int(df_sub['_canal_mt'].apply(lambda cs: 'Google' in cs).sum()),
        'Meta':   int(df_sub['_canal_mt'].apply(lambda cs: 'Meta' in cs).sum()),
        'Otros':  int(df_sub['_canal_mt'].apply(lambda cs: 'Otros' in cs).sum()),
    }
    # Desglose por tipo de match (deduplicado: 1 persona = mejor match)
    mt_desglose = {
        'DNI':      int((df_sub['_best_match'] == 'Exacto (DNI)').sum()),
        'Email':    int((df_sub['_best_match'] == 'Exacto (Email)').sum()),
        'Telefono': int((df_sub['_best_match'] == 'Exacto (Teléfono)').sum()),
        'Celular':  int((df_sub['_best_match'] == 'Exacto (Celular)').sum()),
    }
    return {'total': total, 'n_single': n_s, 'n_multi': n_m,
            'n_1consulta': n_1c, 'avg_consultas': avg_c,
            'top_combos': tc, 'mt_dist': md, 'at': at, 'match_tipos': mt_desglose}

# Calcular para total, campaña actual y campaña anterior
stats_total = calc_mt_at(canales_por_persona, 'Total')
total_insc_mt = stats_total['total']
n_multi = stats_total['n_multi']
n_single = stats_total['n_single']

if label_campana_actual and 'Campana_Lead' in canales_por_persona.columns:
    cp_actual = canales_por_persona[canales_por_persona['Campana_Lead'] == label_campana_actual]
    cp_anterior = canales_por_persona[canales_por_persona['Campana_Lead'] == 'Campaña Anterior']
    stats_actual = calc_mt_at(cp_actual, label_campana_actual)
    stats_anterior = calc_mt_at(cp_anterior, 'Campaña Anterior')
    has_campaign_split = stats_actual['total'] > 0
else:
    stats_actual = calc_mt_at(canales_por_persona, 'Total')
    stats_anterior = calc_mt_at(pd.DataFrame(), 'Anterior')
    has_campaign_split = False

# =========================================================
# GRÁFICOS MULTI-TOUCH (TOTAL)
# =========================================================
mt_dist = stats_total['mt_dist']
plt.figure(figsize=(8, 5))
bars = plt.bar(mt_dist.index.astype(str), mt_dist.values, color='#3498db')
plt.xlabel('Cantidad de canales consultados')
plt.ylabel('Cantidad de inscriptos')
plt.title(f'Multi-Touch: Canales por Inscripto - Total ({segmento.replace("_"," ")})')
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{int(bar.get_height()):,}', ha='center', fontsize=10)
chart_mt1_path = os.path.join(output_dir, "chart_multitouch_canales.png")
plt.savefig(chart_mt1_path, bbox_inches='tight')
plt.close()

top_combos = stats_total['top_combos']
plt.figure(figsize=(10, 6))
bars = plt.barh(top_combos.index[::-1], top_combos.values[::-1], color='#2ecc71')
plt.xlabel('Cantidad de inscriptos')
plt.title(f'Top 10 Combinaciones de Canales - Total ({segmento.replace("_"," ")})')
for bar in bars:
    plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             f'{int(bar.get_width()):,}', va='center', fontsize=9)
plt.tight_layout()
chart_mt2_path = os.path.join(output_dir, "chart_multitouch_combinaciones.png")
plt.savefig(chart_mt2_path, bbox_inches='tight')
plt.close()

# =========================================================
# GRÁFICO MULTI-TOUCH DESAGREGADO POR CAMPAÑA
# =========================================================
if has_campaign_split and stats_anterior['total'] > 0:
    # Barras agrupadas: cantidad de canales por inscripto, split por campaña
    all_n = sorted(set(list(stats_actual['mt_dist'].index) + list(stats_anterior['mt_dist'].index)))
    vals_act = [int(stats_actual['mt_dist'].get(n, 0)) for n in all_n]
    vals_ant = [int(stats_anterior['mt_dist'].get(n, 0)) for n in all_n]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(all_n))
    w = 0.35
    b1 = ax.bar(x - w/2, vals_act, w, label=f'{label_campana_actual}', color='#2ecc71')
    b2 = ax.bar(x + w/2, vals_ant, w, label='Campana Anterior', color='#e67e22')
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in all_n])
    ax.set_xlabel('Cantidad de canales consultados')
    ax.set_ylabel('Inscriptos')
    ax.set_title(f'Multi-Touch por Campana: Canales por Inscripto ({segmento.replace("_"," ")})')
    ax.legend()
    ax.bar_label(b1, fmt='%d', padding=2, fontsize=8)
    ax.bar_label(b2, fmt='%d', padding=2, fontsize=8)
    plt.tight_layout()
    chart_mt_camp_path = os.path.join(output_dir, "chart_multitouch_por_campana.png")
    plt.savefig(chart_mt_camp_path, bbox_inches='tight')
    plt.close()
else:
    chart_mt_camp_path = None

# =========================================================
# GRÁFICO ANY-TOUCH TOTAL
# =========================================================
at = stats_total['at']
at_data = {'Bot': at['Bot'], 'Google Ads': at['Google'],
           'Meta (FB/IG)': at['Meta'], 'Otros / Organico': at['Otros']}

fig, ax = plt.subplots(figsize=(10, 5))
canales_at = list(at_data.keys())
valores_at = list(at_data.values())
pcts_at = [v / total_insc_mt * 100 if total_insc_mt > 0 else 0 for v in valores_at]
colors_at = ['#9b59b6', '#3498db', '#e74c3c', '#f39c12']
bars_at = ax.barh(canales_at[::-1], valores_at[::-1], color=colors_at[::-1])
for bar, pct in zip(bars_at, pcts_at[::-1]):
    ax.text(bar.get_width() + max(valores_at)*0.01, bar.get_y() + bar.get_height()/2,
            f'{int(bar.get_width()):,} ({pct:.1f}%)', va='center', fontsize=10)
ax.set_xlabel('Inscriptos donde intervino el canal')
ax.set_title(f'Any-Touch: Participacion por Canal - Total ({segmento.replace("_"," ")})')
ax.set_xlim(0, max(valores_at) * 1.25 if valores_at else 1)
plt.tight_layout()
chart_at_path = os.path.join(output_dir, "chart_anytouch_participacion.png")
plt.savefig(chart_at_path, bbox_inches='tight')
plt.close()

# =========================================================
# GRÁFICO ANY-TOUCH DESAGREGADO POR CAMPAÑA
# =========================================================
if has_campaign_split and stats_anterior['total'] > 0:
    canal_names = ['Bot', 'Google', 'Meta', 'Otros']
    canal_labels = ['Bot', 'Google Ads', 'Meta (FB/IG)', 'Otros']
    vals_at_act = [stats_actual['at'][c] for c in canal_names]
    vals_at_ant = [stats_anterior['at'][c] for c in canal_names]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(canal_labels))
    w = 0.35
    b1 = ax.bar(x - w/2, vals_at_act, w, label=f'{label_campana_actual}', color='#2ecc71')
    b2 = ax.bar(x + w/2, vals_at_ant, w, label='Campana Anterior', color='#e67e22')
    ax.set_xticks(x)
    ax.set_xticklabels(canal_labels)
    ax.set_ylabel('Inscriptos donde intervino')
    ax.set_title(f'Any-Touch por Campana ({segmento.replace("_"," ")})')
    ax.legend()

    # Labels con valor y % sobre su base
    for bars_grp, base in [(b1, stats_actual['total']), (b2, stats_anterior['total'])]:
        for bar in bars_grp:
            h = int(bar.get_height())
            pct = h / base * 100 if base > 0 else 0
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{h:,}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    chart_at_camp_path = os.path.join(output_dir, "chart_anytouch_por_campana.png")
    plt.savefig(chart_at_camp_path, bbox_inches='tight')
    plt.close()
else:
    chart_at_camp_path = None

# =========================================================
# MARKDOWN MULTI-TOUCH + ANY-TOUCH (con desagregado por campaña)
# =========================================================
def _pct(n, t): return f'{n/t*100:.1f}%' if t > 0 else '0%'

report_multitouch = f"""### Analisis Multi-Touch de Inscriptos
Cada inscripto puede haber consultado por multiples canales antes de inscribirse.

| Metrica | Total | {label_campana_actual} | Campana Anterior |
|---|---|---|---|
| Inscriptos con 1 sola consulta | {stats_total['n_1consulta']:,} ({_pct(stats_total['n_1consulta'], total_insc_mt)}) | {stats_actual['n_1consulta']:,} ({_pct(stats_actual['n_1consulta'], stats_actual['total'])}) | {stats_anterior['n_1consulta']:,} ({_pct(stats_anterior['n_1consulta'], stats_anterior['total'])}) |
| Promedio consultas por inscripto | {stats_total['avg_consultas']:.1f} | {stats_actual['avg_consultas']:.1f} | {stats_anterior['avg_consultas']:.1f} |
| Inscriptos con 1 canal | {n_single:,} ({_pct(n_single, total_insc_mt)}) | {stats_actual['n_single']:,} ({_pct(stats_actual['n_single'], stats_actual['total'])}) | {stats_anterior['n_single']:,} ({_pct(stats_anterior['n_single'], stats_anterior['total'])}) |
| Inscriptos con 2+ canales | {n_multi:,} ({_pct(n_multi, total_insc_mt)}) | {stats_actual['n_multi']:,} ({_pct(stats_actual['n_multi'], stats_actual['total'])}) | {stats_anterior['n_multi']:,} ({_pct(stats_anterior['n_multi'], stats_anterior['total'])}) |
| **Total inscriptos** | **{total_insc_mt:,}** | **{stats_actual['total']:,}** | **{stats_anterior['total']:,}** |

#### Top Combinaciones (Total)
{top_combos.reset_index().rename(columns={top_combos.name if hasattr(top_combos,'name') else 'count':'Inscriptos', 'index':'Combinacion', 'combinacion':'Combinacion'}).to_markdown(index=False)}

![Multi-Touch Canales](chart_multitouch_canales.png)
![Multi-Touch Combinaciones](chart_multitouch_combinaciones.png)
{'![Multi-Touch por Campana](chart_multitouch_por_campana.png)' if chart_mt_camp_path else ''}

### Analisis Any-Touch: Participacion por Canal
Para cada inscripto se verifica si tuvo **al menos 1 contacto** con cada canal.
Un inscripto puede aparecer en varios canales a la vez (la suma supera 100%).

| Canal | Total | {label_campana_actual} | Campana Anterior |
|---|---|---|---|
| **Bot** | {at['Bot']:,} ({_pct(at['Bot'], total_insc_mt)}) | {stats_actual['at']['Bot']:,} ({_pct(stats_actual['at']['Bot'], stats_actual['total'])}) | {stats_anterior['at']['Bot']:,} ({_pct(stats_anterior['at']['Bot'], stats_anterior['total'])}) |
| **Google Ads** | {at['Google']:,} ({_pct(at['Google'], total_insc_mt)}) | {stats_actual['at']['Google']:,} ({_pct(stats_actual['at']['Google'], stats_actual['total'])}) | {stats_anterior['at']['Google']:,} ({_pct(stats_anterior['at']['Google'], stats_anterior['total'])}) |
| **Meta (FB/IG)** | {at['Meta']:,} ({_pct(at['Meta'], total_insc_mt)}) | {stats_actual['at']['Meta']:,} ({_pct(stats_actual['at']['Meta'], stats_actual['total'])}) | {stats_anterior['at']['Meta']:,} ({_pct(stats_anterior['at']['Meta'], stats_anterior['total'])}) |
| **Otros** | {at['Otros']:,} ({_pct(at['Otros'], total_insc_mt)}) | {stats_actual['at']['Otros']:,} ({_pct(stats_actual['at']['Otros'], stats_actual['total'])}) | {stats_anterior['at']['Otros']:,} ({_pct(stats_anterior['at']['Otros'], stats_anterior['total'])}) |

#### Desglose por Tipo de Match (mejor match por persona, prioridad DNI > Email > Tel > Cel)
| Tipo Match | Total | {label_campana_actual} | Campana Anterior |
|---|---|---|---|
| **Exacto (DNI)** | {stats_total['match_tipos']['DNI']:,} ({_pct(stats_total['match_tipos']['DNI'], total_insc_mt)}) | {stats_actual['match_tipos']['DNI']:,} ({_pct(stats_actual['match_tipos']['DNI'], stats_actual['total'])}) | {stats_anterior['match_tipos']['DNI']:,} ({_pct(stats_anterior['match_tipos']['DNI'], stats_anterior['total'])}) |
| **Exacto (Email)** | {stats_total['match_tipos']['Email']:,} ({_pct(stats_total['match_tipos']['Email'], total_insc_mt)}) | {stats_actual['match_tipos']['Email']:,} ({_pct(stats_actual['match_tipos']['Email'], stats_actual['total'])}) | {stats_anterior['match_tipos']['Email']:,} ({_pct(stats_anterior['match_tipos']['Email'], stats_anterior['total'])}) |
| **Exacto (Telefono)** | {stats_total['match_tipos']['Telefono']:,} ({_pct(stats_total['match_tipos']['Telefono'], total_insc_mt)}) | {stats_actual['match_tipos']['Telefono']:,} ({_pct(stats_actual['match_tipos']['Telefono'], stats_actual['total'])}) | {stats_anterior['match_tipos']['Telefono']:,} ({_pct(stats_anterior['match_tipos']['Telefono'], stats_anterior['total'])}) |
| **Exacto (Celular)** | {stats_total['match_tipos']['Celular']:,} ({_pct(stats_total['match_tipos']['Celular'], total_insc_mt)}) | {stats_actual['match_tipos']['Celular']:,} ({_pct(stats_actual['match_tipos']['Celular'], stats_actual['total'])}) | {stats_anterior['match_tipos']['Celular']:,} ({_pct(stats_anterior['match_tipos']['Celular'], stats_anterior['total'])}) |

![Any-Touch Participacion](chart_anytouch_participacion.png)
{'![Any-Touch por Campana](chart_anytouch_por_campana.png)' if chart_at_camp_path else ''}
"""

# Gráfico 9: Curva de Consultas/Leads por Día
# Consulta: Fecha de creación viene en D/M/YYYY desde Salesforce — requiere dayfirst=True
df_leads['Fecha_Limpia_Consulta'] = pd.to_datetime(
    df_leads['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
hoy = pd.Timestamp.now()
df_leads_valid = df_leads[df_leads['Fecha_Limpia_Consulta'] <= hoy].copy()

consultas_por_dia = df_leads_valid.groupby(df_leads_valid['Fecha_Limpia_Consulta'].dt.date).size().reset_index(name='Cantidad')

if not consultas_por_dia.empty:
    consultas_por_dia['Fecha_Limpia_Consulta'] = pd.to_datetime(consultas_por_dia['Fecha_Limpia_Consulta'])
    idx_leads = pd.date_range(consultas_por_dia['Fecha_Limpia_Consulta'].min(), consultas_por_dia['Fecha_Limpia_Consulta'].max())
    consultas_por_dia = consultas_por_dia.set_index('Fecha_Limpia_Consulta').reindex(idx_leads, fill_value=0).rename_axis('Fecha_Limpia_Consulta').reset_index()

    plt.figure(figsize=(12, 5))
    sns.lineplot(data=consultas_por_dia, x='Fecha_Limpia_Consulta', y='Cantidad', marker='o', color='royalblue')
    plt.title('Curva de Consultas (Leads) por Día', fontsize=14)
    plt.xlabel('Fecha de Consulta')
    plt.ylabel('Cantidad de Consultas')
    plt.xticks(rotation=45)
    
    chart9_path = os.path.join(output_dir, "chart_9_consultas_por_dia.png")
    plt.savefig(chart9_path, bbox_inches='tight')
    plt.close()
    
    # NUEVA GRÁFICA: Por mes
    consultas_por_mes = df_leads_valid.copy()
    consultas_por_mes['Mes'] = consultas_por_mes['Fecha_Limpia_Consulta'].dt.to_period('M')
    consultas_por_mes_agrupado = consultas_por_mes.groupby('Mes').size().reset_index(name='Cantidad')
    # Rellenar meses faltantes con 0 para mostrar el timeline completo sin saltos
    if not consultas_por_mes_agrupado.empty:
        min_mes = consultas_por_mes_agrupado['Mes'].min()
        max_mes = consultas_por_mes_agrupado['Mes'].max()
        all_meses = pd.period_range(start=min_mes, end=max_mes, freq='M')
        consultas_por_mes_agrupado = (
            consultas_por_mes_agrupado
            .set_index('Mes')
            .reindex(all_meses, fill_value=0)
            .rename_axis('Mes')
            .reset_index()
        )
    consultas_por_mes_agrupado['Mes_Str'] = consultas_por_mes_agrupado['Mes'].astype(str)
    n_meses = len(consultas_por_mes_agrupado)
    fig_w = max(10, n_meses * 0.8)

    plt.figure(figsize=(fig_w, 5))
    sns.lineplot(data=consultas_por_mes_agrupado, x='Mes_Str', y='Cantidad', marker='s', color='darkorange', linewidth=2.5)
    plt.title('Curva de Consultas (Leads) por Mes', fontsize=14)
    plt.xlabel('Mes de Consulta')
    plt.ylabel('Cantidad de Consultas')
    plt.xticks(rotation=45)
    
    for _, row in consultas_por_mes_agrupado.iterrows():
        plt.annotate(f"{row['Cantidad']}", 
                     xy=(row['Mes_Str'], row['Cantidad']),
                     xytext=(0, 10), textcoords='offset points', ha='center')
                     
    chart9b_path = os.path.join(output_dir, "chart_9b_consultas_por_mes.png")
    plt.savefig(chart9b_path, bbox_inches='tight')
    plt.close()
    
    report_tiempos += "### Volumen de Consultas por Día y Mes\n"
    report_tiempos += "![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)\n\n"
    report_tiempos += "![Volumen Consultas Dia](chart_9_consultas_por_dia.png)\n\n"

# Journey
if not df_journey.empty:
    promedio_consultas = df_journey['Total_Consultas'].mean()
    promedio_dias_inscripcion = df_journey['Dias_hasta_Inscripcion'].mean()
    
    # Mejores fuentes de primer contacto de inscriptos
    inscriptos_journey = df_journey[df_journey['Inscripto'] == 'Sí'].copy()
    
    def clean_fuente(val):
        s = str(val).replace('.0', '').strip()
        if s == '18': return 'Facebook Lead Ads'
        if s == '907': return 'Chatbot (907)'
        if s == '4': return 'Portales (4)'
        if s == '3': return 'Web Orgánico (3)'
        if s in ['nan', 'None', '']: return 'Sin Origen'
        # Podría haber nombres o UTMs aquí, los dejamos igual si no son estos códigos numéricos principales
        if s.isdigit(): return f'Origen {s}'
        return s

    inscriptos_journey['Touch_1_Name'] = inscriptos_journey['Touch_1'].apply(clean_fuente)
    top_fuentes = inscriptos_journey['Touch_1_Name'].value_counts().head(10).to_dict()
    
    # Gráfico 3: Top Fuentes 1er Touch (Inscriptos)
    if top_fuentes:
        plt.figure(figsize=(10, 5))
        sns.barplot(x=list(top_fuentes.values()), y=list(top_fuentes.keys()), palette='magma')
        plt.title('Top 10 - Fuentes Iniciales de Inscriptos (Primer Contacto)')
        plt.xlabel('Cantidad de Inscripciones')
        chart3_path = os.path.join(output_dir, "chart_3_top_fuentes.png")
        plt.savefig(chart3_path, bbox_inches='tight')
        plt.close()
else:
    promedio_consultas = 0
    promedio_dias_inscripcion = 0
    top_fuentes = {}

# ==========================================
# ARMADO DEL INFORME (MARKDOWN)
# ==========================================

report_content = f"""# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al {max_date_str})*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se procesaron **{total_leads:,}** consultas únicas de Salesforce (cada una con su propio ID y origen), correspondientes a **{total_personas:,}** personas distintas. Se cruzaron contra **{total_inscriptos:,}** inscriptos únicos.

| Métrica | Valor |
|---------|-------|
| Total Consultas (ID Consulta único) | {total_leads:,} |
| Personas que consultaron | {total_personas:,} |
| Total Inscriptos | {total_inscriptos:,} |
| Personas convertidas (Exacto) | {leads_convertidos_exact:,} |
| Inscriptos atribuidos a Lead (Exacto) | {inscriptos_con_origen:,} ({tasa_atribucion:.1f}% del total) |
| Inscriptos sin trazabilidad | {inscriptos_directos:,} |
| **Tasa de Conversion sobre Consultas** | **{tasa_conversion_consultas:.2f}%** *(inscriptos / consultas en ventana)* |
| **Tasa de Conversion sobre Personas** | **{tasa_conversion_personas:.2f}%** *(inscriptos / personas en ventana)* |

> **Consultas vs Personas (Embudo):** Cada consulta tiene un ID unico de Salesforce y proviene de un canal especifico. Una persona puede generar multiples consultas desde distintos canales. Se presentan DOS tasas de conversion: sobre consultas (eficiencia por interaccion) y sobre personas (eficiencia por individuo). La tasa sobre personas es el KPI principal del embudo: Consultas -> Personas -> Inscriptos.

### Desglose por Ecosistema Principal (Any-Touch)
*(Nota: Las tasas de conversión reflejan cruces exactos. Modelo Any-Touch: una persona que consultó por Google Y por Meta se cuenta en ambos canales.)*
{f'*(Nota Cohortes: Para {segmento}, las tasas de conversión asumen como denominador las personas que consultaron a partir de Septiembre 2025, coincidiendo con el inicio de inscripción a la primera cohorte. En mayo se abren a la segunda.)*' if segmento == 'Grado_Pregrado' else ''}
| Ecosistema | Consultas | Personas | Convertidas | Tasa s/Consultas | Tasa s/Personas |
|------------|-----------|----------|-------------|------------------|-----------------|
| **Google Ads** | {consultas_google_conv:,} | {total_google_conv:,} | {google_convertidos:,} | {tasa_conversion_google_consultas:.2f}% | **{tasa_conversion_google_personas:.2f}%** |
| **Meta (FB/IG)** | {consultas_meta_conv:,} | {total_meta_conv:,} | {meta_convertidos:,} | {tasa_conversion_meta_consultas:.2f}% | **{tasa_conversion_meta_personas:.2f}%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los {total_leads:,} leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** {total_pago:,} leads ({(total_pago/total_leads)*100:.1f}%)
- **Otros (Orgánico / Sin Tracking ID):** {total_otros:,} leads ({(total_otros/total_leads)*100:.1f}%)

De igual manera, al observar solo las **{len(df_exactos):,} inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** {insc_pago:,} ({(insc_pago/len(df_exactos)*100) if len(df_exactos) > 0 else 0:.1f}%)
- **Inscripciones Orgánicas/Directas:** {insc_otros:,} ({(insc_otros/len(df_exactos)*100) if len(df_exactos) > 0 else 0:.1f}%)

*(Nota sobre Fuzzys: Existen {leads_convertidos_fuzzy:,} leads sospechosos de ser inscriptos ({inscriptos_con_origen_fuzzy:,} inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Atribución por Campaña
{'La columna `Campana_Lead` identifica si el lead que generó la inscripción pertenece a la campaña actual o a una anterior.' if insc_campana_actual > 0 or insc_campana_anterior > 0 else 'Columna Campana_Lead no disponible — ejecutar 02_cruce_datos.py para generarla.'}
{'| Campaña | Inscriptos Exactos |' if (insc_campana_actual + insc_campana_anterior) > 0 else ''}
{'|---|---|' if (insc_campana_actual + insc_campana_anterior) > 0 else ''}
{'| Campaña actual (' + label_campana_actual + ') | ' + f'{insc_campana_actual:,}' + ' |' if (insc_campana_actual + insc_campana_anterior) > 0 else ''}
{'| Campaña anterior (match histórico) | ' + f'{insc_campana_anterior:,}' + ' |' if (insc_campana_actual + insc_campana_anterior) > 0 else ''}

### Visualización de Tasas y Atribución
![Conversión Leads](chart_1_conversion_leads.png)
![Composición Inscriptos](chart_2_composicion_inscriptos.png)
![Pagados vs Otros Leads](chart_5_leads_pagos_vs_otros.png)
![Pagados vs Otros Inscriptos](chart_7_inscriptos_pagos_vs_otros.png)

{'![Comparativa por Campana](chart_2b_campana_comparativa.png)' if insc_campana_anterior > 0 else ''}

{report_tiempos}

{report_multitouch}

## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** {promedio_consultas:.1f} veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **{promedio_dias_inscripcion:.1f} días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
"""

for fuente, cantidad in top_fuentes.items():
    report_content += f"- **{fuente}**: {cantidad} inscriptos\n"

# Gráfico 4: Curva de Inscripciones por Día
# Preferimos 'Insc_Fecha Pago', si no está, usamos 'Fecha Pago'
fecha_col = 'Insc_Fecha Pago' if 'Insc_Fecha Pago' in df_insc.columns else 'Fecha Pago'
if fecha_col in df_insc.columns:
    df_insc['Fecha_Limpia'] = pd.to_datetime(df_insc[fecha_col], format='mixed', errors='coerce')
    
    # Filtrar fechas futuras inválidas (mayores a hoy)
    hoy = pd.Timestamp.now()
    df_insc_valid = df_insc[df_insc['Fecha_Limpia'] <= hoy].copy()
    
    inscripciones_por_dia = df_insc_valid.groupby(df_insc_valid['Fecha_Limpia'].dt.date).size().reset_index(name='Cantidad')
    
    if not inscripciones_por_dia.empty:
        inscripciones_por_dia['Fecha_Limpia'] = pd.to_datetime(inscripciones_por_dia['Fecha_Limpia'])
        idx_insc = pd.date_range(inscripciones_por_dia['Fecha_Limpia'].min(), inscripciones_por_dia['Fecha_Limpia'].max())
        inscripciones_por_dia = inscripciones_por_dia.set_index('Fecha_Limpia').reindex(idx_insc, fill_value=0).rename_axis('Fecha_Limpia').reset_index()

        plt.figure(figsize=(12, 5))
        sns.lineplot(data=inscripciones_por_dia, x='Fecha_Limpia', y='Cantidad', marker='o', color='crimson')
        plt.title('Curva de Inscripciones Confirmadas por Día', fontsize=14)
        plt.xlabel('Fecha de Pago')
        plt.ylabel('Cantidad de Inscripciones')
        plt.xticks(rotation=45)
        
        # Anotar picos
        picos = inscripciones_por_dia.nlargest(4, 'Cantidad')
        for _, row in picos.iterrows():
            plt.annotate(f"{row['Cantidad']}", 
                         xy=(row['Fecha_Limpia'], row['Cantidad']),
                         xytext=(0, 10), textcoords='offset points', ha='center',
                         fontweight='bold')
                         
        chart6_path = os.path.join(output_dir, "chart_6_inscripciones_por_dia.png")
        plt.savefig(chart6_path, bbox_inches='tight')
        plt.close()
        
        # Tablas de Picos y Valles para el Markdown
        dias_espanol = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        # Picos (top 4)
        picos_table = "| Fecha | Día de la Semana | Cantidad de Inscripciones |\n|-------|------------------|---------------------------|\n"
        for _, row in picos.iterrows():
            d_name = dias_espanol[row['Fecha_Limpia'].weekday()]
            picos_table += f"| {row['Fecha_Limpia'].strftime('%d/%m/%Y')} | {d_name} | {row['Cantidad']} |\n"
            
        # Valles (top 10 días con menos inscripciones, excluyendo posibles ceros si no hubo agrupamiento)
        valles = inscripciones_por_dia.nsmallest(15, 'Cantidad')
        valles_table = "| Fecha | Día de la Semana | Cantidad de Inscripciones |\n|-------|------------------|---------------------------|\n"
        valles_finde = 0
        for _, row in valles.iterrows():
            dia_idx = row['Fecha_Limpia'].weekday()
            d_name = dias_espanol[dia_idx]
            if dia_idx >= 5: # Sábado o Domingo
                valles_finde += 1
            valles_table += f"| {row['Fecha_Limpia'].strftime('%d/%m/%Y')} | {d_name} | {row['Cantidad']} |\n"
            
        fines_de_semana_pct = (valles_finde / len(valles)) * 100 if len(valles) > 0 else 0
        
        report_content = str(report_content) + f"""
## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

{picos_table}

### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

{valles_table}

**Observación sobre los valles:** El {fines_de_semana_pct:.1f}% de los días con menor volumen de inscripciones del histórico analizado coinciden directamente con fines de semana (Sábado/Domingo).
"""

report_content += f"""
## Nota Metodologica
- **Cruce de datos:** Deduplicado por persona (DNI). Match exacto por DNI, Email, Telefono y Celular.
- **Modelo de este informe: Any-Touch ESTANDAR** - Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Incluye todas las consultas, sin filtro de fecha vs pago.
- **Modelo Causal (informe separado):** Solo cuenta consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago (Consulta <= Insc_Fecha Pago). Consultas post-pago excluidas. Ver `Presupuesto_ROI_Causal`.
- **Tasas de conversion:** Se presentan dos tasas complementarias: (1) **sobre consultas** = inscriptos / consultas en ventana, mide eficiencia por interaccion; (2) **sobre personas** = inscriptos / personas unicas en ventana, mide eficiencia por individuo (KPI principal). Embudo: Consultas -> Personas -> Inscriptos. Ventana: {'leads desde Sep 2025' if segmento == 'Grado_Pregrado' else 'leads del ano calendario'}.
- **Fuente:** Consultas exportadas de Salesforce, inscriptos del sistema academico.

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.

"""

# --- Sección Causal (Any-Touch filtrado por fecha) ---
causal_data = compute_anytouch_causal(leads_csv, segmento, inscriptos_csv)
report_content += render_causal_md(causal_data, segmento)

# Guardar
with open(report_md_file, "w", encoding="utf-8") as file:
    file.write(report_content)

print(f"-> Informe final Markdown generado en: {report_md_file}")

# ==========================================
# MEMORIA TÉCNICA
# ==========================================
memoria = f"""# Memoria Técnica: Informe Analítico de Marketing

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Segmento:** {segmento}
**Script:** `04_reporte_final.py`

## Fuentes de Datos
- Leads: `{leads_csv}`
- Inscriptos: `{inscriptos_csv}`
- Journey: `{journey_file}`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total Consultas (ID Consulta único) | {total_leads:,} |
| Personas únicas que consultaron | {total_personas:,} |
| Consultas en período de conversión | {total_leads_conv:,} |
| Personas en período de conversión | {total_personas_conv:,} |
| Total Inscriptos | {total_inscriptos:,} |
| Personas convertidas (Exacto) | {leads_convertidos_exact:,} |
| Personas convertidas (Fuzzy) | {leads_convertidos_fuzzy:,} |
| Personas no convertidas | {leads_no_convertidos:,} |
| Inscriptos atribuidos a Lead (Exacto) | {inscriptos_con_origen:,} |
| Inscriptos sin trazabilidad | {inscriptos_directos:,} |

> **Nota:** Cada consulta tiene un ID unico de Salesforce y un origen especifico. Una persona puede tener multiples consultas desde diferentes canales. Se presentan DOS tasas de conversion: sobre consultas (eficiencia por interaccion) y sobre personas (eficiencia por individuo, KPI principal). Embudo: Consultas -> Personas -> Inscriptos.

## Tasas de Conversion Calculadas
| Ecosistema | Consultas | Personas | Convertidas | Tasa s/Consultas | Tasa s/Personas |
|---|---|---|---|---|---|
| **General** | {total_leads_conv:,} | {total_personas_conv:,} | {leads_convertidos_exact:,} | {tasa_conversion_consultas:.2f}% | {tasa_conversion_personas:.2f}% |
| **Google Ads** | {consultas_google_conv:,} | {total_google_conv:,} | {google_convertidos:,} | {tasa_conversion_google_consultas:.2f}% | {tasa_conversion_google_personas:.2f}% |
| **Meta (FB/IG)** | {consultas_meta_conv:,} | {total_meta_conv:,} | {meta_convertidos:,} | {tasa_conversion_meta_consultas:.2f}% | {tasa_conversion_meta_personas:.2f}% |

## Procedencia de Leads
| Categoría | Cantidad | Porcentaje |
|---|---|---|
| Plataformas Pagas (UTM/Ads) | {total_pago:,} | {(total_pago/total_leads)*100:.1f}% |
| Otros (Orgánico/Sin Tracking) | {total_otros:,} | {(total_otros/total_leads)*100:.1f}% |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual ({label_campana_actual}) | {insc_campana_actual:,} |
| Inscriptos campaña anterior (match histórico) | {insc_campana_anterior:,} |

La columna `Campana_Lead` en el CSV maestro indica si la fecha de consulta del lead
cae dentro de la ventana de la campaña actual o es anterior. Generada por `02_cruce_datos.py`.
- Grado_Pregrado: >= 2025-09-01 = "Ingreso 2026", antes = "Campaña Anterior"
- Cursos/Posgrados: >= 2026-01-01 = "2026", antes = "Campaña Anterior"

## Reglas de Negocio Aplicadas
- **Filtro de cohorte (Grado_Pregrado):** {'Sí — leads desde 2025-09-01' if segmento == 'Grado_Pregrado' else 'No — se usan todos los leads'}
- **Match_Tipo para conversión exacta:** Se filtran registros cuyo `Match_Tipo` contenga la cadena `"Exacto"` (incluye: Exacto DNI, Email, Teléfono, Celular)
- **Fuzzy excluidos de tasa:** Los matches fuzzy (nombre/email) NO se cuentan como conversión
- **Fecha de corte del informe:** `{max_date_str}` (extraída de inscriptos, columna `Insc_Fecha Pago`)

## Gráficos Generados
1. `chart_1_conversion_leads.png` — Barras: Total Leads vs Conv. Exactas vs Fuzzy
2. `chart_2_composicion_inscriptos.png` — Pie: Atribuidos vs Sin trazabilidad
3. `chart_5_leads_pagos_vs_otros.png` — Pie: Leads pagados vs orgánicos
4. `chart_7_inscriptos_pagos_vs_otros.png` — Pie: Inscripciones pagas vs orgánicas
5. `chart_8_tiempos_resolucion.png` — Barras: Días resolución pagados vs orgánicos
6. `chart_9_consultas_por_dia.png` — Línea: Volumen consultas diario
7. `chart_9b_consultas_por_mes.png` — Línea: Volumen consultas mensual
8. `chart_6_inscripciones_por_dia.png` — Línea: Curva inscripciones por día
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria)
print(f"-> Memoria técnica generada en: {output_dir}")
