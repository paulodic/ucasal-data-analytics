import pandas as pd
import os
import glob

base_dir = r"h:\Test-Antigravity\marketing_report\data\1_raw\inscriptos"
raw_files = glob.glob(os.path.join(base_dir, "*.xlsx"))

total_rows = 0
total_with_comma = 0
total_missing = 0
total_without_comma = 0

print(f"Analizando {len(raw_files)} archivos raw de inscriptos...\n")

for f in raw_files:
    df = pd.read_excel(f)
    if 'Apellido y Nombre' not in df.columns:
        print(f"La columna 'Apellido y Nombre' no existe en {os.path.basename(f)}")
        continue
    
    col = df['Apellido y Nombre']
    missing = col.isna().sum()
    valid_col = col.dropna()
    
    with_comma = valid_col.astype(str).str.contains(',').sum()
    without_comma = len(valid_col) - with_comma
    
    total_missing += missing
    total_with_comma += with_comma
    total_without_comma += without_comma
    total_rows += len(df)
    
    print(f"--- {os.path.basename(f)} ---")
    print(f"Ejemplos CON coma:")
    print(valid_col[valid_col.astype(str).str.contains(',')].head(3).tolist())
    if without_comma > 0:
        print(f"Ejemplos SIN coma:")
        print(valid_col[~valid_col.astype(str).str.contains(',')].head(3).tolist())
    print("\n")

print("========================================")
print("RESUMEN GLOBAL:")
print(f"Total de registros con 'Apellido y Nombre': {total_rows}")
print(f"Registros vacíos/Nulos en este campo: {total_missing}")
print(f"Registros CON formato de coma (Apellido, Nombre): {total_with_comma} ({round((total_with_comma/ (total_rows - total_missing) * 100) if (total_rows - total_missing) > 0 else 0, 2)}%)")
print(f"Registros SIN coma evidente: {total_without_comma} ({round((total_without_comma/ (total_rows - total_missing) * 100) if (total_rows - total_missing) > 0 else 0, 2)}%)")
print("========================================")
