import os
import subprocess
import sys

base_dir = r"h:\Test-Antigravity\marketing_report\scripts"

# Segmentos definidos en 02_cruce_datos.py
segmentos = ["Grado_Pregrado", "Cursos", "Posgrados"]

# Lista ordenada de los scripts analíticos que construyen los reportes PDF/MD/XLSX
scripts_analiticos = [
    "03_journey_sankey.py",
    "16_analisis_matriculadas.py",
    "18_analisis_promociones.py",
    "17_reporte_asesores.py",
    "04_reporte_final.py",
    "07_pdf_completo.py",
    "09_utm_conversion.py",
    "10_google_ads_deep_dive.py",
    "13_facebook_deep_dive.py",
    "14_bot_deep_dive.py"
]

print("Iniciando Compilación Maestra de Reportes Académicos...")

for segmento in segmentos:
    print(f"\n" + "="*50)
    print(f" CONSTRUYENDO SUITE: {segmento.upper()}")
    print("="*50)
    
    # 1. Asegurarnos que la base de datos de ese segmento exista antes de correr todo
    db_path = os.path.join(r"h:\Test-Antigravity\marketing_report\outputs", "Data_Base", segmento, "reporte_marketing_inscriptos_origenes.csv")
    if not os.path.exists(db_path):
        print(f"No existe la base de datos física para la rama '{segmento}'. Se omitirá.")
        continue
    
    # 2. Correr los reports
    for script_name in scripts_analiticos:
        if script_name == "18_analisis_promociones.py" and segmento != "Grado_Pregrado":
            print(f" > Omitiendo: {script_name} (Aplica solo a Grado y Pregrado)")
            continue
            
        script_path = os.path.join(base_dir, script_name)
        if os.path.exists(script_path):
            print(f" > Ejecutando: {script_name}...")
            result = subprocess.run(["python", script_path, segmento], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   [!] Error detectado en {script_name}. Logs:")
                print(result.stderr)
                print(result.stdout)
            else:
                print(f"   [ok] Procesado correctamente.")
        else:
            print(f"   [?] Script {script_name} no encontrado en /scripts/.")

print("\n>>> PIPELINE COMPLETADO EXITOSAMENTE PARA TODAS LAS RAMAS. <<<")
