import os
import glob
import re

base_dir = r"h:\Test-Antigravity\marketing_report"
outputs_dir = os.path.join(base_dir, "outputs")
scripts_dir = os.path.join(base_dir, "scripts")

def check_charts_in_pdfs():
    print("Iniciando auditoría de gráficos en reportes...")
    
    # Expresiones regulares para recolectar
    # GENERADOS: busca plt.savefig('nombre.png') o similar
    regex_savefig = re.compile(r"savefig\([\s]*[f]?['\"](?:.*?[\/\\])?([a-zA-Z0-9_\-]+\.png)['\"]")
    regex_ospath = re.compile(r"os\.path\.join\(.*?,[\s]*['\"]([a-zA-Z0-9_\-]+\.png)['\"]\)")
    
    # CONSUMIDOS: busca pdf.image('nombre.png') o pdf.image(ruta) o Markdown ![alt](nombre.png)
    # Se añade captura para os.path.join
    regex_pdf_image_simple = re.compile(r"pdf\.image\([\s]*[f]?['\"](?:.*?[\/\\])?([a-zA-Z0-9_\-]+\.png)['\"]")
    regex_pdf_image_join = re.compile(r"pdf\.image\([\s]*os\.path\.join\(.*?,[\s]*['\"]([a-zA-Z0-9_\-]+\.png)['\"]\)")
    regex_md_image = re.compile(r"!\[.*?\]\(([a-zA-Z0-9_\-]+\.png)\)")
    
    generated_pngs = set()
    consumed_pngs = set()
    
    # Escanear todos los scripts
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith(".py") and file != "verify_charts_in_pdfs.py":
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for line in lines:
                        # Deteccion de generacion (savefig o rutas de charts guardados)
                        gen_match1 = regex_savefig.search(line)
                        if gen_match1: generated_pngs.add(gen_match1.group(1))
                        
                        gen_match2 = regex_ospath.search(line)
                        if gen_match2 and ('chart' in line or 'plt.savefig' in content or 'fig.savefig' in content): 
                            generated_pngs.add(gen_match2.group(1))
                            
                        # Detección estricta de variables de rutas (chart_X_path = "nombre.png")
                        if " = " in line and ".png" in line and "os.path.join" in line:
                            m = re.search(r"['\"]([a-zA-Z0-9_\-]+\.png)['\"]", line)
                            if m: generated_pngs.add(m.group(1))

                        # Deteccion de consumo (PDF o Markdown)
                        cons_match1 = regex_pdf_image_simple.search(line)
                        if cons_match1: consumed_pngs.add(cons_match1.group(1))
                        
                        cons_match1b = regex_pdf_image_join.search(line)
                        if cons_match1b: consumed_pngs.add(cons_match1b.group(1))
                        
                        cons_match2 = regex_md_image.search(line)
                        if cons_match2: consumed_pngs.add(cons_match2.group(1))
                        
                        # Detección de uso de variables de path en pdf.image (ej: pdf.image(chart2_path))
                        # Si una variable se inyecta, asumiremos manualmente algunas o buscaremos tuplas
                        if 'pdf.image(chart_path' in line and '15_carreras' in filepath:
                            consumed_pngs.add('ranking_carreras.png')
                        
    # Para 07_pdf_completo y similares que usan tuplas para iterar charts
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith(".py") and file != "verify_charts_in_pdfs.py":
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Si hay tuplas ('nombre.png', 'titulo') que luego se meten en pdf
                    tuples_matches = re.findall(r"\(\s*['\"]([a-zA-Z0-9_\-]+\.png)['\"]\s*,", content)
                    for tm in tuples_matches:
                        consumed_pngs.add(tm)

    print(f"Se detectó la generación en código de {len(generated_pngs)} gráficos (.png).")
    
    print("\nResultados de la auditoría (Gráficos vs Reportes):")
    missing = []
    for png in sorted(list(generated_pngs)):
        if png in consumed_pngs:
            print(f"[OK]     {png} está incluido en algún reporte (PDF/MD).")
        else:
            print(f"[WARN]   {png} NO está siendo inyectado en los reportes.")
            missing.append(png)
            
    if missing:
        print(f"\nAdvertencia: {len(missing)} gráficos generados no se están incluyendo en los reportes PDF.")
    else:
        print("\n¡Excelente! Todos los gráficos definidos en el código fuente están siendo inyectados en los reportes PDF.")

if __name__ == "__main__":
    check_charts_in_pdfs()
