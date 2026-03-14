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
from causal_utils import compute_anytouch_causal, render_causal_pdf, make_pk

# ============================================================
# CONFIG
# ============================================================
base_dir = r"h:\Test-Antigravity\marketing_report"
presupuesto_dir = os.path.join(base_dir, "data", "1_raw", "presupuestos")
output_dir = os.path.join(base_dir, "outputs", "General", "Presupuesto_ROI")
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
# Grado_Pregrado: período cohorte 01/09/2025 - 17/02/2026
# Posgrados: período calendario 01/01/2026 - 17/02/2026
GOOGLE_SPEND = {
    'Grado_Pregrado': 47_387_402.90,
    'Cursos': 0.0,
    'Posgrados': 976_308.10,
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

import re

def classify_fb_segment(nombre):
    n = str(nombre).lower()
    if any(k in n for k in ['posgrado', 'postgrado', 'maestr', 'especiali']):
        return 'Posgrados'
    if 'curso' in n:
        return 'Cursos'
    return 'Grado_Pregrado'

def extract_campaign_year(nombre):
    """Extrae el año de cohorte/período del nombre de la campaña (ej: 'Campaña2026_...' → 2026)."""
    match = re.search(r'20(\d{2})', str(nombre))
    return int('20' + match.group(1)) if match else None

def extract_campaign_group(nombre):
    """Extrae el grupo de carreras (A, B, C, CCC) del nombre de campaña."""
    n = str(nombre).upper()
    # Buscar GRUPO_A, GRUPO_B, GRUPO_C, GRUPO_CCC, etc.
    match = re.search(r'GRUPO[_\s]([A-Z]+)', n)
    return match.group(1) if match else None

# Año de cohorte que se está analizando
COHORTE_YEAR = 2026

if not fb_raw.empty:
    col_campana = 'Nombre de la campaña'
    # Si la columna tiene encoding roto, buscar la correcta
    if col_campana not in fb_raw.columns:
        for c in fb_raw.columns:
            if 'campa' in c.lower():
                col_campana = c
                break

    fb_raw['Segmento'] = fb_raw[col_campana].apply(classify_fb_segment)
    fb_raw['Cohorte_Year'] = fb_raw[col_campana].apply(extract_campaign_year)
    fb_raw['Grupo'] = fb_raw[col_campana].apply(extract_campaign_group)

# Período del export Facebook
fb_periodo = 'Sep 2025 - Feb 2026'
if not fb_raw.empty and 'Inicio del informe' in fb_raw.columns:
    fecha_ini = pd.to_datetime(fb_raw['Inicio del informe'], errors='coerce').min()
    fecha_fin = pd.to_datetime(fb_raw['Fin del informe'], errors='coerce').max()
    if pd.notna(fecha_ini) and pd.notna(fecha_fin):
        fb_periodo = f"{fecha_ini.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"

# ---------- Filtrar campañas por año de cohorte ----------
# Solo se incluyen campañas cuyo nombre contiene el año de la cohorte analizada (2026)
# o campañas sin año en el nombre (se asignan al año actual por defecto).
# Campañas de años anteriores (2025, 2024...) se excluyen del cálculo de inversión.
fb_cohorte = pd.DataFrame()
fb_excluidas = pd.DataFrame()
if not fb_raw.empty:
    mask_cohorte = (fb_raw['Cohorte_Year'] == COHORTE_YEAR) | (fb_raw['Cohorte_Year'].isna())
    fb_cohorte = fb_raw[mask_cohorte].copy()
    fb_excluidas = fb_raw[~mask_cohorte].copy()

    spend_incl = fb_cohorte['Importe gastado (ARS)'].sum()
    spend_excl = fb_excluidas['Importe gastado (ARS)'].sum()
    print(f"\nFiltrado por cohorte {COHORTE_YEAR}:")
    print(f"  Incluidas: {len(fb_cohorte)} filas, Spend = {fmt_ars_full(spend_incl)}")
    print(f"  Excluidas (otros anos): {len(fb_excluidas)} filas, Spend = {fmt_ars_full(spend_excl)}")

    # Detalle de lo excluido por segmento
    if not fb_excluidas.empty:
        for seg, sub in fb_excluidas.groupby('Segmento'):
            yr_spend = sub['Importe gastado (ARS)'].sum()
            years = sorted(sub['Cohorte_Year'].dropna().unique())
            print(f"    Excluido {seg}: {fmt_ars_full(yr_spend)} (anos: {[int(y) for y in years]})")

# Agregado por segmento (solo campañas de la cohorte)
fb_seg = pd.DataFrame()
fb_total = 0
if not fb_cohorte.empty:
    fb_seg = fb_cohorte.groupby('Segmento').agg(
        FB_Spend=('Importe gastado (ARS)', 'sum'),
        FB_Leads_Plat=('Clientes potenciales', 'sum'),
        FB_Impresiones=('Impresiones', 'sum'),
        FB_Clics=('Clics en el enlace', 'sum'),
        Num_Conjuntos=('Nombre del conjunto de anuncios', 'count'),
    ).reset_index()
    fb_total = fb_cohorte['Importe gastado (ARS)'].sum()

print(f"\nFacebook {COHORTE_YEAR} total ARS: {fmt_ars_full(fb_total)}")
for _, row in fb_seg.iterrows():
    print(f"  {row['Segmento']}: {fmt_ars_full(row['FB_Spend'])} ({row['FB_Spend']/fb_total*100:.1f}%)" if fb_total > 0 else "")

# Top campañas por segmento (solo cohorte)
fb_top_by_seg = {}
if not fb_cohorte.empty:
    for seg in SEGMENTOS:
        top = (fb_cohorte[fb_cohorte['Segmento'] == seg]
               .groupby(col_campana)
               .agg(Spend=('Importe gastado (ARS)', 'sum'),
                    Leads_Plat=('Clientes potenciales', 'sum'),
                    Impresiones=('Impresiones', 'sum'),
                    Clics=('Clics en el enlace', 'sum'))
               .sort_values('Spend', ascending=False)
               .head(15)
               .reset_index())
        top.rename(columns={col_campana: 'Campana'}, inplace=True)
        if not top.empty:
            top['CPL_Plat'] = top.apply(lambda r: safe_div(r['Spend'], r['Leads_Plat']), axis=1)
            fb_top_by_seg[seg] = top

# KPIs por Grupo de carreras (solo Grado_Pregrado)
fb_grupo_data = {}
if not fb_cohorte.empty:
    gp_cohorte = fb_cohorte[fb_cohorte['Segmento'] == 'Grado_Pregrado'].copy()
    if not gp_cohorte.empty and 'Grupo' in gp_cohorte.columns:
        grupos = gp_cohorte['Grupo'].dropna().unique()
        print(f"\nGrupos de carreras (Grado_Pregrado): {sorted(grupos)}")
        for grupo in sorted(grupos):
            sub = gp_cohorte[gp_cohorte['Grupo'] == grupo]
            spend = pd.to_numeric(sub['Importe gastado (ARS)'], errors='coerce').sum()
            leads_plat = pd.to_numeric(sub['Clientes potenciales'], errors='coerce').sum()
            impresiones = pd.to_numeric(sub['Impresiones'], errors='coerce').sum()
            clics = pd.to_numeric(sub['Clics en el enlace'], errors='coerce').sum()
            n_campanas = sub[col_campana].nunique()

            fb_grupo_data[grupo] = {
                'spend': spend,
                'leads_plat': leads_plat,
                'impresiones': impresiones,
                'clics': clics,
                'n_campanas': n_campanas,
                'cpl_plat': safe_div(spend, leads_plat),
            }
            print(f"  {grupo}: {fmt_ars_full(spend)} | {int(leads_plat):,} leads")

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

    # PK dedup persona (DNI > Email > Tel > Cel)
    df_main['_pk'] = make_pk(df_main)

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

    # Función para extraer métricas de un canal
    def canal_metrics(sub):
        n_leads = len(sub)
        n_conv = int((sub['_mc'] == 'exacto').sum())
        rev = float(sub[sub['_mc'] == 'exacto']['_haber'].sum())
        return n_leads, n_conv, rev

    def apply_canal_masks(dedup_df):
        m_google = dedup_df['_utm'].str.contains('google', na=False)
        meta_kw = ['fb', 'facebook', 'ig', 'instagram', 'meta']
        m_fb = dedup_df['_utm'].str.contains('|'.join(meta_kw), na=False) | (dedup_df['_fuente'] == 18)
        m_bot = dedup_df['_fuente'] == 907
        m_otros = ~m_google & ~m_fb & ~m_bot
        return m_google, m_fb, m_bot, m_otros

    # ---- LAST-TOUCH: consulta exacta más reciente (modelo principal) ----
    df_dedup = (df_conv
                .sort_values(['_mc', '_fecha'], ascending=[True, False])
                .drop_duplicates(subset='_pk', keep='first'))

    mask_google, mask_fb, mask_bot, mask_otros = apply_canal_masks(df_dedup)

    g_leads, g_conv, g_rev = canal_metrics(df_dedup[mask_google])
    f_leads, f_conv, f_rev = canal_metrics(df_dedup[mask_fb])
    b_leads, b_conv, b_rev = canal_metrics(df_dedup[mask_bot])
    o_leads, o_conv, o_rev = canal_metrics(df_dedup[mask_otros])
    t_leads, t_conv, t_rev = canal_metrics(df_dedup)

    # ---- FIRST-TOUCH: consulta exacta más antigua (modelo alternativo) ----
    df_dedup_ft = (df_conv
                   .sort_values(['_mc', '_fecha'], ascending=[True, True])
                   .drop_duplicates(subset='_pk', keep='first'))

    ft_masks = apply_canal_masks(df_dedup_ft)
    ft_data = {}
    for canal_name, mask in zip(['Google', 'Facebook', 'Bot', 'Otros'], ft_masks):
        leads, conv, rev = canal_metrics(df_dedup_ft[mask])
        ft_data[canal_name] = {'leads': leads, 'conv': conv, 'rev': rev}

    # Facebook extra: leads plataforma y spend
    fb_row = fb_seg[fb_seg['Segmento'] == seg] if not fb_seg.empty else pd.DataFrame()
    f_spend = float(fb_row['FB_Spend'].values[0]) if len(fb_row) > 0 else 0
    f_leads_plat = int(fb_row['FB_Leads_Plat'].values[0]) if len(fb_row) > 0 else 0
    fb_impresiones = int(fb_row['FB_Impresiones'].values[0]) if len(fb_row) > 0 else 0
    fb_clics = int(fb_row['FB_Clics'].values[0]) if len(fb_row) > 0 else 0

    g_spend = GOOGLE_SPEND.get(seg, 0)
    total_spend = g_spend + f_spend

    # Tasa de conversión (sobre personas = KPI principal, Last-Touch)
    tasa_google = safe_div(g_conv, g_leads) * 100
    tasa_fb = safe_div(f_conv, f_leads) * 100
    tasa_bot = safe_div(b_conv, b_leads) * 100
    tasa_total = safe_div(t_conv, t_leads) * 100

    # Tasa sobre consultas (complementaria)
    total_consultas_conv = len(df_conv)  # consultas (sin dedup) en ventana
    tasa_total_consultas = safe_div(t_conv, total_consultas_conv) * 100

    # Desglose por tipo de match
    _m_dni = int((df_dedup['Match_Tipo'] == 'Exacto (DNI)').sum())
    _m_email = int((df_dedup['Match_Tipo'] == 'Exacto (Email)').sum())
    _m_tel = int((df_dedup['Match_Tipo'] == 'Exacto (Teléfono)').sum())
    _m_cel = int((df_dedup['Match_Tipo'] == 'Exacto (Celular)').sum())

    seg_data[seg] = {
        'max_insc_ts': max_insc_ts,
        'max_insc_str': max_insc_ts.strftime('%d/%m/%Y'),
        'inicio': inicio,
        'ventana': f"{inicio.strftime('%d/%m/%Y')} - {max_insc_ts.strftime('%d/%m/%Y')}",
        'total_consultas_conv': total_consultas_conv,
        'total_leads_crm': t_leads,  # personas dedup
        'total_conv': t_conv,
        'total_rev': t_rev,
        'tasa_total': tasa_total,  # s/personas (KPI)
        'tasa_total_consultas': tasa_total_consultas,  # s/consultas
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
        # First-touch (modelo alternativo)
        'ft': ft_data,
        # Match breakdown
        'm_dni': _m_dni, 'm_email': _m_email, 'm_tel': _m_tel, 'm_cel': _m_cel,
    }
    print(f"  {seg} [{PERIODO_LABEL[seg]}]:")
    print(f"    Ventana: {seg_data[seg]['ventana']}")
    print(f"    Leads CRM (dedup): {t_leads:,}  |  Inscriptos exactos: {t_conv:,}  |  Tasa: {tasa_total:.2f}%")
    print(f"    Google: {g_leads:,} leads / {g_conv:,} insc / Rev {fmt_ars(g_rev)}")
    print(f"    Facebook: {f_leads:,} leads / {f_conv:,} insc / Rev {fmt_ars(f_rev)}")
    print(f"    Bot: {b_leads:,} leads / {b_conv:,} insc / Rev {fmt_ars(b_rev)}")

    # Diagnóstico: inscriptos de campaña anterior (si la columna existe)
    if 'Campana_Lead' in df_dedup.columns:
        label_camp = PERIODO_LABEL[seg].split('(')[0].strip()
        n_camp_act = int((df_dedup[df_dedup['_mc'] == 'exacto']['Campana_Lead'] == ('Ingreso 2026' if seg == 'Grado_Pregrado' else '2026')).sum())
        n_camp_ant = int((df_dedup[df_dedup['_mc'] == 'exacto']['Campana_Lead'] == 'Campaña Anterior').sum())
        seg_data[seg]['n_camp_actual'] = n_camp_act
        seg_data[seg]['n_camp_anterior'] = n_camp_ant
        print(f"    Campana actual: {n_camp_act:,} insc | Campana anterior: {n_camp_ant:,} insc")

# Any-Touch Causal por segmento
causal_por_seg = {}
for seg in SEGMENTOS:
    l_csv = os.path.join(base_dir, "outputs", "Data_Base", seg, "reporte_marketing_leads_completos.csv")
    i_csv = os.path.join(base_dir, "outputs", "Data_Base", seg, "reporte_marketing_inscriptos_origenes.csv")
    if os.path.exists(l_csv):
        causal_por_seg[seg] = compute_anytouch_causal(l_csv, seg, i_csv if os.path.exists(i_csv) else None)

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
pdf.set_fill_color(240, 248, 255)
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(0, 6, 'Metodologia aplicada:', new_x='LMARGIN', new_y='NEXT', fill=True)
pdf.set_font('Helvetica', '', 8)
pdf.multi_cell(0, 4,
    'MODELO ESTANDAR (este informe): Match Exacto por DNI > Email > Telefono > Celular. '
    'Deduplicado por persona (DNI). Atribucion Any-Touch (suma > 100%). '
    'Incluye TODAS las consultas sin filtro de fecha vs pago.\n'
    + ''.join([f'{s}: DNI ({seg_data[s]["m_dni"]:,}), Email ({seg_data[s]["m_email"]:,}), Tel ({seg_data[s]["m_tel"]:,}), Cel ({seg_data[s]["m_cel"]:,}). Total: {seg_data[s]["total_conv"]:,}.\n' for s in SEGMENTOS if s in seg_data])
    + 'MODELO CAUSAL (ver Presupuesto_ROI_Causal): Solo consultas con fecha <= fecha de pago. '
    'Excluye consultas post-pago.',
    fill=True)
pdf.set_fill_color(255, 255, 255)
pdf.ln(2)
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
hdrs2 = ['Segmento', 'Período', 'Consultas', 'Personas', 'Inscriptos', 'Tasa s/Cons.', 'Tasa s/Pers.',
         'Inversión Total', 'CPA', 'Rev. Atribuida', 'ROI']
wids2 = [28, 36, 22, 22, 20, 20, 20, 28, 26, 28, 18]
aligns2 = ['L', 'C', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
pdf.table_header(hdrs2, wids2, aligns2)

for i, seg in enumerate(SEGMENTOS):
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    pdf.table_row([
        seg.replace('_', ' '),
        d['ventana'],
        f"{d['total_consultas_conv']:,}",
        f"{d['total_leads_crm']:,}",
        f"{d['total_conv']:,}",
        f"{d['tasa_total_consultas']:.2f}%",
        f"{d['tasa_total']:.2f}%",
        fmt_ars_full(d['total_spend']),
        fmt_ars_full(safe_div(d['total_spend'], d['total_conv'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(d['total_rev']),
        fmt_pct(d['roi_total']),
    ], wids2, fill=(i % 2 == 0), aligns=aligns2)

pdf.ln(3)
pdf.nota(
    'Tasa s/Cons. = Inscriptos / Consultas en ventana. Tasa s/Pers. = Inscriptos / Personas unicas en ventana (KPI principal). '
    'CPA = Inversion / Inscriptos (Match Exacto unicamente). '
    'Rev. Atribuida = suma de Insc_Haber de inscriptos cuyo lead se origino en ese canal. '
    'ROI = (Rev.Atribuida - Inversion) / Inversion x 100. '
    f'Grado/Pregrado: cohorte desde 01/09/2025. Cursos y Posgrados: anio calendario desde 01/01/2026. '
    f'Facebook: solo campanas con "{COHORTE_YEAR}" en el nombre (campanas de anios anteriores excluidas). '
    'Google sin impuestos. Revenue = haber al momento de inscripcion (cuota/arancel), no LTV completo.'
)

# =============== PÁGINA 2: KPIs CONSOLIDADOS SEGMENTO × CANAL ===============
pdf.add_page()
pdf.section_title('2. KPIs Consolidados por Segmento y Canal')
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5, f'Facebook: solo campanas {COHORTE_YEAR}  |  Google: sin impuestos  |  Revenue: Insc_Haber (cuota/arancel, no LTV)',
         new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(2)

hdrs_cross = ['Segmento', 'Canal', 'Periodo Leads', 'Inversion', 'Leads', 'Insc.',
              'Tasa', 'CPL', 'CPA', 'Rev. Atrib.', 'ROI']
wids_cross = [28, 24, 38, 30, 20, 18, 17, 25, 27, 30, 20]
aligns_cross = ['L', 'L', 'C', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
pdf.table_header(hdrs_cross, wids_cross, aligns_cross)

row_idx = 0
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    seg_label = seg.replace('_', ' ')
    canales = [
        ('Google Ads', d['g_spend'], d['g_leads'], d['g_conv'], d['tasa_google'],
         d['g_cpl'], d['g_cpa'], d['g_rev'], d['g_roi']),
        ('Facebook Ads', d['f_spend'], d['f_leads_crm'], d['f_conv'], d['tasa_fb'],
         d['f_cpl'], d['f_cpa'], d['f_rev'], d['f_roi']),
        ('Bot/Chatbot', 0, d['b_leads'], d['b_conv'], d['tasa_bot'], 0, 0, d['b_rev'], 0),
        ('Otros', 0, d['o_leads'], d['o_conv'],
         safe_div(d['o_conv'], d['o_leads'])*100, 0, 0, d['o_rev'], 0),
    ]
    for canal, spend, leads, conv, tasa, cpl, cpa, rev, roi in canales:
        if leads == 0 and spend == 0:
            continue
        pdf.table_row([
            seg_label if canal == 'Google Ads' else '',
            canal,
            d['ventana'],
            fmt_ars_full(spend) if spend > 0 else '-',
            f"{leads:,}",
            f"{conv:,}",
            f"{tasa:.2f}%",
            fmt_ars_full(cpl) if cpl > 0 else '-',
            fmt_ars_full(cpa) if cpa > 0 else '-',
            fmt_ars_full(rev),
            fmt_pct(roi) if spend > 0 else '-',
        ], wids_cross, fill=(row_idx % 2 == 0), aligns=aligns_cross)
        row_idx += 1
    # Subtotal del segmento
    pdf.table_row([
        '', f'Subtotal {seg_label}', d['ventana'],
        fmt_ars_full(d['total_spend']) if d['total_spend'] > 0 else '-',
        f"{d['total_leads_crm']:,}", f"{d['total_conv']:,}",
        f"{d['tasa_total']:.2f}%",
        fmt_ars_full(safe_div(d['total_spend'], d['total_leads_crm'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(safe_div(d['total_spend'], d['total_conv'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(d['total_rev']),
        fmt_pct(d['roi_total']) if d['total_spend'] > 0 else '-',
    ], wids_cross, bold=True, fill=True, aligns=aligns_cross)
    row_idx += 1

pdf.ln(3)
pdf.nota(
    'CPL = Inversion / Leads CRM deduplicados en ventana. '
    'CPA = Inversion / Inscriptos Match Exacto. '
    'Tasa Conv. = Inscriptos / Personas dedup del canal (modelo Last-Touch, cada persona en 1 solo canal). '
    'Grado/Pregrado: cohorte desde 01/09/2025. Cursos y Posgrados: anio calendario desde 01/01/2026.'
)

# =============== PÁGINA 3: COMPARATIVA ATRIBUCIÓN (Last-Touch vs First-Touch) ===============
pdf.add_page()
pdf.section_title('3. Comparativa de Atribución: Last-Touch vs First-Touch')
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5, 'Last-Touch = consulta exacta mas reciente (modelo principal)  |  First-Touch = consulta exacta mas antigua (modelo alternativo)',
         new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(2)

hdrs_attr = ['Segmento', 'Canal', 'Insc. LT', 'Rev. LT', 'Insc. FT', 'Rev. FT', 'Dif. Insc.', 'Dif. %']
wids_attr = [35, 28, 22, 35, 22, 35, 22, 22]
aligns_attr = ['L', 'L', 'R', 'R', 'R', 'R', 'R', 'R']
pdf.table_header(hdrs_attr, wids_attr, aligns_attr)

row_idx = 0
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    ft = d['ft']
    seg_label = seg.replace('_', ' ')
    lt_canales = {
        'Google Ads': (d['g_conv'], d['g_rev']),
        'Facebook Ads': (d['f_conv'], d['f_rev']),
        'Bot/Chatbot': (d['b_conv'], d['b_rev']),
        'Otros': (d['o_conv'], d['o_rev']),
    }
    ft_keys = {'Google Ads': 'Google', 'Facebook Ads': 'Facebook', 'Bot/Chatbot': 'Bot', 'Otros': 'Otros'}
    seg_total_lt_conv = 0
    seg_total_lt_rev = 0
    seg_total_ft_conv = 0
    seg_total_ft_rev = 0
    for canal_label, (lt_conv, lt_rev) in lt_canales.items():
        ft_key = ft_keys[canal_label]
        ft_conv = ft[ft_key]['conv']
        ft_rev = ft[ft_key]['rev']
        diff = lt_conv - ft_conv
        diff_pct = safe_div(diff, ft_conv) * 100 if ft_conv > 0 else (0 if diff == 0 else float('inf'))
        seg_total_lt_conv += lt_conv
        seg_total_lt_rev += lt_rev
        seg_total_ft_conv += ft_conv
        seg_total_ft_rev += ft_rev
        pdf.table_row([
            seg_label if canal_label == 'Google Ads' else '',
            canal_label,
            f"{lt_conv:,}",
            fmt_ars_full(lt_rev),
            f"{ft_conv:,}",
            fmt_ars_full(ft_rev),
            f"{diff:+,}" if diff != 0 else '-',
            f"{diff_pct:+.1f}%" if diff != 0 and diff_pct != float('inf') else ('-' if diff == 0 else 'N/A'),
        ], wids_attr, fill=(row_idx % 2 == 0), aligns=aligns_attr)
        row_idx += 1
    # Subtotal
    diff_tot = seg_total_lt_conv - seg_total_ft_conv
    pdf.table_row([
        '', f'Total {seg_label}',
        f"{seg_total_lt_conv:,}", fmt_ars_full(seg_total_lt_rev),
        f"{seg_total_ft_conv:,}", fmt_ars_full(seg_total_ft_rev),
        f"{diff_tot:+,}" if diff_tot != 0 else '-', '-',
    ], wids_attr, bold=True, fill=True, aligns=aligns_attr)
    row_idx += 1

pdf.ln(3)
pdf.nota(
    'Last-Touch (LT): si un inscripto tiene multiples consultas exactas, se toma la MAS RECIENTE para atribuir el canal. '
    'First-Touch (FT): se toma la MAS ANTIGUA. '
    'El total de inscriptos es igual en ambos modelos (cambia la distribucion entre canales). '
    'Diferencia positiva = el canal gana inscriptos con LT vs FT; negativa = pierde.'
)

# =============== PÁGINA 4: KPIs POR GRUPO (Grado_Pregrado) ===============
if 'Grado_Pregrado' in seg_data and fb_grupo_data:
    pdf.add_page()
    pdf.section_title('4. KPIs por Grupo de Carreras (Grado_Pregrado - Facebook)')
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, f'Desglose de inversion y metricas de Facebook por grupo de carreras',
             new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.ln(2)

    hdrs_grp = ['Grupo', 'Campanas', 'Inversion', 'Leads Plat.', 'Impresiones', 'Clics', 'CPL Plat.']
    wids_grp = [22, 22, 35, 28, 30, 22, 28]
    aligns_grp = ['C', 'C', 'R', 'R', 'R', 'R', 'R']
    pdf.table_header(hdrs_grp, wids_grp, aligns_grp)

    total_spend_grp = 0
    total_leads_grp = 0
    row_idx = 0
    for grupo in sorted(fb_grupo_data.keys()):
        data = fb_grupo_data[grupo]
        total_spend_grp += data['spend']
        total_leads_grp += data['leads_plat']

        pdf.table_row([
            f"Grupo {grupo}",
            f"{data['n_campanas']}",
            fmt_ars_full(data['spend']),
            f"{int(data['leads_plat']):,}" if data['leads_plat'] > 0 else '-',
            f"{int(data['impresiones']):,}" if data['impresiones'] > 0 else '-',
            f"{int(data['clics']):,}" if data['clics'] > 0 else '-',
            fmt_ars_full(data['cpl_plat']) if data['cpl_plat'] > 0 else '-',
        ], wids_grp, fill=(row_idx % 2 == 0), aligns=aligns_grp)
        row_idx += 1

    # Total row
    total_cpl = safe_div(total_spend_grp, total_leads_grp)
    pdf.table_row([
        'TOTAL',
        f"{sum(d['n_campanas'] for d in fb_grupo_data.values())}",
        fmt_ars_full(total_spend_grp),
        f"{int(total_leads_grp):,}" if total_leads_grp > 0 else '-',
        '-', '-',
        fmt_ars_full(total_cpl) if total_cpl > 0 else '-',
    ], wids_grp, bold=True, fill=True, aligns=aligns_grp)
    pdf.ln(3)

# =============== PÁGINAS 4+: DETALLE POR SEGMENTO ===============
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    seg_label = seg.replace('_', ' ')

    pdf.add_page()
    pdf.section_title(f'5. Detalle: {seg_label}')
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

# =============== PÁGINAS FINALES: CHARTS ===============
pdf.add_page()
pdf.section_title('6. Graficos Comparativos')

if os.path.exists(cpl_cpa_path):
    pdf.image(cpl_cpa_path, x=15, w=250)
    pdf.ln(5)

pdf.add_page()
pdf.section_title('7. Facebook Ads: Distribucion de Inversion')

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
# Any-Touch Causal por segmento
for seg, cd in causal_por_seg.items():
    pdf.add_page()
    render_causal_pdf(pdf, cd, seg)

# Nota Metodológica
pdf.add_page()
pdf.section_title('Nota Metodologica')
pdf.set_font('Helvetica', '', 9)
pdf.multi_cell(0, 5,
    'Modelo de atribucion: Last-Touch (consulta exacta mas reciente asigna el canal). '
    'Alternativa First-Touch disponible en pag. 3. Deduplicado por persona (DNI).\n\n'
    'Match Exacto: DNI > Email > Telefono > Celular (prioridad). '
    'Solo se cuentan conversiones por Match Exacto (Fuzzy excluido de KPIs financieros).\n'
    + ''.join([f'{s}: DNI ({seg_data[s]["m_dni"]:,}), Email ({seg_data[s]["m_email"]:,}), Tel ({seg_data[s]["m_tel"]:,}), Cel ({seg_data[s]["m_cel"]:,}). Total: {seg_data[s]["total_conv"]:,}.\n' for s in SEGMENTOS if s in seg_data])
    + '\n'
    'Any-Touch: Para ver cuantos inscriptos tuvieron contacto con cada canal (sin dedup entre canales), '
    'referirse al Informe Analitico (04_reporte_final).\n\n'
    'Ventana de conversion:\n'
    '  - Grado/Pregrado: Leads desde 01/09/2025 (campana ingreso 2026)\n'
    '  - Cursos y Posgrados: Anio calendario desde 01/01/2026\n\n'
    'Definiciones:\n'
    '  - CPL = Inversion / Leads CRM deduplicados en ventana\n'
    '  - CPA = Inversion / Inscriptos Match Exacto\n'
    '  - Revenue = Insc_Haber (cuota/arancel al momento de inscripcion, no LTV)\n'
    '  - ROI = (Revenue - Inversion) / Inversion x 100')

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

    # Hoja 2: Comparativa atribución LT vs FT
    rows_attr = []
    for seg in SEGMENTOS:
        if seg not in seg_data:
            continue
        d = seg_data[seg]
        ft = d['ft']
        for canal, lt_conv, lt_rev, ft_key in [
            ('Google Ads', d['g_conv'], d['g_rev'], 'Google'),
            ('Facebook Ads', d['f_conv'], d['f_rev'], 'Facebook'),
            ('Bot/Chatbot', d['b_conv'], d['b_rev'], 'Bot'),
            ('Otros/Orgánico', d['o_conv'], d['o_rev'], 'Otros'),
        ]:
            ft_conv = ft[ft_key]['conv']
            ft_rev = ft[ft_key]['rev']
            rows_attr.append({
                'Segmento': seg,
                'Canal': canal,
                'Inscriptos_LastTouch': lt_conv,
                'Revenue_LastTouch': round(lt_rev, 2),
                'Inscriptos_FirstTouch': ft_conv,
                'Revenue_FirstTouch': round(ft_rev, 2),
                'Diferencia_Inscriptos': lt_conv - ft_conv,
            })
    pd.DataFrame(rows_attr).to_excel(writer, sheet_name='Atribucion_LT_vs_FT', index=False)

    # Hoja 3: Facebook por campaña (solo cohorte)
    if not fb_cohorte.empty:
        fb_export = fb_cohorte.copy()
        fb_export.to_excel(writer, sheet_name='Facebook_Detalle', index=False)

    # Hoja 3: Top campañas por segmento
    for seg in SEGMENTOS:
        if seg in fb_top_by_seg:
            fb_top_by_seg[seg].to_excel(writer, sheet_name=f'Top_FB_{seg[:15]}', index=False)

    # Hoja 4: Campañas excluidas (otros años) para auditoría
    if not fb_excluidas.empty:
        excl_summary = (fb_excluidas.groupby(['Segmento', 'Cohorte_Year'])
                        .agg(Spend=('Importe gastado (ARS)', 'sum'),
                             Leads=('Clientes potenciales', 'sum'),
                             Filas=('Importe gastado (ARS)', 'count'))
                        .reset_index()
                        .sort_values(['Segmento', 'Cohorte_Year']))
        excl_summary.to_excel(writer, sheet_name='FB_Excluidas_Resumen', index=False)

    # Hoja 5: Resumen FB por segmento y año (todas las campañas, para control)
    if not fb_raw.empty:
        all_summary = (fb_raw.groupby(['Segmento', 'Cohorte_Year'])
                       .agg(Spend=('Importe gastado (ARS)', 'sum'),
                            Leads=('Clientes potenciales', 'sum'),
                            Impresiones=('Impresiones', 'sum'),
                            Clics=('Clics en el enlace', 'sum'),
                            Campanas=(col_campana, 'nunique'))
                       .reset_index()
                       .sort_values(['Segmento', 'Cohorte_Year']))
        all_summary['Incluida_en_ROI'] = all_summary['Cohorte_Year'].apply(
            lambda y: 'Si' if (y == COHORTE_YEAR or pd.isna(y)) else 'No')
        all_summary.to_excel(writer, sheet_name='FB_Por_Segmento_Anio', index=False)

print(f"-> Excel generado: {os.path.join(output_dir, 'Presupuesto_ROI_Datos.xlsx')}")
print(f"-> Total invertido: {fmt_ars_full(grand_total_g + grand_total_f)} ARS")
print("Proceso finalizado.")
