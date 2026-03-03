import pandas as pd
import os
import glob

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs")

# Ya que tenemos el DataFrame original in memory de cruce_datos "df_final_leads" si corremos allí,
# O dado que guardó el file Inscriptos correctamente, pero leads se dañó, probamos cargar lo que se pueda.
# COMO el script original de matplotlib dio error durante la carga, los archivos quizás estén rotos.
# Vamos a ejecutar una lógica rápida de export que parchee el bug del CRC.

def convert_xlsx_to_csv():
    for f in glob.glob(os.path.join(output_dir, "*.xlsx")):
        print(f"Verificando {f}...")
        try:
            df = pd.read_excel(f, engine='openpyxl')
            csv_path = f.replace(".xlsx", ".csv")
            df.to_csv(csv_path, index=False)
            print(f"OK -> Guardado {csv_path}")
        except Exception as e:
            print(f"ERROR LEYENDO {f}: {e}")

if __name__ == '__main__':
    convert_xlsx_to_csv()
