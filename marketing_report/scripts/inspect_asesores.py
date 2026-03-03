import pandas as pd
import os

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir_base = os.path.join(base_dir, "outputs", "Data_Base")
leads_csv = os.path.join(output_dir_base, "reporte_marketing_leads_completos.csv")

try:
    df = pd.read_csv(leads_csv, usecols=['Estado', 'Consulta: Nombre del propietario', 'ColaNombre', 'Sede Nombre'], low_memory=False)
    print("--- ESTADOS ---")
    print(df['Estado'].value_counts().head(10))
    print("\n--- PROPIETARIOS (TOP 30) ---")
    print(df['Consulta: Nombre del propietario'].value_counts().head(30))
    print("\n--- COLAS (TOP 20) ---")
    print(df['ColaNombre'].value_counts().head(20))
    print("\n--- SEDES (TOP 20) ---")
    print(df['Sede Nombre'].value_counts().head(20))
except Exception as e:
    print(f"Error: {e}")
