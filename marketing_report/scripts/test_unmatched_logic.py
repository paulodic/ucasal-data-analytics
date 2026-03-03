import pandas as pd
import numpy as np

base_dir = r"h:\Test-Antigravity\marketing_report"
leads_csv = base_dir + r"\outputs\Data_Base\reporte_marketing_leads_completos.csv"

df = pd.read_csv(leads_csv, low_memory=False)

def classify_mc(v):
    s = str(v)
    if 'Exacto' in s: return 'Exacto'
    return 'No Exacto'

df['Grupo_Match'] = df['Match_Tipo'].apply(classify_mc)

df['Persona_ID'] = df['Correo'].fillna(df['DNI'].astype(str))
df = df[df['Persona_ID'].notna()]
df['Persona_ID'] = df['Persona_ID'].astype(str).str.lower().str.strip()
df = df[~df['Persona_ID'].isin(['nan', '', 'na'])]

if 'Consulta: Fecha de creación' in df.columns:
    df['Fecha_Consulta'] = pd.to_datetime(df['Consulta: Fecha de creación'], dayfirst=True, errors='coerce')
    
    if 'Insc_Fecha Pago' in df.columns and 'Fecha Pago' in df.columns:
        df['Fecha_Pago_Final'] = pd.to_datetime(df['Insc_Fecha Pago'].fillna(df['Fecha Pago']), dayfirst=True, errors='coerce')
    elif 'Fecha Pago' in df.columns:
        df['Fecha_Pago_Final'] = pd.to_datetime(df['Fecha Pago'], dayfirst=True, errors='coerce')
    elif 'Insc_Fecha Pago' in df.columns:
        df['Fecha_Pago_Final'] = pd.to_datetime(df['Insc_Fecha Pago'], dayfirst=True, errors='coerce')
    else:
        df['Fecha_Pago_Final'] = pd.NaT

    fecha_min_razonable = pd.Timestamp('2024-01-01')
    fecha_max_razonable = pd.Timestamp.now() + pd.Timedelta(days=30)
    
    df.loc[df['Fecha_Consulta'] < fecha_min_razonable, 'Fecha_Consulta'] = pd.NaT
    df.loc[df['Fecha_Consulta'] > fecha_max_razonable, 'Fecha_Consulta'] = pd.NaT
    df.loc[df['Fecha_Pago_Final'] < fecha_min_razonable, 'Fecha_Pago_Final'] = pd.NaT
    df.loc[df['Fecha_Pago_Final'] > fecha_max_razonable, 'Fecha_Pago_Final'] = pd.NaT

    df_exactos_only = df[df['Grupo_Match'] == 'Exacto'].copy()
    
    persona_time = df_exactos_only.groupby('Persona_ID').agg(
        Primera_Consulta=('Fecha_Consulta', 'min'),
        Fecha_Pago=('Fecha_Pago_Final', 'first')
    ).reset_index()
    
    persona_time = persona_time.dropna(subset=['Primera_Consulta', 'Fecha_Pago'])
    persona_time['Dias_Resolucion'] = (persona_time['Fecha_Pago'] - persona_time['Primera_Consulta']).dt.days
    
    persona_time_filtered = persona_time[(persona_time['Dias_Resolucion'] >= 0) & (persona_time['Dias_Resolucion'] <= 180)]
    
    print("\n--- MÉTRICAS ACTUALES DEL SCRIPT ---")
    print(f"Personas analizadas (0-180 días): {len(persona_time_filtered)}")
    print(f"Promedio: {persona_time_filtered['Dias_Resolucion'].mean():.2f} días")
    print(f"Mediana: {persona_time_filtered['Dias_Resolucion'].median():.2f} días")
    
    # Análisis sin restricción de 180 días
    persona_time_all = persona_time[persona_time['Dias_Resolucion'] >= 0]
    print("\n--- MÉTRICAS SIN RESTRICCIÓN DE 180 DÍAS ---")
    print(f"Personas analizadas (Todos los días positivos): {len(persona_time_all)}")
    print(f"Promedio: {persona_time_all['Dias_Resolucion'].mean():.2f} días")
    print(f"Mediana: {persona_time_all['Dias_Resolucion'].median():.2f} días")
    print(f"Máximo de días: {persona_time_all['Dias_Resolucion'].max()} días")
