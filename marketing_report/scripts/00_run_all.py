import os
import subprocess
import sys

base_dir = r"h:\Test-Antigravity\marketing_report\scripts"

# Segmentos definidos en 02_cruce_datos.py
segmentos = ["Grado_Pregrado", "Cursos", "Posgrados"]

# Scripts que se ejecutan UNA vez por segmento (reciben el nombre del segmento como argumento)
scripts_analiticos = [
    "03_journey_sankey.py",
    "16_analisis_matriculadas.py",
    "18_analisis_promociones.py",  # solo Grado_Pregrado
    "17_reporte_asesores.py",
    "04_reporte_final.py",
    "07_pdf_completo.py",
    "09_utm_conversion.py",
    "10_google_ads_deep_dive.py",
    "13_facebook_deep_dive.py",
    "14_bot_deep_dive.py",
    "11_exportar_tablas_excel.py",
    "05_mapeo_y_reportes.py",
    "08_tabla_utm.py",
    "12_analisis_no_matcheados.py",
]

# Scripts que se ejecutan UNA sola vez (sin argumento de segmento, datos globales)
scripts_globales = [
    "19_bot_consolidado.py",
    "06_sankeys_extras.py",
    "08_fuzzy_correos.py",
    "15_dominios_invalidos.py",
    "15_carreras.py",
    "generate_eda_pdf.py",
]

def run_script(script_path, args=None, label=""):
    cmd = ["python", script_path] + (args or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   [!] Error en {label}. Logs:")
        print(result.stderr[-2000:] if result.stderr else "")
        print(result.stdout[-500:] if result.stdout else "")
    else:
        print(f"   [ok] Procesado correctamente.")

print("Iniciando Compilación Maestra de Reportes Académicos...")

# =========================================================
# FASE 1: Scripts por segmento
# =========================================================
for segmento in segmentos:
    print(f"\n" + "="*50)
    print(f" CONSTRUYENDO SUITE: {segmento.upper()}")
    print("="*50)

    db_path = os.path.join(r"h:\Test-Antigravity\marketing_report\outputs", "Data_Base", segmento, "reporte_marketing_inscriptos_origenes.csv")
    if not os.path.exists(db_path):
        print(f"No existe la base de datos para '{segmento}'. Se omitirá.")
        continue

    for script_name in scripts_analiticos:
        if script_name == "18_analisis_promociones.py" and segmento != "Grado_Pregrado":
            print(f" > Omitiendo: {script_name} (Solo Grado_Pregrado)")
            continue

        script_path = os.path.join(base_dir, script_name)
        if os.path.exists(script_path):
            print(f" > Ejecutando: {script_name}...")
            run_script(script_path, args=[segmento], label=script_name)
        else:
            print(f"   [?] Script {script_name} no encontrado.")

# =========================================================
# FASE 2: Scripts globales (sin segmento)
# =========================================================
print(f"\n" + "="*50)
print(f" SCRIPTS GLOBALES (sin segmento)")
print("="*50)

for script_name in scripts_globales:
    script_path = os.path.join(base_dir, script_name)
    if os.path.exists(script_path):
        print(f" > Ejecutando: {script_name}...")
        run_script(script_path, label=script_name)
    else:
        print(f"   [?] Script {script_name} no encontrado.")

print("\n>>> PIPELINE COMPLETADO EXITOSAMENTE PARA TODAS LAS RAMAS. <<<")
