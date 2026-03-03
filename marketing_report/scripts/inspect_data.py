import pandas as pd
import glob
import os

base_dir = r"h:\Test-Antigravity\marketing_report\data\1_raw"
leads_files = glob.glob(os.path.join(base_dir, "leads_salesforce", "*.xlsx"))
inscriptos_files = glob.glob(os.path.join(base_dir, "inscriptos", "*.xlsx"))

print(f"Encontrados {len(leads_files)} archivos de leads y {len(inscriptos_files)} de inscriptos.")

if leads_files:
    try:
        df_leads = pd.read_excel(leads_files[0], nrows=5)
        print("\n--- LEADS COLUMNAS (Archivo: {}) ---".format(os.path.basename(leads_files[0])))
        print(df_leads.columns.tolist())
    except Exception as e:
        print("Error leyendo leads:", e)

if inscriptos_files:
    try:
        df_inscriptos = pd.read_excel(inscriptos_files[0], nrows=5)
        print("\n--- INSCRIPTOS COLUMNAS (Archivo: {}) ---".format(os.path.basename(inscriptos_files[0])))
        print(df_inscriptos.columns.tolist())
    except Exception as e:
        print("Error leyendo inscriptos:", e)
