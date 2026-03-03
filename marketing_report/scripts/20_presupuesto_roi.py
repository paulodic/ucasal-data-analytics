"""
20_presupuesto_roi.py
Informe de Inversión Publicitaria, KPIs y ROI por segmento.
Genera PDF landscape con tablas detalladas por segmento + Excel de respaldo.

Periodos de análisis:
  - Grado_Pregrado: cohorte Ingreso 2026 → leads desde 01/09/2025
  - Cursos:         año calendario 2026  → leads desde 01/01/2026
  - Posgrados:      año calendario 2026  → leads desde 01/01/2026
"""
import pandas as pd
import numpy as np
import os, glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
base_dir = r"h:\Test-Antigravity\marketing_report"
presupuesto_dir = os.path.join(base_dir, "data", "1_raw", "presupuestos")
output_dir = os.path.join(base_dir, "outputs", "Presupuesto_ROI")
os.makedirs(output_dir, exist_ok=True)

SEGMENTOS = ['Grado_Pregrado', 'Cursos', 'Posgrados']

# Ventana de leads por segmento (fecha inicio de la cohorte/período)
PERIODO_INICIO = {
    'Grado_Pregrado': pd.Timestamp('2025-09-01'),
    'Cursos':         pd.Timestamp('2026-01-01'),
    'Posgrados':      pd.Timestamp('2026-01-01'),
}

PERIODO_LABEL = {
    'Grado_Pregrado': 'Cohorte Ingreso 2026 (desde 01/09/2025)',
    'Cursos':         'Año Calendario 2026 (desde 01/01/2026)',
    'Posgrados':      'Año Calendario 2026 (desde 01/01/2026)',
}

# Google Ads spend por segmento (hardcoded, sin impuestos)
GOOGLE_SPEND = {
    'Grado_Pregrado': 47_387_402.90,
    'Cursos': 0.0,
    'Posgrados': 0.0,
}
GOOGLE_PERIODO = '01/09/2025 - 17/02/2026'

# Helpers
def safe_div(a, b):
    return a / b if b > 0 else 0

def fmt_ars(v):
    """Formato moneda ARS legible."""
    if abs(v) >= 1_000_000:
        return f"$ {v/1_000_000:,.2f}M"
    if abs(v) >= 1_000:
        return f"$ {v/1_000:,.1f}K"
    return f"$ {v:,.0f}"

def fmt_ars_full(v):
    return f"$ {v:,.0f}"

def fmt_pct(v):
    return f"{v:+.1f}%" if v != 0 else "-"

# ============================================================
# 1. CARGAR FACEBOOK ADS
# ============================================================
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
    print("[!] No se encontraron archivos en la carpeta presupuestos.")
    fb_raw = pd.DataFrame()
else:
    fb_raw = pd.concat(fb_dfs, ignore_index=True)

# Normalizar columnas numéricas
for col in ['Importe gastado (ARS)', 'Clientes potenciales', 'Impresiones', 'Clics en el enlace']:
    if col in fb_raw.columns:
        fb_raw[col] = pd.to_numeric(fb_raw[col], errors='coerce').fillna(0)
    else:
        fb_raw[col] = 0

def classify_fb_segment(nombre):
    n = str(nombre).lower()
    if any(k in n for k in ['posgrado', 'postgrado', 'maestr', 'especiali']):
        return 'Posgrados'
    if 'curso' in n:
        return 'Cursos'
    return 'Grado_Pregrado'

if not fb_raw.empty:
    fb_raw['Segmento'] = fb_raw['Nombre de la campaña'].apply(classify_fb_segment)

# Período del export Facebook
fb_periodo = 'Sep 2025 - Feb 2026'
if not fb_raw.empty and 'Inicio del informe' in fb_raw.columns:
    fecha_ini = pd.to_datetime(fb_raw['Inicio del informe'], errors='coerce').min()
    fecha_fin = pd.to_datetime(fb_raw['Fin del informe'], errors='coerce').max()
    if pd.notna(fecha_ini) and pd.notna(fecha_fin):
        fb_periodo = f"{fecha_ini.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"

# Agregado por segmento
fb_seg = pd.DataFrame()
fb_total = 0
if not fb_raw.empty:
    fb_seg = fb_raw.groupby('Segmento').agg(
        FB_Spend=('Importe gastado (ARS)', 'sum'),
        FB_Leads_Plat=('Clientes potenciales', 'sum'),
        FB_Impresiones=('Impresiones', 'sum'),
        FB_Clics=('Clics en el enlace', 'sum'),
        Num_Conjuntos=('Nombre del conjunto de anuncios', 'count'),
    ).reset_index()
    fb_total = fb_raw['Importe gastado (ARS)'].sum()

print(f"\nFacebook total ARS: {fmt_ars_full(fb_total)}")
for _, row in fb_seg.iterrows():
    print(f"  {row['Segmento']}: {fmt_ars_full(row['FB_Spend'])} ({row['FB_Spend']/fb_total*100:.1f}%)" if fb_total > 0 else "")

# Top campañas por segmento
fb_top_by_seg = {}
if not fb_raw.empty:
    for seg in SEGMENTOS:
        top = (fb_raw[fb_raw['Segmento'] == seg]
               .groupby('Nombre de la campaña')
               .agg(Spend=('Importe gastado (ARS)', 'sum'),
                    Leads_Plat=('Clientes potenciales', 'sum'),
                    Impresiones=('Impresiones', 'sum'),
                    Clics=('Clics en el enlace', 'sum'))
               .sort_values('Spend', ascending=False)
               .head(15)
               .reset_index())
        top.rename(columns={'Nombre de la campaña': 'Campana'}, inplace=True)
        if not top.empty:
            top['CPL_Plat'] = top.apply(lambda r: safe_div(r['Spend'], r['Leads_Plat']), axis=1)
            fb_top_by_seg[seg] = top

# ============================================================
# 2. LEADS, CONVERSIONES Y REVENUE POR SEGMENTO
# ============================================================
print("\nCalculando métricas por canal desde CSVs de leads...")
seg_data = {}

for seg in SEGMENTOS:
    leads_csv = os.path.join(base_dir, "outputs", "Data_Base", seg, "reporte_marketing_leads_completos.csv")
    insc_csv  = os.path.join(base_dir, "outputs", "Data_Base", seg, "reporte_marketing_inscriptos_origenes.csv")
    if not os.path.exists(leads_csv):
        print(f"  [!] No existe CSV para {seg}, omitiendo.")
        continue

    df = pd.read_csv(leads_csv, low_memory=False)
    df_insc = pd.read_csv(insc_csv, low_memory=False)

    # Max fecha inscripción
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
        lambda v: 'exacto' if 'Exacto' in str(v) else ('fuzzy' if 'Fuzzy' in str(v) else 'no_match'))

    # Excluir fuzzy de conteos de conversión
    df_main = df[df['_mc'] != 'fuzzy'].copy()

    # PK dedup persona
    df_main['_pk'] = df_main['DNI'].astype(str).str.split('.').str[0].str.strip()
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
        df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

    # UTM y fuente
    df_main['_utm'] = df_main.get('UtmSource', pd.Series('', index=df_main.index)).astype(str).str.lower().str.strip()
    df_main['_fuente'] = pd.to_numeric(df_main.get('FuenteLead', pd.Series(dtype='float')), errors='coerce')

    # Fecha creación
    df_main['_fecha'] = pd.to_datetime(
        df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

    # Revenue (Insc_Haber)
    df_main['_haber'] = pd.to_numeric(df_main.get('Insc_Haber', pd.Series(dtype='float')), errors='coerce').fillna(0)

    # Ventana de conversión según segmento
    inicio = PERIODO_INICIO[seg]
    df_conv = df_main[(df_main['_fecha'] >= inicio) & (df_main['_fecha'] <= max_insc_ts)].copy()

    # Deduplicar por persona
    df_dedup = df_conv.sort_values('_mc').drop_duplicates(subset='_pk', keep='first')

    # Masks de canal
    mask_google = df_dedup['_utm'].str.contains('google', na=False)
    meta_kw = ['fb', 'facebook', 'ig', 'instagram', 'meta']
    mask_fb = df_dedup['_utm'].str.contains('|'.join(meta_kw), na=False) | (df_dedup['_fuente'] == 18)
    mask_bot = df_dedup['_fuente'] == 907
    mask_otros = ~mask_google & ~mask_fb & ~mask_bot

    # Función para extraer métricas de un canal
    def canal_metrics(sub):
        n_leads = len(sub)
        n_conv = int((sub['_mc'] == 'exacto').sum())
        rev = float(sub[sub['_mc'] == 'exacto']['_haber'].sum())
        return n_leads, n_conv, rev

    g_leads, g_conv, g_rev = canal_metrics(df_dedup[mask_google])
    f_leads, f_conv, f_rev = canal_metrics(df_dedup[mask_fb])
    b_leads, b_conv, b_rev = canal_metrics(df_dedup[mask_bot])
    o_leads, o_conv, o_rev = canal_metrics(df_dedup[mask_otros])
    t_leads, t_conv, t_rev = canal_metrics(df_dedup)

    # Facebook extra: leads plataforma y spend
    fb_row = fb_seg[fb_seg['Segmento'] == seg] if not fb_seg.empty else pd.DataFrame()
    f_spend = float(fb_row['FB_Spend'].values[0]) if len(fb_row) > 0 else 0
    f_leads_plat = int(fb_row['FB_Leads_Plat'].values[0]) if len(fb_row) > 0 else 0
    fb_impresiones = int(fb_row['FB_Impresiones'].values[0]) if len(fb_row) > 0 else 0
    fb_clics = int(fb_row['FB_Clics'].values[0]) if len(fb_row) > 0 else 0

    g_spend = GOOGLE_SPEND.get(seg, 0)
    total_spend = g_spend + f_spend

    # Tasa de conversión
    tasa_google = safe_div(g_conv, g_leads) * 100
    tasa_fb = safe_div(f_conv, f_leads) * 100
    tasa_bot = safe_div(b_conv, b_leads) * 100
    tasa_total = safe_div(t_conv, t_leads) * 100

    seg_data[seg] = {
        'max_insc_ts': max_insc_ts,
        'max_insc_str': max_insc_ts.strftime('%d/%m/%Y'),
        'inicio': inicio,
        'ventana': f"{inicio.strftime('%d/%m/%Y')} - {max_insc_ts.strftime('%d/%m/%Y')}",
        'total_leads_crm': t_leads,
        'total_conv': t_conv,
        'total_rev': t_rev,
        'tasa_total': tasa_total,
        # Google
        'g_spend': g_spend, 'g_leads': g_leads, 'g_conv': g_conv, 'g_rev': g_rev,
        'g_cpl': safe_div(g_spend, g_leads), 'g_cpa': safe_div(g_spend, g_conv),
        'g_roi': safe_div(g_rev - g_spend, g_spend) * 100 if g_spend > 0 else 0,
        'tasa_google': tasa_google,
        # Facebook
        'f_spend': f_spend, 'f_leads_crm': f_leads, 'f_leads_plat': f_leads_plat,
        'f_conv': f_conv, 'f_rev': f_rev,
        'f_cpl': safe_div(f_spend, f_leads), 'f_cpa': safe_div(f_spend, f_conv),
        'f_roi': safe_div(f_rev - f_spend, f_spend) * 100 if f_spend > 0 else 0,
        'f_impresiones': fb_impresiones, 'f_clics': fb_clics,
        'f_cpl_plat': safe_div(f_spend, f_leads_plat),
        'tasa_fb': tasa_fb,
        # Bot
        'b_leads': b_leads, 'b_conv': b_conv, 'b_rev': b_rev, 'tasa_bot': tasa_bot,
        # Otros
        'o_leads': o_leads, 'o_conv': o_conv, 'o_rev': o_rev,
        # Totales inversión
        'total_spend': total_spend,
        'roi_total': safe_div(t_rev - total_spend, total_spend) * 100 if total_spend > 0 else 0,
    }
    print(f"  {seg} [{PERIODO_LABEL[seg]}]:")
    print(f"    Ventana: {seg_data[seg]['ventana']}")
    print(f"    Leads CRM (dedup): {t_leads:,}  |  Inscriptos exactos: {t_conv:,}  |  Tasa: {tasa_total:.2f}%")
    print(f"    Google: {g_leads:,} leads / {g_conv:,} insc / Rev {fmt_ars(g_rev)}")
    print(f"    Facebook: {f_leads:,} leads / {f_conv:,} insc / Rev {fmt_ars(f_rev)}")
    print(f"    Bot: {b_leads:,} leads / {b_conv:,} insc / Rev {fmt_ars(b_rev)}")

# ============================================================
# 3. CHARTS
# ============================================================
print("\nGenerando charts...")

# Chart 1: Facebook spend por segmento (pie)
pie_path = os.path.join(output_dir, 'fb_spend_pie.png')
if not fb_seg.empty:
    fig, ax = plt.subplots(figsize=(7, 5))
    fb_pie = fb_seg[fb_seg['FB_Spend'] > 0].copy()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    pcts = fb_pie['FB_Spend'] / fb_pie['FB_Spend'].sum() * 100
    labels = [f"{row['Segmento']}\n{fmt_ars(row['FB_Spend'])} ({pct:.1f}%)"
              for (_, row), pct in zip(fb_pie.iterrows(), pcts)]
    ax.pie(fb_pie['FB_Spend'], labels=labels, colors=colors[:len(fb_pie)],
           startangle=140, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    ax.set_title(f'Facebook Ads: Inversión por Segmento\n({fb_periodo})', fontsize=12, fontweight='bold')
    plt.savefig(pie_path, bbox_inches='tight', dpi=150)
    plt.close()

# Chart 2: CPL y CPA por segmento (grouped bar)
cpl_cpa_path = os.path.join(output_dir, 'cpl_cpa_por_segmento.png')
segs_with_data = [s for s in SEGMENTOS if s in seg_data]
if segs_with_data:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(segs_with_data))
    w = 0.35

    # CPL
    g_cpls = [seg_data[s]['g_cpl'] for s in segs_with_data]
    f_cpls = [seg_data[s]['f_cpl'] for s in segs_with_data]
    bars1 = axes[0].bar(x - w/2, g_cpls, w, label='Google Ads', color='#4285f4')
    bars2 = axes[0].bar(x + w/2, f_cpls, w, label='Facebook Ads', color='#1877f2')
    axes[0].set_title('CPL - Costo por Lead (CRM)', fontweight='bold')
    axes[0].set_ylabel('ARS')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([s.replace('_', '\n') for s in segs_with_data], fontsize=9)
    axes[0].legend()
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_ars(v)))
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        if h > 0:
            axes[0].text(bar.get_x() + bar.get_width()/2, h * 1.02,
                         fmt_ars(h), ha='center', fontsize=7, fontweight='bold')

    # CPA
    g_cpas = [seg_data[s]['g_cpa'] for s in segs_with_data]
    f_cpas = [seg_data[s]['f_cpa'] for s in segs_with_data]
    bars3 = axes[1].bar(x - w/2, g_cpas, w, label='Google Ads', color='#4285f4')
    bars4 = axes[1].bar(x + w/2, f_cpas, w, label='Facebook Ads', color='#1877f2')
    axes[1].set_title('CPA - Costo por Inscripto', fontweight='bold')
    axes[1].set_ylabel('ARS')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([s.replace('_', '\n') for s in segs_with_data], fontsize=9)
    axes[1].legend()
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_ars(v)))
    for bar in list(bars3) + list(bars4):
        h = bar.get_height()
        if h > 0:
            axes[1].text(bar.get_x() + bar.get_width()/2, h * 1.02,
                         fmt_ars(h), ha='center', fontsize=7, fontweight='bold')

    plt.suptitle('Comparativa CPL / CPA por Segmento y Canal', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(cpl_cpa_path, bbox_inches='tight', dpi=150)
    plt.close()

# Chart 3: Top campañas Facebook por segmento
top_camp_paths = {}
for seg in SEGMENTOS:
    if seg in fb_top_by_seg and len(fb_top_by_seg[seg]) > 0:
        top = fb_top_by_seg[seg].head(12).iloc[::-1]
        fig, ax = plt.subplots(figsize=(11, 6))
        names_short = [n[:50] + '...' if len(n) > 50 else n for n in top['Campana']]
        bars = ax.barh(names_short, top['Spend'], color='#1877f2', edgecolor='white')
        ax.set_xlabel('Importe Gastado (ARS)')
        ax.set_title(f'Top Campañas Facebook - {seg.replace("_", " ")}', fontsize=11, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_ars(v)))
        for bar, val in zip(bars, top['Spend']):
            ax.text(bar.get_width() + top['Spend'].max() * 0.01, bar.get_y() + bar.get_height()/2,
                    fmt_ars(val), va='center', fontsize=8)
        plt.tight_layout()
        path = os.path.join(output_dir, f'fb_top_campanas_{seg.lower()}.png')
        plt.savefig(path, bbox_inches='tight', dpi=150)
        plt.close()
        top_camp_paths[seg] = path

# ============================================================
# 4. GENERAR PDF (LANDSCAPE)
# ============================================================
print("\nGenerando PDF...")

BLUE = (41, 128, 185)
LIGHT_BLUE = (235, 245, 255)
DARK = (30, 30, 30)
GRAY = (120, 120, 120)
GREEN = (39, 174, 96)
RED = (192, 57, 43)

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*DARK)
        self.cell(0, 9, 'UCASAL - Inversión Publicitaria y ROI  |  Ingreso 2026', align='C',
                  new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*GRAY)
        self.cell(0, 8, f'Pág. {self.page_no()}  |  Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                  align='C')

    def section_title(self, txt):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*BLUE)
        self.cell(0, 9, txt, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*DARK)
        self.ln(1)

    def subsection(self, txt):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, txt, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*DARK)

    def table_header(self, headers, widths, aligns=None):
        self.set_fill_color(*BLUE)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        if aligns is None:
            aligns = ['C'] * len(headers)
        for h, w, a in zip(headers, widths, aligns):
            self.cell(w, 7, h, border=1, fill=True, align=a)
        self.ln()
        self.set_text_color(*DARK)

    def table_row(self, values, widths, fill=False, bold=False, aligns=None):
        self.set_fill_color(*(LIGHT_BLUE if fill else (255, 255, 255)))
        self.set_font('Helvetica', 'B' if bold else '', 8)
        if aligns is None:
            aligns = ['C'] * len(values)
        for val, w, a in zip(values, widths, aligns):
            self.cell(w, 6, str(val), border=1, fill=True, align=a)
        self.ln()

    def nota(self, txt):
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*GRAY)
        self.multi_cell(0, 4, txt)
        self.set_text_color(*DARK)


pdf = PDF('L')  # LANDSCAPE
pdf.set_auto_page_break(auto=True, margin=14)

# =============== PÁGINA 1: RESUMEN EJECUTIVO ===============
pdf.add_page()
pdf.section_title('1. Resumen Ejecutivo de Inversión')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5, f'Período Google Ads: {GOOGLE_PERIODO}  |  Período Facebook Ads: {fb_periodo}',
         new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(2)

# Tabla inversión total por segmento
pdf.subsection('Inversión Total por Segmento y Canal (ARS)')
hdrs = ['Segmento', 'Período Análisis', 'Google Ads', 'Facebook Ads', 'TOTAL Invertido']
wids = [42, 55, 50, 50, 50]
aligns = ['L', 'C', 'R', 'R', 'R']
pdf.table_header(hdrs, wids, aligns)

grand_total_g = 0
grand_total_f = 0
for i, seg in enumerate(SEGMENTOS):
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    grand_total_g += d['g_spend']
    grand_total_f += d['f_spend']
    pdf.table_row([
        seg.replace('_', ' '),
        d['ventana'],
        fmt_ars_full(d['g_spend']) if d['g_spend'] > 0 else '-',
        fmt_ars_full(d['f_spend']) if d['f_spend'] > 0 else '-',
        fmt_ars_full(d['total_spend']),
    ], wids, fill=(i % 2 == 0), aligns=aligns)

pdf.table_row([
    'TOTAL', '', fmt_ars_full(grand_total_g), fmt_ars_full(grand_total_f),
    fmt_ars_full(grand_total_g + grand_total_f)
], wids, bold=True, fill=True, aligns=aligns)
pdf.ln(4)

# Tabla KPIs consolidada por segmento
pdf.subsection('KPIs Consolidados por Segmento (todos los canales)')
hdrs2 = ['Segmento', 'Período', 'Leads CRM', 'Inscriptos', 'Tasa Conv.', 'Inversión Total',
         'CPL', 'CPA', 'Rev. Atribuida', 'ROI']
wids2 = [30, 40, 22, 22, 20, 32, 28, 28, 32, 20]
aligns2 = ['L', 'C', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
pdf.table_header(hdrs2, wids2, aligns2)

for i, seg in enumerate(SEGMENTOS):
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    pdf.table_row([
        seg.replace('_', ' '),
        d['ventana'],
        f"{d['total_leads_crm']:,}",
        f"{d['total_conv']:,}",
        f"{d['tasa_total']:.2f}%",
        fmt_ars_full(d['total_spend']),
        fmt_ars_full(safe_div(d['total_spend'], d['total_leads_crm'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(safe_div(d['total_spend'], d['total_conv'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(d['total_rev']),
        fmt_pct(d['roi_total']),
    ], wids2, fill=(i % 2 == 0), aligns=aligns2)

pdf.ln(3)
pdf.nota(
    'CPL = Inversión / Leads CRM (personas deduplicadas en ventana). '
    'CPA = Inversión / Inscriptos (Match Exacto únicamente). '
    'Rev. Atribuida = suma de Insc_Haber de inscriptos cuyo lead se originó en ese canal. '
    'ROI = (Rev.Atribuida - Inversión) / Inversión × 100. '
    'Grado/Pregrado: cohorte desde 01/09/2025. Cursos y Posgrados: año calendario desde 01/01/2026. '
    'Google sin impuestos. Facebook según export plataforma. '
    'Revenue es el haber registrado al momento de inscripción (cuota/arancel), no LTV completo.'
)

# =============== PÁGINAS 2-4: DETALLE POR SEGMENTO ===============
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    seg_label = seg.replace('_', ' ')

    pdf.add_page()
    pdf.section_title(f'2. Detalle: {seg_label}')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, f'{PERIODO_LABEL[seg]}  |  Ventana: {d["ventana"]}  |  Última inscripción: {d["max_insc_str"]}',
             new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.ln(2)

    # Tabla KPIs por canal
    pdf.subsection(f'KPIs por Canal - {seg_label}')
    hdrs_c = ['Canal', 'Inversión', 'Leads CRM', 'Leads Plat.', 'Inscriptos', 'Tasa Conv.',
              'CPL (CRM)', 'CPL (Plat.)', 'CPA', 'Rev. Atribuida', 'ROI']
    wids_c = [30, 32, 22, 22, 22, 18, 25, 25, 28, 30, 20]
    aligns_c = ['L', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
    pdf.table_header(hdrs_c, wids_c, aligns_c)

    # Google Ads row
    if d['g_spend'] > 0 or d['g_leads'] > 0:
        pdf.table_row([
            'Google Ads',
            fmt_ars_full(d['g_spend']),
            f"{d['g_leads']:,}",
            '-',
            f"{d['g_conv']:,}",
            f"{d['tasa_google']:.2f}%",
            fmt_ars_full(d['g_cpl']) if d['g_cpl'] > 0 else '-',
            '-',
            fmt_ars_full(d['g_cpa']) if d['g_cpa'] > 0 else '-',
            fmt_ars_full(d['g_rev']),
            fmt_pct(d['g_roi']),
        ], wids_c, fill=True, aligns=aligns_c)

    # Facebook Ads row
    if d['f_spend'] > 0 or d['f_leads_crm'] > 0:
        pdf.table_row([
            'Facebook Ads',
            fmt_ars_full(d['f_spend']),
            f"{d['f_leads_crm']:,}",
            f"{d['f_leads_plat']:,}",
            f"{d['f_conv']:,}",
            f"{d['tasa_fb']:.2f}%",
            fmt_ars_full(d['f_cpl']) if d['f_cpl'] > 0 else '-',
            fmt_ars_full(d['f_cpl_plat']) if d['f_cpl_plat'] > 0 else '-',
            fmt_ars_full(d['f_cpa']) if d['f_cpa'] > 0 else '-',
            fmt_ars_full(d['f_rev']),
            fmt_pct(d['f_roi']),
        ], wids_c, fill=False, aligns=aligns_c)

    # Bot row (sin inversión)
    if d['b_leads'] > 0:
        pdf.table_row([
            'Bot/Chatbot',
            '-',
            f"{d['b_leads']:,}",
            '-',
            f"{d['b_conv']:,}",
            f"{d['tasa_bot']:.2f}%",
            '-', '-', '-',
            fmt_ars_full(d['b_rev']),
            '-',
        ], wids_c, fill=True, aligns=aligns_c)

    # Otros row
    if d['o_leads'] > 0:
        pdf.table_row([
            'Otros/Orgánico',
            '-',
            f"{d['o_leads']:,}",
            '-',
            f"{d['o_conv']:,}",
            f"{safe_div(d['o_conv'], d['o_leads'])*100:.2f}%",
            '-', '-', '-',
            fmt_ars_full(d['o_rev']),
            '-',
        ], wids_c, fill=False, aligns=aligns_c)

    # Total row
    pdf.table_row([
        'TOTAL',
        fmt_ars_full(d['total_spend']),
        f"{d['total_leads_crm']:,}",
        f"{d['f_leads_plat']:,}",
        f"{d['total_conv']:,}",
        f"{d['tasa_total']:.2f}%",
        fmt_ars_full(safe_div(d['total_spend'], d['total_leads_crm'])) if d['total_spend'] > 0 else '-',
        '-',
        fmt_ars_full(safe_div(d['total_spend'], d['total_conv'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(d['total_rev']),
        fmt_pct(d['roi_total']),
    ], wids_c, bold=True, fill=True, aligns=aligns_c)
    pdf.ln(3)

    # Top campañas Facebook de este segmento
    if seg in fb_top_by_seg and len(fb_top_by_seg[seg]) > 0:
        pdf.subsection(f'Top Campañas Facebook - {seg_label}')
        top_df = fb_top_by_seg[seg]
        seg_spend = d['f_spend'] if d['f_spend'] > 0 else 1

        hdrs_t = ['#', 'Campaña', 'Inversión', '% Seg.', 'Leads Plat.', 'CPL Plat.', 'Impresiones', 'Clics']
        wids_t = [8, 90, 30, 16, 24, 24, 28, 22]
        aligns_t = ['C', 'L', 'R', 'R', 'R', 'R', 'R', 'R']
        pdf.table_header(hdrs_t, wids_t, aligns_t)

        for idx, (_, r) in enumerate(top_df.head(10).iterrows(), 1):
            nombre = str(r['Campana'])[:55]
            pct_seg = r['Spend'] / seg_spend * 100
            pdf.table_row([
                str(idx),
                nombre,
                fmt_ars_full(r['Spend']),
                f"{pct_seg:.1f}%",
                f"{int(r['Leads_Plat']):,}" if r['Leads_Plat'] > 0 else '-',
                fmt_ars_full(r['CPL_Plat']) if r['CPL_Plat'] > 0 else '-',
                f"{int(r['Impresiones']):,}" if r['Impresiones'] > 0 else '-',
                f"{int(r['Clics']):,}" if r['Clics'] > 0 else '-',
            ], wids_t, fill=(idx % 2 == 0), aligns=aligns_t)

# =============== PÁGINA FINAL: CHARTS ===============
pdf.add_page()
pdf.section_title('3. Gráficos Comparativos')

if os.path.exists(cpl_cpa_path):
    pdf.image(cpl_cpa_path, x=15, w=250)
    pdf.ln(5)

pdf.add_page()
pdf.section_title('4. Facebook Ads: Distribución de Inversión')

if os.path.exists(pie_path):
    pdf.image(pie_path, x=50, w=170)
    pdf.ln(5)

for seg in SEGMENTOS:
    if seg in top_camp_paths and os.path.exists(top_camp_paths[seg]):
        pdf.add_page()
        pdf.section_title(f'Top Campañas Facebook - {seg.replace("_", " ")}')
        pdf.image(top_camp_paths[seg], x=10, w=260)

# ============================================================
# 5. OUTPUT
# ============================================================
pdf_path = os.path.join(output_dir, 'Presupuesto_ROI_Ingreso2026.pdf')
pdf.output(pdf_path)
print(f"\n-> PDF generado: {pdf_path}")

# Excel de respaldo con todas las métricas
print("Generando Excel de respaldo...")
with pd.ExcelWriter(os.path.join(output_dir, 'Presupuesto_ROI_Datos.xlsx'), engine='xlsxwriter') as writer:
    # Hoja 1: KPIs por segmento
    rows_excel = []
    for seg in SEGMENTOS:
        if seg not in seg_data:
            continue
        d = seg_data[seg]
        for canal, spend, leads, conv, rev, cpl, cpa, roi, tasa in [
            ('Google Ads', d['g_spend'], d['g_leads'], d['g_conv'], d['g_rev'],
             d['g_cpl'], d['g_cpa'], d['g_roi'], d['tasa_google']),
            ('Facebook Ads', d['f_spend'], d['f_leads_crm'], d['f_conv'], d['f_rev'],
             d['f_cpl'], d['f_cpa'], d['f_roi'], d['tasa_fb']),
            ('Bot/Chatbot', 0, d['b_leads'], d['b_conv'], d['b_rev'], 0, 0, 0, d['tasa_bot']),
            ('Otros/Orgánico', 0, d['o_leads'], d['o_conv'], d['o_rev'], 0, 0, 0,
             safe_div(d['o_conv'], d['o_leads']) * 100),
        ]:
            rows_excel.append({
                'Segmento': seg,
                'Período': d['ventana'],
                'Canal': canal,
                'Inversión_ARS': spend,
                'Leads_CRM': leads,
                'Inscriptos_Exacto': conv,
                'Tasa_Conversión_%': round(tasa, 2),
                'CPL_ARS': round(cpl, 2),
                'CPA_ARS': round(cpa, 2),
                'Revenue_Atribuida_ARS': round(rev, 2),
                'ROI_%': round(roi, 2),
            })
    pd.DataFrame(rows_excel).to_excel(writer, sheet_name='KPIs_Por_Canal', index=False)

    # Hoja 2: Facebook por campaña
    if not fb_raw.empty:
        fb_export = fb_raw.copy()
        fb_export.to_excel(writer, sheet_name='Facebook_Detalle', index=False)

    # Hoja 3: Top campañas por segmento
    for seg in SEGMENTOS:
        if seg in fb_top_by_seg:
            fb_top_by_seg[seg].to_excel(writer, sheet_name=f'Top_FB_{seg[:15]}', index=False)

print(f"-> Excel generado: {os.path.join(output_dir, 'Presupuesto_ROI_Datos.xlsx')}")
print(f"-> Total invertido: {fmt_ars_full(grand_total_g + grand_total_f)} ARS")
print("Proceso finalizado.")
