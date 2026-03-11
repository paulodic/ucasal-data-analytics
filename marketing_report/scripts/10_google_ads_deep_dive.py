"""
10_google_ads_deep_dive.py
Análisis profundo de Google Ads por segmento.

Filtra leads cuyo UTM Source contiene 'google', desglosa por Campaign y Medium,
calcula tasas de conversión, y genera PDF + Excel.

ENTRADA:
  - outputs/Data_Base/<Segmento>/reporte_marketing_leads_completos.csv
  - outputs/Data_Base/<Segmento>/reporte_marketing_inscriptos_origenes.csv
SALIDA (outputs/<Segmento>/Google_Ads_Deep_Dive/):
  - reporte_especifico_googleads.xlsx
  - Informe_Google_Ads_Deep_Dive.pdf
"""
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

sns.set_theme(style="whitegrid")

# ==========================================
# CONFIGURACIÓN
# ==========================================
import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Google_Ads_Deep_Dive")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Cargando datos para Deep Dive Google Ads...")
df = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

def get_max_date(df_i):
    meses = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio",
             7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}
    for col in ['Insc_Fecha Pago', 'Fecha Pago']:
        if col in df_i.columns:
            dates = pd.to_datetime(df_i[col], format='mixed', errors='coerce')
            dates = dates[dates <= pd.Timestamp.now()]
            if not dates.isna().all():
                d = dates.max()
                return (d, f"{d.day} de {meses[d.month]} de {d.year}")
    d = pd.Timestamp.now()
    return (d, f"{d.day} de {meses[d.month]} de {d.year}")

max_insc_ts, max_date_str = get_max_date(df_insc)

def classify(v):
    s = str(v)
    if 'Exacto' in s: return 'exacto'
    if 'Posible Match Fuzzy' in s: return 'fuzzy'
    return 'no_match'

df['_mc'] = df['Match_Tipo'].apply(classify)
df_main = df[df['_mc'] != 'fuzzy'].copy()

# Limpiar UTMs
utm_cols = ['UtmSource', 'UtmCampaign', 'UtmMedium', 'UtmTerm', 'UtmContent']
for col in utm_cols:
    if col in df_main.columns:
        df_main[col] = df_main[col].astype(str).replace('nan', '').str.strip().str.lower()

# Deduplicar por persona
df_main['_pk'] = df_main['DNI'].astype(str).str.replace(r'\.0$', '', regex=True)
df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), '_pk'] = \
    df_main.loc[df_main['_pk'].isin(['nan', '', 'None']), 'Correo'].astype(str)

# FILTRO ESPECÍFICO: Google Ads (Volumen Histórico)
# Buscamos 'googleads' o similar en UtmSource
df_gads = df_main[df_main['UtmSource'].str.contains('google', na=False)].copy()
df_gads_dedup = df_gads.drop_duplicates(subset='_pk')

total_gads = len(df_gads_dedup)

# REGLA DE NEGOCIO COHORTES (Muestra para Conversión)
# Inicio cohorte 2026 = 1-sep-2025. Upper bound = última fecha de inscripción registrada.
df_main['Fecha_Limpia'] = pd.to_datetime(
    df_main['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
if segmento == 'Grado_Pregrado':
    df_main_conv = df_main[
        (df_main['Fecha_Limpia'] >= '2025-09-01') &
        (df_main['Fecha_Limpia'] <= max_insc_ts)
    ].copy()
else:
    df_main_conv = df_main[df_main['Fecha_Limpia'] <= max_insc_ts].copy()

df_gads_conv = df_main_conv[df_main_conv['UtmSource'].str.contains('google', na=False)].copy()
df_gads_dedup_conv = df_gads_conv.drop_duplicates(subset='_pk')

total_gads_conv = len(df_gads_dedup_conv)
conv_gads = len(df_gads_dedup_conv[df_gads_dedup_conv['_mc'] == 'exacto'])
tasa_gads = (conv_gads / total_gads_conv * 100) if total_gads_conv > 0 else 0

print(f"Personas de Google Ads (Muestra): {total_gads_conv:,} | Inscriptos: {conv_gads:,} | Tasa: {tasa_gads:.2f}%")

# ==========================================
# FUNCIÓN DE ANÁLISIS VERTICAL
# ==========================================
def analizar_gads(df_data, df_dedup, df_dedup_conv, campo, top_n=15, min_personas=10):
    df_f = df_dedup[df_dedup[campo] != ''].copy()
    if len(df_f) == 0: return None, None
    
    # 1. Tabla de Volumen Histórico
    tabla_vol = df_f.groupby(campo).agg(
        Personas=('_pk', 'nunique'),
    ).reset_index()

    # 2. Tabla de Conversión en la Muestra
    df_f_conv = df_dedup_conv[df_dedup_conv[campo] != ''].copy()
    tabla_conv = df_f_conv.groupby(campo).agg(
        Personas_Muestra=('_pk', 'nunique'),
        Inscriptos=('_mc', lambda x: (x == 'exacto').sum()),
    ).reset_index()

    # Consolidar (Outer Join para incluir todo)
    tabla = pd.merge(tabla_vol, tabla_conv, on=campo, how='outer').fillna(0)
    tabla['Tasa_%'] = (tabla['Inscriptos'] / tabla['Personas_Muestra'] * 100).round(2)
    # Llenar nulos si hay 0 personas muestra
    tabla.loc[tabla['Personas_Muestra'] == 0, 'Tasa_%'] = 0.0
    
    tabla = tabla.sort_values('Personas', ascending=False)
    
    # Grafico 1: Volumen
    top = tabla.head(top_n).copy()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, y=campo, x='Personas', palette='Blues_r', hue=campo, legend=False)
    plt.title(f'Google Ads: Top {top_n} {campo} (Volumen)')
    for i, v in enumerate(top['Personas']):
        plt.text(v + 5, i, f'{int(v):,}', va='center')
    plt.tight_layout()
    path_vol = os.path.join(output_dir, f"gads_vol_{campo.lower()}.png")
    plt.savefig(path_vol, bbox_inches='tight')
    plt.close()

    # Grafico 2: Conversion (Basado en la Muestra para Conversion)
    top_c = tabla[tabla['Personas_Muestra'] >= min_personas].sort_values('Tasa_%', ascending=False).head(top_n)
    path_rate = None
    if len(top_c) > 0:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top_c, y=campo, x='Tasa_%', palette='Greens_r', hue=campo, legend=False)
        plt.axvline(x=tasa_gads, color='red', linestyle='--', alpha=0.6, label=f'Promedio GAds: {tasa_gads:.1f}%')
        plt.title(f'Google Ads: Top {top_n} {campo} (Tasa de Conversion)')
        plt.legend()
        for i, v in enumerate(top_c['Tasa_%']):
            plt.text(v + 0.2, i, f'{v:.1f}%', va='center')
        plt.tight_layout()
        path_rate = os.path.join(output_dir, f"gads_rate_{campo.lower()}.png")
        plt.savefig(path_rate, bbox_inches='tight')
        plt.close()
    
    return tabla, {'vol': path_vol, 'rate': path_rate}

# ==========================================
# GENERAR REPORTES
# ==========================================
gads_results = {}
for c in ['UtmCampaign', 'UtmMedium', 'UtmTerm']:
    print(f"Analizando {c} para Google Ads...")
    tbl, imgs = analizar_gads(df_gads, df_gads_dedup, df_gads_dedup_conv, c)
    if tbl is not None:
        gads_results[c] = {'tabla': tbl, 'charts': imgs}

# Excel
with pd.ExcelWriter(os.path.join(output_dir, "reporte_especifico_googleads.xlsx")) as writer:
    for c, res in gads_results.items():
        res['tabla'].to_excel(writer, sheet_name=c[:30], index=False)

# Markdown Text
md_path = os.path.join(output_dir, "Informe_Google_Ads_Deep_Dive.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"# Informe de Performance - Google Ads\n\n*(Datos actualizados al {max_date_str})*\n\n")
    f.write("Este informe profundiza exclusivamente en el trafico atribuido a Google Ads.\n\n")
    if segmento == 'Grado_Pregrado':
        f.write("*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2024, coincidiendo con la inscripcion a la primera cohorte. En mayo se abren a la segunda.)*\n\n")
    f.write(f"- Total Personas captadas vía Google Ads (Histórico): {total_gads:,}\n")
    f.write(f"- Total Personas captadas vía Google Ads (Muestra Conversión): {total_gads_conv:,}\n")
    f.write(f"- Inscriptos Confirmados (Muestra): {conv_gads:,}\n")
    f.write(f"- Tasa de Conversión Google Ads: {tasa_gads:.2f}%\n")
print(f"-> Textos exportados a MD: {md_path}\n")

# PDF
class GAdsPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, f'UCASAL - Deep Dive: Google Ads Performance (al {max_date_str})', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

pdf = GAdsPDF('L', 'mm', 'A4')
pdf.set_auto_page_break(True, margin=15)
pdf.add_page()

# Resumen
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Resumen Ejecutivo Google Ads', new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_font('Helvetica', '', 12)
if segmento == 'Grado_Pregrado':
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 6, "Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads desde Septiembre 2024.", ln=True)
    pdf.set_font("Helvetica", size=12)
pdf.cell(0, 8, f'Total Personas captadas vía Google Ads (Histórico): {total_gads:,}', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, f'Total Personas captadas vía Google Ads (Muestra): {total_gads_conv:,}', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, f'Inscriptos Confirmados (Muestra): {conv_gads:,}', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, f'Tasa de Conversión Google Ads: {tasa_gads:.2f}%', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)

for c, res in gads_results.items():
    # Pagina: Volumen
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, f'Google Ads: {c} - Volumen', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.image(res['charts']['vol'], x='C', w=260, h=160, keep_aspect_ratio=True)
    
    # Pagina: Tasa de Conversion
    if res['charts']['rate']:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, f'Google Ads: {c} - Tasa de Conversion', new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.image(res['charts']['rate'], x='C', w=260, h=160, keep_aspect_ratio=True)
    
    # Agregar tabla pequeña
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 10, f'Tabla de Datos: Top {c}', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 8)
    # Encabezados
    pdf.cell(80, 7, c[:40], 1)
    pdf.cell(30, 7, 'Personas(H)', 1)
    pdf.cell(30, 7, 'Personas(M)', 1)
    pdf.cell(30, 7, 'Inscriptos', 1)
    pdf.cell(20, 7, 'Tasa %', 1, new_x="LMARGIN", new_y="NEXT")
    # Datos
    top_table = res['tabla'].head(20) if isinstance(res['tabla'], pd.DataFrame) else res['tabla']
    for _, r in top_table.iterrows():
        val_str = str(r[c])[:40]
        pdf.cell(80, 6, val_str, 1)
        pdf.cell(30, 6, str(int(r['Personas'])), 1)
        pdf.cell(30, 6, str(int(r['Personas_Muestra'])), 1)
        pdf.cell(30, 6, str(int(r['Inscriptos'])), 1)
        pdf.cell(20, 6, f"{r['Tasa_%']:.2f}%", 1, new_x="LMARGIN", new_y="NEXT")

pdf.output(os.path.join(output_dir, "Informe_Google_Ads_Deep_Dive.pdf"))
print("Informe Google Ads generado con exito.")

# Memoria Técnica
memoria_gads = """# Memoria Técnica: Cálculos de Google Ads Deep Dive

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión:** Se aíslan todos los Leads cuyo campo `UtmSource` contenga la cadena `"google"` (case-insensitive).
- **Match Exacto (Conversión):** Se restringe la consideración de "Inscriptos" únicamente a aquellos leads donde el campo `Match_Tipo` dictamina una correlación "Exacta" validada por el CRM frente a la universidad. Las coincidencias difusas (Fuzzy) han sido expresamente retiradas del cálculo estadístico de atribución.
- **Limpieza y Deduplicación:** Como una misma persona pudo consultar en varias ocasiones mediante el mismo Ad, previo a generar la base contable se ejecuta una eliminación de duplicados absolutos empleando el documento de identidad (`DNI`) como clave primaria primaria (Primary Key), y el `Correo` como respaldo en caso de carecer de identificación estatal. Esto asegura que no se inflen artificialmente las interacciones del anuncio.
- **Tasa de Conversión (CR%):** Obtenida mediante la fórmula estricta `(Inscriptos Exactos / Volumen Físico de Personas Únicas de la campaña) * 100`.
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria_gads)

