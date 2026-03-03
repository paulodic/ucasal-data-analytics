import pandas as pd
import glob
import os
import re

print("==== CHEQUEO DE DNI INVALIDOS ====")
def clean_dni(val):
    if pd.isna(val) or val == '': return pd.NA
    s = str(val).split('.')[0]
    s = re.sub(r'\D', '', s)
    if not s or s == '0'*len(s): return pd.NA
    if len(s) < 6: return pd.NA
    if s.startswith('00'): s = s[2:]
    if s.startswith('0'): s = s[1:]
    s = re.sub(r'(^\d{2,4})15(\d{6,8}$)', r'\1\2', s)
    if len(s) > 10: s = s[-10:]
    return s if s else pd.NA

inscriptos_files = glob.glob("h:/Test-Antigravity/marketing_report/data/1_raw/inscriptos/*.xlsx")
inscriptos_list = []
for f in inscriptos_files: inscriptos_list.append(pd.read_excel(f, usecols=['DNI']))
df_insc = pd.concat(inscriptos_list, ignore_index=True)
total_insc = len(df_insc)
insc_valid = df_insc['DNI'].apply(clean_dni).notna().sum()
print(f"Inscriptos -> Total: {total_insc}, Con DNI válido: {insc_valid}, Inválidos: {total_insc - insc_valid}")

leads_files = glob.glob("h:/Test-Antigravity/marketing_report/data/1_raw/leads_salesforce/*.xlsx")
leads_list = []
for f in leads_files: leads_list.append(pd.read_excel(f, usecols=['DNI']))
df_leads = pd.concat(leads_list, ignore_index=True)
total_leads = len(df_leads)
leads_valid = df_leads['DNI'].apply(clean_dni).notna().sum()
print(f"Leads -> Total: {total_leads}, Con DNI válido: {leads_valid}, Inválidos: {total_leads - leads_valid}")

print("\n==== CHEQUEO DE FECHAS DE CREACION (LEADS COMPLETOS) ====")
try:
    df_leads_c = pd.read_csv('h:/Test-Antigravity/marketing_report/outputs/Grado_Pregrado/Data_Base/reporte_marketing_leads_completos.csv', low_memory=False, usecols=['Consulta: Fecha de creación'])
    df_leads_c = df_leads_c.dropna(subset=['Consulta: Fecha de creación'])
    print(f"Total leads con fecha: {len(df_leads_c)}")
    
    df_leads_c['Fecha_M1'] = pd.to_datetime(df_leads_c['Consulta: Fecha de creación'], dayfirst=True, errors='coerce')
    print("M1 (dayfirst=True):")
    print(df_leads_c['Fecha_M1'].dt.to_period('M').value_counts().sort_index())
    
    df_leads_c['Fecha_M2'] = pd.to_datetime(df_leads_c['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    print("\nM2 (mixed, dayfirst=True):")
    print(df_leads_c['Fecha_M2'].dt.to_period('M').value_counts().sort_index())
    
    print("\nEjemplos que caen en Diciembre 2025:")
    print(df_leads_c[df_leads_c['Fecha_M1'].dt.month == 12].head(10)['Consulta: Fecha de creación'].tolist())
except Exception as e:
    print(f"Error parseando fechas: {e}")
