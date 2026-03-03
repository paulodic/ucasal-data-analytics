import pandas as pd
import glob
import os

try:
    print("Leyendo archivo original de inscriptos...")
    base_dir = r"h:\Test-Antigravity\marketing_report"
    raw_dir = os.path.join(base_dir, "data", "1_raw", "inscriptos")
    f = glob.glob(os.path.join(raw_dir, "*.xlsx"))[0]
    df = pd.read_excel(f)
    print(f"Total registros cargados: {len(df)}")
    
    date_col = 'Fecha Pago' if 'Fecha Pago' in df.columns else 'Fecha'
    
    if date_col in df.columns:
        df['FP_Clean'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        meses = df['FP_Clean'].dt.to_period('M').value_counts().sort_index()
        print("\n--- DISTRIBUCIÓN POR MES EN EL EXCEL ORIGINAL ---")
        print(meses)
        
        sept = df[(df['FP_Clean'] >= '2025-09-01') & (df['FP_Clean'] <= '2025-09-30')]
        print(f"\nTotal inscriptos pagados en Septiembre 2025: {len(sept)}")
    else:
        print("No se encontró columna de fecha en el raw.")
except Exception as e:
    print(e)
