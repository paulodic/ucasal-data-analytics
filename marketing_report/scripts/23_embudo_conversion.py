"""
23_embudo_conversion.py — Embudo de conversión: Consulta -> Boleta -> Inscripción

Genera un análisis de funnel por segmento mostrando:
  1. Cuántas personas consultaron (leads únicos)
  2. Cuántas generaron boleta (cruzando contra archivo de boletas)
  3. Cuántas pagaron (inscriptos)
  4. Tasas de conversión entre etapas
  5. Desglose por canal y campaña
"""
import os
import glob
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF
from tabulate import tabulate

# ==========================================
# CONFIGURACIÓN
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
data_dir = os.path.join(base_dir, "outputs", "Data_Base")
raw_dir = os.path.join(base_dir, "data", "1_raw")
output_dir = os.path.join(base_dir, "outputs", "Embudo_Conversion")
os.makedirs(output_dir, exist_ok=True)

SEGMENTOS = ['Grado_Pregrado', 'Cursos', 'Posgrados']

PERIODO_INICIO = {
    'Grado_Pregrado': pd.Timestamp('2025-09-01'),
    'Cursos':         pd.Timestamp('2026-01-01'),
    'Posgrados':      pd.Timestamp('2026-01-01'),
}
CAMPANA_LABEL = {
    'Grado_Pregrado': 'Ingreso 2026',
    'Cursos':         '2026',
    'Posgrados':      '2026',
}

META_KW = ['fb', 'facebook', 'ig', 'instagram', 'meta']


def clean_dni(val):
    if pd.isna(val) or val == '':
        return None
    s = str(val).split('.')[0].strip().replace('.', '').replace('-', '').replace(' ', '')
    return s if s else None


def classify_canal(row):
    utm = str(row.get('_utm', '')).lower()
    fl = row.get('_fuente', np.nan)
    if 'google' in utm:
        return 'Google'
    if any(k in utm for k in META_KW) or fl == 18:
        return 'Meta'
    if fl == 907:
        return 'Bot'
    return 'Otros'


def safe_div(a, b):
    return a / b if b > 0 else 0.0


def fmt_pct(val):
    return f"{val:.1f}%"


def fmt_n(val):
    return f"{val:,}"


# ==========================================
# LECTURA DE BOLETAS RAW (TODAS, incluyendo pagadas)
# ==========================================
print("Leyendo boletas raw...")
boletas_dir = os.path.join(raw_dir, "boletas")
boletas_files = glob.glob(os.path.join(boletas_dir, "*.xlsx")) + \
                glob.glob(os.path.join(boletas_dir, "*.xls"))

df_boletas_all = pd.DataFrame()
if boletas_files:
    bl = []
    for f in boletas_files:
        engine = 'xlrd' if f.endswith('.xls') else None
        df = pd.read_excel(f, engine=engine)
        bl.append(df)
        print(f"  {os.path.basename(f)}: {len(df)} filas")
    df_boletas_all = pd.concat(bl, ignore_index=True)
    if 'Nro Transac' in df_boletas_all.columns:
        df_boletas_all = df_boletas_all.drop_duplicates(subset=['Nro Transac'])
    df_boletas_all['_bol_dni'] = df_boletas_all.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
    print(f"Total boletas únicas: {len(df_boletas_all)}")
else:
    print("No se encontraron archivos de boletas. Abortando.")
    exit()

# Segmentar boletas
def segmentar_tipcar(val):
    v = str(val).lower()
    if 'curso' in v: return 'Cursos'
    if any(k in v for k in ['postgrado', 'maestría', 'maestria', 'posgrado']): return 'Posgrados'
    if 'grado' in v or 'pregrado' in v: return 'Grado_Pregrado'
    return 'Desconocido'

df_boletas_all['_seg'] = df_boletas_all.get('Tipcar', pd.Series(dtype='str')).apply(segmentar_tipcar)

# ==========================================
# PROCESAR CADA SEGMENTO
# ==========================================
all_funnel = []   # lista de dicts para tabla consolidada
all_canal = []    # desglose por canal
all_campana = []  # desglose por campaña
sankey_data = {}  # {seg: {canal: {'sin_boleta': N, 'bol_no_pago': N, 'bol_pago': N}}}

for seg in SEGMENTOS:
    seg_dir = os.path.join(data_dir, seg)
    leads_path = os.path.join(seg_dir, "reporte_marketing_leads_completos.csv")
    insc_path = os.path.join(seg_dir, "reporte_marketing_inscriptos_origenes.csv")

    if not os.path.exists(leads_path):
        print(f"[{seg}] Sin datos de leads, salteando.")
        continue

    print(f"\n=== {seg} ===")
    usecols_leads = [
        'Consulta: Fecha de creación', 'DNI', 'Correo', 'Telefono', 'Celular',
        'FuenteLead', 'UtmSource', 'Match_Tipo', 'Campana_Lead',
    ]
    # Agregar columnas Bol_ si existen
    df_peek = pd.read_csv(leads_path, nrows=0)
    bol_cols = [c for c in df_peek.columns if c.startswith('Bol_')]
    usecols_leads += bol_cols
    usecols_leads = [c for c in usecols_leads if c in df_peek.columns]

    df_leads = pd.read_csv(leads_path, usecols=usecols_leads)
    print(f"  Leads: {len(df_leads)}")

    # Limpiar DNI de leads
    df_leads['_dni'] = df_leads.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
    df_leads['_utm'] = df_leads.get('UtmSource', pd.Series(dtype='str')).astype(str).str.lower().str.strip()
    df_leads['_fuente'] = pd.to_numeric(df_leads.get('FuenteLead', pd.Series(dtype='float')), errors='coerce')
    df_leads['_canal'] = df_leads.apply(classify_canal, axis=1)
    df_leads['_fecha'] = pd.to_datetime(
        df_leads['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_leads['_mc'] = df_leads['Match_Tipo'].astype(str).str.lower()

    # Boletas de este segmento
    bol_seg = df_boletas_all[df_boletas_all['_seg'] == seg]
    bol_dnis = set(bol_seg['_bol_dni'].dropna())
    print(f"  Boletas (segmento): {len(bol_seg)} ({len(bol_dnis)} DNIs únicos)")

    # Inscriptos
    if os.path.exists(insc_path):
        df_insc = pd.read_csv(insc_path, usecols=lambda c: c in ['Insc_DNI', 'DNI', 'Insc_Apellido y Nombre'])
        insc_dni_col = 'Insc_DNI' if 'Insc_DNI' in df_insc.columns else 'DNI'
        df_insc['_dni'] = df_insc[insc_dni_col].apply(clean_dni)
        insc_dnis = set(df_insc['_dni'].dropna())
        n_inscriptos = len(insc_dnis)
    else:
        insc_dnis = set()
        n_inscriptos = 0
    print(f"  Inscriptos (DNIs únicos): {n_inscriptos}")

    # ----- EMBUDO POR PERSONA (DNI) -----
    # Dedup leads: una fila por persona (más reciente primero)
    df_personas = (df_leads[df_leads['_dni'].notna()]
                   .sort_values('_fecha', ascending=False)
                   .drop_duplicates(subset='_dni', keep='first')
                   .copy())
    n_personas = len(df_personas)

    # Marcar etapas
    df_personas['tiene_boleta'] = df_personas['_dni'].isin(bol_dnis)
    df_personas['es_inscripto'] = df_personas['_mc'].str.contains('exacto', na=False)

    # Boletas que NO son leads (personas que generaron boleta sin consulta previa)
    lead_dnis = set(df_personas['_dni'].dropna())
    bol_sin_lead = bol_dnis - lead_dnis

    # Inscriptos que NO son leads (inscripción directa)
    insc_sin_lead = insc_dnis - lead_dnis

    n_con_boleta = int(df_personas['tiene_boleta'].sum())
    n_inscripto_lead = int(df_personas['es_inscripto'].sum())
    # Boletas que pagaron (están en inscriptos)
    n_bol_pagaron = len(bol_dnis & insc_dnis)

    # Tasas del embudo
    tasa_lead_bol = safe_div(n_con_boleta, n_personas) * 100
    tasa_bol_pago = safe_div(n_bol_pagaron, len(bol_dnis)) * 100
    tasa_lead_pago = safe_div(n_inscripto_lead, n_personas) * 100

    print(f"  Personas con DNI (leads): {fmt_n(n_personas)}")
    print(f"  Con boleta: {fmt_n(n_con_boleta)} ({fmt_pct(tasa_lead_bol)})")
    print(f"  Boletas->Pago: {fmt_n(n_bol_pagaron)}/{fmt_n(len(bol_dnis))} ({fmt_pct(tasa_bol_pago)})")
    print(f"  Lead->Inscripto: {fmt_n(n_inscripto_lead)} ({fmt_pct(tasa_lead_pago)})")
    print(f"  Boletas sin lead: {fmt_n(len(bol_sin_lead))}")
    print(f"  Inscriptos sin lead: {fmt_n(len(insc_sin_lead))}")

    funnel = {
        'Segmento': seg,
        'Leads (personas)': n_personas,
        'Con Boleta': n_con_boleta,
        'Tasa Lead->Boleta': tasa_lead_bol,
        'Boletas Totales (DNI)': len(bol_dnis),
        'Boletas Pagaron': n_bol_pagaron,
        'Boletas Sin Pago': len(bol_dnis) - n_bol_pagaron,
        'Tasa Boleta->Pago': tasa_bol_pago,
        'Inscriptos (lead)': n_inscripto_lead,
        'Tasa Lead->Pago': tasa_lead_pago,
        'Boletas sin Lead': len(bol_sin_lead),
        'Inscriptos sin Lead': len(insc_sin_lead),
    }
    all_funnel.append(funnel)

    # ----- DESGLOSE POR CANAL -----
    sankey_data[seg] = {}
    for canal in ['Google', 'Meta', 'Bot', 'Otros']:
        sub = df_personas[df_personas['_canal'] == canal]
        n_p = len(sub)
        n_b = int(sub['tiene_boleta'].sum())
        n_i = int(sub['es_inscripto'].sum())
        # Para Sankey: personas con boleta que pagaron vs no pagaron
        sub_bol = sub[sub['tiene_boleta']]
        n_bol_pago = int(sub_bol['es_inscripto'].sum())
        n_bol_no_pago = n_b - n_bol_pago
        sankey_data[seg][canal] = {
            'sin_boleta': n_p - n_b,
            'bol_no_pago': n_bol_no_pago,
            'bol_pago': n_bol_pago,
        }
        all_canal.append({
            'Segmento': seg,
            'Canal': canal,
            'Leads': n_p,
            'Con Boleta': n_b,
            'Tasa L->B': safe_div(n_b, n_p) * 100,
            'Inscriptos': n_i,
            'Tasa L->I': safe_div(n_i, n_p) * 100,
            'Tasa B->I': safe_div(n_i, n_b) * 100 if n_b > 0 else 0,
        })

    # ----- DESGLOSE POR CAMPAÑA -----
    inicio = PERIODO_INICIO[seg]
    label_actual = CAMPANA_LABEL[seg]
    if 'Campana_Lead' in df_personas.columns:
        for camp_label in [label_actual, 'Campaña Anterior']:
            sub = df_personas[df_personas['Campana_Lead'] == camp_label]
            n_p = len(sub)
            n_b = int(sub['tiene_boleta'].sum())
            n_i = int(sub['es_inscripto'].sum())
            all_campana.append({
                'Segmento': seg,
                'Campana': camp_label,
                'Leads': n_p,
                'Con Boleta': n_b,
                'Tasa L->B': safe_div(n_b, n_p) * 100,
                'Inscriptos': n_i,
                'Tasa L->I': safe_div(n_i, n_p) * 100,
                'Tasa B->I': safe_div(n_i, n_b) * 100 if n_b > 0 else 0,
            })

# ==========================================
# DATAFRAMES CONSOLIDADOS
# ==========================================
df_funnel = pd.DataFrame(all_funnel)
df_canal = pd.DataFrame(all_canal)
df_campana = pd.DataFrame(all_campana)

# ==========================================
# GRÁFICO: EMBUDO POR SEGMENTO
# ==========================================
print("\nGenerando gráficos...")

for seg in SEGMENTOS:
    row = df_funnel[df_funnel['Segmento'] == seg]
    if row.empty:
        continue
    r = row.iloc[0]

    stages = ['Consulta\n(Leads)', 'Boleta\nGenerada', 'Boleta\nPagada']
    values = [int(r['Leads (personas)']), int(r['Con Boleta']), int(r['Inscriptos (lead)'])]
    colors = ['#3498db', '#f39c12', '#2ecc71']

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(stages[::-1], values[::-1], color=colors[::-1], height=0.5)
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f'{val:,}', va='center', fontsize=12, fontweight='bold')

    # Tasas entre etapas
    ax.annotate(f'{safe_div(values[1], values[0])*100:.1f}%',
                xy=(0.3, 0.55), xycoords='axes fraction', fontsize=11, color='#e67e22',
                ha='center', fontweight='bold')
    ax.annotate(f'{safe_div(values[2], values[1])*100:.1f}%',
                xy=(0.3, 0.22), xycoords='axes fraction', fontsize=11, color='#27ae60',
                ha='center', fontweight='bold')

    ax.set_xlabel('Personas')
    ax.set_title(f'Embudo de Conversion — {seg}', fontsize=14, fontweight='bold')
    ax.set_xlim(0, max(values) * 1.15)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, f'chart_embudo_{seg}.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

# Gráfico: desglose por canal (Grado_Pregrado)
seg_main = 'Grado_Pregrado'
df_c = df_canal[df_canal['Segmento'] == seg_main]
if not df_c.empty:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    canales = df_c['Canal'].values
    x = np.arange(len(canales))
    w = 0.25

    # Panel 1: Volumen
    axes[0].bar(x - w, df_c['Leads'].values, w, label='Leads', color='#3498db')
    axes[0].bar(x, df_c['Con Boleta'].values, w, label='Con Boleta', color='#f39c12')
    axes[0].bar(x + w, df_c['Inscriptos'].values, w, label='Inscriptos', color='#2ecc71')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(canales)
    axes[0].set_title(f'Embudo por Canal — {seg_main} (Volumen)')
    axes[0].legend()
    for bar_group in [axes[0].containers[0], axes[0].containers[1], axes[0].containers[2]]:
        axes[0].bar_label(bar_group, fmt='{:,.0f}', fontsize=7, rotation=45)

    # Panel 2: Tasas
    axes[1].bar(x - w/2, df_c['Tasa L->B'].values, w, label='Lead->Boleta %', color='#f39c12')
    axes[1].bar(x + w/2, df_c['Tasa L->I'].values, w, label='Lead->Inscripto %', color='#2ecc71')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(canales)
    axes[1].set_title(f'Tasas de Conversion por Canal — {seg_main}')
    axes[1].set_ylabel('%')
    axes[1].legend()
    for bar_group in [axes[1].containers[0], axes[1].containers[1]]:
        axes[1].bar_label(bar_group, fmt='{:.1f}%', fontsize=8)

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart_embudo_canal.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

# ==========================================
# SANKEY: Canal -> Boleta -> Pago (por segmento)
# ==========================================
print("Generando Sankeys...")

for seg, canal_dict in sankey_data.items():
    canales = list(canal_dict.keys())
    # Nodes: 0..3 = canales, 4 = Sin Boleta, 5 = Boleta No Pagada, 6 = Boleta Pagada
    node_labels = canales + ['Sin Boleta', 'Boleta No Pagada*', 'Boleta Pagada']
    node_colors = ['#3498db', '#9b59b6', '#e67e22', '#95a5a6',   # canales
                   '#bdc3c7', '#e74c3c', '#2ecc71']               # destinos

    sources, targets, values, link_colors = [], [], [], []
    for i, canal in enumerate(canales):
        d = canal_dict[canal]
        # Canal -> Sin Boleta
        if d['sin_boleta'] > 0:
            sources.append(i); targets.append(4); values.append(d['sin_boleta'])
            link_colors.append('rgba(189,195,199,0.4)')
        # Canal -> Boleta No Pagada
        if d['bol_no_pago'] > 0:
            sources.append(i); targets.append(5); values.append(d['bol_no_pago'])
            link_colors.append('rgba(231,76,60,0.4)')
        # Canal -> Boleta Pagada
        if d['bol_pago'] > 0:
            sources.append(i); targets.append(6); values.append(d['bol_pago'])
            link_colors.append('rgba(46,204,113,0.4)')

    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=20, thickness=25,
            label=node_labels,
            color=node_colors,
        ),
        link=dict(
            source=sources, target=targets, value=values,
            color=link_colors,
        ),
    ))
    fig_sankey.update_layout(
        title_text=f'Sankey: Origen -> Boleta -> Pago  |  {seg}',
        font_size=12,
        width=1000, height=500,
        annotations=[dict(
            text='* "Boleta No Pagada" refleja el snapshot actual. Boletas ya pagadas desaparecen del archivo fuente.',
            xref='paper', yref='paper', x=0.5, y=-0.08,
            showarrow=False, font=dict(size=9, color='gray'),
        )],
    )
    sankey_png = os.path.join(output_dir, f'sankey_embudo_{seg}.png')
    try:
        fig_sankey.write_image(sankey_png, width=1000, height=500, scale=2)
        print(f"  -> {sankey_png}")
    except Exception as e:
        print(f"  [!] No se pudo generar PNG del Sankey ({e})")

# ==========================================
# MARKDOWN
# ==========================================
print("Generando Markdown...")
md = []
md.append('# Embudo de Conversion: Consulta -> Boleta -> Inscripción\n')
md.append(f'Fecha: {pd.Timestamp.now().strftime("%Y-%m-%d")}\n')

md.append('## Resumen por Segmento\n')
for _, r in df_funnel.iterrows():
    seg = r['Segmento']
    md.append(f'### {seg}\n')
    md.append(f'| Etapa | Personas | Tasa desde anterior |')
    md.append(f'|---|---:|---:|')
    md.append(f'| Consulta (leads con DNI) | {int(r["Leads (personas)"]):,} | - |')
    md.append(f'| Generó Boleta | {int(r["Con Boleta"]):,} | {r["Tasa Lead->Boleta"]:.1f}% |')
    md.append(f'| Pagó (inscripto) | {int(r["Inscriptos (lead)"]):,} | {r["Tasa Lead->Pago"]:.1f}% |')
    md.append('')
    md.append(f'**Boleta -> Pago (todas las boletas):** {int(r["Boletas Pagaron"]):,} / {int(r["Boletas Totales (DNI)"]):,} = {r["Tasa Boleta->Pago"]:.1f}%\n')
    md.append(f'**Boletas sin lead asociado:** {int(r["Boletas sin Lead"]):,}  |  **Inscriptos sin lead:** {int(r["Inscriptos sin Lead"]):,}\n')
    md.append(f'![Embudo {seg}](chart_embudo_{seg}.png)\n')

md.append('## Desglose por Canal\n')
md.append('| Segmento | Canal | Leads | Con Boleta | Tasa L->B | Inscriptos | Tasa L->I | Tasa B->I |')
md.append('|---|---|---:|---:|---:|---:|---:|---:|')
for _, r in df_canal.iterrows():
    md.append(f'| {r["Segmento"]} | {r["Canal"]} | {int(r["Leads"]):,} | {int(r["Con Boleta"]):,} | {r["Tasa L->B"]:.1f}% | {int(r["Inscriptos"]):,} | {r["Tasa L->I"]:.1f}% | {r["Tasa B->I"]:.1f}% |')

md.append('')
if os.path.exists(os.path.join(output_dir, 'chart_embudo_canal.png')):
    md.append('![Canal](chart_embudo_canal.png)\n')

md.append('## Desglose por Campana\n')
md.append('| Segmento | Campana | Leads | Con Boleta | Tasa L->B | Inscriptos | Tasa L->I |')
md.append('|---|---|---:|---:|---:|---:|---:|')
for _, r in df_campana.iterrows():
    md.append(f'| {r["Segmento"]} | {r["Campana"]} | {int(r["Leads"]):,} | {int(r["Con Boleta"]):,} | {r["Tasa L->B"]:.1f}% | {int(r["Inscriptos"]):,} | {r["Tasa L->I"]:.1f}% |')

md.append('\n## Sankey: Origen -> Boleta -> Pago\n')
for seg in SEGMENTOS:
    if seg in sankey_data:
        md.append(f'### {seg}\n')
        md.append(f'![Sankey {seg}](sankey_embudo_{seg}.png)\n')
        md.append('> *"Boleta No Pagada" refleja el snapshot actual del archivo. Boletas ya pagadas')
        md.append('> desaparecen del archivo fuente, por lo que la cifra real de boletas generadas es mayor.*\n')

md.append('\n## Nota Metodológica\n')
md.append('- **Modelo de atribución:** Embudo por persona (DNI). Deduplicado por DNI limpio.')
md.append('- **Persona** = DNI limpio único. Leads sin DNI no se incluyen en el embudo.')
md.append('- **Consulta**: persona que generó al menos 1 lead/consulta en Salesforce.')
md.append('- **Boleta**: persona cuyo DNI aparece en el archivo de boletas generadas.')
md.append('- **Inscripto**: persona cuyo lead matcheó exactamente con un inscripto (pagó matrícula). Match Exacto: DNI > Email > Teléfono > Celular (prioridad).')
md.append('- La tasa Lead->Boleta puede subestimarse si la persona usó datos diferentes en Salesforce vs sistema de boletas.')
md.append('- La tasa Boleta->Pago se calcula sobre TODAS las boletas del segmento (no solo las conectadas a leads).')
md.append('- **Any-Touch:** Para atribución multi-canal (inscriptos que consultaron por más de un canal), referirse al Informe Analítico (04_reporte_final).')
md.append('- **Ventana:** Grado/Pregrado desde 01/09/2025, Cursos y Posgrados desde 01/01/2026.')

md_text = '\n'.join(md)
md_path = os.path.join(output_dir, 'embudo_conversion.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_text)
print(f"  -> {md_path}")

# ==========================================
# EXCEL
# ==========================================
print("Generando Excel...")
xlsx_path = os.path.join(output_dir, 'Embudo_Conversion_Datos.xlsx')
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    df_funnel.to_excel(writer, sheet_name='Embudo_Resumen', index=False)
    df_canal.to_excel(writer, sheet_name='Embudo_Canal', index=False)
    if not df_campana.empty:
        df_campana.to_excel(writer, sheet_name='Embudo_Campana', index=False)
print(f"  -> {xlsx_path}")

# ==========================================
# PDF
# ==========================================
print("Generando PDF...")


BLUE = (41, 128, 185)
LIGHT_BLUE = (214, 234, 248)
DARK = (30, 30, 30)


class FunnelPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 6, 'UCASAL - Embudo de Conversion: Consulta -> Boleta -> Inscripcion', align='C')
        self.ln(6)
        self.set_font('Helvetica', '', 7)
        self.cell(0, 4, f'Generado: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}', align='C')
        self.ln(6)

    def footer(self):
        self.set_y(-10)
        self.set_font('Helvetica', 'I', 7)
        self.cell(0, 5, f'Pag. {self.page_no()}/{{nb}}', align='C')

    def section_title(self, txt):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 8, txt)
        self.ln(10)

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
        self.multi_cell(0, 4, txt)


pdf = FunnelPDF(orientation='L', format='A4')
pdf.set_auto_page_break(auto=True, margin=15)
pdf.alias_nb_pages()

# Pag 1: Resumen ejecutivo
pdf.add_page()
pdf.section_title('Resumen del Embudo por Segmento')

hdrs1 = ['Segmento', 'Leads', 'Con Boleta', 'L->B %', 'Boletas Tot.', 'Pagaron', 'B->P %', 'Inscr.(lead)', 'L->I %']
w1 = [35, 22, 22, 16, 22, 20, 16, 22, 16]
pdf.table_header(hdrs1, w1)

for i, (_, r) in enumerate(df_funnel.iterrows()):
    pdf.table_row([
        r['Segmento'],
        f"{int(r['Leads (personas)']):,}",
        f"{int(r['Con Boleta']):,}",
        f"{r['Tasa Lead->Boleta']:.1f}%",
        f"{int(r['Boletas Totales (DNI)']):,}",
        f"{int(r['Boletas Pagaron']):,}",
        f"{r['Tasa Boleta->Pago']:.1f}%",
        f"{int(r['Inscriptos (lead)']):,}",
        f"{r['Tasa Lead->Pago']:.1f}%",
    ], w1, fill=(i % 2 == 1))

pdf.ln(5)
pdf.nota(
    'Nota: "Leads" = personas unicas con DNI que consultaron. '
    '"Con Boleta" = leads cuyo DNI aparece en boletas generadas. '
    '"Boletas Tot." = total de DNIs unicos en archivo de boletas del segmento. '
    '"B->P" = tasa de pago sobre todas las boletas (no solo las conectadas a leads).')

# Pag 2: Desglose por canal
pdf.add_page()
pdf.section_title('Embudo por Canal')

hdrs2 = ['Segmento', 'Canal', 'Leads', 'Con Boleta', 'L->B %', 'Inscr.', 'L->I %', 'B->I %']
w2 = [35, 20, 22, 22, 16, 20, 16, 16]
pdf.table_header(hdrs2, w2)

prev_seg = ''
for i, (_, r) in enumerate(df_canal.iterrows()):
    pdf.table_row([
        r['Segmento'] if r['Segmento'] != prev_seg else '',
        r['Canal'],
        f"{int(r['Leads']):,}",
        f"{int(r['Con Boleta']):,}",
        f"{r['Tasa L->B']:.1f}%",
        f"{int(r['Inscriptos']):,}",
        f"{r['Tasa L->I']:.1f}%",
        f"{r['Tasa B->I']:.1f}%",
    ], w2, fill=(i % 2 == 1))
    prev_seg = r['Segmento']

# Pag 3: Desglose por campana
if not df_campana.empty:
    pdf.add_page()
    pdf.section_title('Embudo por Campana')

    hdrs3 = ['Segmento', 'Campana', 'Leads', 'Con Boleta', 'L->B %', 'Inscr.', 'L->I %']
    w3 = [35, 28, 22, 22, 16, 20, 16]
    pdf.table_header(hdrs3, w3)

    prev_seg = ''
    for i, (_, r) in enumerate(df_campana.iterrows()):
        pdf.table_row([
            r['Segmento'] if r['Segmento'] != prev_seg else '',
            r['Campana'],
            f"{int(r['Leads']):,}",
            f"{int(r['Con Boleta']):,}",
            f"{r['Tasa L->B']:.1f}%",
            f"{int(r['Inscriptos']):,}",
            f"{r['Tasa L->I']:.1f}%",
        ], w3, fill=(i % 2 == 1))
        prev_seg = r['Segmento']

# Pag 4+: Graficos
for seg in SEGMENTOS:
    chart_path = os.path.join(output_dir, f'chart_embudo_{seg}.png')
    if os.path.exists(chart_path):
        pdf.add_page()
        pdf.section_title(f'Embudo -- {seg}')
        pdf.image(chart_path, x=20, y=30, w=250)

chart_canal = os.path.join(output_dir, 'chart_embudo_canal.png')
if os.path.exists(chart_canal):
    pdf.add_page()
    pdf.section_title('Embudo por Canal -- Grado_Pregrado')
    pdf.image(chart_canal, x=10, y=30, w=270)

# Sankey pages
for seg in SEGMENTOS:
    sankey_img = os.path.join(output_dir, f'sankey_embudo_{seg}.png')
    if os.path.exists(sankey_img):
        pdf.add_page()
        pdf.section_title(f'Sankey: Origen -> Boleta -> Pago  |  {seg}')
        pdf.image(sankey_img, x=10, y=30, w=270)
        pdf.set_y(-25)
        pdf.nota(
            '* "Boleta No Pagada" refleja el snapshot actual del archivo de boletas. '
            'Cuando una boleta se paga, desaparece del listado. '
            'La cifra real de boletas generadas es mayor que las visibles en el archivo.')

# Nota Metodológica
pdf.add_page()
pdf.section_title('Nota Metodologica')
pdf.set_font('Helvetica', '', 9)
pdf.multi_cell(0, 5,
    'Modelo de atribucion: Embudo por persona (DNI limpio unico). '
    'Leads sin DNI no se incluyen en el embudo.\n\n'
    'Etapas: Consulta (lead en Salesforce) -> Boleta Generada (DNI en archivo de boletas) -> '
    'Pago (inscripto con Match Exacto: DNI > Email > Telefono > Celular).\n\n'
    'Canal: Clasificado por UTM/FuenteLead del lead mas reciente de la persona.\n\n'
    'La tasa Boleta->Pago se calcula sobre TODAS las boletas del segmento, '
    'no solo las conectadas a leads.\n\n'
    'Any-Touch: Para atribucion multi-canal (inscriptos que consultaron por mas de un canal), '
    'referirse al Informe Analitico (04_reporte_final).\n\n'
    'Ventana: Grado/Pregrado desde 01/09/2025 (campana ingreso 2026). '
    'Cursos y Posgrados desde 01/01/2026.')

pdf_path = os.path.join(output_dir, 'Embudo_Conversion.pdf')
pdf.output(pdf_path)
print(f"  -> {pdf_path}")

# ==========================================
# MEMORIA TÉCNICA
# ==========================================
mem = []
mem.append('# Memoria Técnica — 23_embudo_conversion.py\n')
mem.append(f'Generado: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}\n')
mem.append('## Fuentes')
mem.append(f'- Boletas raw: {len(df_boletas_all)} únicas')
for seg in SEGMENTOS:
    r = df_funnel[df_funnel['Segmento'] == seg]
    if r.empty:
        continue
    r = r.iloc[0]
    mem.append(f'\n## {seg}')
    mem.append(f'- Leads con DNI: {int(r["Leads (personas)"]):,}')
    mem.append(f'- Con boleta: {int(r["Con Boleta"]):,} ({r["Tasa Lead->Boleta"]:.1f}%)')
    mem.append(f'- Inscriptos (desde lead): {int(r["Inscriptos (lead)"]):,} ({r["Tasa Lead->Pago"]:.1f}%)')
    mem.append(f'- Boletas totales: {int(r["Boletas Totales (DNI)"]):,}')
    mem.append(f'- Boletas pagaron: {int(r["Boletas Pagaron"]):,} ({r["Tasa Boleta->Pago"]:.1f}%)')
    mem.append(f'- Boletas sin lead: {int(r["Boletas sin Lead"]):,}')
    mem.append(f'- Inscriptos sin lead: {int(r["Inscriptos sin Lead"]):,}')

mem_path = os.path.join(output_dir, 'memoria_tecnica.md')
with open(mem_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(mem))

print(f"\n{'='*50}")
print("Embudo de conversión generado exitosamente.")
print(f"Outputs en: {output_dir}")
