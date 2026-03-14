import os
import textwrap
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Analisis Exploratorio de Datos (EDA) y Resolucion de Anomalias', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf():
    # El archivo origen (Artefacto MD de Gemini que actua como fuente de verdad)
    md_file = r'C:\Users\Paulo\.gemini\antigravity\brain\31c83128-f29d-4b23-9261-3273ffb5adad\EDA_Anomalies_Ads_Integration.md'
    # Destino físico en la carpeta root del marketing report o en reportes
    output_dir = r'h:\Test-Antigravity\marketing_report\outputs\General'
    pdf_out = os.path.join(output_dir, 'EDA_Anomalies_Report.pdf')

    if not os.path.exists(md_file):
        print("El artefacto EDA MarkDown no existe en la ruta esperada.")
        return

    with open(md_file, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    for linea in lineas:
        linea = linea.strip()
        
        # Eliminar asteriscos de markdown
        linea = linea.replace('**', '').replace('*', '').replace('`', '').replace('>', '').replace('---', '')

        if linea.startswith('#') or linea.startswith('##') or linea.startswith('###'):
            pdf.set_font('Arial', 'B', 12)
            titulo = linea.replace('#', '').strip()
            # Envolvemos el título si es largo
            wrapped = textwrap.fill(titulo, width=80)
            for chunk in wrapped.split('\n'):
                pdf.cell(0, 8, chunk.encode('latin-1', 'replace').decode('latin-1'), ln=1)
        elif linea == "":
            pdf.ln(2)
        else:
            pdf.set_font('Arial', '', 10)
            wrapped = textwrap.fill(linea, width=105) # 105 caracteres aprox entran cómodos en A4
            for chunk in wrapped.split('\n'):
                pdf.cell(0, 6, chunk.encode('latin-1', 'replace').decode('latin-1'), ln=1)


    pdf.output(pdf_out)
    print(f"Reporte EDA PDF físico generado exitosamente en: {pdf_out}")

if __name__ == '__main__':
    generar_pdf()
