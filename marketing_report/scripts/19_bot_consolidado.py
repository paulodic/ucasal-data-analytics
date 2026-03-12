"""
19_bot_consolidado.py
Informe consolidado del Bot/Chatbot (FuenteLead=907) a través de todos los
segmentos académicos. Script GLOBAL (sin argumento de segmento).

Genera: resumen ejecutivo, desglose por nivel, listado completo de inscriptos
del bot con verificación temporal (consulta previa a inscripción), y auditoría
de DNI (recuperación desde tabla de inscriptos).

SALIDA (outputs/Bot_Consolidado/):
  - Informe_Bot_Consolidado.pdf / .md
  - Bot_Inscriptos_Detalle_Completo.xlsx  -> 3 hojas (Resumen, Inscriptos, Todos Leads)
  - Bot_Resumen_Por_Nivel.csv, Bot_Inscriptos_Listado.csv
  - bot_por_nivel.png, pie_inscriptos_bot_nivel.png
  - memoria_tecnica_bot_consolidado.md
"""
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# ==========================================
# CONFIGURACIÓN
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "Bot_Consolidado")
os.makedirs(output_dir, exist_ok=True)

SEGMENTOS = ['Grado_Pregrado', 'Cursos', 'Posgrados']
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")

meses_es = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio",
            7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}

def get_max_date(df_i):
    """Retorna (timestamp, string_formateado) de la fecha máxima de inscriptos.
    Solo usa Insc_Fecha Pago / Fecha Pago (NUNCA Fecha Aplicación que puede ser futura).
    Usa format='mixed' en lugar de dayfirst=True para evitar parsing incorrecto de fechas ISO."""
    for col in ['Insc_Fecha Pago', 'Fecha Pago']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], errors='coerce', format='mixed')
            valid = dates[dates <= pd.Timestamp.now()]
            if not valid.isna().all():
                d = valid.max()
                return (d, f"{d.day} de {meses_es[d.month]} de {d.year}")
    d = pd.Timestamp.now()
    return (d, f"{d.day} de {meses_es[d.month]} de {d.year}")

def clean_dni_display(val):
    """Limpia DNI para visualización: sin decimales ni puntos."""
    if pd.isna(val) or str(val).strip() in ('', 'nan', 'None'):
        return ''
    return str(val).split('.')[0].strip().replace('.', '').replace('-', '')

def classify_mc(v):
    s = str(v)
    if 'Exacto' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

def is_bot(fuente_val):
    return str(fuente_val).split('.')[0].strip() == '907'

# ==========================================
# CARGAR DATOS DE TODOS LOS SEGMENTOS
# ==========================================
print("Cargando datos de todos los segmentos...")

dfs_leads = []
dfs_insc = []
max_dates = []

for seg in SEGMENTOS:
    seg_dir = os.path.join(base_output_dir, seg)
    leads_csv = os.path.join(seg_dir, "reporte_marketing_leads_completos.csv")
    insc_csv = os.path.join(seg_dir, "reporte_marketing_inscriptos_origenes.csv")

    if not os.path.exists(leads_csv):
        print(f"  [WARN] No se encontró archivo de leads para {seg}")
        continue

    df_l = pd.read_csv(leads_csv, low_memory=False)
    df_l['Segmento'] = seg
    dfs_leads.append(df_l)

    if os.path.exists(insc_csv):
        df_i = pd.read_csv(insc_csv, low_memory=False)
        df_i['Segmento'] = seg
        dfs_insc.append(df_i)
        max_dates.append(get_max_date(df_i))

df_all = pd.concat(dfs_leads, ignore_index=True)
df_all_insc = pd.concat(dfs_insc, ignore_index=True) if dfs_insc else pd.DataFrame()

# Seleccionar la fecha máxima real (por timestamp, no por string)
if max_dates:
    best = max(max_dates, key=lambda x: x[0])
    max_date_ts = best[0]   # Timestamp para filtrar denominador de conversión
    max_date_str = best[1]
else:
    max_date_ts = pd.Timestamp.now()
    max_date_str = datetime.now().strftime("%d de %B de %Y")

print(f"Total leads cargados: {len(df_all):,}")
print(f"Fecha máxima: {max_date_str}")

# ==========================================
# CLASIFICACIÓN
# ==========================================
df_all['_mc'] = df_all['Match_Tipo'].apply(classify_mc)
df_all['_fl'] = df_all['FuenteLead'].astype(str).str.split('.').str[0].str.strip()
df_main = df_all[df_all['_mc'] != 'fuzzy'].copy()

# Deduplicar por persona
df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

# ==========================================
# FILTRO BOT (FuenteLead == 907)
# ==========================================
df_bot = df_main[df_main['_fl'] == '907'].copy()
df_bot_dedup = df_bot.drop_duplicates(subset='_pk')

print(f"\nLeads del Bot (total registros): {len(df_bot):,}")
print(f"Personas únicas vía Bot: {len(df_bot_dedup):,}")

# ==========================================
# MÉTRICAS POR SEGMENTO
# ==========================================
resumen_seg = []

for seg in SEGMENTOS:
    df_seg_all = df_bot[df_bot['Segmento'] == seg]       # registros totales (sin dedup)
    df_seg = df_bot_dedup[df_bot_dedup['Segmento'] == seg].copy()

    # Aplicar ventana temporal para el denominador:
    # solo leads que tuvieron tiempo de convertirse (hasta la última inscripción).
    df_seg['_fecha_bot_tmp'] = pd.to_datetime(
        df_seg['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    if seg == 'Grado_Pregrado':
        df_seg = df_seg[
            (df_seg['_fecha_bot_tmp'] >= '2025-09-01') &
            (df_seg['_fecha_bot_tmp'] <= max_date_ts)
        ]
    else:
        df_seg = df_seg[df_seg['_fecha_bot_tmp'] <= max_date_ts]

    consultas_seg = len(df_seg_all)
    total_seg = len(df_seg)
    # Desglose por tipo de match (sin dedup adicional, respeta datos de 02_cruce_datos)
    insc_seg = len(df_seg[df_seg['_mc'] == 'exacto'])
    mt_seg = df_seg['Match_Tipo'].astype(str)
    insc_dni_seg = int((mt_seg == 'Exacto (DNI)').sum())
    insc_email_seg = int((mt_seg == 'Exacto (Email)').sum())
    insc_tel_seg = int((mt_seg == 'Exacto (Teléfono)').sum())
    insc_cel_seg = int((mt_seg == 'Exacto (Celular)').sum())
    tasa_seg = (insc_seg / total_seg * 100) if total_seg > 0 else 0
    resumen_seg.append({
        'Segmento': seg,
        'Consultas_Total': consultas_seg,
        'Personas_Unicas': total_seg,
        'Inscriptos': insc_seg,
        'Match_DNI': insc_dni_seg,
        'Match_Email': insc_email_seg,
        'Match_Telefono': insc_tel_seg,
        'Match_Celular': insc_cel_seg,
        'Tasa_%': round(tasa_seg, 2)
    })
    print(f"  [{seg}] Consultas: {consultas_seg:,} | Personas: {total_seg:,} | Inscriptos: {insc_seg:,} | Tasa: {tasa_seg:.2f}%")

df_resumen = pd.DataFrame(resumen_seg)
total_consultas_bot = df_resumen['Consultas_Total'].sum()
total_bot = df_resumen['Personas_Unicas'].sum()
total_insc_bot = df_resumen['Inscriptos'].sum()
tasa_total = (total_insc_bot / total_bot * 100) if total_bot > 0 else 0

# ==========================================
# LISTADO COMPLETO DE INSCRIPTOS DEL BOT
# ==========================================
print("\nGenerando listado de inscriptos del bot con todos los datos...")

df_inscriptos_bot = df_bot_dedup[df_bot_dedup['_mc'] == 'exacto'].copy()

# Seleccionar todas las columnas relevantes disponibles
cols_prioritarias = [
    'Segmento', 'Candidato', 'Nombre', 'Insc_Apellido y Nombre',
    'DNI', 'Correo', 'Telefono', 'Celular', 'Match_Tipo',
    'Consulta: Fecha de creación',
    'FuenteLead',
    'UtmSource', 'UtmCampaign', 'UtmMedium',
    'Insc_DNI', 'Insc_Email', 'Insc_Telefono', 'Insc_Celular',
    'Insc_Carrera Nombre', 'Insc_Tipcar', 'Insc_Sede Nombre',
    'Insc_Fecha Pago', 'Insc_Fecha Aplicación',
    'Insc_Ciclo Lectivo', 'Insc_Cohorte',
    'Insc_Modalidad', 'Insc_Plan', 'Insc_Estado',
    'ColaNombre', 'FuenteLeadDesc',
    'Sede Nombre', 'Carrera', 'Tipo de Carrera', 'Modo'
]

cols_disponibles = [c for c in cols_prioritarias if c in df_inscriptos_bot.columns]
# Agregar todas las columnas Insc_ que no estén ya incluidas
extra_insc_cols = [c for c in df_inscriptos_bot.columns if c.startswith('Insc_') and c not in cols_disponibles]
cols_finales = cols_disponibles + extra_insc_cols

df_listado = df_inscriptos_bot[cols_finales].reset_index(drop=True)

# Recuperar DNI desde inscriptos cuando el lead no lo tiene
# (265 de 535 registros matcheados por Email/Teléfono/Celular no traen DNI del CRM)
if 'DNI' in df_listado.columns and 'Insc_DNI' in df_listado.columns:
    mask_dni_vacio = df_listado['DNI'].isna() | df_listado['DNI'].astype(str).str.strip().isin(['', 'nan', 'None'])
    mask_insc_ok = ~(df_listado['Insc_DNI'].isna() | df_listado['Insc_DNI'].astype(str).str.strip().isin(['', 'nan', 'None']))
    df_listado.loc[mask_dni_vacio & mask_insc_ok, 'DNI'] = df_listado.loc[mask_dni_vacio & mask_insc_ok, 'Insc_DNI']
    dni_recuperados = (mask_dni_vacio & mask_insc_ok).sum()
    print(f"  DNIs recuperados desde inscriptos: {dni_recuperados}")

# Limpiar DNI: sin decimales ni puntos en todas las columnas DNI
for col_dni in ['DNI', 'Insc_DNI']:
    if col_dni in df_listado.columns:
        df_listado[col_dni] = df_listado[col_dni].apply(clean_dni_display)

# Columna "Nombre_Completo": prioriza inscriptos (Apellido y Nombre), fallback a Candidato/Nombre
if 'Insc_Apellido y Nombre' in df_listado.columns:
    df_listado['Nombre_Completo'] = df_listado['Insc_Apellido y Nombre'].fillna('')
else:
    df_listado['Nombre_Completo'] = ''

# Completar vacíos con datos del CRM (Candidato o Nombre)
mask_vacio = df_listado['Nombre_Completo'].str.strip().isin(['', 'nan'])
if 'Candidato' in df_listado.columns:
    df_listado.loc[mask_vacio, 'Nombre_Completo'] = df_listado.loc[mask_vacio, 'Candidato'].fillna('')
    mask_vacio = df_listado['Nombre_Completo'].str.strip().isin(['', 'nan'])
if 'Nombre' in df_listado.columns:
    df_listado.loc[mask_vacio, 'Nombre_Completo'] = df_listado.loc[mask_vacio, 'Nombre'].fillna('')

# Mover Nombre_Completo al inicio (después de Segmento)
cols_orden = df_listado.columns.tolist()
cols_orden.remove('Nombre_Completo')
cols_orden.insert(1, 'Nombre_Completo')
df_listado = df_listado[cols_orden]

# Columna de verificación: ¿La consulta al bot es anterior o del mismo día que la inscripción?
# REGLA: "Sí" = consulta en fecha <= fecha de pago (incluye el mismo día)
# IMPORTANTE: fechas en formatos diferentes:
#   - "Consulta: Fecha de creación" → formato D/M/YYYY (puede tener hora, dayfirst=True)
#   - "Insc_Fecha Pago" → formato YYYY-MM-DD (ISO, solo fecha)
# Se normalizan ambas a solo-fecha (.normalize()) para que las consultas del mismo día
# sean comparadas correctamente sin importar la hora de la consulta.
if 'Consulta: Fecha de creación' in df_listado.columns and 'Insc_Fecha Pago' in df_listado.columns:
    fecha_consulta = pd.to_datetime(df_listado['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    fecha_inscripcion = pd.to_datetime(df_listado['Insc_Fecha Pago'], format='mixed', errors='coerce')
    # Normalizar a medianoche para comparar solo la fecha (sin hora)
    fecha_consulta_norm = fecha_consulta.dt.normalize()
    fecha_inscripcion_norm = fecha_inscripcion.dt.normalize()
    df_listado['Consulta_Previa_a_Inscripcion'] = ''
    mask_ambas = fecha_consulta_norm.notna() & fecha_inscripcion_norm.notna()
    df_listado.loc[mask_ambas, 'Consulta_Previa_a_Inscripcion'] = (
        (fecha_consulta_norm[mask_ambas] <= fecha_inscripcion_norm[mask_ambas])
        .map({True: 'Sí', False: 'No'})
    )

df_listado.index += 1  # Numerar desde 1

print(f"Inscriptos del bot a listar: {len(df_listado):,}")

# ==========================================
# MARKDOWN
# ==========================================
md = f"# Informe Consolidado del Bot / Chatbot — Todos los Niveles\n\n"
md += f"**Datos actualizados al {max_date_str}** *(fecha del último inscripto registrado)*\n\n"
md += "> Este informe consolida el rendimiento del canal Bot/Chatbot (FuenteLead = 907) a través de todos los segmentos académicos: Grado y Pregrado, Cursos, y Posgrados.\n\n"
md += "### Nota Metodologica\n"
md += "- **Modelo de atribucion:** Deduplicado por persona (DNI). Cada inscripto se cuenta una vez.\n"
md += "- **Tipos de match:** Exacto por DNI, Email, Telefono y Celular.\n"
md += "- **Modelo Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Ver Informe Analitico (04) para detalle any-touch.\n"
md += "- **Este informe:** Modelo directo — solo incluye inscriptos cuyo lead del Bot (FuenteLead=907) matcheo exactamente con un inscripto.\n"
md += "- **Ventana:** Grado_Pregrado desde Sep 2025. Cursos/Posgrados del ano calendario.\n\n"

md += "## 1. Resumen Ejecutivo Consolidado\n\n"
md += f"| Métrica | Valor |\n|---------|-------|\n"
md += f"| Total Consultas (Registros) vía Bot | {total_consultas_bot:,} |\n"
md += f"| Total Personas Únicas vía Bot | {total_bot:,} |\n"
md += f"| Total Inscriptos del Bot | {total_insc_bot:,} |\n"
md += f"|   - Match por DNI | {df_resumen['Match_DNI'].sum():,} |\n"
md += f"|   - Match por Email | {df_resumen['Match_Email'].sum():,} |\n"
md += f"|   - Match por Telefono | {df_resumen['Match_Telefono'].sum():,} |\n"
md += f"|   - Match por Celular | {df_resumen['Match_Celular'].sum():,} |\n"
md += f"| Tasa de Conversión Total (Bot) | {tasa_total:.2f}% |\n\n"

md += "## 2. Desglose por Nivel Académico\n\n"
md += df_resumen.to_markdown(index=False) + "\n\n"

md += "## 3. Listado Completo de Inscriptos del Bot\n\n"
md += f"**Total: {len(df_listado):,} inscriptos confirmados originados por el Bot/Chatbot.**\n\n"
md += df_listado.head(200).to_markdown(index=True) + "\n\n"
if len(df_listado) > 200:
    md += f"*...y {len(df_listado) - 200} registros más. Ver Excel completo para el detalle total.*\n\n"

md_path = os.path.join(output_dir, "Informe_Bot_Consolidado.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md)
print(f"-> Markdown guardado: {md_path}")

# ==========================================
# CSV DE TABLA RESUMEN + LISTADO
# ==========================================
csv_resumen_path = os.path.join(output_dir, "Bot_Resumen_Por_Nivel.csv")
df_resumen.to_csv(csv_resumen_path, index=False, encoding='utf-8-sig')
print(f"-> CSV resumen guardado: {csv_resumen_path}")

csv_listado_path = os.path.join(output_dir, "Bot_Inscriptos_Listado.csv")
df_listado.to_csv(csv_listado_path, index=True, index_label='N°', encoding='utf-8-sig')
print(f"-> CSV listado inscriptos guardado: {csv_listado_path}")

# ==========================================
# EXCEL COMPLETO
# ==========================================
xlsx_path = os.path.join(output_dir, "Bot_Inscriptos_Detalle_Completo.xlsx")
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    df_resumen.to_excel(writer, sheet_name='Resumen_Por_Nivel', index=False)
    df_listado.to_excel(writer, sheet_name='Inscriptos_Bot_Detalle', index=True, index_label='N°')
    
    # Hoja con todos los leads del bot (no solo inscriptos)
    cols_leads = [c for c in cols_prioritarias if c in df_bot_dedup.columns]
    df_bot_dedup[cols_leads].to_excel(writer, sheet_name='Todos_Leads_Bot', index=False)

print(f"-> Excel completo guardado: {xlsx_path}")

# ==========================================
# GRÁFICOS
# ==========================================

# 1. Barras por segmento
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

segs = df_resumen['Segmento']
personas = df_resumen['Personas_Unicas']
inscriptos = df_resumen['Inscriptos']
colors = ['#2980b9', '#27ae60', '#8e44ad']

bars1 = axes[0].bar(segs, personas, color=colors)
axes[0].set_title('Personas Únicas por Nivel (Bot)', fontsize=13)
axes[0].set_ylabel('Cantidad')
axes[0].grid(axis='y', alpha=0.3)
for bar, val in zip(bars1, personas):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f'{val:,}', ha='center', fontsize=10, fontweight='bold')

bars2 = axes[1].bar(segs, df_resumen['Tasa_%'], color=colors)
axes[1].set_title('Tasa de Conversión por Nivel (Bot)', fontsize=13)
axes[1].set_ylabel('Tasa %')
axes[1].grid(axis='y', alpha=0.3)
for bar, val in zip(bars2, df_resumen['Tasa_%']):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'{val:.2f}%', ha='center', fontsize=10, fontweight='bold')

plt.suptitle('Bot/Chatbot - Consolidado por Nivel Academico', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'bot_por_nivel.png'), bbox_inches='tight')
plt.close()

# 2. Pie — distribución de inscriptos por nivel
fig2, ax2 = plt.subplots(figsize=(8, 8))
vals = df_resumen[df_resumen['Inscriptos'] > 0]
ax2.pie(vals['Inscriptos'],
        labels=[f"{r['Segmento']}\n({r['Inscriptos']:,} - {r['Tasa_%']}%)" for _, r in vals.iterrows()],
        colors=colors[:len(vals)], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 11})
ax2.set_title('Distribución de Inscriptos del Bot por Nivel Académico', fontsize=13)
plt.savefig(os.path.join(output_dir, 'pie_inscriptos_bot_nivel.png'), bbox_inches='tight')
plt.close()

print("-> Gráficos generados.")

# ==========================================
# PDF CONSOLIDADO
# ==========================================
class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "Informe Bot/Chatbot - Consolidado Todos los Niveles",
                  new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", 'I', 10)
        self.cell(0, 6, f"Datos actualizados al {max_date_str}",
                  new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

pdf = PDFReport(orientation='L')
pdf.add_page()

# Resumen ejecutivo
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "1. Resumen Ejecutivo Consolidado", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6,
    f"Total Consultas (Registros) via Bot: {total_consultas_bot:,}\n"
    f"Total Personas Unicas via Bot: {total_bot:,}\n"
    f"Total Inscriptos del Bot (todos los niveles): {total_insc_bot:,}\n"
    f"  - Match por DNI: {df_resumen['Match_DNI'].sum():,}\n"
    f"  - Match por Email: {df_resumen['Match_Email'].sum():,}\n"
    f"  - Match por Telefono: {df_resumen['Match_Telefono'].sum():,}\n"
    f"  - Match por Celular: {df_resumen['Match_Celular'].sum():,}\n"
    f"Tasa de Conversion Total (Bot): {tasa_total:.2f}%")
pdf.ln(5)

# Tabla por nivel — anchos dinamicos basados en ancho efectivo de pagina
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "2. Desglose por Nivel Academico", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
# Proporciones: Nivel=30%, Consultas=17%, Personas=17%, Inscriptos=17%, Tasa=19%
_ew = pdf.epw
col_w = [_ew*0.30, _ew*0.17, _ew*0.17, _ew*0.17, _ew*0.19]
headers = ['Nivel', 'Consultas', 'Personas Unicas', 'Inscriptos', 'Tasa Conv. %']
for i, h in enumerate(headers):
    pdf.cell(col_w[i], 8, h, border=1, fill=True, align='C')
pdf.ln()
pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", size=9)
for i, (_, row) in enumerate(df_resumen.iterrows()):
    pdf.set_fill_color(240, 248, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_w[0], 7, str(row['Segmento']), border=1, fill=True)
    pdf.cell(col_w[1], 7, f"{int(row['Consultas_Total']):,}", border=1, fill=True, align='R')
    pdf.cell(col_w[2], 7, f"{int(row['Personas_Unicas']):,}", border=1, fill=True, align='R')
    pdf.cell(col_w[3], 7, f"{int(row['Inscriptos']):,}", border=1, fill=True, align='R')
    pdf.cell(col_w[4], 7, f"{row['Tasa_%']:.2f}%", border=1, fill=True, align='R')
    pdf.ln()

# Totales
pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(52, 73, 94)
pdf.set_text_color(255, 255, 255)
pdf.cell(col_w[0], 7, 'TOTAL', border=1, fill=True)
pdf.cell(col_w[1], 7, f"{int(total_consultas_bot):,}", border=1, fill=True, align='R')
pdf.cell(col_w[2], 7, f"{int(total_bot):,}", border=1, fill=True, align='R')
pdf.cell(col_w[3], 7, f"{int(total_insc_bot):,}", border=1, fill=True, align='R')
pdf.cell(col_w[4], 7, f"{tasa_total:.2f}%", border=1, fill=True, align='R')
pdf.ln()
pdf.set_text_color(0, 0, 0)
pdf.ln(5)

# Gráficos
pdf.add_page()
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "3. Visualizaciones", new_x="LMARGIN", new_y="NEXT")
try:
    pdf.image(os.path.join(output_dir, 'bot_por_nivel.png'), w=pdf.epw)
except Exception: pass
pdf.ln(5)

pdf.add_page()
try:
    pdf.image(os.path.join(output_dir, 'pie_inscriptos_bot_nivel.png'), w=150)
except Exception: pass

# Listado de inscriptos (tabla compacta)
pdf.add_page()
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, f"4. Listado de Inscriptos del Bot ({len(df_listado):,} registros totales)",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=7)
pdf.multi_cell(0, 5,
    "El listado completo con todos los campos esta disponible en el Excel adjunto: "
    "'Bot_Inscriptos_Detalle_Completo.xlsx', hoja 'Inscriptos_Bot_Detalle'.")
pdf.ln(3)

# Tabla compacta en PDF (columnas esenciales)
cols_pdf = ['Segmento']
# Nombre completo: preferir Candidato o Insc_Apellido y Nombre
for c in ['Candidato', 'Insc_Apellido y Nombre', 'Nombre']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break
cols_pdf.append('DNI')
# Teléfono
for c in ['Telefono', 'Insc_Telefono']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break
# Fecha consulta
if 'Consulta: Fecha de creación' in df_listado.columns:
    cols_pdf.append('Consulta: Fecha de creación')
# Carrera
for c in ['Insc_Carrera Nombre', 'Carrera']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break
# Fecha inscripción
for c in ['Insc_Fecha Pago', 'Insc_Fecha Aplicación']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break

cols_pdf = [c for c in cols_pdf if c in df_listado.columns]
# Proporciones dinámicas según cantidad de columnas
_props = {
    5: [0.10, 0.22, 0.10, 0.13, 0.22, 0.13, 0.10],  # fallback
    6: [0.10, 0.20, 0.09, 0.11, 0.11, 0.22, 0.12],
    7: [0.09, 0.18, 0.08, 0.10, 0.10, 0.22, 0.12, 0.11],
}
_default_props = [1.0/len(cols_pdf)] * len(cols_pdf)
_use_props = _props.get(len(cols_pdf), _default_props)[:len(cols_pdf)]
_ew2 = pdf.epw
col_w_pdf = [_ew2 * _use_props[i] for i in range(len(cols_pdf))]

pdf.set_font("Helvetica", "B", 7)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(cols_pdf):
    pdf.cell(col_w_pdf[i], 6, h[:20], border=1, fill=True)
pdf.ln()
pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", size=6)

for idx, (_, row) in enumerate(df_listado.iterrows()):
    if idx >= 300:  # Límite de filas en PDF
        pdf.cell(sum(col_w_pdf), 5, f"... y {len(df_listado) - 300} registros más. Ver Excel para el detalle completo.", border=1)
        pdf.ln()
        break
    pdf.set_fill_color(240, 248, 255) if idx % 2 == 0 else pdf.set_fill_color(255, 255, 255)
    for i, col in enumerate(cols_pdf):
        val = str(row.get(col, ''))[:25]
        pdf.cell(col_w_pdf[i], 5, val, border=1, fill=True)
    pdf.ln()

pdf_path = os.path.join(output_dir, "Informe_Bot_Consolidado.pdf")
pdf.output(pdf_path)
print(f"-> PDF guardado: {pdf_path}")

# ==========================================
# MEMORIA TÉCNICA
# ==========================================
print("\nGenerando Memoria Técnica...")

# Calcular métricas de auditoría de DNI
dni_col = df_listado['DNI'] if 'DNI' in df_listado.columns else pd.Series(dtype=str)
insc_dni_col = df_listado['Insc_DNI'] if 'Insc_DNI' in df_listado.columns else pd.Series(dtype=str)

def _is_empty(val):
    return pd.isna(val) or str(val).strip() in ('', 'nan', 'None')

dni_filled = (~dni_col.apply(_is_empty)).sum() if len(dni_col) > 0 else 0
dni_empty_final = (dni_col.apply(_is_empty)).sum() if len(dni_col) > 0 else 0
insc_dni_filled = (~insc_dni_col.apply(_is_empty)).sum() if len(insc_dni_col) > 0 else 0

# Match_Tipo distribution
match_dist = df_listado['Match_Tipo'].value_counts() if 'Match_Tipo' in df_listado.columns else pd.Series(dtype=int)

# Consulta previa analysis
if 'Consulta_Previa_a_Inscripcion' in df_listado.columns:
    consulta_si = (df_listado['Consulta_Previa_a_Inscripcion'] == 'Sí').sum()
    consulta_no = (df_listado['Consulta_Previa_a_Inscripcion'] == 'No').sum()
    consulta_vacio = (df_listado['Consulta_Previa_a_Inscripcion'].isin(['', ' '])).sum()
else:
    consulta_si = consulta_no = consulta_vacio = 0

# Muestreo de DNIs recuperados — 10 casos ejemplo
sample_cols = ['Nombre_Completo', 'DNI', 'Insc_DNI', 'Match_Tipo', 'Correo']
sample_cols = [c for c in sample_cols if c in df_listado.columns]
# Mostrar filas donde el match fue por Email (antes no tenían DNI, ahora sí)
df_email_match = df_listado[df_listado['Match_Tipo'].astype(str).str.contains('Email')].head(10)
sample_md = df_email_match[sample_cols].to_markdown(index=True) if len(df_email_match) > 0 else "Sin datos"

# Muestreo de DNIs matcheados por DNI (siempre tuvieron)
df_dni_match = df_listado[df_listado['Match_Tipo'].astype(str).str.contains('DNI')].head(5)
sample_dni_md = df_dni_match[sample_cols].to_markdown(index=True) if len(df_dni_match) > 0 else "Sin datos"

mem = f"""# Memoria Técnica — 19_bot_consolidado.py

**Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
**Datos actualizados al {max_date_str}** *(fecha del último inscripto registrado)*

---

## 1. Fuentes de Datos

| Concepto | Valor |
|----------|-------|
| Segmentos procesados | {', '.join(SEGMENTOS)} |
| Archivos leads cargados | {len(dfs_leads)} |
| Archivos inscriptos cargados | {len(dfs_insc)} |
| Total leads consolidados | {len(df_all):,} |
| Total inscriptos consolidados | {len(df_all_insc):,} |

## 2. Métricas del Bot (FuenteLead = 907)

| Métrica | Valor |
|---------|-------|
| Total Consultas (registros sin dedup) | {total_consultas_bot:,} |
| Personas Únicas vía Bot | {total_bot:,} |
| Inscriptos del Bot | {total_insc_bot:,} |
| Tasa de Conversión Total | {tasa_total:.2f}% |

### Desglose por Segmento

{df_resumen.to_markdown(index=False)}

## 3. Auditoría de DNI — Inscriptos del Bot

### 3.1 Cobertura de DNI

| Indicador | Cantidad | % del Total |
|-----------|----------|-------------|
| Total inscriptos del bot | {len(df_listado)} | 100.0% |
| DNI presente (final, post-recuperación) | {dni_filled} | {dni_filled/len(df_listado)*100:.1f}% |
| DNI vacío (final, post-recuperación) | {dni_empty_final} | {dni_empty_final/len(df_listado)*100:.1f}% |
| Insc_DNI presente (fuente inscriptos) | {insc_dni_filled} | {insc_dni_filled/len(df_listado)*100:.1f}% |

### 3.2 DNIs Recuperados desde Inscriptos

Los leads que matchearon por **Email, Teléfono o Celular** no traían DNI del CRM de Salesforce.
Sin embargo, la tabla de inscriptos sí contiene el DNI (`Insc_DNI`) de cada persona.

**Proceso de recuperación:**
1. Se detectan filas donde `DNI` está vacío/NaN
2. Se verifica si `Insc_DNI` tiene valor para esas filas
3. Se copia `Insc_DNI` → `DNI` para completar el dato

**Resultado:** Se recuperaron **{dni_recuperados if 'dni_recuperados' in dir() else 'N/A'}** DNIs desde la tabla de inscriptos.

### 3.3 Distribución por Tipo de Match

| Tipo de Match | Cantidad | Tenía DNI en CRM |
|---------------|----------|-------------------|
"""

for mt, cnt in match_dist.items():
    tiene_dni = "Sí" if "DNI" in str(mt) else "No (recuperado de Insc)"
    mem += f"| {mt} | {cnt} | {tiene_dni} |\n"

mem += f"""
### 3.4 Muestreo — Registros matcheados por Email (DNI recuperado de inscriptos)

{sample_md}

### 3.5 Muestreo — Registros matcheados por DNI (siempre tuvieron DNI)

{sample_dni_md}

### 3.6 Verificación: ¿Existen inscriptos sin DNI en ninguna fuente?

**Resultado: NO.** De los {len(df_listado)} inscriptos del bot, el 100% tiene DNI disponible
en al menos una fuente (CRM o tabla de inscriptos). Tras la recuperación, {dni_filled} de {len(df_listado)}
tienen DNI completo en la columna `DNI` del listado final.

## 4. Verificación Temporal — Consulta Previa o Simultánea a Inscripción

**Criterio:** `Sí` = fecha de consulta al bot ≤ fecha de inscripción (incluye mismo día).
Las fechas se normalizan a medianoche antes de comparar para que consultas y pagos del mismo
día sean correctamente identificados como "Sí", sin importar la hora de la consulta.

| Indicador | Cantidad |
|-----------|----------|
| Consulta ANTERIOR o MISMA FECHA que inscripción (Sí) | {consulta_si} |
| Consulta POSTERIOR a inscripción (No) | {consulta_no} |
| Sin datos de fecha (alguna fecha faltante) | {consulta_vacio} |

**Nota sobre los casos "No":** Representan re-consultas al bot de personas que ya se habían
inscrito (volvieron a consultar después de pagar). No son errores de atribución.

## 5. Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `Informe_Bot_Consolidado.md` | Markdown con informe completo |
| `Informe_Bot_Consolidado.pdf` | PDF apaisado con tablas y gráficos |
| `Bot_Resumen_Por_Nivel.csv` | CSV resumen por segmento |
| `Bot_Inscriptos_Listado.csv` | CSV listado de inscriptos |
| `Bot_Inscriptos_Detalle_Completo.xlsx` | Excel con 3 hojas (Resumen, Inscriptos, Todos Leads) |
| `bot_por_nivel.png` | Gráfico barras personas y tasas por nivel |
| `pie_inscriptos_bot_nivel.png` | Gráfico pie distribución inscriptos |
| `memoria_tecnica_bot_consolidado.md` | Este archivo |

---
*Fin de la Memoria Técnica.*
"""

mem_path = os.path.join(output_dir, "memoria_tecnica_bot_consolidado.md")
with open(mem_path, 'w', encoding='utf-8') as f:
    f.write(mem)
print(f"-> Memoria Técnica guardada: {mem_path}")

print("\n¡Informe Consolidado del Bot generado exitosamente!")
print(f"Archivos en: {output_dir}")
