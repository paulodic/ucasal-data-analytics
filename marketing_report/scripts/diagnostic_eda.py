import pandas as pd
import numpy as np

# Rutas originales
leads_path = r"h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv"

print("Cargando raw data de Leads...")
df_leads = pd.read_csv(leads_path, low_memory=False)

# 1. Analizar el Pico Anómalo Diario
print("\n--- 1. PICO ANÓMALO DIARIO ---")
df_leads['Fecha_Limpia'] = pd.to_datetime(df_leads['Consulta: Fecha de creación'], dayfirst=True, errors='coerce').dt.date
conteo_diario = df_leads.groupby('Fecha_Limpia').size().reset_index(name='Cantidad')
conteo_diario = conteo_diario.sort_values(by='Cantidad', ascending=False)
pico_dia = conteo_diario.iloc[0]['Fecha_Limpia']
pico_volumen = conteo_diario.iloc[0]['Cantidad']

print(f"El día con mayor volumen histórico es: {pico_dia} con {pico_volumen} leads.")

# Analizar la composición de ese pico
df_pico = df_leads[df_leads['Fecha_Limpia'] == pico_dia]
print("\nDesglose por UTM Source ese día:")
print(df_pico['UtmSource'].value_counts().head(5))
print("\nDesglose por UTM Campaign ese día:")
print(df_pico['UtmCampaign'].value_counts().head(5))
print("\nDesglose por Estado ese día:")
print(df_pico['Estado'].value_counts().head(5))

# 2. Análisis de Coherencia de Fechas y IDs
print("\n--- 2. COHERENCIA DE FECHAS E IDs ---")
df_leads['Consulta_ID'] = pd.to_numeric(df_leads['Consulta: ID Consulta'], errors='coerce')
df_fechas = df_leads.dropna(subset=['Consulta_ID', 'Fecha_Limpia']).copy()
df_fechas = df_fechas.sort_values(by='Consulta_ID')

print("\nMuestra de los 10 IDs más bajos (más antiguos teóricamente):")
print(df_fechas[['Consulta_ID', 'Consulta: Fecha de creación']].head(10))

# Revisar leads previos a septiembre 2024 (Se asume que la campaña real es para ciclo 2025, empezando en sept 2024 o 2025?)
df_antiguos = df_fechas[df_fechas['Fecha_Limpia'] < pd.to_datetime('2024-09-01').date()]
print(f"\nCantidad de Leads pre-Septiembre 2024: {len(df_antiguos)}")
if not df_antiguos.empty:
    print(df_antiguos['Consulta: Fecha de creación'].value_counts().head(10))

