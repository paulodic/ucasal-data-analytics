import pandas as pd
df = pd.read_csv(r"h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv", low_memory=False)
print(df['Consulta: Nombre del propietario'].value_counts().head(20))
print("===")
print(df['Estado'].value_counts().head(10))
