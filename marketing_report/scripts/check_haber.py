import pandas as pd
import glob
import os

base_dir = r"h:\Test-Antigravity\marketing_report\data\1_raw\inscriptos"
f = glob.glob(os.path.join(base_dir, "*.xlsx"))[0]

print(f"Abriendo archivo de inscriptos: {os.path.basename(f)}")
df = pd.read_excel(f)

if 'Haber' in df.columns:
    print("Columna 'Haber' encontrada.")
    haber_col = df['Haber'].dropna()
    print(f"Tipo de dato: {haber_col.dtype}")
    print("Muestra de los primeros 10 valores:")
    print(haber_col.head(10).tolist())
    
    # Check if there are commas as decimals (European/Argentine style) or dots
    # But since it's read by pd.read_excel, it might already be float
else:
    print("LA COLUMNA 'Haber' NO EXISTE. Columnas disponibles:")
    print(df.columns.tolist())
