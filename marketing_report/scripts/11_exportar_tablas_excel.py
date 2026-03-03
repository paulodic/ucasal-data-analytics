import pandas as pd
import os

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

# ==========================================
# CONFIGURACIÓN
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Informe_Analitico")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)

leads_file = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_file = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Cargando datos para exportacion de tablas Excel...")
df = pd.read_csv(leads_file, low_memory=False)
df_insc = pd.read_csv(inscriptos_file, low_memory=False)

# Clasificar
def classify(v):
    s = str(v)
    if 'Si (Lead -> Inscripto Exacto)' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

df['_mc'] = df['Match_Tipo'].apply(classify)
df_main = df[df['_mc'] != 'fuzzy'].copy()

# Deduplicar por persona
df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

personas = df_main.drop_duplicates(subset='_pk')

# REGLA DE NEGOCIO COHORTES (Muestra para Conversión)
if segmento == 'Grado_Pregrado':
    df_main['Fecha_Limpia'] = pd.to_datetime(df_main['Consulta: Fecha de creación'], errors='coerce')
    df_main_conv = df_main[df_main['Fecha_Limpia'] >= '2024-09-01'].copy()
else:
    df_main_conv = df_main.copy()

personas_conv_df = df_main_conv.drop_duplicates(subset='_pk')

# ==========================================
# 1. TABLA: RESUMEN EJECUTIVO
# ==========================================
print("Generando Tabla: Resumen Ejecutivo...")
total_personas = len(personas)
total_personas_muestra = len(personas_conv_df)

personas_conv_hist = len(personas[personas['_mc'] == 'exacto'])
personas_conv_muestra = len(personas_conv_df[personas_conv_df['_mc'] == 'exacto'])

tasa_dedup_muestra = (personas_conv_muestra / total_personas_muestra * 100) if total_personas_muestra > 0 else 0

total_registros = len(df_main)
total_exactos_muestra = len(df_main_conv[df_main_conv['_mc'] == 'exacto'])
total_fuzzy = len(df[df['_mc'] == 'fuzzy'])

insc_exactos = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Exacto')])
insc_directos = len(df_insc[df_insc['Match_Tipo'] == 'No (Solo Inscripto Directo)'])

resumen_data = {
    'Metrica': [
        'Total Registros de Leads (sin fuzzy)',
        'Personas Unicas (deduplicado Histórico)',
        'Personas Unicas (Muestra Conversión)',
        'Leads Convertidos Muestra (exacto)',
        'Personas Convertidas Histórico (deduplicadas)',
        'Personas Convertidas Muestra (deduplicadas)',
        'Tasa de Conversion Real Muestra (deduplicada)',
        'Inscriptos Atribuidos Marketing',
        'Inscriptos sin trazabilidad',
        'Coincidencias Fuzzy (Pendientes)'
    ],
    'Valor': [
        f'{total_registros:,}',
        f'{total_personas:,}',
        f'{total_personas_muestra:,}',
        f'{total_exactos_muestra:,}',
        f'{personas_conv_hist:,}',
        f'{personas_conv_muestra:,}',
        f'{tasa_dedup_muestra:.2f}%',
        f'{insc_exactos:,}',
        f'{insc_directos:,}',
        f'{total_fuzzy:,}'
    ]
}
df_resumen = pd.DataFrame(resumen_data)

# ==========================================
# 2. LIMPIEZA Y MAPEADO (COMO EN EL REPORTE)
# ==========================================
print("Mapeando orígenes y normalizando modalidades...")
df_main['FuenteLead_clean'] = df_main['FuenteLead'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# Simular mapping (podríamos leer el Excel, pero para el resumen usamos la lógica de 05)
def get_origen_name(fuente_id):
    if pd.isna(fuente_id) or fuente_id == 'nan' or not fuente_id: return 'Desconocido'
    if fuente_id == '18': return 'Facebook Lead Ads'
    if fuente_id == '907': return 'Chatbot'
    return f"Origen ({fuente_id})"

df_main['Formulario_Origen'] = df_main['FuenteLead_clean'].apply(get_origen_name)

def normalize_modo(val):
    v_str = str(val).strip().lower()
    if v_str in ['1', '1.0'] or 'presencial' in v_str: return 'Presencial'
    if v_str in ['2', '2.0'] or 'semi' in v_str: return 'Semipresencial'
    if v_str in ['7', '7.0'] or 'distancia' in v_str: return 'A Distancia'
    return 'Otro'

df_main['Modo_Limpio'] = df_main['Modo'].apply(normalize_modo)
df_main_conv['Modo_Limpio'] = df_main_conv['Modo'].apply(normalize_modo)

personas = df_main.drop_duplicates(subset='_pk')
personas_conv_df = df_main_conv.drop_duplicates(subset='_pk')

# ==========================================
# 3. TABLA: PERFORMANCE DEL BOT (907)
# ==========================================
print("Generando Tabla: Performance Bot (907)...")
df_bot_conv = personas_conv_df[personas_conv_df['FuenteLead_clean'] == '907'].copy()
bp_total_m = len(df_bot_conv)
bp_conv_m = len(df_bot_conv[df_bot_conv['_mc'] == 'exacto'])
bp_tasa = (bp_conv_m / bp_total_m * 100) if bp_total_m > 0 else 0

bot_data = {
    'Metrica': ['Personas captadas por Bot (Muestra)', 'Inscriptos del Bot (Muestra)', 'Tasa de Conversion Bot (Muestra)'],
    'Valor': [f'{bp_total_m:,}', f'{bp_conv_m:,}', f'{bp_tasa:.2f}%']
}
df_bot_res = pd.DataFrame(bot_data)

# ==========================================
# 4. TABLA: CONVERSION POR MODALIDAD
# ==========================================
print("Generando Tabla: Conversion por Modalidad...")
df_modo_vol = personas.groupby('Modo_Limpio').agg(
    Personas=('_pk', 'count')
).reset_index()

df_modo_conv = personas_conv_df.groupby('Modo_Limpio').agg(
    Personas_Muestra=('_pk', 'count'),
    Inscriptos=('_mc', lambda x: (x == 'exacto').sum())
).reset_index()

df_modo = pd.merge(df_modo_vol, df_modo_conv, on='Modo_Limpio', how='outer').fillna(0)
df_modo['Tasa_%'] = (df_modo['Inscriptos'] / df_modo['Personas_Muestra'] * 100).round(2)
df_modo.loc[df_modo['Personas_Muestra'] == 0, 'Tasa_%'] = 0.0
df_modo = df_modo.sort_values('Personas', ascending=False)

# ==========================================
# 5. TABLA: TOP ORÍGENES
# ==========================================
print("Generando Tabla: Top Origenes...")

df_origen_vol = personas.groupby('Formulario_Origen').agg(
    Personas=('_pk', 'count')
).reset_index()

df_origen_conv = personas_conv_df.groupby('Formulario_Origen').agg(
    Personas_Muestra=('_pk', 'count'),
    Inscriptos=('_mc', lambda x: (x == 'exacto').sum())
).reset_index()

df_origen = pd.merge(df_origen_vol, df_origen_conv, on='Formulario_Origen', how='outer').fillna(0)
df_origen['Tasa_%'] = (df_origen['Inscriptos'] / df_origen['Personas_Muestra'] * 100).round(2)
df_origen.loc[df_origen['Personas_Muestra'] == 0, 'Tasa_%'] = 0.0
df_origen = df_origen.sort_values('Personas', ascending=False).head(50)

# ==========================================
# EXPORTAR MASTER EXCEL
# ==========================================
master_xlsx = os.path.join(output_dir, "Tablas_Informe_Analitico.xlsx")
with pd.ExcelWriter(master_xlsx, engine='openpyxl') as writer:
    df_resumen.to_excel(writer, sheet_name='Resumen_Ejecutivo', index=False)
    df_bot_res.to_excel(writer, sheet_name='Performance_Bot', index=False)
    df_modo.to_excel(writer, sheet_name='Por_Modalidad', index=False)
    df_origen.to_excel(writer, sheet_name='Top_50_Origenes', index=False)

print(f"\n-> Master Excel generado: {master_xlsx}")
print("¡Tablas exportadas con exito!")
