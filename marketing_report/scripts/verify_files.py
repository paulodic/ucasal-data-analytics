import os

base_dir = r"h:\Test-Antigravity\marketing_report\outputs"
segmentos = ["Grado_Pregrado", "Cursos", "Posgrados"]

reportes_esperados = {
    "Informe_Analitico": ["Informe_Analitico_Marketing_Completo.pdf", "Informe_Analitico_Marketing_Completo.md"],
    "Reporte_Promociones": ["18_grafica_inscripciones_dias_semana.png", "18_reporte_promociones.md", "18_tabla_promociones.csv"],
    "Reporte_Asesores": ["17_reporte_asesores.pdf", "17_reporte_asesores.md", "17_ranking_asesores.csv", "17_informe_estados_asesor.csv", "17_ranking_vendedores_inscriptos.csv"],
    "Analisis_CRM": ["auditoria_crm_matriculadas.pdf", "16_analisis_matriculadas.md", "16_Falsos_Positivos_CRM.csv", "16_Inscriptos_Sin_Lead.csv"]
}

missing_files = []

for segmento in segmentos:
    print(f"\n--- Verificando segmento: {segmento} ---")
    
    for reporte, archivos in reportes_esperados.items():
        # Promociones apply only to Grado_Pregrado
        if reporte == "Reporte_Promociones" and segmento != "Grado_Pregrado":
            continue
            
        dir_path = os.path.join(base_dir, segmento, reporte)
        if not os.path.exists(dir_path):
            print(f"[!] Faltó carpeta entera de reporte: {dir_path}")
            missing_files.append(dir_path)
            continue
            
        for archivo in archivos:
            filepath = os.path.join(dir_path, archivo)
            if not os.path.exists(filepath):
                print(f"[X] Faltante: {archivo} (en {reporte})")
                missing_files.append(filepath)
            else:
                pass # print(f"[OK] Encontrado: {archivo}")
                
if not missing_files:
    print("\n✅ VERIFICACIÓN EXITOSA: Todos los informes contienen sus componentes originales (.md, .pdf, .csv, gráficas) en sus respectivas carpetas por segmento.")
else:
    print(f"\n❌ SE ENCONTRARON {len(missing_files)} ARCHIVOS FALTANTES.")
