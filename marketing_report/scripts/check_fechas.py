import pandas as pd

try:
    df = pd.read_csv('h:/Test-Antigravity/marketing_report/outputs/Data_Base/Grado_Pregrado/reporte_marketing_leads_completos.csv', low_memory=False, usecols=['Consulta: Fecha de creación'])
    df = df.dropna()
    print("Head Original:")
    print(df.head(10))
    print("\nParseo Automático (dayfirst=False):")
    p1 = pd.to_datetime(df['Consulta: Fecha de creación'], errors='coerce')
    print(p1.head(10))
    print("\nParseo Forzado (dayfirst=True):")
    p2 = pd.to_datetime(df['Consulta: Fecha de creación'], dayfirst=True, errors='coerce')
    print(p2.head(10))
    print("\nFechas en Diciembre con dayfirst=True:")
    mask12 = p2.dt.month == 12
    print(df[mask12].head())
    print("\nFechas en Enero con dayfirst=True:")
    mask1 = p2.dt.month == 1
    print(df[mask1].head())
except Exception as e:
    print(f"Error: {e}")
