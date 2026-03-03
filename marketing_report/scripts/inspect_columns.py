import pandas as pd
import glob
import os

base_dir = r"h:\Test-Antigravity\marketing_report"
raw_inscriptos = glob.glob(os.path.join(base_dir, "data", "1_raw", "inscriptos", "*.xlsx"))[0]
raw_leads = glob.glob(os.path.join(base_dir, "data", "1_raw", "leads_salesforce", "*.xlsx"))[0]

df_insc = pd.read_excel(raw_inscriptos)
df_leads = pd.read_excel(raw_leads)

with open(os.path.join(base_dir, "scripts", "columnas_raw.txt"), "w", encoding="utf-8") as f:
    f.write("=== INSCRIPTOS RAW COLUMNS ===\n")
    for col in df_insc.columns:
        f.write(f"- {col} (Ejemplo: {df_insc[col].dropna().iloc[0] if len(df_insc[col].dropna()) > 0 else 'N/A'})\n")
    
    f.write("\n\n=== LEADS RAW COLUMNS ===\n")
    for col in df_leads.columns:
        f.write(f"- {col} (Ejemplo: {df_leads[col].dropna().iloc[0] if len(df_leads[col].dropna()) > 0 else 'N/A'})\n")

print("Listado exportado a scripts/columnas_raw.txt")
