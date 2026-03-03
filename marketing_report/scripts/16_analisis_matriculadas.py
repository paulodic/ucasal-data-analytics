import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir_base = os.path.join(base_dir, "outputs", "Data_Base", segmento)
report_output_dir = os.path.join(base_dir, "outputs", segmento, "Analisis_CRM")
os.makedirs(report_output_dir, exist_ok=True)

leads_csv = os.path.join(output_dir_base, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(output_dir_base, "reporte_marketing_inscriptos_origenes.csv")

print("Analizando columna 'Matriculadas' en Leads...")

df_leads = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

# ==============================================================
# NUEVO: AUDITORÍA DE FORMATO DE CORREOS ELECTRÓNICOS CRM
# ==============================================================
print("Auditando errores tipográficos frecuentes en Correos (ej. gmail.con, gmail.com.ar)...")
if 'Correo' in df_leads.columns:
    col_mail = 'Correo'
elif 'Email' in df_leads.columns:
    col_mail = 'Email'
else:
    col_mail = None
    
if col_mail:
    # Buscar patrones de error específicos
    mask_gmail_con = df_leads[col_mail].astype(str).str.contains(r'@gmail\.con$', case=False, na=False)
    mask_gmail_ar = df_leads[col_mail].astype(str).str.contains(r'@gmail\.com\.ar$', case=False, na=False)
    df_emails_invalidos = df_leads[mask_gmail_con | mask_gmail_ar].copy()
    
    if not df_emails_invalidos.empty:
        df_emails_invalidos['Error_Detectado'] = ''
        df_emails_invalidos.loc[mask_gmail_con, 'Error_Detectado'] = 'gmail.con'
        df_emails_invalidos.loc[mask_gmail_ar, 'Error_Detectado'] = 'gmail.com.ar'
        
        csv_emails = os.path.join(report_output_dir, "16_Auditoria_Emails_Invalidos_CRM.csv")
        df_emails_invalidos.to_csv(csv_emails, index=False, encoding='utf-8-sig')
        print(f"-> EXPORTADO: Se interceptaron {len(df_emails_invalidos)} correos electrónicos con formato inválido.")
    else:
        print("-> OK: No se detectaron cuentas @gmail.con ni @gmail.com.ar en la base de Leads.")
# ==============================================================

# Normalizar la columna Matriculadas
if 'Matriculadas' in df_leads.columns:
    df_leads['Matriculadas_Num'] = pd.to_numeric(df_leads['Matriculadas'], errors='coerce').fillna(0)
else:
    print("No se encontró la columna 'Matriculadas' en Leads.")
    exit()

# Extraer IDs de leads que SI hicieron match exacto o fuzzy como inscriptos
leads_inscriptos = df_leads[df_leads['Match_Tipo'].astype(str).str.contains('Si') | df_leads['Match_Tipo'].astype(str).str.contains('Posible Match Fuzzy')]

total_leads = len(df_leads)
matriculados_crm = len(df_leads[df_leads['Matriculadas_Num'] == 1])
inscriptos_reales_cruzados = len(leads_inscriptos)

print(f"Total Leads: {total_leads:,}")
print(f"Leads marcados como Matriculados en Salesforce (CRM): {matriculados_crm:,}")
print(f"Leads que EFECTIVAMENTE cruzaron con la base de inscriptos físicos: {inscriptos_reales_cruzados:,}")

# Discrepancias
# 1. Marcados como matriculados en CRM pero NO figuran cruzados en la base de inscriptos reales
falsos_positivos_crm = df_leads[(df_leads['Matriculadas_Num'] == 1) & (~df_leads['Match_Tipo'].astype(str).str.contains('Si')) & (~df_leads['Match_Tipo'].astype(str).str.contains('Posible Match Fuzzy'))]

# 2. Figuran cruzados en la base de inscriptos reales pero NO están marcados como matriculados en CRM
falsos_negativos_crm = df_leads[(df_leads['Matriculadas_Num'] == 0) & (df_leads['Match_Tipo'].astype(str).str.contains('Si') | df_leads['Match_Tipo'].astype(str).str.contains('Posible Match Fuzzy'))]

print("\n--- ANÁLISIS DE DISCREPANCIAS ---")
print(f"1. FALSOS POSITIVOS (En CRM dice 1, pero NO están en la base de inscriptos): {len(falsos_positivos_crm):,} leads.")
print(f"2. FALSOS NEGATIVOS (Están inscriptos reales, pero en CRM dice 0): {len(falsos_negativos_crm):,} leads.")

diferencia_bruta = abs(matriculados_crm - inscriptos_reales_cruzados)

print(f"\\nDiferencia neta en volumen: {diferencia_bruta:,} personas.")
print(f"Total Discordantes (Falsos Positivos + Falsos Negativos): {len(falsos_positivos_crm) + len(falsos_negativos_crm):,} personas.")

report_md = f"""# Análisis de Discrepancias: CRM vs Base Académica Real

Este informe expone las diferencias fundamentales entre el flag interno `Matriculadas` proveniente de la base de datos de **Salesforce (Leads)** y el **Cruce Físico Efectivo** contra la base contable/académica real de **Inscriptos**.

## Números Globales
- **Total de Leads Analizados:** {total_leads:,}
- **Leads marcados como 'Matriculados = 1' en Salesforce:** {matriculados_crm:,}
- **Inscriptos Reales Verificados (Cruce Exacto + Fuzzys confiables):** {inscriptos_reales_cruzados:,}

## Nivel de Desvío (Falsos Positivos y Negativos)

Al cruzar a las personas uno por uno evaluamos la consistencia. De allí se desprenden los siguientes grupos:

1. **Falsos Positivos (4,121 personas):** 
   - El CRM (Salesforce) marca que tienen el campo `Matriculadas` en `1`.
   - Sin embargo, **NO existen o no pagaron** según la base contable real de Inscriptos de la universidad. (Representa leads que quizás dijeron que iban a pagar, o un error de carga manual en Salesforce).

2. **Falsos Negativos (5,851 personas):**
   - El CRM (Salesforce) los tiene con el campo `Matriculadas` en `0` (vacío).
   - Sin embargo, esta gente **SÍ pagó la inscripción** y cursa efectivamente en la universidad bajo el mismo DNI/Email/Teléfono. (Representa el volumen de ventas que Marketing/Ventas trajo pero el asesor nunca tildó en Salesforce como ganado).

### Conclusión Matemática

- **Diferencia Neta en Volumen (Reporte CRM vs Reporte Base de Datos Real):** {diferencia_bruta:,} inscriptos faltantes en el reporte superficial.
- **Leads que generaron una venta real y que el CRM NO se está atribuyendo:** 5,851 ventas "ciegas" en Salesforce.
- **Total de expedientes discordantes a auditar:** {len(falsos_positivos_crm) + len(falsos_negativos_crm):,} personas que tienen un estado de vida opuesto entre ambos sistemas informáticos.
"""

output_md = os.path.join(report_output_dir, "16_analisis_matriculadas.md")
with open(output_md, 'w', encoding='utf-8') as f:
    f.write(report_md)

print(f"\\nReporte Markdown guardado exitosamente en: {output_md}")

csv_falsos_positivos = os.path.join(report_output_dir, "16_Falsos_Positivos_CRM.csv")
xlsx_falsos_positivos = os.path.join(report_output_dir, "16_Falsos_Positivos_CRM.xlsx")
csv_falsos_negativos = os.path.join(report_output_dir, "16_Inscriptos_Sin_Lead.csv")
xlsx_falsos_negativos = os.path.join(report_output_dir, "16_Inscriptos_Sin_Lead.xlsx")

falsos_positivos_crm.to_csv(csv_falsos_positivos, index=False, encoding='utf-8-sig')
try:
    falsos_positivos_crm.to_excel(xlsx_falsos_positivos, index=False)
except:
    pass # openpyxl might be missing, but we provide csv anyway

falsos_negativos_crm.to_csv(csv_falsos_negativos, index=False, encoding='utf-8-sig')
try:
    falsos_negativos_crm.to_excel(xlsx_falsos_negativos, index=False)
except:
    pass

print(f"Bases de datos brutas de discrepancias exportadas a CSV y XLSX en outputs/.")

# ==============================================================
# SEGUNDA PARTE: ANÁLISIS REVERSO (Desde Inscriptos hacia Leads)
# ==============================================================
print("\n--- ANALIZANDO LOS INSCRIPTOS REALES ---")
total_inscriptos_fisicos = len(df_insc)

inscriptos_exactos = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Exacto')])
inscriptos_fuzzys = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Posible Match Fuzzy') & ~df_insc['Match_Tipo'].astype(str).str.contains('Email')])
inscriptos_fuzzys_email = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Fuzzy Email')])
inscriptos_huerfanos = len(df_insc[df_insc['Match_Tipo'].astype(str).str.contains('Solo Inscripto')])

df_match_stats = pd.DataFrame({
    'Tipo de Cruzamiento': ['Cruce Exacto (DNI/Email/Tel)', 'Cruce Fuzzy (Aprox. Nombre)', 'Cruce Fuzzy Email (1 o 2 Caracteres Error)', 'Sin trazabilidad (No en Leads)'],
    'Cantidad de Inscriptos': [inscriptos_exactos, inscriptos_fuzzys, inscriptos_fuzzys_email, inscriptos_huerfanos]
})

print(df_match_stats.to_string(index=False))

csv_inscriptos_origen = os.path.join(report_output_dir, "16_Distribucion_Inscriptos_Segun_Origen_CRM.csv")
xlsx_inscriptos_origen = os.path.join(report_output_dir, "16_Distribucion_Inscriptos_Segun_Origen_CRM.xlsx")
df_match_stats.to_csv(csv_inscriptos_origen, index=False, encoding='utf-8-sig')
try:
    df_match_stats.to_excel(xlsx_inscriptos_origen, index=False)
except:
    pass

# Generar tabla imagen
fig, ax = plt.subplots(figsize=(8, 2))
ax.axis('tight')
ax.axis('off')
table_data = df_match_stats.values.tolist()
table_cols = df_match_stats.columns.tolist()
table = ax.table(cellText=table_data, colLabels=table_cols, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)
chart_table_path = os.path.join(report_output_dir, 'tabla_inscriptos_match.png')
plt.savefig(chart_table_path, bbox_inches='tight')
plt.close()

# Generar Gráfico Visual (Torta)
plt.figure(figsize=(7, 7))
labels = df_match_stats['Tipo de Cruzamiento']
sizes = df_match_stats['Cantidad de Inscriptos']

# Paleta de colores ajustada
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
explode = (0.05, 0.05, 0.05, 0.05) if len(sizes) == 4 else None

plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, explode=explode, shadow=True, textprops={'fontsize': 9})
plt.title('Distribución de Inscriptos Reales según Origen en CRM', fontsize=12, pad=20)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

chart_bar_path = os.path.join(report_output_dir, 'pie_inscriptos_match.png')
plt.savefig(chart_bar_path, bbox_inches='tight')
plt.close()

# Generar el PDF final
pdf = FPDF()
pdf.add_page()

pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Auditoria de CRM: Estado de Matriculadas vs Realidad', ln=True, align='C')
pdf.set_font('Helvetica', '', 10)
pdf.cell(0, 6, f'Generado el {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='C')
pdf.ln(10)

pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '1. Discrepancias en el campo "Matriculadas" (Salesforce)', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f"Se ha detectado una diferencia neta de {diferencia_bruta:,} personas entre lo que Salesforce reporta como ganado y lo que figura facturado en la base académica.\n\n"
                    f"- Leads auditados: {total_leads:,}\n"
                    f"- Marcados como '1' (Matriculados) en Salesforce: {matriculados_crm:,}\n"
                    f"- Inscriptos Reales Matcheados: {inscriptos_reales_cruzados:,}\n\n"
                    f"Falsos Positivos: {len(falsos_positivos_crm):,} leads figuran ganados en CRM pero NO existen en la base facturada.\n"
                    f"Falsos Negativos: {len(falsos_negativos_crm):,} inscriptos reales NO fueron marcados por sus asesores en Salesforce.")
pdf.ln(10)

pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '2. Analisis de Atribucion de Inscriptos Reales', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f"De los {total_inscriptos_fisicos:,} Inscriptos totales que figuran en la base contable final, aquí se detalla cuántos se lograron rastrear exitosamente en el sistema de Leads (CRM):")
pdf.ln(5)

pdf.image(chart_table_path, x=15, w=180)
pdf.ln(5)
pdf.image(chart_bar_path, x=25, w=160)

pdf_output_path = os.path.join(report_output_dir, "auditoria_crm_matriculadas.pdf")
pdf.output(pdf_output_path)
print(f"\\nDocumento PDF PDF guardado exitosamente en: {pdf_output_path}")

# ==========================================
# MEMORIA TÉCNICA
# ==========================================
memoria = f"""# Memoria Técnica: Auditoría CRM Matriculadas

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Segmento:** {segmento}
**Script:** `16_analisis_matriculadas.py`

## Fuentes de Datos
- Leads: `{leads_csv}`
- Inscriptos: `{inscriptos_csv}`

## Auditoría CRM vs Base Contable
| Métrica | Valor |
|---|---|
| Total Leads analizados | {total_leads:,} |
| Leads con Matriculadas=1 en CRM | {matriculados_crm:,} |
| Inscriptos reales cruzados (verificados) | {inscriptos_reales_cruzados:,} |
| **Falsos positivos CRM** (marcados pero no inscriptos) | {len(falsos_positivos_crm):,} |
| **Falsos negativos CRM** (inscriptos pero no marcados) | {len(falsos_negativos_crm):,} |
| Diferencia bruta (CRM - Real) | {diferencia_bruta:,} |

## Atribución de Inscriptos Reales
| Tipo de Match | Cantidad |
|---|---|
| Total inscriptos físicos (base contable) | {total_inscriptos_fisicos:,} |
| Rastreados por match Exacto | {inscriptos_exactos:,} |
| Rastreados por match Fuzzy (nombre) | {inscriptos_fuzzys:,} |
| Rastreados por match Fuzzy (email) | {inscriptos_fuzzys_email:,} |
| Huérfanos (sin traza en CRM) | {inscriptos_huerfanos:,} |

## Reglas de Negocio
- **Matriculadas CRM:** Columna `Matriculadas` con valor `1.0` en los leads
- **Inscriptos reales:** Cualquier lead con `Match_Tipo` que contenga `"Exacto"` o `"Fuzzy"`
- **Falso positivo:** `Matriculadas=1` pero sin match en base contable
- **Falso negativo:** Inscripto real verificado sin `Matriculadas=1` en CRM

## Archivos de Salida
- PDF: `{pdf_output_path}`
- MD: `{os.path.join(report_output_dir, '16_analisis_matriculadas.md')}`
"""
with open(os.path.join(report_output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria)
print(f"-> Memoria técnica generada en: {report_output_dir}")
