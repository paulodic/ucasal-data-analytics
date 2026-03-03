import pandas as pd
import os

base_dir = r"h:\Test-Antigravity\marketing_report"
inscriptos_csv = os.path.join(base_dir, "outputs", "Data_Base", "reporte_marketing_inscriptos_origenes.csv")

df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

date_col = 'Insc_Fecha Aplicación' if 'Insc_Fecha Aplicación' in df_insc.columns else 'Insc_Fecha Pago' if 'Insc_Fecha Pago' in df_insc.columns else None

if date_col:
    df_insc['Fecha_Clean'] = pd.to_datetime(df_insc[date_col], dayfirst=True, errors='coerce')
    print("Mínima fecha:", df_insc['Fecha_Clean'].min())
    print("Máxima fecha:", df_insc['Fecha_Clean'].max())
    
    print("\nDistribución por Año:")
    print(df_insc['Fecha_Clean'].dt.year.value_counts())
    
    print("\nDistribución por Mes (Todos los años):")
    print(df_insc['Fecha_Clean'].dt.to_period('M').value_counts().sort_index())
else:
    print("No date col")
