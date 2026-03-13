"""
17_reporte_asesores.py
Analiza el volumen de leads y conversiones por asesor/propietario del CRM.
Segmenta en: Asesores UCASAL (Central) | Sedes / Delegaciones | Sistemas.

SALIDA (output_dir = outputs/{segmento}/Reporte_Asesores/):
  - 17_reporte_asesores.pdf            -> Informe visual multi-página
  - 17_reporte_asesores.xlsx           -> Datos consolidados (4 hojas)
  - 17_reporte_asesores.md             -> Documentacion textual (top rankings)
  - memoria_tecnica.md                 -> Metadata del proceso
  - chart_volumen_grupos.png           -> Leads por grupo de asesores
  - chart_estados_grupos.png           -> Distribucion de estados por grupo
  - chart_ranking_inscriptos.png       -> Top 20 asesores por inscriptos
  - chart_ranking_vendedores.png       -> Top 20 vendedores financieros
  - chart_ranking_empresas.png         -> Top 20 empresas (si existe columna)
  - chart_origen_inscriptos_pie.png    -> Pie chart origen de inscriptos
"""
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

import locale
# Intentar setear locale para formateo de moneda; fallback a formateo manual si falla
try:
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass

def formato_pesos_arg(valor):
    """Formatea un número a formato moneda Argentina $ 1.234,56"""
    try:
        if pd.isna(valor):
            return "$ 0,00"
        # Usamos format con separador de miles y luego reemplazamos
        s = f"{valor:,.2f}"
        s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"$ {s}"
    except:
        return f"$ {valor}"

import sys

# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir_base = os.path.join(base_dir, "outputs", segmento, "Reporte_Asesores")
os.makedirs(output_dir_base, exist_ok=True)
leads_csv = os.path.join(base_dir, "outputs", "Data_Base", segmento, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_dir, "outputs", "Data_Base", segmento, "reporte_marketing_inscriptos_origenes.csv")

print("Generando Reporte de Asesores por Estado del Lead...")

# ============================================================
# CARGA Y CLASIFICACIÓN DE ASESORES
# ============================================================
df = pd.read_csv(leads_csv, low_memory=False)

# Normalizar columnas clave
df['Propietario'] = df['Consulta: Nombre del propietario'].fillna('Sin Asignar').astype(str)
df['Estado'] = df['Estado'].fillna('No Especificado').astype(str)

# Clasificar asesor en grupo: la nomenclatura de colas en Salesforce diferencia
# central (nombre de persona) vs sedes (contienen "sede" o "delegacion")
def clasificar_asesor(nombre):
    nombre_lower = nombre.lower()
    if 'sede' in nombre_lower or 'delegacion' in nombre_lower or 'delegación' in nombre_lower:
        return 'Sedes / Delegaciones'
    elif nombre == 'Sin Asignar' or 'automatizad' in nombre_lower or 'bot' in nombre_lower:
        return 'Sistemas / Automatizado'
    else:
        # Nombres de pila normales y colas oficiales centrales
        return 'Asesores UCASAL (Central)'

df['Grupo_Asesor'] = df['Propietario'].apply(clasificar_asesor)

# ============================================================
# MÉTRICAS MACRO
# ============================================================
# Distribución de estados por grupo de asesor
grupo_estado = df.groupby(['Grupo_Asesor', 'Estado']).size().reset_index(name='Cantidad')

# Analisis Estadistico Adicional (Contact Center y Estados Globales)
total_leads_macro = len(df)
estados_globales = df['Estado'].value_counts().reset_index()
estados_globales.columns = ['Estado', 'Cantidad']
estados_globales['Porcentaje'] = (estados_globales['Cantidad'] / total_leads_macro) * 100

volumen_contact_center = len(df[df['Propietario'].str.contains('Contact Center', case=False, na=False)])
pct_contact_center = (volumen_contact_center / total_leads_macro) * 100 if total_leads_macro > 0 else 0
volumen_abiertos = len(df[df['Estado'] == 'Abierto'])
pct_abiertos = (volumen_abiertos / total_leads_macro) * 100 if total_leads_macro > 0 else 0

# ============================================================
# GRÁFICOS PNG
# ============================================================
# Gráfica 1: volumen total de leads por grupo de asesores
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='Grupo_Asesor', order=df['Grupo_Asesor'].value_counts().index, palette='crest')
plt.title('Volumen Total de Leads asignados por Grupo de Asesores')
plt.ylabel('Cantidad de Leads')
plt.xlabel('')
plt.tight_layout()
chart1_path = os.path.join(output_dir_base, 'chart_volumen_grupos.png')
plt.savefig(chart1_path)
plt.close()

# Gráfica 2: distribución de los top 6 estados más comunes por grupo de asesor
plt.figure(figsize=(12, 6))
# Top 6 para que la grafica no quede ilegible con demasiados estados
top_estados = df['Estado'].value_counts().head(6).index
df_top_estados = df[df['Estado'].isin(top_estados)]

sns.countplot(data=df_top_estados, y='Grupo_Asesor', hue='Estado', palette='Set2')
plt.title('Distribución del "Estado del Lead" entre UCASAL y Sedes (Top 6 Estados)')
plt.xlabel('Cantidad de Leads')
plt.ylabel('')
plt.legend(title='Estado en CRM', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
chart2_path = os.path.join(output_dir_base, 'chart_estados_grupos.png')
plt.savefig(chart2_path)
plt.close()

# Gráfica 3: ranking de asesores por cantidad de inscriptos cerrados (solo exactos)
# Solo Leads con Match_Tipo exacto (excluye Fuzzy para pureza en la atribucion comercial)
df_inscriptos_por_asesor = df[df['Match_Tipo'].astype(str).str.contains('Si') & ~df['Match_Tipo'].astype(str).str.contains('Fuzzy')]

# Agrupar por asesor y contar el volumen de Inscriptos ganados
ranking_inscriptos = df_inscriptos_por_asesor.groupby('Propietario').size().reset_index(name='Total_Inscriptos')
ranking_inscriptos = ranking_inscriptos.sort_values(by='Total_Inscriptos', ascending=False)

# Excluir 'Sin Asignar' del ranking superior si se desea, o lo dejamos para transparencia
top_20_inscriptos = ranking_inscriptos.head(20)

# Gráfica 3: Top 20 Asesores por Volumen de Inscriptos
plt.figure(figsize=(10, 8))
sns.barplot(data=top_20_inscriptos, x='Total_Inscriptos', y='Propietario', palette='magma')
plt.title('Top 20 Asesores con mayor volumen de Inscriptos Cerrados (Matcheados)')
plt.xlabel('Cantidad de Inscriptos Reales')
plt.ylabel('Asesor / Propietario')
plt.tight_layout()
chart3_path = os.path.join(output_dir_base, 'chart_ranking_inscriptos.png')
plt.savefig(chart3_path)
plt.close()
# --------------------------------------------------------------------------

# ============================================================
# RANKING DE VENDEDORES (BASE INSCRIPTOS)
# ============================================================
# Diferente al ranking de asesores: el vendedor es quien cobró (sistema financiero),
# no quien gestionó el lead en el CRM. Son perspectivas complementarias.
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)
col_vend = 'Insc_Vendedor' if 'Insc_Vendedor' in df_insc.columns else 'Vendedor'
col_haber = 'Insc_Haber' if 'Insc_Haber' in df_insc.columns else 'Haber'
df_insc[col_vend] = df_insc[col_vend].fillna('Desconocido / Sin Vendedor').astype(str)

ranking_vend = df_insc.groupby(col_vend).agg(
    Total_Pagados=('Insc_DNI', 'count'), # Usamos el DNI como pivot count
    Volumen_ARS=(col_haber, 'sum')
).reset_index()

ranking_vend = ranking_vend.sort_values(by='Total_Pagados', ascending=False)
top_20_vend = ranking_vend.head(20)

# ============================================================
# RANKING POR EMPRESA / GRUPO COMERCIAL
# ============================================================
# Consolida vendedores bajo su empresa/franquicia para una visión institucional
col_empresa = 'Insc_Empresa' if 'Insc_Empresa' in df_insc.columns else 'Empresa'
if col_empresa in df_insc.columns:
    df_insc[col_empresa] = df_insc[col_empresa].fillna('Desconocido / Sin Entidad').astype(str)
    ranking_empresa = df_insc.groupby(col_empresa).agg(
        Total_Pagados=('Insc_DNI', 'count'),
        Volumen_ARS=(col_haber, 'sum')
    ).reset_index()
    
    ranking_empresa = ranking_empresa.sort_values(by='Total_Pagados', ascending=False)
    top_20_empresa = ranking_empresa.head(20)
    
    # Gráfica: Top 20 Empresas por Volumen
    plt.figure(figsize=(10, 8))
    sns.barplot(data=top_20_empresa, x='Total_Pagados', y=col_empresa, palette='mako')
    plt.title('Top 20 Empresas (Grupos) por Volumen de Inscriptos Facturados')
    plt.xlabel('Cantidad Operaciones Cobradas')
    plt.ylabel('Empresa / Grupo Asesor')
    plt.tight_layout()
    chart_empresa_path = os.path.join(output_dir_base, 'chart_ranking_empresas.png')
    plt.savefig(chart_empresa_path)
    plt.close()
else:
    chart_empresa_path = None
    top_20_empresa = None
# ------------------------------------------------------------------------------------------
top_20_vend = ranking_vend.head(20)

plt.figure(figsize=(10, 8))
sns.barplot(data=top_20_vend, x='Total_Pagados', y=col_vend, palette='viridis')
plt.title('Ranking Global: Top 20 Vendedores Financieros (Base Inscriptos Original)')
plt.xlabel('Cantidad Total de Inscriptos Pagados')
plt.ylabel('Vendedor Contable / Cobrador')

plt.tight_layout()
chart4_path = os.path.join(output_dir_base, 'chart_ranking_vendedores.png')
plt.savefig(chart4_path)
plt.close()
# --------------------------------------------------------------------------

# ----------------- NUEVO: DESGLOSE GLOBAL DE ORIGEN DE INSCRIPTOS (Directo vs Sedes vs Asesores) -----------------
# 1. Total Inscriptos
total_inscriptos = len(df_insc)

# Cruzar los Inscriptos con los Leads para heredar el Grupo_Asesor
# IMPORTANT: Drop duplicates on the right side to prevent a Cartesian memory explosion (42GB+)
df_leads_unique = df[['Id. candidato/contacto', 'Grupo_Asesor']].drop_duplicates(subset=['Id. candidato/contacto'])
df_insc_con_asesor = pd.merge(df_insc, df_leads_unique, on='Id. candidato/contacto', how='left')

df_insc_con_asesor['Origen_Cierre'] = df_insc_con_asesor['Grupo_Asesor'].fillna('Sin trazabilidad (Sin CRM)')

# Agrupar y contar
origen_breakdown = df_insc_con_asesor.groupby('Origen_Cierre').size().reset_index(name='Cantidad')
origen_breakdown['Porcentaje'] = (origen_breakdown['Cantidad'] / total_inscriptos) * 100
origen_breakdown = origen_breakdown.sort_values(by='Cantidad', ascending=False)

plt.figure(figsize=(10, 7))
colores_pie = sns.color_palette("muted", len(origen_breakdown))
explode = [0.05 if i == 0 else 0 for i in range(len(origen_breakdown))]
plt.pie(origen_breakdown['Cantidad'], 
        labels=origen_breakdown['Origen_Cierre'], 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colores_pie,
        explode=explode,
        shadow=True,
        textprops={'fontsize': 11, 'weight': 'bold'})
plt.title('Distribución Global de Inscriptos Facturados\n(Sin Trazabilidad vs Atribuidos a Asesores/Sedes)')
plt.tight_layout()
chart5_path = os.path.join(output_dir_base, 'chart_origen_inscriptos_pie.png')
plt.savefig(chart5_path)
plt.close()
# --------------------------------------------------------------------------
def add_table_to_pdf(pdf, df_group, title):
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font('Helvetica', 'B', 10)
    
    # Headers
    pdf.cell(90, 8, 'Asesor / Propietario', 1)
    pdf.cell(60, 8, 'Estado Principal', 1)
    pdf.cell(30, 8, 'Total Leads', 1, ln=True, align='C')
    
    pdf.set_font('Helvetica', '', 9)
    # Mostramos los asesores top de ese grupo
    top_asesores = df_group['Propietario'].value_counts().head(20).index
    
    for asesor in top_asesores:
        df_asesor = df_group[df_group['Propietario'] == asesor]
        total_asesor = len(df_asesor)
        estado_mayor = df_asesor['Estado'].value_counts().index[0]
        
        pdf.cell(90, 8, str(asesor)[:40], 1)
        pdf.cell(60, 8, str(estado_mayor)[:30], 1)
        pdf.cell(30, 8, f"{total_asesor:,}", 1, ln=True, align='C')
        
    pdf.ln(5)

# Generar PDF
pdf = FPDF()
pdf.add_page()

pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Reporte de Status: Estado de Leads por Asesores', ln=True, align='C')
pdf.set_font('Helvetica', '', 10)
pdf.cell(0, 6, f'Generado el {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='C')
pdf.ln(5)

pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, "Este reporte agrupa el volumen de leads capturados según su propietario dentro del CRM, "
                     "separando lógicamente al equipo de la universidad (Asesores UCASAL) de las delegaciones físicas (Sedes).\n"
                     "Nota: La clasificación entre UCASAL y Sedes se basa en el nombre de la Cola/Delegación en Salesforce.")
pdf.ln(5)

pdf.image(chart1_path, x=15, w=180)
pdf.ln(5)
pdf.image(chart2_path, x=15, w=180)

# ======= NUEVA SECCION: ESTATUS GLOBAL ======
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Salud General de la Base: Estados CRM y Contact Center', ln=True, align='L')
pdf.ln(2)
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, "A continuacion se devela el estatus absoluto global de todos los prospects que residen en el CRM, "
                     "sin importar que asesor los tenga. Adicionalmente, se mide la concentracion volumetrica de la "
                     "cola inicial 'Contact Center' (Bandeja sin atender).")
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, 'Volumen en Cola Contact Center:', ln=True)
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, f"- Total de Leads estancados en 'Contact Center': {volumen_contact_center:,} leads.\n"
                     f"- Representan el {pct_contact_center:.1f}% de toda la base historica de la categoria.")
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, 'Volumen de Leads Abiertos Globales:', ln=True)
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, f"- Total Leads con estado 'Abierto' en toda la base: {volumen_abiertos:,} leads.\n"
                     f"- Representan el {pct_abiertos:.1f}% de la base.")
pdf.ln(5)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(80, 8, 'Estado del Lead (CRM)', 1)
pdf.cell(50, 8, 'Cantidad Neta', 1, align='C')
pdf.cell(40, 8, 'Porcentaje (%)', 1, ln=True, align='C')

pdf.set_font('Helvetica', '', 10)
for _, row in estados_globales.iterrows():
    pdf.cell(80, 8, str(row['Estado']), 1)
    pdf.cell(50, 8, f"{row['Cantidad']:,}", 1, align='C')
    pdf.cell(40, 8, f"{row['Porcentaje']:.1f} %", 1, ln=True, align='C')

pdf.ln(5)
# ============================================

pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Desglose por Asesor - Top 20 Representantes', ln=True, align='L')
pdf.ln(5)

# Top 20 Asesores UCASAL
df_ucasal = df[df['Grupo_Asesor'] == 'Asesores UCASAL (Central)']
add_table_to_pdf(pdf, df_ucasal, "Grupo: Asesores UCASAL")

# Top 20 Asesores Sedes
df_sedes = df[df['Grupo_Asesor'] == 'Sedes / Delegaciones']
add_table_to_pdf(pdf, df_sedes, "Grupo: Asesores de Sedes Físicas")

# Nueva página para el Ranking de Inscriptos
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Ranking de Productividad: Inscriptos Físicos Cerrados por Asesor (SOLO EXACTOS)', ln=True, align='L')
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, "Este gráfico clasifica a los asesores basándose EXCLUSIVAMENTE en los Leads que cruzaron "
                     "de forma EXACTA (misma cédula, teléfono o correo) con la base imponible financiera de la universidad.\n"
                     "Nota: Se han retirado completamente las aproximaciones (Fuzzys) de esta métrica para mantener pureza en la atribución comercial.")
pdf.ln(5)
pdf.image(chart3_path, x=15, w=180)

# Nueva página para el Ranking Global de Vendedores (Base Inscriptos)
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Ranking Contable: Vendedores de Inscriptos (Volumen Bruto Total)', ln=True, align='L')
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, "Este gráfico clasifica a los responsables financieros ('Vendedor'/'Cod. Vendedor') "
                     "extraídos puramente de la tabla original contable inalterada de Inscriptos Generales.\n"
                     "Nota: Refleja el total cerrado, sin importar si llegaron vía publicidad (Leads) o inscripciones espontáneas.\n"
                     "Adicionalmente, se incluye en la tabla inferior la facturación transaccionada en Pesos Argentinos (ARS).")
pdf.ln(5)
pdf.image(chart4_path, x=15, w=180)
pdf.ln(5)

# Renderizar Tabla Financiera
pdf.set_font('Helvetica', 'B', 10)
pdf.cell(75, 8, 'Vendedor / Cobrador', 1)
pdf.cell(35, 8, 'Total Inscriptos', 1, align='C')
pdf.cell(50, 8, 'Ingreso Bruto (ARS)', 1, ln=True, align='R')

pdf.set_font('Helvetica', '', 9)
for index, row in top_20_vend.iterrows():
    pdf.cell(75, 8, str(row[col_vend])[:35], 1)
    pdf.cell(35, 8, f"{row['Total_Pagados']:,}", 1, align='C')
    pdf.cell(50, 8, formato_pesos_arg(row['Volumen_ARS']), 1, ln=True, align='R')

pdf.ln(5)

# Nueva página para Ranking por Empresa
if chart_empresa_path and top_20_empresa is not None:
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Ranking Contable Agrupado: Volumen por Empresa', ln=True, align='L')
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, "Este gráfico consolida a los Vendedores/Cobradores bajo el paraguas de su 'Empresa' (Franquicias/Sedes), "
                         "permitiendo dimensionar el impacto financiero de cada estructura institucional global.")
    pdf.ln(5)
    pdf.image(chart_empresa_path, x=15, w=180)
    pdf.ln(5)
    
    # Tabla Financiera por Empresa
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(75, 8, 'Empresa / Grupo Institucional', 1)
    pdf.cell(35, 8, 'Total Inscriptos', 1, align='C')
    pdf.cell(50, 8, 'Ingreso Bruto (ARS)', 1, ln=True, align='R')
    
    pdf.set_font('Helvetica', '', 9)
    for index, row in top_20_empresa.iterrows():
        pdf.cell(75, 8, str(row[col_empresa])[:35], 1)
        pdf.cell(35, 8, f"{row['Total_Pagados']:,}", 1, align='C')
        pdf.cell(50, 8, formato_pesos_arg(row['Volumen_ARS']), 1, ln=True, align='R')

    pdf.ln(5)

# Nueva página para Desglose Global (Pie Chart)
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'Vision Macro: Origen Final de las Inscripciones Cobradas', ln=True, align='L')
pdf.set_font('Helvetica', '', 11)
pdf.multi_cell(0, 6, "Este gráfico de distribución responde a la pregunta fundamental: Del 100% de la masa "
                     "de estudiantes que efectivamente le pagaron a la universidad, ¿qué porcentaje "
                     "provino de forma Directa/Orgánica (sin requerir carga en el CRM de ventas), "
                     "qué porcentaje fue cerrado por Asesores Centrales (UCASAL) y qué porcentaje "
                     "corresponde al terreno de las Delegaciones y Sedes físicas?")
pdf.ln(5)
pdf.image(chart5_path, x=15, w=180)

# Renderizar Tabla 
pdf.ln(10)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(85, 8, 'Origen del Cierre Fiscal', 1)
pdf.cell(50, 8, 'Volumen de Estudiantes', 1, align='C')
pdf.cell(30, 8, '% del Total', 1, ln=True, align='C')

pdf.set_font('Helvetica', '', 10)
for index, row in origen_breakdown.iterrows():
    pdf.cell(85, 8, str(row['Origen_Cierre']), 1)
    pdf.cell(50, 8, f"{row['Cantidad']:,}", 1, align='C')
    pdf.cell(30, 8, f"{row['Porcentaje']:.1f}%", 1, ln=True, align='C')

pdf_file = os.path.join(output_dir_base, '17_reporte_asesores.pdf')
pdf.output(pdf_file)
print(f"\\n>>> Reporte de Asesores generado con éxito en: {pdf_file}")

# ============================================================
# EXPORTAR DATOS: CSV + EXCEL
# ============================================================
# CSVs: tablas crudas para uso programático
csv_ranking_inscriptos = os.path.join(output_dir_base, '17_ranking_asesores.csv')
ranking_inscriptos.to_csv(csv_ranking_inscriptos, index=False)

csv_informe_estados = os.path.join(output_dir_base, '17_informe_estados_asesor.csv')
grupo_estado.to_csv(csv_informe_estados, index=False)

csv_ranking_vendedores = os.path.join(output_dir_base, '17_ranking_vendedores_inscriptos.csv')
ranking_vend.to_csv(csv_ranking_vendedores, index=False)

# Excel consolidado: todas las tablas en un solo archivo multi-hoja
xlsx_path = os.path.join(output_dir_base, '17_reporte_asesores.xlsx')
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    # Hoja 1: ranking de asesores CRM por inscriptos cerrados (exactos)
    ranking_inscriptos.to_excel(writer, sheet_name='Ranking_Asesores_CRM', index=False)
    # Hoja 2: distribución de estados por grupo de asesor
    grupo_estado.to_excel(writer, sheet_name='Estados_Por_Grupo', index=False)
    # Hoja 3: ranking de vendedores financieros (base inscriptos)
    ranking_vend.to_excel(writer, sheet_name='Ranking_Vendedores', index=False)
    # Hoja 4: distribución de origen de inscriptos (con/sin trazabilidad CRM)
    origen_breakdown.to_excel(writer, sheet_name='Origen_Inscriptos', index=False)
    # Hoja 5: distribución de estados globales de todos los leads
    estados_globales.to_excel(writer, sheet_name='Estados_Globales', index=False)
    # Hoja 6: ranking por empresa (si existe la columna)
    if top_20_empresa is not None:
        ranking_empresa.to_excel(writer, sheet_name='Ranking_Empresas', index=False)
print(f"-> Excel generado: {xlsx_path}")

md_file = os.path.join(output_dir_base, '17_reporte_asesores.md')
with open(md_file, "w", encoding="utf-8") as f:
    f.write("# Reporte de Asesores y Canales de Venta\n\n")
    f.write("## 1. Top Asesores por Volumen Cierre\n\n")
    f.write(top_20_inscriptos.to_markdown(index=False))
    f.write("\n\n## 2. Top Vendedores (Sist. Financiero)\n\n")
    f.write(top_20_vend.to_markdown(index=False))
    f.write("\n\n## Nota Metodologica\n")
    f.write("- **Modelo Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Detalle en el Informe Analitico (04_reporte_final).\n")
    f.write("- **Match:** Exacto por DNI, Email, Telefono y Celular.\n")

# ==========================================
# MEMORIA TÉCNICA
# ==========================================
memoria = f"""# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Segmento:** {segmento}
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `{leads_csv}`
- Inscriptos: `{inscriptos_csv}`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | {total_leads_macro:,} |
| Total Inscriptos físicos | {total_inscriptos:,} |
| Leads en Contact Center | {volumen_contact_center:,} ({pct_contact_center:.1f}%) |
| Leads con Estado "Abierto" | {volumen_abiertos:,} ({pct_abiertos:.1f}%) |

## Distribución de Estados (Top 10)
{estados_globales.head(10).to_markdown(index=False)}

## Origen de Inscripciones (Atribución por Canal)
{origen_breakdown.to_markdown(index=False)}

## Reglas de Negocio
- **Propietario del lead:** Columna `Consulta: Nombre del propietario` (o equivalente), usada para agrupar por asesor
- **Inscripciones atribuidas:** Leads con `Match_Tipo` que contenga `"Exacto"` se consideran inscripciones confirmadas
- **Ranking de vendedores:** Basado en columna `Insc_Vendedor` de la base contable de inscriptos
- **Montos en ARS:** Sumados desde la columna `Insc_Haber` de inscriptos matcheados

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `17_reporte_asesores.pdf` | Informe visual multi-pagina |
| `17_reporte_asesores.xlsx` | Datos consolidados (5-6 hojas) |
| `17_reporte_asesores.md` | Documentacion textual (top rankings) |
| `17_ranking_asesores.csv` | Ranking asesores CRM |
| `17_informe_estados_asesor.csv` | Estados por grupo de asesor |
| `17_ranking_vendedores_inscriptos.csv` | Ranking vendedores financieros |
| `memoria_tecnica.md` | Este archivo |

## Nota Metodologica
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Para atribucion multi-canal, referirse al Informe Analitico (04_reporte_final).
- **Match:** Exacto por DNI, Email, Telefono y Celular.
"""
with open(os.path.join(output_dir_base, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria)
print(f"-> Memoria técnica generada en: {output_dir_base}")

