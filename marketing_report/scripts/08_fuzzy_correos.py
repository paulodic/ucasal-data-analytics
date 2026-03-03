import pandas as pd
import os
import Levenshtein
import numpy as np

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "Calidad_Datos")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")

leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")
output_excel = os.path.join(output_dir, "control_manual_correos.xlsx")

print("Cargando bases de datos para búsqueda Fuzzy de Correos...")
df_leads = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

# Filtramos LEADS que no matchearon
def classify_mc(v):
    s = str(v)
    if 'Si' in s and 'Exacto' in s: return 'exacto'
    return 'no_match'

df_leads['_mc'] = df_leads['Match_Tipo'].apply(classify_mc)
leads_unmatched = df_leads[df_leads['_mc'] != 'exacto'].dropna(subset=['Correo']).copy()
leads_unmatched['Correo_low'] = leads_unmatched['Correo'].astype(str).str.lower().str.strip()

# Filtramos INSCRIPTOS que no matchearon (los que no tienen origen exacto)
# En reporte_marketing_inscriptos_origenes, si Match_Tipo esta vacio, no matcheo
df_insc['Match_Tipo'] = df_insc['Match_Tipo'].fillna('')
insc_unmatched = df_insc[~df_insc['Match_Tipo'].str.contains('Exacto')].copy()

# El correo del inscripto suele estar en Insc_Email o Email. Usaremos el que tenga.
col_email_insc = 'Insc_Email' if 'Insc_Email' in df_insc.columns else 'Email'
insc_unmatched = insc_unmatched.dropna(subset=[col_email_insc]).copy()
insc_unmatched['Email_low'] = insc_unmatched[col_email_insc].astype(str).str.lower().str.strip()

print(f"Buscando matches fuzzy entre {len(insc_unmatched)} inscriptos y {len(leads_unmatched)} leads no matcheados...")

# Cargar output anterior si existe, para no repetir
existing_pairs = set()
df_existing = pd.DataFrame()

if os.path.exists(output_excel):
    print("Detectado archivo previo. Cargando validaciones previas para no pisarlas...")
    df_existing = pd.read_excel(output_excel)
    for _, row in df_existing.iterrows():
        l_mail = str(row.get('Lead_Correo', '')).lower().strip()
        i_mail = str(row.get('Insc_Correo', '')).lower().strip()
        if l_mail and i_mail:
            existing_pairs.add((l_mail, i_mail))
else:
    df_existing = pd.DataFrame(columns=[
        'Validado', 'Distancia', 'Lead_DNI', 'Lead_Nombre', 'Lead_Correo', 
        'Insc_DNI', 'Insc_Nombre', 'Insc_Correo'
    ])

from collections import defaultdict
leads_by_len = defaultdict(list)
for l in leads_unmatched[['DNI', 'Nombre', 'Correo', 'Correo_low']].to_dict('records'):
    leads_by_len[len(l['Correo_low'])].append(l)

# Búsqueda
nuevos_matches = []
count_new = 0
total_insc = len(insc_unmatched)

for i_idx, (idx, insc) in enumerate(insc_unmatched.iterrows(), 1):
    e_insc = insc['Email_low']
    if len(e_insc) < 5: continue
    if "nan" in e_insc: continue
    
    if i_idx % 500 == 0:
        print(f"  ...Procesando inscriptos: {i_idx}/{total_insc}")
    
    # Nombre para log
    i_name = insc.get('Insc_Apellido y Nombre', insc.get('Apellido y Nombre', ''))
    i_dni = insc.get('Insc_DNI', insc.get('DNI', ''))
    
    L = len(e_insc)
    candidates = leads_by_len.get(L-1, []) + leads_by_len.get(L, []) + leads_by_len.get(L+1, [])
    
    for l in candidates:
        e_lead = l['Correo_low']
        if len(e_lead) < 5: continue
        
        # Si ya lo revisamos en corridas anteriores
        if (e_lead, e_insc) in existing_pairs:
            continue
            
        dist = Levenshtein.distance(e_insc, e_lead)
        if dist == 1:
            nuevos_matches.append({
                'Validado': '',            # Columna para el humano
                'Distancia': dist,
                'Lead_DNI': l.get('DNI', ''),
                'Lead_Nombre': l.get('Nombre', ''),
                'Lead_Correo': l.get('Correo', ''),
                'Insc_DNI': i_dni,
                'Insc_Nombre': i_name,
                'Insc_Correo': insc.get(col_email_insc, '')
            })
            existing_pairs.add((e_lead, e_insc)) # Para no duplicar en la misma corrida
            count_new += 1

if count_new > 0:
    print(f"¡Se hallaron {count_new} nuevos posibles matches de correo!")
    df_nuevos = pd.DataFrame(nuevos_matches)
    df_final = pd.concat([df_existing, df_nuevos], ignore_index=True)
else:
    print("No se encontraron nuevos matches fuzzy.")
    df_final = df_existing

# Guardar
df_final.to_excel(output_excel, index=False)
print(f"Archivo de control guardado en: {output_excel}")
print("Puedes editar la columna 'Validado' indicando 'SI' o 'NO' para dejar constancia humana.")
