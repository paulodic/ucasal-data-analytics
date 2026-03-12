"""
09_utm_conversion.py
Análisis profundo de conversión UTM por segmento.

Desglosa leads e inscriptos por cada campo UTM (Source, Campaign, Medium, Term,
Content), genera gráficos de barras horizontales con tasas de conversión, y
compila todo en un PDF + Excel detallado.

ENTRADA:
  - outputs/Data_Base/<Segmento>/reporte_marketing_leads_completos.csv
  - outputs/Data_Base/<Segmento>/reporte_marketing_inscriptos_origenes.csv
SALIDA (outputs/<Segmento>/Analisis_UTM/):
  - analisis_utm_completo.xlsx     -> Tablas por campo UTM
  - Analisis_UTM_Conversion.pdf    -> PDF con gráficos y tablas
"""
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

sns.set_theme(style="whitegrid")

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Analisis_UTM")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Cargando datos...")
df = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

def get_max_date(df_i):
    meses = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio", 
             7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}
    for col in ['Insc_Fecha Pago', 'Insc_Fecha Aplicación', 'Fecha Pago', 'Fecha Aplicación']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], errors='coerce', dayfirst=True)
            if not dates.isna().all():
                d = dates.max()
                return f"{d.day} de {meses[d.month]} de {d.year}"
    d = datetime.now()
    return f"{d.day} de {meses[d.month]} de {d.year}"

max_date_str = get_max_date(df_insc)

def classify(v):
    s = str(v)
    if 'Exacto' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

df['_mc'] = df['Match_Tipo'].apply(classify)
df_main = df[df['_mc'] != 'fuzzy'].copy()

# Limpiar UTMs
utm_cols = ['UtmSource', 'UtmCampaign', 'UtmMedium', 'UtmTerm', 'UtmContent']
for col in utm_cols:
    if col in df_main.columns:
        df_main[col] = df_main[col].astype(str).replace('nan', '').str.strip()

# Deduplicar por persona
df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

# Filtrar: cualquier UTM no vacio
mask_utm = (df_main['UtmSource'] != '') | (df_main['UtmCampaign'] != '') | \
           (df_main['UtmMedium'] != '') | (df_main['UtmTerm'] != '') | (df_main['UtmContent'] != '')
df_utm = df_main[mask_utm].copy()
df_utm_dedup = df_utm.drop_duplicates(subset='_pk')

total_utm = len(df_utm_dedup)

# REGLA DE NEGOCIO COHORTES (Muestra para Conversión)
if segmento == 'Grado_Pregrado':
    df_main['Fecha_Limpia'] = pd.to_datetime(df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_main_conv = df_main[df_main['Fecha_Limpia'] >= '2025-09-01'].copy()
else:
    df_main_conv = df_main.copy()

mask_utm_conv = (df_main_conv['UtmSource'] != '') | (df_main_conv['UtmCampaign'] != '') | \
                (df_main_conv['UtmMedium'] != '') | (df_main_conv['UtmTerm'] != '') | (df_main_conv['UtmContent'] != '')
df_utm_conv = df_main_conv[mask_utm_conv].copy()
df_utm_dedup_conv = df_utm_conv.drop_duplicates(subset='_pk')

total_utm_conv = len(df_utm_dedup_conv)
conv_utm = len(df_utm_dedup_conv[df_utm_dedup_conv['_mc'] == 'exacto'])
tasa_utm = (conv_utm / total_utm_conv * 100) if total_utm_conv > 0 else 0

print(f"Personas con algun UTM: {total_utm:,} | Convertidos: {conv_utm:,} | Tasa: {tasa_utm:.2f}%")

# ==========================================
# FUNCION PARA GENERAR TABLA Y GRAFICO POR CAMPO UTM
# ==========================================
def analizar_utm(df_data, df_dedup, df_dedup_conv, campo, top_n=15, min_personas=10):
    """Genera tabla y grafico para un campo UTM"""
    df_f = df_dedup[df_dedup[campo] != ''].copy()
    if len(df_f) == 0: return pd.DataFrame(), None
    
    # 1. Volumen histórico
    tabla_vol = df_f.groupby(campo).agg(
        Personas=('_pk', 'nunique'),
    ).reset_index()
    
    # 2. Volumen y conversión en la muestra
    df_f_conv = df_dedup_conv[df_dedup_conv[campo] != ''].copy()
    if len(df_f_conv) > 0:
        tabla_conv = df_f_conv.groupby(campo).agg(
            Personas_Muestra=('_pk', 'nunique'),
            Inscriptos=('_mc', lambda x: (x == 'exacto').sum()),
        ).reset_index()
    else:
        tabla_conv = pd.DataFrame(columns=[campo, 'Personas_Muestra', 'Inscriptos'])
    
    # Consolidar
    tabla = pd.merge(tabla_vol, tabla_conv, on=campo, how='outer').fillna(0)
    
    consultas = df_data[df_data[campo] != ''].groupby(campo).size().reset_index(name='Consultas')
    tabla = tabla.merge(consultas, on=campo, how='left')
    tabla['Tasa_%'] = (tabla['Inscriptos'] / tabla['Personas_Muestra'] * 100).round(2)
    # Llenar nulos
    tabla.loc[tabla['Personas_Muestra'] == 0, 'Tasa_%'] = 0.0
    tabla = tabla.sort_values('Personas', ascending=False)
    
    # Grafico 1: Volumen
    top = tabla.head(top_n).copy()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top, y=campo, x='Personas', palette='Blues_r')
    plt.title(f'Volumen: Top {top_n} {campo}')
    plt.xlabel('Personas Unicas')
    for i, v in enumerate(top['Personas'].values):
        plt.text(v + 5, i, f'{int(v):,}', va='center', fontsize=8)
    plt.tight_layout()
    path_vol = os.path.join(output_dir, f"chart_vol_{campo.lower()}.png")
    plt.savefig(path_vol, bbox_inches='tight', dpi=150)
    plt.close()

    # Grafico 2: Conversion (basado en la muestra)
    top_conv = tabla[tabla['Personas_Muestra'] >= min_personas].sort_values('Tasa_%', ascending=False).head(top_n)
    plt.figure(figsize=(12, 6))
    colors_conv = ['#2ecc71' if t > tasa_utm else '#e74c3c' for t in top_conv['Tasa_%'].values]
    sns.barplot(data=top_conv, y=campo, x='Tasa_%', palette=colors_conv)
    plt.title(f'Conversion: Top {top_n} {campo} (min. {min_personas} pers.)')
    plt.xlabel('% Conversion')
    plt.axvline(x=tasa_utm, color='gray', linestyle='--', alpha=0.7, label=f'Promedio UTM: {tasa_utm:.1f}%')
    plt.legend(fontsize=8)
    for i, v in enumerate(top_conv['Tasa_%'].values):
        plt.text(v + 0.1, i, f'{v:.1f}%', va='center', fontsize=8)
    plt.tight_layout()
    path_conv = os.path.join(output_dir, f"chart_rate_{campo.lower()}.png")
    plt.savefig(path_conv, bbox_inches='tight', dpi=150)
    plt.close()
    
    return tabla, {'vol': path_vol, 'rate': path_conv}

# ==========================================
# GENERAR PARA CADA CAMPO UTM
# ==========================================
resultados = {}
for campo in ['UtmSource', 'UtmCampaign', 'UtmMedium']:
    print(f"\nAnalizando {campo}...")
    tabla, charts = analizar_utm(df_utm, df_utm_dedup, df_utm_dedup_conv, campo)
    if not tabla.empty:
        resultados[campo] = {'tabla': tabla, 'charts': charts}
        print(f"  -> {len(tabla)} valores distintos")

# UtmTerm y UtmContent si tienen datos
for campo in ['UtmTerm', 'UtmContent']:
    df_check = df_utm_dedup[df_utm_dedup[campo] != '']
    if len(df_check) > 50:
        print(f"\nAnalizando {campo}...")
        tabla, charts = analizar_utm(df_utm, df_utm_dedup, df_utm_dedup_conv, campo, top_n=10, min_personas=5)
        if not tabla.empty:
            resultados[campo] = {'tabla': tabla, 'charts': charts}
            print(f"  -> {len(tabla)} valores distintos")

# ==========================================
# EXPORTAR TODO A EXCEL (multiples hojas)
# ==========================================
xlsx_all = os.path.join(output_dir, "analisis_utm_completo.xlsx")
with pd.ExcelWriter(xlsx_all, engine='openpyxl') as writer:
    for campo, data in resultados.items():
        data['tabla'].to_excel(writer, sheet_name=campo, index=False)
    
    # Hoja resumen
    resumen = pd.DataFrame({
        'Campo UTM': list(resultados.keys()),
        'Valores Distintos': [len(r['tabla']) for r in resultados.values()],
        'Total Personas': [int(r['tabla']['Personas'].sum()) for r in resultados.values()],
        'Total Inscriptos': [int(r['tabla']['Inscriptos'].sum()) for r in resultados.values()],
    })
    resumen.to_excel(writer, sheet_name='Resumen', index=False)

print(f"\n-> Excel completo: {xlsx_all}")

# ==========================================
# EXPORTAR TEXTOS A MARKDOWN
# ==========================================
md_path = os.path.join(output_dir, "Analisis_UTM_Conversion.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"# Analisis de Conversion por UTM\n\n*(Datos actualizados al {max_date_str})*\n\n")
    f.write("Tasas de conversion para todos los campos UTM no vacios.\n\n")
    if segmento == 'Grado_Pregrado':
        f.write("*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2024, coincidiendo con la inscripcion a la primera cohorte. En mayo se abren a la segunda.)*\n\n")
    f.write("## Metrica Global UTM\n")
    f.write(f"- Personas con algun UTM (Histórico): {total_utm:,}\n")
    f.write(f"- Personas con algun UTM (Muestra Conversión): {total_utm_conv:,}\n")
    f.write(f"- Inscriptos (exacto - en Muestra): {conv_utm:,}\n")
    f.write(f"- Tasa de Conversion UTM Global (Muestra): {tasa_utm:.2f}%\n")
print(f"-> Textos exportados a MD: {md_path}\n")

# ==========================================
# GENERAR PDF CON TODOS LOS GRAFICOS Y TABLAS
# ==========================================
print("Generando PDF de analisis UTM completo...")

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Analisis de Conversion por UTM', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_text_color(0, 0, 0)
        self.ln(1)
    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, f'Pag. {self.page_no()}/{{nb}}', new_x="LMARGIN", new_y="NEXT", align='C')

pdf = PDF('L')
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)

# Portada
pdf.add_page()
pdf.set_font('Helvetica', 'B', 22)
pdf.ln(30)
pdf.cell(0, 14, 'Analisis de Conversion por UTM', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(5)
pdf.set_font('Helvetica', '', 12)
pdf.cell(0, 10, f'Tasas de conversion para todos los campos UTM no vacios (al {max_date_str})', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(5)
pdf.set_font('Helvetica', 'I', 8)
pdf.multi_cell(0, 4,
    'Modelo: Deduplicado por persona (DNI) dentro de cada valor UTM. Match: Exacto (DNI/Email/Telefono/Celular). '
    'Any-Touch: ver Informe Analitico (04) para inscriptos que consultaron por multiples canales.')
pdf.ln(5)

# Resumen global
pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
pdf.cell(140, 9, '  Metrica Global UTM', border=1, fill=True)
pdf.cell(60, 9, '  Valor', border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.set_font('Helvetica', '', 9)

if segmento == 'Grado_Pregrado':
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 6, "Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads desde Septiembre 2024.", ln=True)
    pdf.set_font("Helvetica", '', 9)

rows = [
    ('Personas con algun UTM (Histórico)', f'{total_utm:,}'),
    ('Personas con algun UTM (Muestra)', f'{total_utm_conv:,}'),
    ('Inscriptos (exacto - Muestra)', f'{conv_utm:,}'),
    ('Tasa de Conversion UTM Global', f'{tasa_utm:.2f}%'),
]
for label, val in rows:
    pdf.cell(140, 7, f'  {label}', border=1)
    pdf.cell(60, 7, f'  {val}', border=1, new_x="LMARGIN", new_y="NEXT")

# Graficos por campo
for campo, data in resultados.items():
    # Pagina 1: Volumen
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(52, 73, 94)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'  {campo} - Volumen', new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    if os.path.exists(data['charts']['vol']):
        pdf.image(data['charts']['vol'], x='C', w=260, h=160, keep_aspect_ratio=True)
    
    # Pagina 2: Tasa de Conversion
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(52, 73, 94)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'  {campo} - Tasa de Conversion', new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    if os.path.exists(data['charts']['rate']):
        pdf.image(data['charts']['rate'], x='C', w=260, h=160, keep_aspect_ratio=True)
    
    # Tabla top 20
    tabla = data['tabla'].head(20)
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, f'Tabla: Top 20 {campo}', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(2)
    
    col_w = [90, 25, 25, 25, 25, 10]
    headers = [campo, 'Consultas', 'Pers.(H)', 'Pers.(M)', 'Inscrip.', 'Conv. %']
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, h, border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 7)
    
    top_table = tabla.head(20) if isinstance(tabla, pd.DataFrame) else tabla
    for idx, r in enumerate(top_table.itertuples()):
        row = r._asdict()
        if idx % 2 == 0:
            pdf.set_fill_color(240, 248, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w[0], 6, str(row[campo])[:55], border=1, fill=True)
        pdf.cell(col_w[1], 6, f"{int(row['Consultas']):,}", border=1, fill=True, align='R')
        pdf.cell(col_w[2], 6, f"{int(row['Personas']):,}", border=1, fill=True, align='R')
        pdf.cell(col_w[3], 6, f"{int(row.get('Personas_Muestra', 0)):,}", border=1, fill=True, align='R')
        pdf.cell(col_w[4], 6, f"{int(row['Inscriptos']):,}", border=1, fill=True, align='R')
        tasa_val = row.get('Tasa_Conversion_%', row.get('Tasa_%', 0.0))
        pdf.cell(col_w[5], 6, f"{tasa_val:.2f}%", border=1, fill=True, align='R')
        pdf.ln()

# Nota Metodologica
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Nota Metodologica', new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.set_font('Helvetica', '', 9)
pdf.multi_cell(0, 5,
    'Cruce de datos: Deduplicado por persona (DNI). Match exacto por DNI, Email, Telefono y Celular.\n'
    'Modelo Any-Touch: Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). '
    'Detalle en el Informe Analitico (04_reporte_final).\n'
    'Fuente: Consultas exportadas de Salesforce, inscriptos del sistema academico.')

pdf_path = os.path.join(output_dir, "Analisis_UTM_Conversion.pdf")
pdf.output(pdf_path)
print(f"\n-> PDF UTM Conversion: {pdf_path}")
print("Listo!")

# Memoria Técnica
memoria_utm = """# Memoria Técnica: Análisis de Conversión UTM

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión Global:** Cualquier Lead que registre un valor no nulo ni vacío en al menos una de las dimensiones de rastreo estandar (Source, Medium, Campaign, Term, Content). Se unifican todas en minúsculas para eliminar duplicidades lógicas (ej. 'Instagram' vs 'instagram').
- **Deduplicación:** Se aglutina a la persona por su Documento Nacional de Identidad (`DNI`) para medir "Personas Únicas", utilizando el Correo Electrónico como comodín secundario de clave primaria para aquellos leads capturados tempranamente sin DNI.
- **Tasa de Conversión Pura:** La fórmula ejecutada se remite a aislar de un clúster UTM las Personas Únicas, dividir dentro de ellas las conversiones de Match "Exacto" en Inscriptos Base General, y eliminar los Fuzzys para atribuir métricas fiables ajenas al ruido humano de facturación.
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria_utm)

