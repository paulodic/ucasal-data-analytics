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
    for col in ['Insc_Fecha Pago', 'Fecha Pago', 'Insc_Fecha Aplicación', 'Fecha Aplicación']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], errors='coerce', dayfirst=True)
            valid = dates[dates <= pd.Timestamp.now()]
            if not valid.isna().all():
                d = valid.max()
                return f"{d.day} de {meses_es[d.month]} de {d.year}"
    d = datetime.now()
    return f"{d.day} de {meses_es[d.month]} de {d.year}"

def classify_mc(v):
    s = str(v)
    if 'Si (Lead -> Inscripto Exacto)' in s: return 'exacto'
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

max_date_str = max(max_dates, key=lambda x: x) if max_dates else datetime.now().strftime("%d de %B de %Y")

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
    df_seg = df_bot_dedup[df_bot_dedup['Segmento'] == seg]
    consultas_seg = len(df_seg_all)
    total_seg = len(df_seg)
    insc_seg = len(df_seg[df_seg['_mc'] == 'exacto'])
    tasa_seg = (insc_seg / total_seg * 100) if total_seg > 0 else 0
    resumen_seg.append({
        'Segmento': seg,
        'Consultas_Total': consultas_seg,
        'Personas_Unicas': total_seg,
        'Inscriptos': insc_seg,
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
    'Segmento', 'Nombre', 'DNI', 'Correo', 'FuenteLead', 'Match_Tipo',
    'Consulta: Fecha de creación',
    'UtmSource', 'UtmCampaign', 'UtmMedium',
    'Insc_Apellido y Nombre', 'Insc_DNI', 'Insc_Email',
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
df_listado.index += 1  # Numerar desde 1

print(f"Inscriptos del bot a listar: {len(df_listado):,}")

# ==========================================
# MARKDOWN
# ==========================================
md = f"# Informe Consolidado del Bot / Chatbot — Todos los Niveles\n\n"
md += f"**Datos actualizados al {max_date_str}**\n\n"
md += "> Este informe consolida el rendimiento del canal Bot/Chatbot (FuenteLead = 907) a través de todos los segmentos académicos: Grado y Pregrado, Cursos, y Posgrados.\n\n"

md += "## 1. Resumen Ejecutivo Consolidado\n\n"
md += f"| Métrica | Valor |\n|---------|-------|\n"
md += f"| Total Consultas (Registros) vía Bot | {total_consultas_bot:,} |\n"
md += f"| Total Personas Únicas vía Bot | {total_bot:,} |\n"
md += f"| Total Inscriptos del Bot | {total_insc_bot:,} |\n"
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
cols_pdf = ['Segmento', 'Nombre', 'DNI']
for c in ['Insc_Carrera Nombre', 'Carrera']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break
for c in ['Insc_Fecha Pago', 'Insc_Fecha Aplicación']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break
for c in ['Insc_Sede Nombre', 'Sede Nombre']:
    if c in df_listado.columns:
        cols_pdf.append(c)
        break

cols_pdf = [c for c in cols_pdf if c in df_listado.columns]
# Proporciones de ancho: Segmento=12%, Nombre=22%, DNI=10%, Carrera=28%, Fecha=14%, Sede=14%
_props = [0.12, 0.22, 0.10, 0.28, 0.14, 0.14]
_ew2 = pdf.epw
col_w_pdf = [_ew2 * _props[i] for i in range(len(cols_pdf))]

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
print("\n¡Informe Consolidado del Bot generado exitosamente!")
print(f"Archivos en: {output_dir}")
