"""
06_sankeys_extras.py
Genera 5 diagramas Sankey adicionales + gráficos UTM complementarios en PDF.
Script GLOBAL (sin argumento de segmento), lee datos consolidados.

Sankey A: Inscriptos Exactos (Origen → Modalidad)
Sankey B: Consultas → Resultado (inscripto/no inscripto)
Sankey C: Bot cross-origin (interacción Bot con otros canales)
Sankey D: Flujo oportunidades (Origen → Modalidad → Inscripto)
Sankey E: Flujo Bot específico

SALIDA (outputs/Informe_Analitico/):
  - sankey_A..E_*.pdf  -> Diagramas Sankey individuales
  - diagrama_sankey_agrupado.pdf  -> PDF consolidado
"""
import pandas as pd
import os
import re
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "Informe_Analitico")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")
data_dir = os.path.join(base_dir, "data", "1_raw")

leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")
mapping_xlsx = os.path.join(data_dir, "origenes_leads", "mapping_origenes.xlsx")

# ==========================================
# 1. CARGA DE DATOS
# ==========================================
print("Cargando datos...")
df = pd.read_csv(leads_csv, low_memory=False)

# Mapping de orígenes
try:
    df_map = pd.read_excel(mapping_xlsx)
    df_map_u = df_map.dropna(subset=['id_origen | Fuente lead', 'nombre']).copy()
    df_map_u['id_str'] = df_map_u['id_origen | Fuente lead'].astype(str).str.replace(r'\.0$', '', regex=True)
    dict_orig = dict(zip(df_map_u['id_str'], df_map_u['nombre']))
except:
    dict_orig = {}

df['FuenteLead_clean'] = df['FuenteLead'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

def get_origen(fid):
    if pd.isna(fid) or fid == 'nan' or not fid:
        return 'Sin Origen'
    if fid == '18': return 'Facebook Lead Ads'
    if fid == '907': return 'Chatbot (Bot)'
    n = dict_orig.get(fid)
    if n: return f"LP: {n[:35]}"
    return f"Landing ({fid})"

df['Formulario_Origen'] = df['FuenteLead_clean'].apply(get_origen)

def norm_modo(v):
    s = str(v).strip().lower()
    if s in ['1','1.0'] or ('presencial' in s and 'semi' not in s): return 'Presencial'
    if s in ['2','2.0'] or 'semi' in s: return 'Semipresencial'
    if s in ['7','7.0'] or 'distancia' in s: return 'A Distancia'
    return 'Otro'

df['Modo_Limpio'] = df['Modo'].apply(norm_modo)

# Clasificar match
def classify(v):
    s = str(v)
    if 'Exacto' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

df['_mc'] = df['Match_Tipo'].apply(classify)

# Solo exactos + no-match para análisis principal
df_main = df[df['_mc'] != 'fuzzy'].copy()

# ==========================================
# 2. TASA DE CONVERSIÓN DEDUPLICADA
# ==========================================
print("Calculando tasa de conversión deduplicada (por persona única)...")

# Crear una clave de persona: usar DNI preferentemente, si no Email, si no Candidato
df_main['_persona_key'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_persona_key'].isin(['nan', '', 'None']), '_persona_key'] = \
    df_main.loc[df_main['_persona_key'].isin(['nan', '', 'None']), 'Correo'].astype(str)

# Personas únicas
personas = df_main.drop_duplicates(subset='_persona_key')
total_personas_unicas = len(personas)
personas_convertidas = len(personas[personas['_mc'] == 'exacto'])
tasa_conversion_dedup = (personas_convertidas / total_personas_unicas * 100) if total_personas_unicas > 0 else 0

print(f"-> Personas únicas: {total_personas_unicas:,}")
print(f"-> Personas convertidas (exacto): {personas_convertidas:,}")
print(f"-> Tasa de conversión deduplicada: {tasa_conversion_dedup:.2f}%")

# ==========================================
# 3. SANKEY A: Solo inscriptos exactos (Origen -> Modalidad)
# ==========================================
print("Generando Sankey A: Inscriptos Exactos (Origen -> Modalidad)...")
df_insc_exact = df_main[df_main['_mc'] == 'exacto'].copy()

# Agrupar orígenes menores
orig_counts = df_insc_exact['Formulario_Origen'].value_counts()
top_orig = orig_counts[orig_counts >= 10].index.tolist()
df_insc_exact['Orig_Agrup'] = df_insc_exact['Formulario_Origen'].apply(lambda x: x if x in top_orig else 'Otros Formularios')

nodes_a = list(df_insc_exact['Orig_Agrup'].unique()) + list(df_insc_exact['Modo_Limpio'].unique())
nd_a = {n: i for i, n in enumerate(nodes_a)}
lnk_a = df_insc_exact.groupby(['Orig_Agrup', 'Modo_Limpio']).size().reset_index(name='v')

fig_a = go.Figure(data=[go.Sankey(
    node=dict(pad=20, thickness=25, label=nodes_a,
              color=['rgba(44,160,44,0.8)'] * len(df_insc_exact['Orig_Agrup'].unique()) +
                    ['rgba(255,127,14,0.8)'] * len(df_insc_exact['Modo_Limpio'].unique())),
    link=dict(
        source=[nd_a[x] for x in lnk_a['Orig_Agrup']],
        target=[nd_a[x] for x in lnk_a['Modo_Limpio']],
        value=lnk_a['v'].tolist()
    )
)])
fig_a.update_layout(title_text="Inscriptos Confirmados: Formulario Origen -> Modalidad", font_size=11, width=1200, height=600)
fig_a.write_image(os.path.join(output_dir, "sankey_A_inscriptos_origen_modo.png"))
fig_a.write_image(os.path.join(output_dir, "sankey_A_inscriptos_origen_modo.pdf"))
print("-> Sankey A guardado.")

# ==========================================
# 4. SANKEY B: Cantidad de consultas -> Inscripción
# ==========================================
print("Generando Sankey B: Cantidad de consultas hasta inscripción...")

# Contar consultas por persona (agrupando por _persona_key)
consultas_per_persona = df_main.groupby('_persona_key').agg(
    n_consultas=('_persona_key', 'size'),
    se_inscribio=('_mc', lambda x: 'exacto' in x.values)
).reset_index()

# Categorizar cantidad de consultas
def cat_consultas(n):
    if n == 1: return '1 Consulta'
    if n == 2: return '2 Consultas'
    if n <= 5: return '3-5 Consultas'
    if n <= 10: return '6-10 Consultas'
    return '11+ Consultas'

consultas_per_persona['Cat_Consultas'] = consultas_per_persona['n_consultas'].apply(cat_consultas)
consultas_per_persona['Resultado'] = consultas_per_persona['se_inscribio'].apply(
    lambda x: '✅ Inscripto' if x else '❌ No Inscripto'
)

nodes_b = ['1 Consulta', '2 Consultas', '3-5 Consultas', '6-10 Consultas', '11+ Consultas',
           '✅ Inscripto', '❌ No Inscripto']
nd_b = {n: i for i, n in enumerate(nodes_b)}
lnk_b = consultas_per_persona.groupby(['Cat_Consultas', 'Resultado']).size().reset_index(name='v')

fig_b = go.Figure(data=[go.Sankey(
    node=dict(pad=20, thickness=25, label=nodes_b,
              color=['rgba(31,119,180,0.8)'] * 5 + ['rgba(44,160,44,0.8)', 'rgba(214,39,40,0.6)']),
    link=dict(
        source=[nd_b[x] for x in lnk_b['Cat_Consultas']],
        target=[nd_b[x] for x in lnk_b['Resultado']],
        value=lnk_b['v'].tolist()
    )
)])
fig_b.update_layout(title_text="Cantidad de Consultas -> Resultado de Inscripción (por persona única)", font_size=11, width=1000, height=500)
fig_b.write_image(os.path.join(output_dir, "sankey_B_consultas_inscripcion.png"))
fig_b.write_image(os.path.join(output_dir, "sankey_B_consultas_inscripcion.pdf"))
print("-> Sankey B guardado.")

# ==========================================
# 5. SANKEY C: Bot — ¿Qué otros orígenes consultaron las personas del Bot?
# ==========================================
print("Generando Sankey C: Bot — Otros orígenes consultados...")

# Personas que pasaron por el Bot
bot_personas = df_main[df_main['FuenteLead_clean'] == '907']['_persona_key'].unique()
df_bot_all = df_main[df_main['_persona_key'].isin(bot_personas)].copy()

# Todos los orígenes que tocaron esas personas
df_bot_origins = df_bot_all[['_persona_key', 'Formulario_Origen', '_mc']].copy()

# Nivel 1: Bot -> Otros Orígenes que también consultaron
otros = df_bot_origins[df_bot_origins['Formulario_Origen'] != 'Chatbot (Bot)'].copy()
otros_counts = otros['Formulario_Origen'].value_counts()
top_otros = otros_counts[otros_counts >= 5].index.tolist()
otros['Orig_Agrup'] = otros['Formulario_Origen'].apply(lambda x: x if x in top_otros else 'Otros')

# Resultado final de esas personas
resultado_bot = df_bot_all.groupby('_persona_key')['_mc'].apply(
    lambda x: '✅ Inscripto' if 'exacto' in x.values else '❌ No Inscripto'
).reset_index(name='Resultado')

# Merge
otros_merge = otros.merge(resultado_bot, on='_persona_key')

nodes_c = ['Chatbot (Bot)'] + list(otros_merge['Orig_Agrup'].unique()) + ['✅ Inscripto', '❌ No Inscripto']
nd_c = {n: i for i, n in enumerate(nodes_c)}

# Links nivel 1: Bot -> Otros Orígenes
l1 = otros_merge.groupby('Orig_Agrup').size().reset_index(name='v')
# Links nivel 2: Otros Orígenes -> Resultado
l2 = otros_merge.groupby(['Orig_Agrup', 'Resultado']).size().reset_index(name='v')

src_c = [nd_c['Chatbot (Bot)']] * len(l1) + [nd_c[x] for x in l2['Orig_Agrup']]
tgt_c = [nd_c[x] for x in l1['Orig_Agrup']] + [nd_c[x] for x in l2['Resultado']]
val_c = l1['v'].tolist() + l2['v'].tolist()

n_otros = len(otros_merge['Orig_Agrup'].unique())
colors_c = ['rgba(148,103,189,0.8)'] + ['rgba(31,119,180,0.7)'] * n_otros + ['rgba(44,160,44,0.8)', 'rgba(214,39,40,0.6)']

fig_c = go.Figure(data=[go.Sankey(
    node=dict(pad=20, thickness=25, label=nodes_c, color=colors_c),
    link=dict(source=src_c, target=tgt_c, value=val_c)
)])
fig_c.update_layout(title_text="Personas del Bot: ¿Qué otros formularios consultaron?", font_size=11, width=1200, height=600)
fig_c.write_image(os.path.join(output_dir, "sankey_C_bot_cross_origin.png"))
fig_c.write_image(os.path.join(output_dir, "sankey_C_bot_cross_origin.pdf"))
print("-> Sankey C guardado.")

# ==========================================
# 5.1 SANKEY D: Flujo de Oportunidades (Origen -> Modalidad -> Inscripto Confirmado)
# ==========================================
print("Generando Sankey D: Flujo de Oportunidades (Inscriptos Exactos)...")
# Usamos df_insc_exact que ya tiene Orig_Agrup
df_sd = df_insc_exact.copy()
df_sd['Resultado_Final'] = '✅ Inscripto Confirmado'

nodes_d = list(df_sd['Orig_Agrup'].unique()) + list(df_sd['Modo_Limpio'].unique()) + ['✅ Inscripto Confirmado']
nd_d = {n: i for i, n in enumerate(nodes_d)}

l1_d = df_sd.groupby(['Orig_Agrup', 'Modo_Limpio']).size().reset_index(name='v')
l2_d = df_sd.groupby(['Modo_Limpio', 'Resultado_Final']).size().reset_index(name='v')

src_d = [nd_d[x] for x in l1_d['Orig_Agrup']] + [nd_d[x] for x in l2_d['Modo_Limpio']]
tgt_d = [nd_d[x] for x in l1_d['Modo_Limpio']] + [nd_d[x] for x in l2_d['Resultado_Final']]
val_d = l1_d['v'].tolist() + l2_d['v'].tolist()

fig_d = go.Figure(data=[go.Sankey(
    node=dict(pad=20, thickness=25, label=nodes_d, color=['rgba(44,160,44,0.8)'] * len(nodes_d)),
    link=dict(source=src_d, target=tgt_d, value=val_d)
)])
fig_d.update_layout(title_text="Flujo de Oportunidades: Origen -> Modalidad -> Inscripto", font_size=11, width=1200, height=600)
fig_d.write_image(os.path.join(output_dir, "sankey_D_flujo_oportunidades.png"))
fig_d.write_image(os.path.join(output_dir, "sankey_D_flujo_oportunidades.pdf"))
print("-> Sankey D guardado.")

# ==========================================
# 5.2 SANKEY E: Flujo del Bot (Bot -> Modalidad -> Inscripto Confirmado)
# ==========================================
print("Generando Sankey E: Flujo exclusivo del Bot...")
df_se = df_insc_exact[df_insc_exact['Formulario_Origen'] == 'Chatbot (Bot)'].copy()
df_se['Resultado_Final'] = '✅ Inscripto Confirmado'

if len(df_se) > 0:
    nodes_e = ['Chatbot (Bot)'] + list(df_se['Modo_Limpio'].unique()) + ['✅ Inscripto Confirmado']
    nd_e = {n: i for i, n in enumerate(nodes_e)}

    l1_e = df_se.groupby(['Formulario_Origen', 'Modo_Limpio']).size().reset_index(name='v')
    l2_e = df_se.groupby(['Modo_Limpio', 'Resultado_Final']).size().reset_index(name='v')

    src_e = [nd_e[x] for x in l1_e['Formulario_Origen']] + [nd_e[x] for x in l2_e['Modo_Limpio']]
    tgt_e = [nd_e[x] for x in l1_e['Modo_Limpio']] + [nd_e[x] for x in l2_e['Resultado_Final']]
    val_e = l1_e['v'].tolist() + l2_e['v'].tolist()

    fig_e = go.Figure(data=[go.Sankey(
        node=dict(pad=20, thickness=25, label=nodes_e, color=['rgba(148,103,189,0.8)'] * len(nodes_e)),
        link=dict(source=src_e, target=tgt_e, value=val_e)
    )])
    fig_e.update_layout(title_text="Flujo Bot: Chatbot -> Modalidad -> Inscripto", font_size=11, width=1000, height=500)
    fig_e.write_image(os.path.join(output_dir, "sankey_E_flujo_bot.png"))
    fig_e.write_image(os.path.join(output_dir, "sankey_E_flujo_bot.pdf"))
    print("-> Sankey E guardado.")
else:
    print("-> Sankey E no generado: No hay inscriptos exactos desde el Bot.")

# ==========================================
# 6. REPORTE UTM
# ==========================================
print("Generando reporte UTM...")

# Limpiar UTMs
for col in ['UtmSource', 'UtmCampaign', 'UtmMedium', 'UtmTerm', 'UtmContent']:
    if col in df_main.columns:
        df_main[col] = df_main[col].astype(str).replace('nan', '').str.strip()

df_utm = df_main[(df_main['UtmSource'] != '') | (df_main['UtmCampaign'] != '') | (df_main['UtmMedium'] != '')].copy()
total_con_utm = len(df_utm)
total_sin_utm = len(df_main) - total_con_utm

print(f"-> Leads con UTM: {total_con_utm:,} | Sin UTM: {total_sin_utm:,}")

# Top UTM Source
plt.figure(figsize=(12, 6))
top_src = df_utm['UtmSource'].value_counts().head(10)
if len(top_src) > 0:
    sns.barplot(y=top_src.index, x=top_src.values, hue=top_src.index, palette='Blues_r', legend=False)
    plt.title('Top 10 UTM Source')
    plt.xlabel('Cantidad de Leads')
    for i, v in enumerate(top_src.values):
        plt.text(v + 10, i, f'{v:,}', va='center')
plt.savefig(os.path.join(output_dir, "chart_utm_source.png"), bbox_inches='tight')
plt.close()

# Top UTM Campaign
plt.figure(figsize=(14, 7))
top_camp = df_utm['UtmCampaign'].value_counts().head(15)
if len(top_camp) > 0:
    sns.barplot(y=top_camp.index, x=top_camp.values, hue=top_camp.index, palette='Oranges_r', legend=False)
    plt.title('Top 15 UTM Campaign')
    plt.xlabel('Cantidad de Leads')
    for i, v in enumerate(top_camp.values):
        plt.text(v + 10, i, f'{v:,}', va='center')
plt.savefig(os.path.join(output_dir, "chart_utm_campaign.png"), bbox_inches='tight')
plt.close()

# Top UTM Medium
plt.figure(figsize=(10, 5))
top_med = df_utm['UtmMedium'].value_counts().head(10)
if len(top_med) > 0:
    sns.barplot(y=top_med.index, x=top_med.values, hue=top_med.index, palette='Greens_r', legend=False)
    plt.title('Top 10 UTM Medium')
    plt.xlabel('Cantidad de Leads')
plt.savefig(os.path.join(output_dir, "chart_utm_medium.png"), bbox_inches='tight')
plt.close()

# Conversión por UTM Source (deduplicado)
df_utm_personas = df_utm.drop_duplicates(subset='_persona_key')
conv_utm = df_utm_personas.groupby('UtmSource').agg(
    total=('_mc', 'size'),
    conv=('_mc', lambda x: (x == 'exacto').sum())
).reset_index()
conv_utm['tasa'] = conv_utm['conv'] / conv_utm['total'] * 100
conv_utm = conv_utm[conv_utm['total'] >= 20].sort_values('tasa', ascending=False).head(10)

plt.figure(figsize=(12, 6))
if len(conv_utm) > 0:
    sns.barplot(y='UtmSource', x='tasa', data=conv_utm, hue='UtmSource', palette='YlGn', legend=False)
    plt.title('Tasa de Conversión por UTM Source (mín. 20 personas, deduplicado)')
    plt.xlabel('% Conversión')
plt.savefig(os.path.join(output_dir, "chart_utm_conversion.png"), bbox_inches='tight')
plt.close()

# Informe UTM en Markdown
utm_md = f"""# Reporte de UTMs

## Cobertura
| Métrica | Valor |
|---------|-------|
| Leads con UTM | {total_con_utm:,} ({total_con_utm/len(df_main)*100:.1f}%) |
| Leads sin UTM | {total_sin_utm:,} ({total_sin_utm/len(df_main)*100:.1f}%) |

## Top 10 UTM Source
![UTM Source](chart_utm_source.png)

## Top 15 UTM Campaign
![UTM Campaign](chart_utm_campaign.png)

## Top 10 UTM Medium
![UTM Medium](chart_utm_medium.png)

## Tasa de Conversión por UTM Source (deduplicado por persona)
![UTM Conversión](chart_utm_conversion.png)
"""
with open(os.path.join(output_dir, "informe_utm.md"), "w", encoding="utf-8") as f:
    f.write(utm_md)

# ==========================================
# 7. ACTUALIZAR INFORME PRINCIPAL CON TASA DEDUPLICADA Y NUEVOS GRÁFICOS
# ==========================================
print("Actualizando informe principal con tasa deduplicada y nuevos Sankeys...")

# Leer informe existente y agregar las nuevas secciones
extra_md = f"""

---

## Tasa de Conversión Deduplicada (por persona única)

Para evitar contar el mismo Lead más de una vez (una persona puede generar múltiples consultas), se deduplicó por DNI/Email:

| Métrica | Valor |
|---------|-------|
| Personas únicas | {total_personas_unicas:,} |
| Personas convertidas (exacto) | {personas_convertidas:,} |
| **Tasa de conversión real** | **{tasa_conversion_dedup:.2f}%** |

## Sankey: Inscriptos Exactos (Origen -> Modalidad)
![Sankey Inscriptos](sankey_A_inscriptos_origen_modo.png)

## Sankey: Consultas hasta Inscripción
![Sankey Consultas](sankey_B_consultas_inscripcion.png)

## Sankey: Personas del Bot — Otros orígenes consultados
![Sankey Bot Cross](sankey_C_bot_cross_origin.png)

## Análisis UTM
Ver reporte completo en `informe_utm.md`.

### UTM Source (Top 10)
![UTM Source](chart_utm_source.png)

### UTM Campaign (Top 15)
![UTM Campaign](chart_utm_campaign.png)

### Conversión por UTM Source
![UTM Conversión](chart_utm_conversion.png)
"""

report_md_file = os.path.join(output_dir, "Informe_Analitico_Marketing.md")
with open(report_md_file, "a", encoding="utf-8") as f:
    f.write(extra_md)

print(f"-> Informe Markdown actualizado: {report_md_file}")

# ==========================================
# 8. ACTUALIZAR PDF
# ==========================================
print("Regenerando PDF completo...")
try:
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 10)
            self.cell(0, 8, 'Informe Analítico de Marketing', new_x="LMARGIN", new_y="NEXT", align='C')
        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Pág. {self.page_no()}', new_x="LMARGIN", new_y="NEXT", align='C')

    pdf = PDF('L')
    pdf.set_auto_page_break(auto=True, margin=25)

    # Portada
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.ln(40)
    pdf.cell(0, 15, 'Informe Analítico de Marketing', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, 'y Trazabilidad de Leads', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 8, '(Solo cruces exactos - Fuzzy en informe complementario)', new_x="LMARGIN", new_y="NEXT", align='C')

    # Resumen ejecutivo
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 12, 'Resumen Ejecutivo', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Tabla
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(130, 8, 'Metrica', border=1)
    pdf.cell(50, 8, 'Valor', border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 9)

    leads_exactos = len(df_main[df_main['_mc'] == 'exacto'])
    leads_solo = len(df_main[df_main['_mc'] == 'no_match'])

    # Bot stats
    df_bot_main = df_main[df_main['FuenteLead_clean'] == '907']
    bot_leads = len(df_bot_main)
    bot_insc = len(df_bot_main[df_bot_main['_mc'] == 'exacto'])
    bot_tasa = (bot_insc / bot_leads * 100) if bot_leads > 0 else 0

    rows = [
        ('Total Leads (registros)', f'{len(df_main):,}'),
        ('Personas Unicas (deduplicado)', f'{total_personas_unicas:,}'),
        ('Convertidos (exacto)', f'{leads_exactos:,}'),
        ('Personas Convertidas (dedup)', f'{personas_convertidas:,}'),
        ('Tasa Conversion (dedup)', f'{tasa_conversion_dedup:.2f}%'),
        ('', ''),
        ('Bot (907) - Leads', f'{bot_leads:,}'),
        ('Bot (907) - Inscriptos', f'{bot_insc:,}'),
        ('Bot (907) - Conversion', f'{bot_tasa:.2f}%'),
        ('', ''),
        ('Leads con UTM', f'{total_con_utm:,}'),
        ('Leads sin UTM', f'{total_sin_utm:,}'),
    ]
    for label, val in rows:
        pdf.cell(130, 7, label, border=1)
        pdf.cell(50, 7, val, border=1, new_x="LMARGIN", new_y="NEXT")

    # Gráficos
    charts = [
        ('chart_4_top10_origenes.png', 'Top 10 Formularios de Origen'),
        ('chart_5_distribucion_modalidad.png', 'Distribucion por Modalidad'),
        ('chart_6_conversion_modalidad.png', 'Conversion por Modalidad'),
        ('chart_7_conversion_origenes.png', 'Conversion por Origen'),
        ('sankey_A_inscriptos_origen_modo.png', 'Sankey: Inscriptos Exactos (Origen -> Modalidad)'),
        ('sankey_B_consultas_inscripcion.png', 'Sankey: Consultas hasta Inscripcion'),
        ('sankey_C_bot_cross_origin.png', 'Sankey: Bot - Otros Origenes Consultados'),
        ('sankey_D_flujo_oportunidades.png', 'Sankey: Flujo Oportunidades (Modalidades y Confirmados)'),
        ('sankey_E_flujo_bot.png', 'Sankey: Modalidades Inscriptos desde Bot'),
        ('diagrama_sankey_agrupado.png', 'Sankey General: Origen -> Modalidad -> Resultado'),
        ('chart_utm_source.png', 'UTM Source (Top 10)'),
        ('chart_utm_campaign.png', 'UTM Campaign (Top 15)'),
        ('chart_utm_medium.png', 'UTM Medium'),
        ('chart_utm_conversion.png', 'Conversion por UTM Source'),
    ]

    for fname, title in charts:
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(3)
            pdf.image(fpath, x='C', w=260, h=160, keep_aspect_ratio=True)

    # Conclusiones
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Conclusiones y Recomendaciones', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    concl = [
        f'1. Tasa de conversion real (deduplicada): {tasa_conversion_dedup:.2f}%.',
        f'2. El Bot (907) tiene una conversion de {bot_tasa:.2f}%, {"superior" if bot_tasa > tasa_conversion_dedup else "inferior"} al promedio.',
        f'3. {total_con_utm:,} leads ({total_con_utm/len(df_main)*100:.1f}%) tienen UTMs, lo que permite rastrear las campanas digitales.',
        f'4. {len(df[df["_mc"]=="fuzzy"]):,} registros fuzzy estan pendientes de verificacion humana.',
    ]
    for c in concl:
        pdf.multi_cell(0, 6, c)
        pdf.ln(2)

    pdf_path = os.path.join(output_dir, "Informe_Analitico_Marketing.pdf")
    pdf.output(pdf_path)
    print(f"-> PDF actualizado: {pdf_path}")
except Exception as e:
    print(f"Error generando PDF: {e}")

print("\n¡Todo listo!")
