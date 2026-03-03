import pandas as pd
import numpy as np
import os
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

base_dir = r"h:\Test-Antigravity\marketing_report"
presupuesto_dir = os.path.join(base_dir, "data", "1_raw", "presupuestos")
output_dir = os.path.join(base_dir, "outputs", "Presupuesto_ROI")
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 1. PRESUPUESTO GOOGLE ADS (hardcoded)
# Ingreso 2026: 1-sep-2025 al 17-feb-2026, sin impuestos
# ==========================================
GOOGLE_SPEND = {
    'Grado_Pregrado': 47_387_402.90,
    'Cursos': 0.0,
    'Posgrados': 0.0,
}
GOOGLE_PERIODO = '01/09/2025 - 17/02/2026'

# ==========================================
# 2. FACEBOOK ADS: Cargar export y clasificar
# ==========================================
def classify_fb_segment(nombre):
    n = str(nombre).lower()
    if any(k in n for k in ['posgrado', 'postgrado', 'maestr', 'especiali']):
        return 'Posgrados'
    if 'curso' in n:
        return 'Cursos'
    return 'Grado_Pregrado'

print("Cargando archivos de presupuesto Facebook...")
fb_files = (glob.glob(os.path.join(presupuesto_dir, "*.xlsx")) +
            glob.glob(os.path.join(presupuesto_dir, "*.csv")))

fb_dfs = []
for f in fb_files:
    try:
        if f.endswith('.csv'):
            df_tmp = pd.read_csv(f, encoding='utf-8', errors='replace')
        else:
            df_tmp = pd.read_excel(f)
        fb_dfs.append(df_tmp)
        print(f"  Cargado: {os.path.basename(f)} ({len(df_tmp)} filas)")
    except Exception as e:
        print(f"  Error cargando {f}: {e}")

if not fb_dfs:
    print("[!] No se encontraron archivos en la carpeta presupuestos. Abortando.")
    exit()

fb_raw = pd.concat(fb_dfs, ignore_index=True)

# Normalizar columnas numéricas
for col in ['Importe gastado (ARS)', 'Clientes potenciales', 'Impresiones', 'Clics en el enlace']:
    if col in fb_raw.columns:
        fb_raw[col] = pd.to_numeric(fb_raw[col], errors='coerce').fillna(0)
    else:
        fb_raw[col] = 0

fb_raw['Segmento'] = fb_raw['Nombre de la campaña'].apply(classify_fb_segment)

# Período del export (de nombre de archivo o de columnas)
fb_periodo = 'Sep 2025 - Feb 2026'
if 'Inicio del informe' in fb_raw.columns and 'Fin del informe' in fb_raw.columns:
    fecha_ini = pd.to_datetime(fb_raw['Inicio del informe'], errors='coerce').min()
    fecha_fin = pd.to_datetime(fb_raw['Fin del informe'], errors='coerce').max()
    if pd.notna(fecha_ini) and pd.notna(fecha_fin):
        fb_periodo = f"{fecha_ini.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"

# Agregado por segmento
fb_seg = fb_raw.groupby('Segmento').agg(
    FB_Spend=('Importe gastado (ARS)', 'sum'),
    FB_Leads_Plataforma=('Clientes potenciales', 'sum'),
    FB_Impresiones=('Impresiones', 'sum'),
    FB_Clics=('Clics en el enlace', 'sum'),
    Num_Conjuntos=('Nombre del conjunto de anuncios', 'count'),
).reset_index()
fb_total = fb_raw['Importe gastado (ARS)'].sum()

print(f"\nFacebook total ARS: $ {fb_total:,.2f}")
for _, row in fb_seg.iterrows():
    print(f"  {row['Segmento']}: $ {row['FB_Spend']:,.2f} ({row['FB_Spend']/fb_total*100:.1f}%)")

# Top campañas Grado_Pregrado
fb_top_grado = (
    fb_raw[fb_raw['Segmento'] == 'Grado_Pregrado']
    .groupby('Nombre de la campaña')['Importe gastado (ARS)']
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)
fb_top_grado.columns = ['Campana', 'Spend']

# ==========================================
# 3. LEADS Y CONVERSIONES DESDE CSVs
# ==========================================
print("\nCalculando metricas por canal desde CSVs de leads...")
segmentos = ['Grado_Pregrado', 'Cursos', 'Posgrados']
results = {}

for seg in segmentos:
    leads_csv = os.path.join(base_dir, "outputs", "Data_Base", seg, "reporte_marketing_leads_completos.csv")
    insc_csv = os.path.join(base_dir, "outputs", "Data_Base", seg, "reporte_marketing_inscriptos_origenes.csv")
    if not os.path.exists(leads_csv):
        print(f"  [!] No existe CSV para {seg}, omitiendo.")
        continue

    df = pd.read_csv(leads_csv, low_memory=False)
    df_insc = pd.read_csv(insc_csv, low_memory=False)

    # Max fecha inscripcion (upper bound)
    max_insc_ts = pd.Timestamp.now()
    for col in ['Insc_Fecha Pago', 'Fecha Pago']:
        if col in df_insc.columns:
            d = pd.to_datetime(df_insc[col], format='mixed', errors='coerce')
            d = d[d <= pd.Timestamp.now()]
            if not d.isna().all():
                max_insc_ts = d.max()
                break

    # Clasificar Match
    df['_mc'] = df['Match_Tipo'].apply(
        lambda v: 'exacto' if 'Exacto' in str(v) else ('fuzzy' if 'Fuzzy' in str(v) else 'no_match')
    )
    df_main = df[df['_mc'] != 'fuzzy'].copy()

    # PK dedup persona
    df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
        df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

    # UTM y fuente
    df_main['_utm'] = df_main.get('UtmSource', pd.Series('', index=df_main.index)).astype(str).str.lower().str.strip()
    df_main['_fuente'] = pd.to_numeric(df_main.get('FuenteLead', pd.Series(dtype='float')), errors='coerce')

    # Fecha creacion
    df_main['_fecha'] = pd.to_datetime(
        df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

    # Ventana conversión (cohorte 2026)
    if seg == 'Grado_Pregrado':
        df_conv = df_main[
            (df_main['_fecha'] >= '2025-09-01') &
            (df_main['_fecha'] <= max_insc_ts)
        ].copy()
    else:
        df_conv = df_main[df_main['_fecha'] <= max_insc_ts].copy()

    # Métricas por canal
    def channel_metrics(df_c, mask):
        sub = df_c[mask].drop_duplicates(subset='_pk')
        return len(sub), int((sub['_mc'] == 'exacto').sum())

    mask_google = df_conv['_utm'].str.contains('google', na=False)
    meta_kw = ['fb', 'facebook', 'ig', 'instagram', 'meta']
    mask_fb_utm = df_conv['_utm'].str.contains('|'.join(meta_kw), na=False)
    mask_fb_fuente = df_conv['_fuente'] == 18
    mask_fb = mask_fb_utm | mask_fb_fuente

    g_leads, g_conv = channel_metrics(df_conv, mask_google)
    f_leads, f_conv = channel_metrics(df_conv, mask_fb)

    total_conv = df_conv.drop_duplicates(subset='_pk')
    total_leads = len(total_conv)
    total_conv_n = int((total_conv['_mc'] == 'exacto').sum())

    results[seg] = {
        'max_insc_ts': max_insc_ts,
        'total_leads': total_leads,
        'total_conv': total_conv_n,
        'google_leads': g_leads,
        'google_conv': g_conv,
        'fb_leads_crm': f_leads,
        'fb_conv': f_conv,
    }
    print(f"  {seg}: Google={g_leads} leads / {g_conv} insc | Facebook CRM={f_leads} leads / {f_conv} insc")

# ==========================================
# 4. TABLA MÉTRICAS CONSOLIDADA
# ==========================================
metrics = []
for seg in segmentos:
    if seg not in results:
        continue
    r = results[seg]
    g_spend = GOOGLE_SPEND.get(seg, 0)
    fb_row = fb_seg[fb_seg['Segmento'] == seg]
    f_spend = float(fb_row['FB_Spend'].values[0]) if len(fb_row) > 0 else 0
    f_leads_plat = int(fb_row['FB_Leads_Plataforma'].values[0]) if len(fb_row) > 0 else 0

    def safe_div(a, b):
        return a / b if b > 0 else 0

    # ROI: leer Insc_Haber de inscriptos atribuidos para estimar ingreso atribuible
    # ROI = (Ingreso_Atribuido - Inversion) / Inversion * 100
    leads_csv_path = os.path.join(base_dir, "outputs", "Data_Base", seg,
                                  "reporte_marketing_leads_completos.csv")
    rev_google, rev_fb = 0.0, 0.0
    try:
        df_tmp = pd.read_csv(leads_csv_path,
                             usecols=['Match_Tipo', 'Insc_Haber', '_mc_tmp'],
                             low_memory=False)
    except Exception:
        df_tmp = pd.read_csv(leads_csv_path,
                             usecols=lambda c: c in ['Match_Tipo', 'Insc_Haber', 'UtmSource',
                                                     'FuenteLead', 'DNI', 'Correo'],
                             low_memory=False)
        df_tmp['_is_exacto'] = df_tmp['Match_Tipo'].astype(str).str.contains('Exacto')
        df_tmp['_pk2'] = df_tmp['DNI'].astype(str).str.split('.').str[0].str.strip()
        df_tmp.loc[df_tmp['_pk2'].isin(['nan','','None']), '_pk2'] = \
            df_tmp.loc[df_tmp['_pk2'].isin(['nan','','None']), 'Correo'].astype(str)
        df_tmp['_utm'] = df_tmp.get('UtmSource', pd.Series('', index=df_tmp.index)).astype(str).str.lower()
        df_tmp['_fuente'] = pd.to_numeric(df_tmp.get('FuenteLead', pd.Series(dtype='float')),
                                          errors='coerce')
        df_tmp['_haber'] = pd.to_numeric(df_tmp.get('Insc_Haber', pd.Series(dtype='float')),
                                         errors='coerce').fillna(0)

        exactos = df_tmp[df_tmp['_is_exacto']].drop_duplicates(subset='_pk2')
        mask_g = exactos['_utm'].str.contains('google', na=False)
        meta_kw = ['fb', 'facebook', 'ig', 'instagram', 'meta']
        mask_f = exactos['_utm'].str.contains('|'.join(meta_kw), na=False) | (exactos['_fuente'] == 18)
        rev_google = float(exactos[mask_g]['_haber'].sum())
        rev_fb     = float(exactos[mask_f]['_haber'].sum())

    total_spend = g_spend + f_spend
    total_conv  = r['google_conv'] + r['fb_conv']
    total_rev   = rev_google + rev_fb
    roi_google  = safe_div(rev_google - g_spend, g_spend) * 100 if g_spend > 0 else 0
    roi_fb      = safe_div(rev_fb     - f_spend, f_spend) * 100 if f_spend > 0 else 0
    roi_total   = safe_div(total_rev  - total_spend, total_spend) * 100 if total_spend > 0 else 0

    metrics.append({
        'Segmento': seg,
        'G_Spend': g_spend,
        'G_Leads': r['google_leads'],
        'G_Conv': r['google_conv'],
        'G_CPL': safe_div(g_spend, r['google_leads']),
        'G_CPA': safe_div(g_spend, r['google_conv']),
        'G_RevAtrib': rev_google,
        'G_ROI': roi_google,
        'F_Spend': f_spend,
        'F_Leads_Plat': f_leads_plat,
        'F_Leads_CRM': r['fb_leads_crm'],
        'F_Conv': r['fb_conv'],
        'F_CPL': safe_div(f_spend, r['fb_leads_crm']),
        'F_CPA': safe_div(f_spend, r['fb_conv']),
        'F_RevAtrib': rev_fb,
        'F_ROI': roi_fb,
        'Total_Spend': total_spend,
        'Total_RevAtrib': total_rev,
        'ROI_Total': roi_total,
    })

df_metrics = pd.DataFrame(metrics)

# ==========================================
# 5. CHARTS
# ==========================================
print("\nGenerando charts...")

# - Chart 1: Facebook spend por segmento (pie) -
fig, ax = plt.subplots(figsize=(7, 5))
fb_pie = fb_seg[fb_seg['FB_Spend'] > 0].copy()
colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
pcts = fb_pie['FB_Spend'] / fb_pie['FB_Spend'].sum() * 100
labels = [f"{row['Segmento']}\n$ {row['FB_Spend']/1_000_000:.1f}M ({pct:.1f}%)"
          for (_, row), pct in zip(fb_pie.iterrows(), pcts)]
ax.pie(fb_pie['FB_Spend'], labels=labels, colors=colors[:len(fb_pie)],
       startangle=140, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
ax.set_title('Facebook Ads: Inversion por Segmento\n(Sep 2025 - Feb 2026)', fontsize=12, fontweight='bold')
pie_path = os.path.join(output_dir, 'fb_spend_pie.png')
plt.savefig(pie_path, bbox_inches='tight', dpi=150)
plt.close()

# - Chart 2: CPL y CPA Google vs Facebook (Grado_Pregrado) -
grado_row = df_metrics[df_metrics['Segmento'] == 'Grado_Pregrado']
comp_path = None
if len(grado_row) > 0 and grado_row.iloc[0]['G_Spend'] > 0:
    r = grado_row.iloc[0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    channels = ['Google Ads', 'Facebook\nAds']
    colors_bar = ['#4285f4', '#1877f2']

    # CPL
    cpl_vals = [r['G_CPL'], r['F_CPL']]
    bars = axes[0].bar(channels, cpl_vals, color=colors_bar, width=0.5, edgecolor='white')
    axes[0].set_title('CPL - Costo por Lead (CRM)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('ARS')
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'$ {v/1000:.0f}K'))
    for bar, val in zip(bars, cpl_vals):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                     f'$ {val:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # CPA
    cpa_vals = [r['G_CPA'], r['F_CPA']]
    bars2 = axes[1].bar(channels, cpa_vals, color=colors_bar, width=0.5, edgecolor='white')
    axes[1].set_title('CPA - Costo por Inscripto', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('ARS')
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'$ {v/1_000_000:.1f}M' if v >= 1_000_000 else f'$ {v/1000:.0f}K'))
    for bar, val in zip(bars2, cpa_vals):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                     f'$ {val:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.suptitle('Grado y Pregrado - Google Ads vs Facebook Ads', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    comp_path = os.path.join(output_dir, 'canal_cpl_cpa.png')
    plt.savefig(comp_path, bbox_inches='tight', dpi=150)
    plt.close()

# - Chart 3: Top campañas Facebook Grado_Pregrado (barh) -
top_camp_path = None
if len(fb_top_grado) > 0:
    fig, ax = plt.subplots(figsize=(10, 6))
    top = fb_top_grado.head(12).iloc[::-1]
    names_short = [n[:45] + '...' if len(n) > 45 else n for n in top['Campana']]
    bars = ax.barh(names_short, top['Spend'], color='#1877f2', edgecolor='white')
    ax.set_xlabel('Importe Gastado (ARS)')
    ax.set_title('Top Campanas Facebook - Grado y Pregrado (por inversion)', fontsize=11, fontweight='bold')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'$ {v/1_000_000:.1f}M'))
    for bar, val in zip(bars, top['Spend']):
        ax.text(bar.get_width() + top['Spend'].max() * 0.01, bar.get_y() + bar.get_height()/2,
                f'$ {val/1_000_000:.2f}M', va='center', fontsize=8)
    plt.tight_layout()
    top_camp_path = os.path.join(output_dir, 'fb_top_campanas_grado.png')
    plt.savefig(top_camp_path, bbox_inches='tight', dpi=150)
    plt.close()

# ==========================================
# 6. GENERAR PDF
# ==========================================
print("Generando PDF...")

BLUE = (41, 128, 185)
LIGHT_BLUE = (235, 245, 255)
DARK = (30, 30, 30)
GRAY = (120, 120, 120)

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*DARK)
        self.cell(0, 9, 'UCASAL - Inversion Publicitaria y ROI  |  Ingreso 2026', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(200, 200, 200)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*GRAY)
        self.cell(0, 8, f'Pagina {self.page_no()}  |  Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C')

    def section_title(self, txt):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*BLUE)
        self.cell(0, 9, txt, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*DARK)
        self.ln(1)

    def kv_row(self, label, value, bold_value=False):
        self.set_font('Helvetica', '', 10)
        self.cell(80, 7, label)
        self.set_font('Helvetica', 'B' if bold_value else '', 10)
        self.cell(0, 7, value, new_x='LMARGIN', new_y='NEXT')

    def table_header(self, headers, widths):
        self.set_fill_color(*BLUE)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        for h, w in zip(headers, widths):
            self.cell(w, 8, h, border=1, fill=True, align='C')
        self.ln()
        self.set_text_color(*DARK)

    def table_row(self, values, widths, fill):
        self.set_fill_color(*(LIGHT_BLUE if fill else (255, 255, 255)))
        self.set_font('Helvetica', '', 9)
        for val, w in zip(values, widths):
            self.cell(w, 7, str(val), border=1, fill=True, align='C')
        self.ln()

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# =============== PÁGINA 1: RESUMEN EJECUTIVO ===============
pdf.section_title('Inversion Publicitaria - Grado y Pregrado (Ingreso 2026)')
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(*GRAY)
pdf.cell(0, 6, f'Periodo Google Ads: {GOOGLE_PERIODO}  |  Periodo Facebook Ads: {fb_periodo}', new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(3)

# Totales de inversión
total_google = sum(GOOGLE_SPEND.values())
total_inv = total_google + fb_total

pdf.set_font('Helvetica', 'B', 10)
pdf.set_fill_color(*LIGHT_BLUE)
pdf.cell(0, 8, '  Resumen de Inversion Total (ARS)', fill=True, new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', '', 10)

inv_data = [
    ('Google Ads (sin impuestos, Grado y Pregrado):', f'$ {total_google:,.2f}'),
    ('Facebook Ads (todas las campanas):', f'$ {fb_total:,.2f}'),
]
for label, val in inv_data:
    pdf.cell(110, 7, label)
    pdf.cell(0, 7, val, new_x='LMARGIN', new_y='NEXT')

pdf.set_font('Helvetica', 'B', 10)
pdf.cell(110, 7, 'TOTAL INVERTIDO:')
pdf.cell(0, 7, f'$ {total_inv:,.2f}', new_x='LMARGIN', new_y='NEXT')
pdf.ln(5)

# Tabla KPIs Google vs Facebook - Grado_Pregrado
pdf.section_title('KPIs por Canal - Grado y Pregrado (Muestra Cohorte 2026)')

hdrs = ['Canal', 'Inversion ARS', 'Leads CRM', 'Inscriptos', 'CPL', 'CPA', 'Rev.Atribuida', 'ROI']
wids = [27, 33, 22, 22, 27, 27, 30, 20]
pdf.table_header(hdrs, wids)

if len(grado_row) > 0:
    r = grado_row.iloc[0]
    rows_data = [
        ('Google Ads',
         f"$ {r['G_Spend']:,.0f}", f"{int(r['G_Leads']):,}", f"{int(r['G_Conv']):,}",
         f"$ {r['G_CPL']:,.0f}", f"$ {r['G_CPA']:,.0f}",
         f"$ {r['G_RevAtrib']:,.0f}", f"{r['G_ROI']:+.0f}%"),
        ('Facebook Ads',
         f"$ {r['F_Spend']:,.0f}", f"{int(r['F_Leads_CRM']):,}", f"{int(r['F_Conv']):,}",
         f"$ {r['F_CPL']:,.0f}", f"$ {r['F_CPA']:,.0f}",
         f"$ {r['F_RevAtrib']:,.0f}", f"{r['F_ROI']:+.0f}%"),
        ('TOTAL',
         f"$ {r['Total_Spend']:,.0f}", '-', f"{int(r['G_Conv']+r['F_Conv']):,}",
         '-', '-',
         f"$ {r['Total_RevAtrib']:,.0f}", f"{r['ROI_Total']:+.0f}%"),
    ]
    for i, row_d in enumerate(rows_data):
        pdf.table_row(row_d, wids, fill=(i % 2 == 0))

pdf.ln(3)
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.multi_cell(0, 5,
    'CPL = Costo por Lead CRM (personas deduplicadas, ventana cohorte). '
    'CPA = Inversion / Inscriptos atribuidos (Match Exacto). '
    'Rev. Atribuida = suma de Insc_Haber de inscriptos cuyo primer contacto fue via ese canal. '
    'ROI = (Rev.Atribuida - Inversion) / Inversion * 100. '
    'Ingreso es el haber registrado al momento de inscripcion (cuota o arancel), no LTV completo. '
    'Google sin impuestos. Facebook segun export plataforma.')
pdf.set_text_color(*DARK)
pdf.ln(4)

# Tabla Facebook por segmento
pdf.section_title('Facebook Ads: Inversion y Leads por Segmento')
hdrs2 = ['Segmento', 'Inversion ARS', '% del Total', 'Leads (Plataforma)', 'Conj. Anuncios']
wids2 = [40, 40, 25, 40, 35]
pdf.table_header(hdrs2, wids2)

for i, row_d in fb_seg.sort_values('FB_Spend', ascending=False).iterrows():
    pct = row_d['FB_Spend'] / fb_total * 100 if fb_total > 0 else 0
    pdf.table_row([
        row_d['Segmento'],
        f"$ {row_d['FB_Spend']:,.0f}",
        f"{pct:.1f}%",
        f"{int(row_d['FB_Leads_Plataforma']):,}",
        f"{int(row_d['Num_Conjuntos']):,}",
    ], wids2, fill=(i % 2 == 0))

# Total row
pdf.set_font('Helvetica', 'B', 9)
pdf.set_fill_color(220, 230, 240)
total_leads_plat = int(fb_seg['FB_Leads_Plataforma'].sum())
total_conj = int(fb_seg['Num_Conjuntos'].sum())
pdf.table_row(['TOTAL', f"$ {fb_total:,.0f}", '100%', f"{total_leads_plat:,}", f"{total_conj:,}"], wids2, fill=True)

# =============== PÁGINA 2: CHARTS ===============
pdf.add_page()
pdf.section_title('Google Ads vs Facebook Ads - Grado y Pregrado')

if comp_path and os.path.exists(comp_path):
    pdf.image(comp_path, x=10, w=185)
    pdf.ln(4)
else:
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 8, '(No hay datos de Google Ads para comparar en este segmento)', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

# Tabla detalle Google vs Facebook con todos los segmentos (incluye ROI)
pdf.section_title('Detalle por Segmento')
hdrs3 = ['Segmento', 'Canal', 'Inversion', 'Leads CRM', 'Insc.', 'CPL', 'CPA', 'Rev.Atrib.', 'ROI']
wids3 = [25, 20, 32, 22, 18, 25, 25, 28, 18]
pdf.table_header(hdrs3, wids3)

fill_toggle = True
for _, row_d in df_metrics.iterrows():
    seg_label = row_d['Segmento'].replace('_', ' ')
    for canal, sk, lk, ck, cplk, cpak, rvk, roik in [
        ('Google Ads', 'G_Spend', 'G_Leads', 'G_Conv', 'G_CPL', 'G_CPA', 'G_RevAtrib', 'G_ROI'),
        ('Facebook',   'F_Spend', 'F_Leads_CRM', 'F_Conv', 'F_CPL', 'F_CPA', 'F_RevAtrib', 'F_ROI'),
    ]:
        spend_v = row_d[sk]
        if spend_v == 0 and canal == 'Google Ads':
            continue
        pdf.table_row([
            seg_label if canal == 'Google Ads' else '',
            canal,
            f"$ {spend_v:,.0f}",
            f"{int(row_d[lk]):,}",
            f"{int(row_d[ck]):,}",
            f"$ {row_d[cplk]:,.0f}" if row_d[cplk] > 0 else '-',
            f"$ {row_d[cpak]:,.0f}" if row_d[cpak] > 0 else '-',
            f"$ {row_d[rvk]:,.0f}" if row_d[rvk] > 0 else '-',
            f"{row_d[roik]:+.0f}%" if row_d[roik] != 0 else '-',
        ], wids3, fill=fill_toggle)
        fill_toggle = not fill_toggle

# =============== PÁGINA 3: FACEBOOK DETALLE ===============
pdf.add_page()
pdf.section_title('Facebook Ads: Distribucion de Inversion por Segmento')

if os.path.exists(pie_path):
    pdf.image(pie_path, x=30, w=150)
    pdf.ln(4)

if top_camp_path and os.path.exists(top_camp_path):
    pdf.section_title('Top Campanas Facebook - Grado y Pregrado (por inversion)')
    pdf.image(top_camp_path, x=10, w=185)
    pdf.ln(4)

# Tabla top campañas Grado numéricamente
pdf.section_title('Top 15 Campanas Facebook - Grado y Pregrado (detalle)')
hdrs4 = ['#', 'Campana (nombre abreviado)', 'Inversion ARS', '% del segmento']
wids4 = [10, 110, 40, 30]
pdf.table_header(hdrs4, wids4)

grado_spend_total = fb_seg[fb_seg['Segmento'] == 'Grado_Pregrado']['FB_Spend'].values[0] if len(fb_seg[fb_seg['Segmento'] == 'Grado_Pregrado']) > 0 else 1
for idx, (_, row_d) in enumerate(fb_top_grado.iterrows(), 1):
    nombre_short = str(row_d['Campana'])[:60]
    pct = row_d['Spend'] / grado_spend_total * 100 if grado_spend_total > 0 else 0
    pdf.table_row([
        str(idx),
        nombre_short,
        f"$ {row_d['Spend']:,.0f}",
        f"{pct:.1f}%",
    ], wids4, fill=(idx % 2 == 0))

pdf.ln(4)
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.multi_cell(0, 5,
    'Clasificacion de campanas: "Posgrado/Postgrado/Maestr/Especiali" -> Posgrados | '
    '"Curso" -> Cursos | resto -> Grado y Pregrado. '
    'Las campanas de Branding general y Remarketing quedan clasificadas en Grado y Pregrado '
    'por ser el segmento principal del ingreso 2026.')

# ==========================================
# 7. OUTPUT
# ==========================================
pdf_path = os.path.join(output_dir, 'Presupuesto_ROI_Ingreso2026.pdf')
pdf.output(pdf_path)
print(f"\n-> PDF generado: {pdf_path}")
print(f"-> Total invertido: $ {total_inv:,.2f} ARS")
print("Proceso finalizado.")
