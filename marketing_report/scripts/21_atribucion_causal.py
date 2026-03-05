"""
21_atribucion_causal.py
Informe de Inversión Publicitaria y ROI — Modelo de Atribución Causal.

Diferencia clave vs 20_presupuesto_roi.py:
  Solo se cuenta como conversión una consulta cuya fecha de creación es
  ANTERIOR O IGUAL a la fecha de pago de la inscripción (Insc_Fecha Pago).
  Consultas posteriores al pago (post-venta, soporte, reactivación) se excluyen.

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
import re

# ============================================================
# CONFIG
# ============================================================
base_dir = r"h:\Test-Antigravity\marketing_report"
presupuesto_dir = os.path.join(base_dir, "data", "1_raw", "presupuestos")
output_dir = os.path.join(base_dir, "outputs", "Presupuesto_ROI_Causal")
os.makedirs(output_dir, exist_ok=True)

SEGMENTOS = ['Grado_Pregrado', 'Cursos', 'Posgrados']

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

# Google Ads spend por segmento (hardcodeado, sin impuestos)
GOOGLE_SPEND = {
    'Grado_Pregrado': 47_387_402.90,
    'Cursos': 0.0,
    'Posgrados': 976_308.10,
}
GOOGLE_PERIODO = '01/09/2025 - 17/02/2026'

COHORTE_YEAR = 2026

# ============================================================
# HELPERS
# ============================================================
def safe_div(a, b):
    return a / b if b > 0 else 0

def fmt_ars(v):
    if abs(v) >= 1_000_000:
        return f"$ {v/1_000_000:,.2f}M"
    if abs(v) >= 1_000:
        return f"$ {v/1_000:,.1f}K"
    return f"$ {v:,.0f}"

def fmt_ars_full(v):
    return f"$ {v:,.0f}"

def fmt_pct(v):
    return f"{v:+.1f}%" if v != 0 else "-"

def classify_fb_segment(nombre):
    n = str(nombre).lower()
    if any(k in n for k in ['posgrado', 'postgrado', 'maestr', 'especiali']):
        return 'Posgrados'
    if 'curso' in n:
        return 'Cursos'
    return 'Grado_Pregrado'

def extract_campaign_year(nombre):
    match = re.search(r'20(\d{2})', str(nombre))
    return int('20' + match.group(1)) if match else None

def extract_campaign_group(nombre):
    n = str(nombre).upper()
    match = re.search(r'GRUPO[_\s]([A-Z]+)', n)
    return match.group(1) if match else None

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

for col in ['Importe gastado (ARS)', 'Clientes potenciales', 'Impresiones', 'Clics en el enlace']:
    if col in fb_raw.columns:
        fb_raw[col] = pd.to_numeric(fb_raw[col], errors='coerce').fillna(0)
    else:
        fb_raw[col] = 0

if not fb_raw.empty:
    col_campana = 'Nombre de la campaña'
    if col_campana not in fb_raw.columns:
        for c in fb_raw.columns:
            if 'campa' in c.lower():
                col_campana = c
                break

    fb_raw['Segmento'] = fb_raw[col_campana].apply(classify_fb_segment)
    fb_raw['Cohorte_Year'] = fb_raw[col_campana].apply(extract_campaign_year)
    fb_raw['Grupo'] = fb_raw[col_campana].apply(extract_campaign_group)

fb_periodo = 'Sep 2025 - Feb 2026'
if not fb_raw.empty and 'Inicio del informe' in fb_raw.columns:
    fecha_ini = pd.to_datetime(fb_raw['Inicio del informe'], errors='coerce').min()
    fecha_fin = pd.to_datetime(fb_raw['Fin del informe'], errors='coerce').max()
    if pd.notna(fecha_ini) and pd.notna(fecha_fin):
        fb_periodo = f"{fecha_ini.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"

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

fb_grupo_data = {}
if not fb_cohorte.empty:
    gp_cohorte = fb_cohorte[fb_cohorte['Segmento'] == 'Grado_Pregrado'].copy()
    if not gp_cohorte.empty and 'Grupo' in gp_cohorte.columns:
        grupos = gp_cohorte['Grupo'].dropna().unique()
        for grupo in sorted(grupos):
            sub = gp_cohorte[gp_cohorte['Grupo'] == grupo]
            spend = pd.to_numeric(sub['Importe gastado (ARS)'], errors='coerce').sum()
            leads_plat = pd.to_numeric(sub['Clientes potenciales'], errors='coerce').sum()
            impresiones = pd.to_numeric(sub['Impresiones'], errors='coerce').sum()
            clics = pd.to_numeric(sub['Clics en el enlace'], errors='coerce').sum()
            n_campanas = sub[col_campana].nunique()
            fb_grupo_data[grupo] = {
                'spend': spend, 'leads_plat': leads_plat, 'impresiones': impresiones,
                'clics': clics, 'n_campanas': n_campanas,
                'cpl_plat': safe_div(spend, leads_plat),
            }

# ============================================================
# 2. LEADS, CONVERSIONES Y REVENUE POR SEGMENTO
# ============================================================
print("\nCalculando métricas por canal desde CSVs de leads...")
seg_data = {}    # KPIs modelo causal (principal)
std_data = {}    # KPIs modelo estándar (para comparativa)

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

    # Fecha creación de la consulta
    df_main['_fecha'] = pd.to_datetime(
        df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

    # Revenue
    df_main['_haber'] = pd.to_numeric(df_main.get('Insc_Haber', pd.Series(dtype='float')), errors='coerce').fillna(0)

    # Ventana de conversión
    inicio = PERIODO_INICIO[seg]
    df_conv = df_main[(df_main['_fecha'] >= inicio) & (df_main['_fecha'] <= max_insc_ts)].copy()

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

    # ---- MODELO ESTÁNDAR (sin filtro causal) — para referencia comparativa ----
    df_std = (df_conv
              .sort_values(['_mc', '_fecha'], ascending=[True, False])
              .drop_duplicates(subset='_pk', keep='first'))

    std_masks = apply_canal_masks(df_std)
    std_data[seg] = {}
    for canal_name, mask in zip(['Google', 'Facebook', 'Bot', 'Otros'], std_masks):
        _, conv, rev = canal_metrics(df_std[mask])
        std_data[seg][canal_name] = {'conv': conv, 'rev': rev}
    _, std_total_conv, std_total_rev = canal_metrics(df_std)
    std_data[seg]['Total'] = {'conv': std_total_conv, 'rev': std_total_rev}

    # ---- FILTRO CAUSAL: consulta <= fecha de pago ----
    df_conv_causal = df_conv.copy()
    df_conv_causal['_insc_fecha'] = pd.to_datetime(
        df_conv_causal.get('Insc_Fecha Pago', pd.Series(dtype='str')),
        format='mixed', errors='coerce')

    # Para exacto: si consulta es POSTERIOR al pago → reclasificar como no_match
    late_mask = (df_conv_causal['_mc'] == 'exacto') & (df_conv_causal['_fecha'] > df_conv_causal['_insc_fecha'])
    n_late = int(late_mask.sum())
    df_conv_causal.loc[late_mask, '_mc'] = 'no_match'

    # Exacto sin fecha de pago (unmatched con _mc==exacto no debería pasar, pero por si acaso)
    n_sin_fecha = int((df_conv_causal['_mc'] == 'exacto') & df_conv_causal['_insc_fecha'].isna()).sum() if False else 0

    print(f"  {seg}: {n_late} consultas post-pago excluidas por filtro causal")

    # Dedup Last-Touch sobre el set causal
    df_dedup = (df_conv_causal
                .sort_values(['_mc', '_fecha'], ascending=[True, False])
                .drop_duplicates(subset='_pk', keep='first'))

    mask_google, mask_fb, mask_bot, mask_otros = apply_canal_masks(df_dedup)

    g_leads, g_conv, g_rev = canal_metrics(df_dedup[mask_google])
    f_leads, f_conv, f_rev = canal_metrics(df_dedup[mask_fb])
    b_leads, b_conv, b_rev = canal_metrics(df_dedup[mask_bot])
    o_leads, o_conv, o_rev = canal_metrics(df_dedup[mask_otros])
    t_leads, t_conv, t_rev = canal_metrics(df_dedup)

    fb_row = fb_seg[fb_seg['Segmento'] == seg] if not fb_seg.empty else pd.DataFrame()
    f_spend = float(fb_row['FB_Spend'].values[0]) if len(fb_row) > 0 else 0
    f_leads_plat = int(fb_row['FB_Leads_Plat'].values[0]) if len(fb_row) > 0 else 0
    fb_impresiones = int(fb_row['FB_Impresiones'].values[0]) if len(fb_row) > 0 else 0
    fb_clics = int(fb_row['FB_Clics'].values[0]) if len(fb_row) > 0 else 0

    g_spend = GOOGLE_SPEND.get(seg, 0)
    total_spend = g_spend + f_spend

    tasa_google = safe_div(g_conv, g_leads) * 100
    tasa_fb = safe_div(f_conv, f_leads) * 100
    tasa_bot = safe_div(b_conv, b_leads) * 100
    tasa_total = safe_div(t_conv, t_leads) * 100

    # ---- MODELO ANY-TOUCH CAUSAL: cada canal recibe crédito si tuvo ALGUNA consulta causal ----
    # Sin dedup global → un inscripto puede contar en múltiples canales simultáneamente.
    # Se cuenta la persona una vez por canal (dedup within canal).
    df_exacto_causal = df_conv_causal[df_conv_causal['_mc'] == 'exacto'].copy()
    at_data = {}
    for canal_name, at_mask in zip(
        ['Google', 'Facebook', 'Bot', 'Otros'],
        apply_canal_masks(df_exacto_causal)
    ):
        sub = df_exacto_causal[at_mask].drop_duplicates(subset='_pk', keep='first')
        at_data[canal_name] = {
            'conv': len(sub),
            'rev': float(sub['_haber'].sum()),
        }
    at_total_unico = df_exacto_causal['_pk'].nunique()
    at_total_rev = float(df_exacto_causal.drop_duplicates(subset='_pk', keep='first')['_haber'].sum())
    at_data['Total_Unico'] = {'conv': at_total_unico, 'rev': at_total_rev}

    # Sankey: flujo First-Touch → Last-Touch para cada inscripto causal
    df_ec = df_exacto_causal.copy()
    df_ec['_canal'] = 'Otros'
    _m_bot_ec = df_ec['_fuente'] == 907
    _meta_kw = ['fb', 'facebook', 'ig', 'instagram', 'meta']
    _m_fb_ec = df_ec['_utm'].str.contains('|'.join(_meta_kw), na=False) | (df_ec['_fuente'] == 18)
    _m_google_ec = df_ec['_utm'].str.contains('google', na=False)
    df_ec.loc[_m_bot_ec, '_canal'] = 'Bot'
    df_ec.loc[_m_fb_ec, '_canal'] = 'Facebook'
    df_ec.loc[_m_google_ec, '_canal'] = 'Google'
    # Por persona: primer y último canal causal (ordenados por fecha)
    sankey_df = (df_ec.sort_values('_fecha')
                 .groupby('_pk')
                 .agg(first_touch=('_canal', 'first'), last_touch=('_canal', 'last'))
                 .reset_index())
    sankey_matrix = sankey_df.groupby(['first_touch', 'last_touch']).size().reset_index(name='count')

    print(f"    Any-Touch causal: Google={at_data['Google']['conv']} | "
          f"Facebook={at_data['Facebook']['conv']} | "
          f"Bot={at_data['Bot']['conv']} | "
          f"Otros={at_data['Otros']['conv']} | "
          f"Total unico={at_total_unico}")

    seg_data[seg] = {
        'max_insc_ts': max_insc_ts,
        'max_insc_str': max_insc_ts.strftime('%d/%m/%Y'),
        'inicio': inicio,
        'ventana': f"{inicio.strftime('%d/%m/%Y')} - {max_insc_ts.strftime('%d/%m/%Y')}",
        'n_late': n_late,
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
        # Any-Touch causal (sin dedup global)
        'at': at_data,
        # Datos para Sankey
        'sankey_matrix': sankey_matrix,
    }

    print(f"    Ventana: {seg_data[seg]['ventana']}")
    print(f"    Leads CRM causal (dedup): {t_leads:,}  |  Inscriptos causales: {t_conv:,}  |  Tasa: {tasa_total:.2f}%")
    print(f"    Google: {g_leads:,} leads / {g_conv:,} insc")
    print(f"    Facebook: {f_leads:,} leads / {f_conv:,} insc")
    print(f"    Bot: {b_leads:,} leads / {b_conv:,} insc")

# ============================================================
# 3. CHARTS
# ============================================================
print("\nGenerando charts...")

pie_path = os.path.join(output_dir, 'fb_spend_pie.png')
if not fb_seg.empty:
    fig, ax = plt.subplots(figsize=(7, 5))
    fb_pie = fb_seg[fb_seg['FB_Spend'] > 0].copy()
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    pcts = fb_pie['FB_Spend'] / fb_pie['FB_Spend'].sum() * 100
    labels = [f"{row['Segmento']}\n{fmt_ars(row['FB_Spend'])} ({pct:.1f}%)"
              for (_, row), pct in zip(fb_pie.iterrows(), pcts)]
    ax.pie(fb_pie['FB_Spend'], labels=labels, colors=colors[:len(fb_pie)],
           startangle=140, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    ax.set_title(f'Facebook Ads: Inversión por Segmento\n({fb_periodo})', fontsize=12, fontweight='bold')
    plt.savefig(pie_path, bbox_inches='tight', dpi=150)
    plt.close()

cpl_cpa_path = os.path.join(output_dir, 'cpl_cpa_por_segmento.png')
segs_with_data = [s for s in SEGMENTOS if s in seg_data]
if segs_with_data:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(segs_with_data))
    w = 0.35

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

    g_cpas = [seg_data[s]['g_cpa'] for s in segs_with_data]
    f_cpas = [seg_data[s]['f_cpa'] for s in segs_with_data]
    bars3 = axes[1].bar(x - w/2, g_cpas, w, label='Google Ads', color='#4285f4')
    bars4 = axes[1].bar(x + w/2, f_cpas, w, label='Facebook Ads', color='#1877f2')
    axes[1].set_title('CPA - Costo por Inscripto (Causal)', fontweight='bold')
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

    plt.suptitle('Comparativa CPL / CPA por Segmento y Canal - Modelo Causal', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(cpl_cpa_path, bbox_inches='tight', dpi=150)
    plt.close()

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
# SANKEY CHARTS (plotly + kaleido)
# ============================================================
print("\nGenerando Sankey diagrams...")
import plotly.graph_objects as go

_CANAL_HEX = {
    'Google':   '#4285f4',
    'Facebook': '#1877f2',
    'Bot':      '#e74c3c',
    'Otros':    '#95a5a6',
}
_CANALES_ORDER = ['Google', 'Facebook', 'Bot', 'Otros']

sankey_paths = {}
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    flow_df = seg_data[seg].get('sankey_matrix', pd.DataFrame())
    if flow_df.empty:
        continue

    total_uniq = seg_data[seg]['at']['Total_Unico']['conv']

    # Nodes: 0-3 = First-Touch (izquierda), 4-7 = Last-Touch (derecha)
    node_labels = [f"{c}<br>(1er contacto)" for c in _CANALES_ORDER] + \
                  [f"{c}<br>(ult. contacto)" for c in _CANALES_ORDER]
    node_colors = [_CANAL_HEX[c] for c in _CANALES_ORDER] * 2

    ft_idx = {c: i for i, c in enumerate(_CANALES_ORDER)}
    lt_idx = {c: i + len(_CANALES_ORDER) for i, c in enumerate(_CANALES_ORDER)}

    sources, targets, values, link_colors = [], [], [], []
    for _, r in flow_df.iterrows():
        ft, lt, cnt = r['first_touch'], r['last_touch'], int(r['count'])
        if ft not in ft_idx or lt not in lt_idx:
            continue
        sources.append(ft_idx[ft])
        targets.append(lt_idx[lt])
        values.append(cnt)
        hx = _CANAL_HEX.get(ft, '#aaaaaa')
        rv, gv, bv = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
        link_colors.append(f'rgba({rv},{gv},{bv},0.40)')

    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            pad=30,
            thickness=35,
            label=node_labels,
            color=node_colors,
            line=dict(color='white', width=0.5),
        ),
        link=dict(source=sources, target=targets, value=values, color=link_colors),
    ))
    fig.update_layout(
        title=dict(
            text=f"Flujo de Atribucion Causal: First-Touch - Last-Touch | Campana Ingreso {COHORTE_YEAR}<br>"
                 f"<sup>{seg.replace('_', ' ')} | {PERIODO_LABEL[seg]} | {total_uniq:,} inscriptos unicos causales</sup>",
            font=dict(size=15, family='Arial'),
            x=0.5, xanchor='center',
        ),
        font=dict(size=12, family='Arial'),
        width=1100, height=640,
        margin=dict(l=30, r=30, t=80, b=30),
        paper_bgcolor='white',
    )
    sankey_path = os.path.join(output_dir, f'sankey_{seg.lower()}.png')
    try:
        fig.write_image(sankey_path, width=1100, height=640, scale=1.5)
        sankey_paths[seg] = sankey_path
        print(f"  Sankey {seg}: OK ({len(flow_df)} flujos)")
    except Exception as e:
        print(f"  [!] Error Sankey PNG {seg}: {e}")

# Bar charts: distribución First-Touch vs Last-Touch por canal
print("\nGenerando bar charts FT vs LT...")
bar_paths = {}
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    flow_df = seg_data[seg].get('sankey_matrix', pd.DataFrame())
    if flow_df.empty:
        continue

    ft_counts = flow_df.groupby('first_touch')['count'].sum()
    lt_counts = flow_df.groupby('last_touch')['count'].sum()
    ft_vals = [int(ft_counts.get(c, 0)) for c in _CANALES_ORDER]
    lt_vals = [int(lt_counts.get(c, 0)) for c in _CANALES_ORDER]

    x = np.arange(len(_CANALES_ORDER))
    w = 0.35
    fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
    bars_ft = ax_bar.bar(x - w/2, ft_vals, w, label='First-Touch',
                         color=[_CANAL_HEX[c] for c in _CANALES_ORDER], alpha=0.85)
    bars_lt = ax_bar.bar(x + w/2, lt_vals, w, label='Last-Touch',
                         color=[_CANAL_HEX[c] for c in _CANALES_ORDER], alpha=0.45,
                         edgecolor=[_CANAL_HEX[c] for c in _CANALES_ORDER], linewidth=1.5)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(_CANALES_ORDER, fontsize=12)
    ax_bar.set_ylabel('Inscriptos Causales', fontsize=11)
    max_val = max(ft_vals + lt_vals) if (ft_vals + lt_vals) else 1
    ax_bar.set_title(
        f'Distribucion First-Touch vs Last-Touch por Canal\n'
        f'{seg.replace("_", " ")} | {PERIODO_LABEL[seg]} | Campana Ingreso {COHORTE_YEAR}',
        fontsize=12)
    ax_bar.legend(fontsize=11)
    for bar in list(bars_ft) + list(bars_lt):
        h = bar.get_height()
        if h > 0:
            ax_bar.text(bar.get_x() + bar.get_width() / 2, h + max_val * 0.01,
                        f'{int(h):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    plt.tight_layout()
    bar_path = os.path.join(output_dir, f'sankey_bar_{seg.lower()}.png')
    fig_bar.savefig(bar_path, dpi=140, bbox_inches='tight')
    plt.close(fig_bar)
    bar_paths[seg] = bar_path
    print(f"  Bar chart FT/LT {seg}: OK")

# ============================================================
# 4. GENERAR PDF (LANDSCAPE)
# ============================================================
print("\nGenerando PDF...")

BLUE = (41, 128, 185)
LIGHT_BLUE = (235, 245, 255)
DARK = (30, 30, 30)
GRAY = (120, 120, 120)
ORANGE = (211, 84, 0)

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*DARK)
        self.cell(0, 9, 'UCASAL - Inversion Publicitaria y ROI  |  Atribucion Causal  |  Ingreso 2026',
                  align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*GRAY)
        self.cell(0, 8, f'Pag. {self.page_no()}  |  Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}  |  Modelo Causal: consulta <= fecha de pago',
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

    def alerta(self, txt):
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*ORANGE)
        self.multi_cell(0, 4, txt)
        self.set_text_color(*DARK)


pdf = PDF('L')
pdf.set_auto_page_break(auto=True, margin=14)

# =============== PÁGINA 1: RESUMEN EJECUTIVO ===============
pdf.add_page()
pdf.section_title('1. Resumen Ejecutivo - Atribucion Causal')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5, f'Período Google Ads: {GOOGLE_PERIODO}  |  Período Facebook Ads: {fb_periodo}',
         new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(1)
pdf.alerta(
    'MODELO CAUSAL: solo se cuentan como conversión las consultas cuya fecha de creación es '
    'ANTERIOR O IGUAL a la fecha de pago de inscripción. Consultas post-pago excluidas.'
)
pdf.ln(2)

# Tabla inversión total por segmento
pdf.subsection('Inversión Total por Segmento y Canal (ARS)')
hdrs = ['Segmento', 'Período Análisis', 'Google Ads', 'Facebook Ads', 'TOTAL Invertido', 'Excl. post-pago']
wids = [40, 52, 45, 45, 45, 30]
aligns = ['L', 'C', 'R', 'R', 'R', 'R']
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
        f"{d['n_late']:,}",
    ], wids, fill=(i % 2 == 0), aligns=aligns)

pdf.table_row([
    'TOTAL', '', fmt_ars_full(grand_total_g), fmt_ars_full(grand_total_f),
    fmt_ars_full(grand_total_g + grand_total_f),
    f"{sum(seg_data[s]['n_late'] for s in seg_data):,}",
], wids, bold=True, fill=True, aligns=aligns)
pdf.ln(4)

# Tabla KPIs consolidada
pdf.subsection('KPIs Consolidados por Segmento (modelo causal, todos los canales)')
hdrs2 = ['Segmento', 'Período', 'Leads CRM', 'Insc. Causal', 'Tasa Conv.', 'Inversión Total',
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
    'Causal: solo se atribuye la consulta si ocurrió ANTES o el MISMO DIA del pago de inscripcion. '
    'CPL = Inversion / Leads CRM deduplicados. CPA = Inversion / Inscriptos causales. '
    f'Facebook: solo campanas {COHORTE_YEAR}. Google sin impuestos. Revenue = Insc_Haber al momento de inscripcion.'
)

# =============== PÁGINA 2: KPIs CONSOLIDADOS SEGMENTO × CANAL ===============
pdf.add_page()
pdf.section_title('2. KPIs Consolidados por Segmento y Canal - Modelo Causal')
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5, f'Facebook: solo campanas {COHORTE_YEAR}  |  Google: sin impuestos  |  Solo conversiones causales (consulta <= fecha pago)',
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
    'Solo se atribuyen como conversiones las consultas cuya Consulta: Fecha de creacion <= Insc_Fecha Pago. '
    'Consultas generadas DESPUES del pago (post-venta, soporte) quedan excluidas. '
    'La columna "Leads" no cambia (el filtro solo afecta la clasificacion de conversiones).'
)

# =============== PÁGINA 3: COMPARATIVA ESTÁNDAR VS CAUSAL ===============
pdf.add_page()
pdf.section_title('3. Comparativa: Modelo Estándar vs Modelo Causal')
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5,
         'Estandar = sin filtro de fecha  |  Causal = consulta <= fecha de pago  |  '
         'Diferencia = cuántos inscriptos se pierden al aplicar el filtro causal',
         new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(2)

hdrs_comp = ['Segmento', 'Canal', 'Insc. Estándar', 'Rev. Estándar', 'Insc. Causal', 'Rev. Causal', 'Dif. Insc.', 'Dif. %']
wids_comp = [35, 28, 25, 35, 25, 35, 22, 22]
aligns_comp = ['L', 'L', 'R', 'R', 'R', 'R', 'R', 'R']
pdf.table_header(hdrs_comp, wids_comp, aligns_comp)

row_idx = 0
canal_keys = {
    'Google Ads': ('g_conv', 'g_rev', 'Google'),
    'Facebook Ads': ('f_conv', 'f_rev', 'Facebook'),
    'Bot/Chatbot': ('b_conv', 'b_rev', 'Bot'),
    'Otros': ('o_conv', 'o_rev', 'Otros'),
}
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    sd = std_data[seg]
    seg_label = seg.replace('_', ' ')
    seg_std_total = sd['Total']['conv']
    seg_cau_total = d['total_conv']

    for canal_label, (cau_key, rev_key, std_key) in canal_keys.items():
        cau_conv = d[cau_key]
        cau_rev = d[rev_key]
        std_conv = sd[std_key]['conv']
        std_rev = sd[std_key]['rev']
        diff = cau_conv - std_conv
        diff_pct = safe_div(diff, std_conv) * 100 if std_conv > 0 else (0 if diff == 0 else float('inf'))
        pdf.table_row([
            seg_label if canal_label == 'Google Ads' else '',
            canal_label,
            f"{std_conv:,}",
            fmt_ars_full(std_rev),
            f"{cau_conv:,}",
            fmt_ars_full(cau_rev),
            f"{diff:+,}" if diff != 0 else '-',
            f"{diff_pct:+.1f}%" if diff != 0 and diff_pct != float('inf') else ('-' if diff == 0 else 'N/A'),
        ], wids_comp, fill=(row_idx % 2 == 0), aligns=aligns_comp)
        row_idx += 1

    diff_tot = seg_cau_total - seg_std_total
    pdf.table_row([
        '', f'Total {seg_label}',
        f"{seg_std_total:,}", fmt_ars_full(sd['Total']['rev']),
        f"{seg_cau_total:,}", fmt_ars_full(d['total_rev']),
        f"{diff_tot:+,}" if diff_tot != 0 else '-', '-',
    ], wids_comp, bold=True, fill=True, aligns=aligns_comp)
    row_idx += 1

pdf.ln(3)
pdf.nota(
    'Diferencia negativa = el canal pierde inscriptos al aplicar el filtro causal (sus consultas son post-pago). '
    'Bot/Chatbot suele perder mas porque atiende tambien seguimiento post-venta. '
    'Los totales de personas inscritas son iguales; cambia la atribucion por canal. '
    'El modelo Causal es el recomendado para evaluar el impacto REAL de la publicidad en la decision de compra.'
)

# =============== PÁGINA 4: COMPARATIVA LT-CAUSAL vs ANY-TOUCH CAUSAL ===============
pdf.add_page()
pdf.section_title('4. Comparativa: Last-Touch Causal vs Any-Touch Causal')
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5,
    'Last-Touch Causal: 1 canal por inscripto (el mas reciente antes del pago)  |  '
    'Any-Touch Causal: todos los canales que tuvieron contacto causal con el inscripto (sin dedup global)',
    new_x='LMARGIN', new_y='NEXT')
pdf.set_text_color(*DARK)
pdf.ln(2)

hdrs_at = ['Segmento', 'Canal', 'LT-Causal', '% del Total', 'Any-Touch', '% del Total', 'Dif. Insc.']
wids_at = [35, 28, 25, 22, 25, 22, 22]
aligns_at = ['L', 'L', 'R', 'R', 'R', 'R', 'R']
pdf.table_header(hdrs_at, wids_at, aligns_at)

row_idx = 0
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    at = d['at']
    seg_label = seg.replace('_', ' ')
    total_lt = d['total_conv']
    total_at = at['Total_Unico']['conv']

    lt_vals = {
        'Google Ads': d['g_conv'],
        'Facebook Ads': d['f_conv'],
        'Bot/Chatbot': d['b_conv'],
        'Otros': d['o_conv'],
    }
    at_keys = {'Google Ads': 'Google', 'Facebook Ads': 'Facebook', 'Bot/Chatbot': 'Bot', 'Otros': 'Otros'}

    for canal_label, lt_conv in lt_vals.items():
        at_conv = at[at_keys[canal_label]]['conv']
        diff = at_conv - lt_conv
        pct_lt = safe_div(lt_conv, total_lt) * 100
        pct_at = safe_div(at_conv, total_at) * 100
        pdf.table_row([
            seg_label if canal_label == 'Google Ads' else '',
            canal_label,
            f"{lt_conv:,}",
            f"{pct_lt:.1f}%",
            f"{at_conv:,}",
            f"{pct_at:.1f}%",
            f"{diff:+,}" if diff != 0 else '-',
        ], wids_at, fill=(row_idx % 2 == 0), aligns=aligns_at)
        row_idx += 1

    # Totales del segmento
    sum_at_canales = sum(at[k]['conv'] for k in ['Google', 'Facebook', 'Bot', 'Otros'])
    pdf.table_row([
        '', f'Total {seg_label}',
        f"{total_lt:,}", '100%',
        f"{total_at:,} ({sum_at_canales:,} sum)",
        f"{safe_div(sum_at_canales, total_at)*100:.1f}x" if total_at > 0 else '-',
        f"+{sum_at_canales - total_lt:,}" if sum_at_canales > total_lt else '-',
    ], wids_at, bold=True, fill=True, aligns=aligns_at)
    row_idx += 1

pdf.ln(3)
pdf.nota(
    'Any-Touch Causal: un inscripto puede contarse en varios canales si interactuó causalmente con todos ellos. '
    'La suma de Any-Touch por canal es MAYOR que el total de inscriptos unicos. '
    'LT-Causal: 1 canal exclusivo por inscripto (el más reciente antes del pago). '
    '"Total (sum)" = suma bruta por canal; "Total unico" = inscriptos únicos (sin doble conteo). '
    'El % de Any-Touch se calcula sobre el total de inscriptos únicos causales.'
)

# =============== PÁGINA 5: KPIs POR GRUPO (Grado_Pregrado) ===============
if 'Grado_Pregrado' in seg_data and fb_grupo_data:
    pdf.add_page()
    pdf.section_title('5. KPIs por Grupo de Carreras (Grado_Pregrado - Facebook)')
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, 'Desglose de inversion y metricas de Facebook por grupo de carreras (inversion = igual en ambos modelos)',
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

    total_cpl = safe_div(total_spend_grp, total_leads_grp)
    pdf.table_row([
        'TOTAL', f"{sum(d['n_campanas'] for d in fb_grupo_data.values())}",
        fmt_ars_full(total_spend_grp),
        f"{int(total_leads_grp):,}" if total_leads_grp > 0 else '-',
        '-', '-',
        fmt_ars_full(total_cpl) if total_cpl > 0 else '-',
    ], wids_grp, bold=True, fill=True, aligns=aligns_grp)
    pdf.ln(3)

# =============== PÁGINAS 5+: DETALLE POR SEGMENTO ===============
for seg in SEGMENTOS:
    if seg not in seg_data:
        continue
    d = seg_data[seg]
    seg_label = seg.replace('_', ' ')

    pdf.add_page()
    pdf.section_title(f'6. Detalle Causal: {seg_label}')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, f'{PERIODO_LABEL[seg]}  |  Ventana: {d["ventana"]}  |  Última inscripción: {d["max_insc_str"]}  |  Consultas post-pago excluidas: {d["n_late"]:,}',
             new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.ln(2)

    pdf.subsection(f'KPIs por Canal (modelo causal) - {seg_label}')
    hdrs_c = ['Canal', 'Inversión', 'Leads CRM', 'Leads Plat.', 'Inscriptos', 'Tasa Conv.',
              'CPL (CRM)', 'CPL (Plat.)', 'CPA', 'Rev. Atribuida', 'ROI']
    wids_c = [30, 32, 22, 22, 22, 18, 25, 25, 28, 30, 20]
    aligns_c = ['L', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
    pdf.table_header(hdrs_c, wids_c, aligns_c)

    if d['g_spend'] > 0 or d['g_leads'] > 0:
        pdf.table_row([
            'Google Ads', fmt_ars_full(d['g_spend']),
            f"{d['g_leads']:,}", '-',
            f"{d['g_conv']:,}", f"{d['tasa_google']:.2f}%",
            fmt_ars_full(d['g_cpl']) if d['g_cpl'] > 0 else '-',
            '-',
            fmt_ars_full(d['g_cpa']) if d['g_cpa'] > 0 else '-',
            fmt_ars_full(d['g_rev']), fmt_pct(d['g_roi']),
        ], wids_c, fill=True, aligns=aligns_c)

    if d['f_spend'] > 0 or d['f_leads_crm'] > 0:
        pdf.table_row([
            'Facebook Ads', fmt_ars_full(d['f_spend']),
            f"{d['f_leads_crm']:,}", f"{d['f_leads_plat']:,}",
            f"{d['f_conv']:,}", f"{d['tasa_fb']:.2f}%",
            fmt_ars_full(d['f_cpl']) if d['f_cpl'] > 0 else '-',
            fmt_ars_full(d['f_cpl_plat']) if d['f_cpl_plat'] > 0 else '-',
            fmt_ars_full(d['f_cpa']) if d['f_cpa'] > 0 else '-',
            fmt_ars_full(d['f_rev']), fmt_pct(d['f_roi']),
        ], wids_c, fill=False, aligns=aligns_c)

    if d['b_leads'] > 0:
        pdf.table_row([
            'Bot/Chatbot', '-',
            f"{d['b_leads']:,}", '-',
            f"{d['b_conv']:,}", f"{d['tasa_bot']:.2f}%",
            '-', '-', '-', fmt_ars_full(d['b_rev']), '-',
        ], wids_c, fill=True, aligns=aligns_c)

    if d['o_leads'] > 0:
        pdf.table_row([
            'Otros/Orgánico', '-',
            f"{d['o_leads']:,}", '-',
            f"{d['o_conv']:,}", f"{safe_div(d['o_conv'], d['o_leads'])*100:.2f}%",
            '-', '-', '-', fmt_ars_full(d['o_rev']), '-',
        ], wids_c, fill=False, aligns=aligns_c)

    pdf.table_row([
        'TOTAL', fmt_ars_full(d['total_spend']),
        f"{d['total_leads_crm']:,}", f"{d['f_leads_plat']:,}",
        f"{d['total_conv']:,}", f"{d['tasa_total']:.2f}%",
        fmt_ars_full(safe_div(d['total_spend'], d['total_leads_crm'])) if d['total_spend'] > 0 else '-',
        '-',
        fmt_ars_full(safe_div(d['total_spend'], d['total_conv'])) if d['total_spend'] > 0 else '-',
        fmt_ars_full(d['total_rev']), fmt_pct(d['roi_total']),
    ], wids_c, bold=True, fill=True, aligns=aligns_c)
    pdf.ln(3)

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
                str(idx), nombre,
                fmt_ars_full(r['Spend']), f"{pct_seg:.1f}%",
                f"{int(r['Leads_Plat']):,}" if r['Leads_Plat'] > 0 else '-',
                fmt_ars_full(r['CPL_Plat']) if r['CPL_Plat'] > 0 else '-',
                f"{int(r['Impresiones']):,}" if r['Impresiones'] > 0 else '-',
                f"{int(r['Clics']):,}" if r['Clics'] > 0 else '-',
            ], wids_t, fill=(idx % 2 == 0), aligns=aligns_t)

# =============== PÁGINAS FINALES: CHARTS ===============
pdf.add_page()
pdf.section_title('7. Graficos Comparativos (Modelo Causal)')
if os.path.exists(cpl_cpa_path):
    pdf.image(cpl_cpa_path, x=15, w=250)
    pdf.ln(5)

pdf.add_page()
pdf.section_title('8. Facebook Ads: Distribucion de Inversion')
if os.path.exists(pie_path):
    pdf.image(pie_path, x=50, w=170)
    pdf.ln(5)

for seg in SEGMENTOS:
    if seg in top_camp_paths and os.path.exists(top_camp_paths[seg]):
        pdf.add_page()
        pdf.section_title(f'Top Campanas Facebook - {seg.replace("_", " ")}')
        pdf.image(top_camp_paths[seg], x=10, w=260)

# =============== PÁGINAS SANKEY: BAR CHART + FLUJO FIRST-TOUCH → LAST-TOUCH ===============
for seg in SEGMENTOS:
    has_bar = seg in bar_paths and os.path.exists(bar_paths[seg])
    has_sankey = seg in sankey_paths and os.path.exists(sankey_paths[seg])
    if not has_bar and not has_sankey:
        continue
    seg_label = seg.replace('_', ' ')

    # --- Página A: Bar chart FT vs LT ---
    if has_bar:
        pdf.add_page()
        pdf.section_title(f'9. Distribucion First-Touch vs Last-Touch | Campana Ingreso {COHORTE_YEAR} [{seg_label}]')
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 5,
            f'{PERIODO_LABEL[seg]}  |  Leads clasificados segun primer y ultimo canal de contacto causal.',
            new_x='LMARGIN', new_y='NEXT')
        pdf.set_text_color(*DARK)
        pdf.ln(3)
        pdf.image(bar_paths[seg], x=40, w=210)
        pdf.ln(3)
        pdf.nota(
            f'First-Touch (barras opacas): canal del primer contacto causal con el inscripto. '
            f'Last-Touch (barras semitransparentes): canal del ultimo contacto causal antes del pago. '
            f'Solo incluye leads de {PERIODO_LABEL[seg]} (Campana Ingreso {COHORTE_YEAR}). '
            f'Facebook clasificado por FuenteLead=18 (Lead Ads) y UtmSource; '
            f'la ventana temporal garantiza cobertura de la campana activa.'
        )

    # --- Página B: Sankey FT -> LT ---
    if has_sankey:
        pdf.add_page()
        pdf.section_title(f'9. Flujo de Atribucion: First-Touch >> Last-Touch | Campana Ingreso {COHORTE_YEAR} [{seg_label}]')
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(*GRAY)
        total_uniq = seg_data[seg]['at']['Total_Unico']['conv']
        n_stays = sum(int(r['count']) for _, r in seg_data[seg]['sankey_matrix'].iterrows()
                      if r['first_touch'] == r['last_touch'])
        n_changes = total_uniq - n_stays
        pdf.cell(0, 5,
            f'{PERIODO_LABEL[seg]}  |  '
            f'{total_uniq:,} inscriptos causales | '
            f'{n_stays:,} mismo canal ({safe_div(n_stays, total_uniq)*100:.1f}%) | '
            f'{n_changes:,} cambiaron de canal ({safe_div(n_changes, total_uniq)*100:.1f}%)',
            new_x='LMARGIN', new_y='NEXT')
        pdf.set_text_color(*DARK)
        pdf.ln(2)
        pdf.image(sankey_paths[seg], x=5, w=282)
        pdf.ln(3)
        pdf.nota(
            f'Solo incluye leads de {PERIODO_LABEL[seg]} (Campana Ingreso {COHORTE_YEAR}). '
            'Nodo izquierdo = primer contacto causal (First-Touch). '
            'Nodo derecho = ultimo contacto causal antes del pago (Last-Touch). '
            'El grosor de cada flujo es proporcional al numero de inscriptos. '
            'Flujos cruzados = persona contactada por multiples canales antes del pago. '
            'Facebook clasificado por FuenteLead=18 y UtmSource; '
            'la ventana temporal cubre el periodo activo de la campana.'
        )

# ============================================================
# 5. OUTPUT
# ============================================================
pdf_path = os.path.join(output_dir, 'Presupuesto_ROI_Causal_Ingreso2026.pdf')
pdf.output(pdf_path)
print(f"\n-> PDF generado: {pdf_path}")

print("Generando Excel de respaldo...")
with pd.ExcelWriter(os.path.join(output_dir, 'Presupuesto_ROI_Causal_Datos.xlsx'), engine='xlsxwriter') as writer:
    # Hoja 1: KPIs causales por canal
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
                'Consultas_PostPago_Excluidas': d['n_late'],
                'Inversión_ARS': spend,
                'Leads_CRM': leads,
                'Inscriptos_Causal': conv,
                'Tasa_Conversión_%': round(tasa, 2),
                'CPL_ARS': round(cpl, 2),
                'CPA_ARS': round(cpa, 2),
                'Revenue_Atribuida_ARS': round(rev, 2),
                'ROI_%': round(roi, 2),
            })
    pd.DataFrame(rows_excel).to_excel(writer, sheet_name='KPIs_Causal_Por_Canal', index=False)

    # Hoja 2: Comparativa Estándar vs Causal
    rows_comp = []
    for seg in SEGMENTOS:
        if seg not in seg_data:
            continue
        d = seg_data[seg]
        sd = std_data[seg]
        for canal, cau_key, rev_key, std_key in [
            ('Google Ads', 'g_conv', 'g_rev', 'Google'),
            ('Facebook Ads', 'f_conv', 'f_rev', 'Facebook'),
            ('Bot/Chatbot', 'b_conv', 'b_rev', 'Bot'),
            ('Otros/Orgánico', 'o_conv', 'o_rev', 'Otros'),
        ]:
            rows_comp.append({
                'Segmento': seg,
                'Canal': canal,
                'Inscriptos_Estandar': sd[std_key]['conv'],
                'Revenue_Estandar': round(sd[std_key]['rev'], 2),
                'Inscriptos_Causal': d[cau_key],
                'Revenue_Causal': round(d[rev_key], 2),
                'Diferencia_Inscriptos': d[cau_key] - sd[std_key]['conv'],
            })
    pd.DataFrame(rows_comp).to_excel(writer, sheet_name='Causal_vs_Estandar', index=False)

    # Hoja 3: Any-Touch Causal vs Last-Touch Causal
    rows_at = []
    for seg in SEGMENTOS:
        if seg not in seg_data:
            continue
        d = seg_data[seg]
        at = d['at']
        for canal, lt_key, at_key in [
            ('Google Ads', 'g_conv', 'Google'),
            ('Facebook Ads', 'f_conv', 'Facebook'),
            ('Bot/Chatbot', 'b_conv', 'Bot'),
            ('Otros/Organico', 'o_conv', 'Otros'),
        ]:
            lt_conv = d[lt_key]
            at_conv = at[at_key]['conv']
            rows_at.append({
                'Segmento': seg,
                'Canal': canal,
                'Inscriptos_LastTouch_Causal': lt_conv,
                'Inscriptos_AnyTouch_Causal': at_conv,
                'Diferencia': at_conv - lt_conv,
                'Revenue_AnyTouch': round(at[at_key]['rev'], 2),
            })
        rows_at.append({
            'Segmento': seg,
            'Canal': 'TOTAL UNICO',
            'Inscriptos_LastTouch_Causal': d['total_conv'],
            'Inscriptos_AnyTouch_Causal': at['Total_Unico']['conv'],
            'Diferencia': '',
            'Revenue_AnyTouch': round(at['Total_Unico']['rev'], 2),
        })
    pd.DataFrame(rows_at).to_excel(writer, sheet_name='AnyTouch_vs_LastTouch', index=False)

    # Hoja 4: Facebook por campaña (solo cohorte)
    if not fb_cohorte.empty:
        fb_cohorte.copy().to_excel(writer, sheet_name='Facebook_Detalle', index=False)

    # Hoja 4: Top campañas por segmento
    for seg in SEGMENTOS:
        if seg in fb_top_by_seg:
            fb_top_by_seg[seg].to_excel(writer, sheet_name=f'Top_FB_{seg[:15]}', index=False)

    # Hoja 5: Campañas excluidas (otros años)
    if not fb_excluidas.empty:
        excl_summary = (fb_excluidas.groupby(['Segmento', 'Cohorte_Year'])
                        .agg(Spend=('Importe gastado (ARS)', 'sum'),
                             Leads=('Clientes potenciales', 'sum'),
                             Filas=('Importe gastado (ARS)', 'count'))
                        .reset_index()
                        .sort_values(['Segmento', 'Cohorte_Year']))
        excl_summary.to_excel(writer, sheet_name='FB_Excluidas_Resumen', index=False)

print(f"-> Excel generado: {os.path.join(output_dir, 'Presupuesto_ROI_Causal_Datos.xlsx')}")
print(f"-> Total invertido: {fmt_ars_full(grand_total_g + grand_total_f)} ARS")
print("Proceso finalizado — Modelo Causal.")
