import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para evitar hang de tkinter
import matplotlib.pyplot as plt
import seaborn as sns
import os
from fpdf import FPDF
from datetime import datetime

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Analisis_No_Matcheados")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

# ======================================================
# FECHA MÁXIMA: leer desde INSCRIPTOS (no leads)
# ======================================================
meses_es = {1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio", 
            7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"}

def get_max_date_from_inscriptos():
    """Retorna (Timestamp, string_formateado) de la última fecha de pago de inscriptos."""
    try:
        cols_i = pd.read_csv(inscriptos_csv, nrows=1).columns.tolist()
        # SOLO columnas de PAGO, no Aplicación (que puede ser futura: ej. 2026-12-26)
        pago_candidates = [c for c in cols_i if 'fecha' in c.lower() and 'pago' in c.lower()]
        if not pago_candidates:
            d = pd.Timestamp.now()
            return (d, f"{d.day} de {meses_es[d.month]} de {d.year}")

        df_i = pd.read_csv(inscriptos_csv, usecols=pago_candidates, low_memory=False)
        max_date = pd.NaT
        for col in pago_candidates:
            parsed = pd.to_datetime(df_i[col], format='mixed', dayfirst=True, errors='coerce')
            # Filtrar fechas futuras por seguridad
            hoy = pd.Timestamp.now()
            parsed = parsed[parsed <= hoy]
            col_max = parsed.max()
            if pd.notna(col_max):
                if pd.isna(max_date) or col_max > max_date:
                    max_date = col_max

        if pd.notna(max_date):
            return (max_date, f"{max_date.day} de {meses_es[max_date.month]} de {max_date.year}")
    except Exception as e:
        print(f"Error leyendo inscriptos para fecha: {e}")

    d = pd.Timestamp.now()
    return (d, f"{d.day} de {meses_es[d.month]} de {d.year}")

print("Obteniendo fecha máxima desde inscriptos...")
max_insc_ts, max_date_str = get_max_date_from_inscriptos()
print(f"Fecha máxima inscriptos: {max_date_str}")

# ======================================================
# CARGAR LEADS
# ======================================================
print("Cargando leads...")
usecols = [
    'Match_Tipo', 'Correo', 'DNI', 'Id. candidato/contacto', 
    'Consulta: Fecha de creación', 'Insc_Fecha Pago', 'Fecha Pago',
    'UtmSource', 'UtmCampaign', 'FuenteLead'
]
try:
    cols_available = pd.read_csv(leads_csv, nrows=1).columns.tolist()
    use_cols_filtered = [c for c in usecols if c in cols_available]
    df = pd.read_csv(leads_csv, usecols=use_cols_filtered, low_memory=False)
except Exception:
    df = pd.read_csv(leads_csv, low_memory=False)

# Clasificación
def classify_mc(v):
    s = str(v)
    if 'Exacto' in s: return 'Exacto'
    return 'No Exacto'

df['Grupo_Match'] = df['Match_Tipo'].apply(classify_mc)

# Identificar persona única por Correo (preferido) o DNI
df['Persona_ID'] = df['Correo'].fillna(df['DNI'].astype(str))
df = df[df['Persona_ID'].notna()]
df['Persona_ID'] = df['Persona_ID'].astype(str).str.lower().str.strip()
df = df[~df['Persona_ID'].isin(['nan', '', 'na'])]

md_content = f"# Análisis Profundo: Leads No Matcheados\n\n**Datos actualizados al {max_date_str}**\n\n"
md_content += "Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.\n\n"

# ======================================================
# 0. PIE CHART: Por personas únicas (sin repetidos)
# ======================================================
print("Generando proporción por personas únicas...")

# Pre-compute boolean for speed
df['_is_exacto'] = (df['Grupo_Match'] == 'Exacto').astype(int)

persona_group = df.groupby('Persona_ID').agg(
    Consultas=('Id. candidato/contacto', 'count'),
    Es_Exacto=('_is_exacto', 'max')
).reset_index()

total_personas = len(persona_group)
personas_exactas = int(persona_group['Es_Exacto'].sum())
personas_no_exactas = total_personas - personas_exactas
pct_exactas = (personas_exactas / total_personas * 100) if total_personas > 0 else 0
pct_no_exactas = (personas_no_exactas / total_personas * 100) if total_personas > 0 else 0

md_content += "## 0. Proporción General: Personas Matcheadas vs No Matcheadas\n\n"
md_content += f"Se identificaron **{total_personas:,}** personas únicas (sin repetidos) en la base de datos.\n"
md_content += f"- **Personas Matcheadas (Exacto):** {personas_exactas:,} ({pct_exactas:.1f}%)\n"
md_content += f"- **Personas No Matcheadas:** {personas_no_exactas:,} ({pct_no_exactas:.1f}%)\n\n"

plt.figure(figsize=(8, 8))
colors_pie = ['#2ecc71', '#e74c3c']
labels_pie = [f'Matcheadas\n{personas_exactas:,} ({pct_exactas:.1f}%)', 
              f'No Matcheadas\n{personas_no_exactas:,} ({pct_no_exactas:.1f}%)']
plt.pie([personas_exactas, personas_no_exactas], labels=labels_pie, colors=colors_pie, 
        autopct='', startangle=140, textprops={'fontsize': 13})
plt.title('Proporción de Personas Matcheadas vs No Matcheadas', fontsize=14)
plt.savefig(os.path.join(output_dir, 'pie_matcheados.png'), bbox_inches='tight')
plt.close()

# ======================================================
# 1. DISTRIBUCIÓN DE CONSULTAS (1 a 10+)
# ======================================================
print("Analizando distribución de consultas...")

def bucket_consultas(n):
    if n <= 10: return f'{n} consulta{"s" if n > 1 else ""}'
    else: return '10+ consultas'

persona_group['Rango_Consultas'] = persona_group['Consultas'].apply(bucket_consultas)

dist_exacto = persona_group[persona_group['Es_Exacto'] == 1]['Rango_Consultas'].value_counts()
dist_noexacto = persona_group[persona_group['Es_Exacto'] == 0]['Rango_Consultas'].value_counts()

order = [f'{i} consulta{"s" if i > 1 else ""}' for i in range(1, 11)] + ['10+ consultas']
dist_exacto = dist_exacto.reindex(order, fill_value=0)
dist_noexacto = dist_noexacto.reindex(order, fill_value=0)

pct_exacto = (dist_exacto / dist_exacto.sum() * 100).round(1)
pct_noexacto = (dist_noexacto / dist_noexacto.sum() * 100).round(1)

df_consultas = pd.DataFrame({
    'Rango': order,
    'Inscriptos_Cant': dist_exacto.values,
    'Inscriptos_%': pct_exacto.values,
    'No_Inscriptos_Cant': dist_noexacto.values,
    'No_Inscriptos_%': pct_noexacto.values
})

md_content += "## 1. Distribución de Consultas por Persona\n\n"
md_content += "La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.\n"
md_content += "**Ejemplo de lectura:** *\"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse.\"*\n\n"
md_content += df_consultas.to_markdown(index=False) + "\n\n"

# Gráfico distribución
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
bars1 = axes[0].bar(range(len(order)), dist_exacto.values, color='#2ecc71')
axes[0].set_title('Inscriptos (Matcheados)')
axes[0].set_ylabel('Cantidad de Personas')
axes[0].set_xticks(range(len(order)))
axes[0].set_xticklabels(order, rotation=45, ha='right', fontsize=8)
for i, (v, p) in enumerate(zip(dist_exacto.values, pct_exacto.values)):
    if v > 0:
        axes[0].text(i, v + max(dist_exacto.values)*0.01, f'{p}%', ha='center', fontsize=7)

bars2 = axes[1].bar(range(len(order)), dist_noexacto.values, color='#e74c3c')
axes[1].set_title('No Inscriptos (No Matcheados)')
axes[1].set_ylabel('Cantidad de Personas')
axes[1].set_xticks(range(len(order)))
axes[1].set_xticklabels(order, rotation=45, ha='right', fontsize=8)
for i, (v, p) in enumerate(zip(dist_noexacto.values, pct_noexacto.values)):
    if v > 0:
        axes[1].text(i, v + max(dist_noexacto.values)*0.01, f'{p}%', ha='center', fontsize=7)

fig.suptitle('Distribución de Consultas por Persona', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'volumen_consultas.png'), bbox_inches='tight')
plt.close()

# Gráficos circulares de distribución
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 7))

# Pie Inscriptos
pairs_e = [(r, v, p) for r, v, p in zip(order, dist_exacto.values, pct_exacto.values) if v > 0]
labels_e = [f'{r}\n({p}%)' for r, v, p in pairs_e]
sizes_e = [v for r, v, p in pairs_e]
colors_e = plt.cm.Greens(np.linspace(0.3, 0.9, len(sizes_e)))
axes2[0].pie(sizes_e, labels=labels_e, colors=colors_e, autopct='', startangle=140, textprops={'fontsize': 8})
axes2[0].set_title('Inscriptos (Matcheados)', fontsize=12)

# Pie No Inscriptos
pairs_ne = [(r, v, p) for r, v, p in zip(order, dist_noexacto.values, pct_noexacto.values) if v > 0]
labels_ne = [f'{r}\n({p}%)' for r, v, p in pairs_ne]
sizes_ne = [v for r, v, p in pairs_ne]
colors_ne = plt.cm.Reds(np.linspace(0.3, 0.9, len(sizes_ne)))
axes2[1].pie(sizes_ne, labels=labels_ne, colors=colors_ne, autopct='', startangle=140, textprops={'fontsize': 8})
axes2[1].set_title('No Inscriptos (No Matcheados)', fontsize=12)

fig2.suptitle('Distribución Porcentual de Consultas', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'distribucion_consultas_pie.png'), bbox_inches='tight')
plt.close()

# ======================================================
# 2. TIEMPOS DE RESOLUCIÓN (Solo Matcheados, fechas estrictas)
# ======================================================
print("Analizando tiempos de resolución (solo inscriptos matcheados)...")

has_time_data = False
avg_dias_exacto = 0
mediana_exacto = 0
df_tiempos = pd.DataFrame()
df_deciles = pd.DataFrame()

if 'Consulta: Fecha de creación' in df.columns:
    # Parsear fechas: intentar dd/mm/yyyy primero, luego yyyy-mm-dd
    df['Fecha_Consulta'] = pd.to_datetime(df['Consulta: Fecha de creación'], dayfirst=True, errors='coerce')
    
    # Fecha de pago
    if 'Insc_Fecha Pago' in df.columns and 'Fecha Pago' in df.columns:
        df['Fecha_Pago_Final'] = pd.to_datetime(df['Insc_Fecha Pago'].fillna(df['Fecha Pago']), dayfirst=True, errors='coerce')
    elif 'Fecha Pago' in df.columns:
        df['Fecha_Pago_Final'] = pd.to_datetime(df['Fecha Pago'], dayfirst=True, errors='coerce')
    elif 'Insc_Fecha Pago' in df.columns:
        df['Fecha_Pago_Final'] = pd.to_datetime(df['Insc_Fecha Pago'], dayfirst=True, errors='coerce')
    else:
        df['Fecha_Pago_Final'] = pd.NaT

    # Verificar rango de fechas razonables (ej: 2024-01-01 a hoy + 30 días)
    fecha_min_razonable = pd.Timestamp('2024-01-01')
    fecha_max_razonable = pd.Timestamp.now() + pd.Timedelta(days=30)
    
    df.loc[df['Fecha_Consulta'] < fecha_min_razonable, 'Fecha_Consulta'] = pd.NaT
    df.loc[df['Fecha_Consulta'] > fecha_max_razonable, 'Fecha_Consulta'] = pd.NaT
    df.loc[df['Fecha_Pago_Final'] < fecha_min_razonable, 'Fecha_Pago_Final'] = pd.NaT
    df.loc[df['Fecha_Pago_Final'] > fecha_max_razonable, 'Fecha_Pago_Final'] = pd.NaT

    # SOLO MATCHEADOS EXACTOS
    df_exactos_only = df[df['Grupo_Match'] == 'Exacto'].copy()
    
    persona_time = df_exactos_only.groupby('Persona_ID').agg(
        Primera_Consulta=('Fecha_Consulta', 'min'),
        Fecha_Pago=('Fecha_Pago_Final', 'first')
    ).reset_index()
    
    persona_time = persona_time.dropna(subset=['Primera_Consulta', 'Fecha_Pago'])
    persona_time['Dias_Resolucion'] = (persona_time['Fecha_Pago'] - persona_time['Primera_Consulta']).dt.days
    
    # Filtro: solo días positivos (consulta siempre debe ser igual o anterior al pago)
    persona_time_valid = persona_time[persona_time['Dias_Resolucion'] >= 0]
    
    if len(persona_time_valid) >= 5:
        has_time_data = True
        exactos_t = persona_time_valid['Dias_Resolucion']

        avg_dias_exacto = exactos_t.mean()
        mediana_exacto = exactos_t.median()
        moda_exacto = exactos_t.mode()[0] if not exactos_t.mode().empty else np.nan
        
        md_content += "## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)\n\n"
        md_content += "Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.\n\n"
        md_content += "Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).\n\n"
        md_content += f"**Personas analizadas:** {len(exactos_t):,}\n"
        md_content += f"- **Promedio:** {avg_dias_exacto:.0f} días\n"
        md_content += f"- **Mediana:** {mediana_exacto:.0f} días\n"
        md_content += f"- **Moda (Valor Más Frecuente):** {moda_exacto:.0f} días\n\n"
        md_content += "**Nota:** Las gráficas 2a y 2b utilizan los mismos rangos de días para garantizar coherencia. La gráfica 2a muestra la distribución como histograma continuo, mientras que 2b presenta los datos como barras categóricas con porcentajes y acumulados.\n\n"
        
        df_tiempos = pd.DataFrame({
            'Metrica': ['Promedio', 'Mediana', 'Moda', 'Personas Analizadas'],
            'Valor': [f'{avg_dias_exacto:.0f} días', f'{mediana_exacto:.0f} días', f'{moda_exacto:.0f} días', f'{len(exactos_t):,}']
        })

        # Histograma 2a: usa los MISMOS bins que la gráfica 2b para coherencia visual
        bins_hist = [0, 1, 3, 7, 14, 30, 60, 90, 120, 150, 180, 210, 240, 270, max(exactos_t.max() + 1, 271)]
        plt.figure(figsize=(10, 5))
        counts_h, edges_h, patches = plt.hist(exactos_t, bins=bins_hist, color='#3498db', edgecolor='white', alpha=0.85)
        # Etiquetas centradas en cada barra con la cantidad
        for i, (cnt, left, right) in enumerate(zip(counts_h, edges_h[:-1], edges_h[1:])):
            if cnt > 0:
                mid = (left + right) / 2
                plt.text(mid, cnt + max(counts_h) * 0.01, f'{int(cnt)}', ha='center', fontsize=7, fontweight='bold')
        plt.axvline(mediana_exacto, color='#e67e22', linewidth=2, linestyle='--', label=f'Mediana: {mediana_exacto:.0f} días')
        plt.axvline(avg_dias_exacto, color='#e74c3c', linewidth=2, linestyle=':', label=f'Promedio: {avg_dias_exacto:.0f} días')
        plt.xlabel('Días desde Primera Consulta hasta Pago')
        plt.ylabel('Cantidad de Personas')
        plt.title('Distribución de Tiempos de Resolución (Inscriptos Matcheados)')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'tiempos_resolucion.png'), bbox_inches='tight')
        plt.close()

        # --- 2b. DISTRIBUCIÓN POR RANGOS DE DÍAS ABSOLUTOS ---
        # Muestra cuántas personas se inscribieron en cada rango de días
        md_content += "### 2b. Distribución por Rangos de Días hasta Inscripción\n\n"
        md_content += "**Nota Metodológica:** Este análisis calcula los días desde la **PRIMERA CONSULTA REGISTRADA** hasta el pago/inscripción. Si una persona consultó múltiples veces, el reloj comienza en el primer contacto registrado, independientemente de cuántas veces volvió a consultar después.\n\n"
        md_content += "Esta métrica busca responder: **\"¿Cuánto tiempo desde que primero se interesó hasta que efectivamente se inscribió?\"** de forma conservadora y realista, midiendo la velocidad de conversión desde el primer contacto.\n\n"
        md_content += "**Definición de rangos:** 'Mismo día' incluye personas que se inscribieron el mismo día o el día siguiente de su primera consulta (0-1 días). Los demás rangos son acumulativos hasta cada límite superior.\n\n"
        
        # Definir rangos: fine-grained para 0-30 días, luego uniforme ~30 días hasta 270
        bins_dias = [0, 1, 3, 7, 14, 30, 60, 90, 120, 150, 180, 210, 240, 270, float('inf')]
        labels_dias = ['Mismo día', '1-3 días', '4-7 días', '8-14 días', '15-30 días',
                       '31-60 días', '61-90 días', '91-120 días', '121-150 días',
                       '151-180 días', '181-210 días', '211-240 días', '241-270 días',
                       'Más de 270 días']
        
        # Clasificar cada persona en su rango de días
        persona_time_valid['Rango_Dias'] = pd.cut(persona_time_valid['Dias_Resolucion'], bins=bins_dias, 
                                            labels=labels_dias, right=True, include_lowest=True)
        
        # Contar personas por rango
        dist_dias = persona_time_valid['Rango_Dias'].value_counts().reindex(labels_dias, fill_value=0)
        total_analizado = dist_dias.sum()
        pct_dias = (dist_dias / total_analizado * 100).round(1) if total_analizado > 0 else dist_dias * 0
        
        # Acumulado para saber "qué % ya pagó en X días o menos"
        pct_acum = pct_dias.cumsum().round(1)
        
        df_dist_dias = pd.DataFrame({
            'Rango': labels_dias,
            'Personas': dist_dias.values,
            '%': pct_dias.values,
            '% Acumulado': pct_acum.values
        })
        
        md_content += df_dist_dias.to_markdown(index=False) + "\n\n"
        md_content += "*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*\n\n"
        
        # Gráfico de barras con días absolutos
        fig, ax = plt.subplots(figsize=(12, 6))
        x_pos = np.arange(len(labels_dias))
        bars = ax.bar(x_pos, dist_dias.values, color='#3498db', edgecolor='white')
        
        # Agregar etiquetas con cantidad y porcentaje en cada barra
        for i, (v, p) in enumerate(zip(dist_dias.values, pct_dias.values)):
            if v > 0:
                ax.text(i, v + max(dist_dias.values) * 0.01, f'{v}\n({p}%)', 
                        ha='center', fontsize=8, fontweight='bold')
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels_dias, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('Cantidad de Personas')
        ax.set_xlabel('Días desde Primera Consulta hasta Pago')
        ax.set_title('¿Cuántos días tardan en inscribirse? (Solo Matcheados)')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'distribucion_dias_inscripcion.png'), bbox_inches='tight')
        plt.close()

        # --- 2b-2: CURVA ACUMULADA CONTINUA (ECDF) ---
        # Eje X: días desde primera consulta. Eje Y: % acumulado de inscriptos que ya pagaron.
        dias_sorted = np.sort(exactos_t.values)
        pct_cumsum = np.arange(1, len(dias_sorted) + 1) / len(dias_sorted) * 100

        fig_curva, ax_curva = plt.subplots(figsize=(12, 6))
        ax_curva.plot(dias_sorted, pct_cumsum, color='#2ecc71', linewidth=2.5, label='% acumulado de inscriptos')

        # Líneas de referencia verticales en días clave (cada 30d dentro del rango principal)
        ref_days_list = [30, 60, 90, 120, 150, 180, 210, 240, 270]
        for ref_d in ref_days_list:
            pct_at = (dias_sorted <= ref_d).mean() * 100
            ax_curva.axvline(x=ref_d, color='gray', linestyle='--', alpha=0.45, linewidth=1)
            ax_curva.text(ref_d + 1, pct_at + 1.5, f'{ref_d}d\n{pct_at:.0f}%',
                          fontsize=7.5, color='dimgray', va='bottom')

        ax_curva.set_xlabel('Días desde Primera Consulta hasta Pago')
        ax_curva.set_ylabel('% Acumulado de Inscriptos')
        ax_curva.set_title('Curva Acumulada de Conversión: velocidad de inscripción de leads')
        ax_curva.set_xlim(left=0, right=max(dias_sorted.max(), 280))
        ax_curva.set_ylim(0, 105)
        ax_curva.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
        ax_curva.legend(fontsize=10)
        ax_curva.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'curva_acumulada_conversion.png'), bbox_inches='tight')
        plt.close()

        # --- Tabla de deciles (referencia estadística) ---
        md_content += "### 2c. Referencia Estadística: Deciles\n\n"
        deciles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        decile_labels = ['D10', 'D20', 'D30', 'D40', 'D50 (Mediana)', 'D60', 'D70', 'D80', 'D90', 'D100 (Máx)']
        
        dec_exacto = exactos_t.quantile(deciles).values
        
        df_deciles = pd.DataFrame({
            'Decil': decile_labels,
            'Dias': [f"{v:.0f}" for v in dec_exacto]
        })

        md_content += df_deciles.to_markdown(index=False) + "\n\n"
        md_content += "*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*\n\n"

if not has_time_data:
    md_content += "## 2. Tiempo de Resolución\nNo se hallaron suficientes registros con fechas válidas para calcular esta métrica.\n\n"

# ======================================================
# 3. RENDIMIENTO POR DOMINIOS DE EMAIL
# ======================================================
print("Analizando dominios de correo...")
df_emails = df.dropna(subset=['Correo']).copy()
df_emails['Correo'] = df_emails['Correo'].astype(str).str.lower().str.strip()
df_emails['Domain'] = df_emails['Correo'].apply(lambda d: d.split('@')[-1] if '@' in d else 'Invalido')

# Pre-compute flags for vectorized aggregation
df_emails['_es_exacto'] = (df_emails['Grupo_Match'] == 'Exacto').astype(int)
df_emails['_es_no_exacto'] = (df_emails['Grupo_Match'] == 'No Exacto').astype(int)

domain_gb = df_emails.groupby('Domain').agg(
    Total_Leads=('Id. candidato/contacto', 'count'),
    Exactos=('_es_exacto', 'sum'),
    No_Exactos=('_es_no_exacto', 'sum')
).reset_index()

domain_gb['Tasa_Inscripcion_%'] = (domain_gb['Exactos'] / domain_gb['Total_Leads'] * 100).round(2)
domain_top = domain_gb[domain_gb['Total_Leads'] >= 50].sort_values('Total_Leads', ascending=False).head(15)

md_content += "## 3. Tasa de Inscripción por Dominio de Correo Electrónico\n\n"
md_content += "Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. "
md_content += "Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.\n\n"

md_content += domain_top.to_markdown(index=False) + "\n\n"

# Gráfico dominios: barras horizontales en un solo color con etiquetas claras
plt.figure(figsize=(10, 7))
domain_sorted = domain_top.sort_values('Tasa_Inscripcion_%', ascending=True)
bars = plt.barh(domain_sorted['Domain'], domain_sorted['Tasa_Inscripcion_%'], color='#3498db', edgecolor='white')
for bar, val in zip(bars, domain_sorted['Tasa_Inscripcion_%']):
    plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', va='center', fontsize=9)
plt.xlabel('Tasa de Inscripción (%)')
plt.ylabel('Dominio de Correo')
plt.title('Tasa de Inscripción por Dominio de Correo (Top 15)')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'dominios_match.png'), bbox_inches='tight')
plt.close()

# ======================================================
# 3b. HISTOGRAMA GRANULAR DE TIEMPOS (día a día)
# ======================================================
if has_time_data:
    print("Generando histograma granular de tiempos (3b)...")
    md_content += "## 3b. Distribución Granular: Día a Día hasta Inscripción\n\n"
    md_content += "Esta gráfica complementa la sección 2b mostrando un **histograma continuo día a día**, "
    md_content += "donde cada barra representa un intervalo pequeño de días. "
    md_content += "Permite visualizar con mayor detalle los picos y la forma de la distribución, "
    md_content += "especialmente en los primeros días donde se concentra la mayor cantidad de inscripciones.\n\n"
    md_content += f"**Personas analizadas:** {len(exactos_t):,} (mismas que sección 2)\n\n"

    plt.figure(figsize=(12, 6))
    plt.hist(exactos_t, bins=50, color='#9b59b6', edgecolor='white', alpha=0.85)
    plt.axvline(mediana_exacto, color='#e67e22', linewidth=2, linestyle='--',
                label=f'Mediana: {mediana_exacto:.0f} días')
    plt.axvline(avg_dias_exacto, color='#e74c3c', linewidth=2, linestyle=':',
                label=f'Promedio: {avg_dias_exacto:.0f} días')
    # Marcar "Mismo día" (0-1 días) explícitamente
    n_mismo_dia = ((exactos_t >= 0) & (exactos_t <= 1)).sum()
    plt.annotate(f'Mismo día\n(0-1 días)\n{n_mismo_dia} personas',
                 xy=(0.5, n_mismo_dia * 0.3), fontsize=9, fontweight='bold',
                 color='#8e44ad', ha='center',
                 arrowprops=dict(arrowstyle='->', color='#8e44ad'),
                 xytext=(40, n_mismo_dia * 0.6))
    plt.xlabel('Días desde Primera Consulta hasta Pago')
    plt.ylabel('Cantidad de Personas')
    plt.title('Distribución Granular: Día a Día hasta Inscripción\n(histograma continuo con 50 intervalos)')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'histograma_granular_dias.png'), bbox_inches='tight')
    plt.close()

# ======================================================
# EXPORTACIONES
# ======================================================
print("Guardando archivos y PDF...")
with open(os.path.join(output_dir, 'Analisis_No_Matcheados.md'), 'w', encoding='utf-8') as f:
    f.write(md_content)

with pd.ExcelWriter(os.path.join(output_dir, 'datos_analisis_no_matcheados.xlsx')) as writer:
    df_consultas.to_excel(writer, sheet_name='Distribucion_Consultas', index=False)
    if not df_tiempos.empty:
        df_tiempos.to_excel(writer, sheet_name='Tiempos_Resolucion', index=False)
    if not df_deciles.empty:
        df_deciles.to_excel(writer, sheet_name='Deciles_Tiempos', index=False)
    domain_gb.to_excel(writer, sheet_name='Dominios', index=False)

# PDF
class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "Análisis de Leads No Matcheados", ln=True, align="C")
        self.set_font("Helvetica", 'I', 10)
        self.cell(0, 6, f"Datos actualizados al {max_date_str}", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

pdf = PDFReport('L')
pdf.add_page()

# 0. Pie chart
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "0. Personas Matcheadas vs No Matcheadas", ln=True)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, f"Personas únicas: {total_personas:,}\n"
                     f"Matcheadas: {personas_exactas:,} ({pct_exactas:.1f}%)\n"
                     f"No Matcheadas: {personas_no_exactas:,} ({pct_no_exactas:.1f}%)")
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'pie_matcheados.png'), w=140)
except Exception: pass

# 1. Distribución
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "1. Distribución de Consultas por Persona", ln=True)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, "Distribución de cuántas consultas hizo cada persona antes de su resultado final.")
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'volumen_consultas.png'), w=250)
except Exception: pass

pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "1b. Distribución Porcentual (Gráficos Circulares)", ln=True)
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'distribucion_consultas_pie.png'), w=250)
except Exception: pass

# 2. Tiempos
if has_time_data:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Tiempos de Resolución (Solo Inscriptos)", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"Promedio: {avg_dias_exacto:.0f} días | Mediana: {mediana_exacto:.0f} días\n"
                         f"Personas analizadas: {len(exactos_t):,}\n\n"
                         f"Las gráficas 2a y 2b utilizan los mismos rangos de días para garantizar coherencia. "
                         f"La gráfica 2a muestra la distribución como histograma, 2b agrega porcentajes y acumulados.")
    pdf.ln(5)
    try:
        pdf.image(os.path.join(output_dir, 'tiempos_resolucion.png'), w=150)
    except Exception: pass
    
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2b. ¿Cuántos días tardan en inscribirse?", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, "Distribución de inscriptos por rangos de días específicos (mismos rangos que la gráfica 2a). "
                         "Los primeros rangos son detallados (0-30 días) y desde 30 hasta 270 días se usan intervalos uniformes de ~30 días.\n\n"
                         "'Mismo día' = 0-1 días (persona se inscribió el mismo día o el siguiente de su primera consulta). "
                         "Se calcula desde la PRIMERA CONSULTA REGISTRADA (si consultó múltiples veces, el reloj comienza en el primer contacto). "
                         "Responde: '¿Cuánto tiempo desde que primero se interesó hasta que efectivamente se inscribió?', "
                         "de forma conservadora y realista.")
    pdf.ln(5)
    try:
        pdf.image(os.path.join(output_dir, 'distribucion_dias_inscripcion.png'), w=230)
    except Exception: pass

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2c. Curva Acumulada de Conversión", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, "Cada punto de la curva responde: '¿Qué % de los inscriptos ya habían pagado dentro de N días "
                         "de su primera consulta?'. Las líneas punteadas muestran el % alcanzado en cada umbral de 30 días.")
    pdf.ln(5)
    try:
        pdf.image(os.path.join(output_dir, 'curva_acumulada_conversion.png'), w=230)
    except Exception: pass

# 3. Dominios
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "3. Tasa de Inscripción por Dominio de Correo", ln=True)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, "Muestra el porcentaje de leads que se inscribieron según el dominio de su correo electrónico.")
pdf.ln(5)
try:
    pdf.image(os.path.join(output_dir, 'dominios_match.png'), w=160)
except Exception: pass

# 3b. Histograma granular
if has_time_data:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3b. Distribución Granular: Día a Día hasta Inscripción", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, "Histograma continuo con 50 intervalos que muestra la distribución día a día. "
                         "Complementa la sección 2b permitiendo ver con mayor detalle los picos y la forma "
                         "de la distribución, especialmente en los primeros días donde se concentra la mayor "
                         "cantidad de inscripciones.\n\n"
                         f"Personas analizadas: {len(exactos_t):,} (mismas que sección 2). "
                         "Se calcula desde la PRIMERA CONSULTA REGISTRADA de cada persona.")
    pdf.ln(5)
    try:
        pdf.image(os.path.join(output_dir, 'histograma_granular_dias.png'), w=230)
    except Exception: pass

pdf.output(os.path.join(output_dir, 'Analisis_No_Matcheados_Reporte.pdf'))

# ======================================================
# MEMORIA TÉCNICA (PDF aparte con muestreo de datos)
# ======================================================
# Genera un PDF separado con muestras de los datos usados en cada gráfica,
# para que un humano pueda verificar que los cálculos tienen sentido.
print("Generando Memoria Técnica...")

class PDFMemoria(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 12)
        self.cell(0, 8, "Memoria Técnica - Análisis de Leads No Matcheados", ln=True, align="C")
        self.set_font("Helvetica", 'I', 9)
        self.cell(0, 5, f"Datos actualizados al {max_date_str} | Documento de control interno", ln=True, align="C")
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Memoria Técnica - Pág. {self.page_no()}", align="C")

mt = PDFMemoria('L')

# --- Sección 0: Datos del Pie Chart (Matcheados vs No Matcheados) ---
mt.add_page()
mt.set_font("Helvetica", "B", 11)
mt.cell(0, 8, "0. VERIFICACIÓN: Proporción Matcheados vs No Matcheados", ln=True)
mt.set_font("Helvetica", size=9)
mt.multi_cell(0, 5,
    f"Total personas únicas analizadas: {total_personas:,}\n"
    f"Personas Matcheadas (Exactas): {personas_exactas:,} ({pct_exactas:.1f}%)\n"
    f"Personas No Matcheadas: {personas_no_exactas:,} ({pct_no_exactas:.1f}%)\n"
    f"Criterio: Persona = Correo (o DNI si Correo es nulo). Match_Tipo contiene 'Exacto' o 'Si (Lead'.\n"
    f"Se desduplicó por Persona_ID para contar personas únicas, no filas.")
mt.ln(3)
mt.set_font("Helvetica", "B", 9)
mt.cell(0, 6, "Muestreo de 10 personas matcheadas:", ln=True)
mt.set_font("Helvetica", size=8)
sample_match = persona_group[persona_group['Es_Exacto'] == 1].head(10)
for _, r in sample_match.iterrows():
    pid = str(r['Persona_ID'])[:40]
    mt.cell(0, 4, f"  ID: {pid} | Consultas: {r['Consultas']}", ln=True)
mt.ln(3)
mt.set_font("Helvetica", "B", 9)
mt.cell(0, 6, "Muestreo de 10 personas NO matcheadas:", ln=True)
mt.set_font("Helvetica", size=8)
sample_nomatch = persona_group[persona_group['Es_Exacto'] == 0].head(10)
for _, r in sample_nomatch.iterrows():
    pid = str(r['Persona_ID'])[:40]
    mt.cell(0, 4, f"  ID: {pid} | Consultas: {r['Consultas']}", ln=True)

# --- Sección 1: Distribución de Consultas ---
mt.add_page()
mt.set_font("Helvetica", "B", 11)
mt.cell(0, 8, "1. VERIFICACIÓN: Distribución de Consultas por Persona", ln=True)
mt.set_font("Helvetica", size=9)
mt.multi_cell(0, 5,
    f"Se agrupó por Persona_ID y se contó la cantidad de filas (consultas) por persona.\n"
    f"Luego se clasificó en rangos: 1, 2, 3, ... 9, 10+.\n"
    f"Los datos se separaron en Matcheados (Es_Exacto=1) y No Matcheados (Es_Exacto=0).")
mt.ln(3)
mt.set_font("Helvetica", "B", 9)
mt.cell(0, 6, "Tabla completa de distribución:", ln=True)
mt.set_font("Helvetica", size=8)
mt.cell(0, 4, f"{'Rango':<15} {'Matcheados':>12} {'No Matcheados':>15} {'% Match':>10} {'% NoMatch':>10}", ln=True)
mt.cell(0, 3, "-" * 65, ln=True)
for rango in order:
    v_e = dist_exacto.get(rango, 0)
    v_ne = dist_noexacto.get(rango, 0)
    p_e = pct_exacto.get(rango, 0)
    p_ne = pct_noexacto.get(rango, 0)
    mt.cell(0, 4, f"  {rango:<13} {v_e:>12,} {v_ne:>15,} {p_e:>9.1f}% {p_ne:>9.1f}%", ln=True)

# --- Sección 2: Tiempos de Resolución ---
if has_time_data:
    mt.add_page()
    mt.set_font("Helvetica", "B", 11)
    mt.cell(0, 8, "2. VERIFICACIÓN: Tiempos de Resolución (Solo Inscriptos)", ln=True)
    mt.set_font("Helvetica", size=9)
    mt.multi_cell(0, 5,
        f"Cálculo: Dias_Resolucion = Fecha_Pago - Primera_Consulta (en días)\n"
        f"  - Primera_Consulta = MIN de todas las fechas de consulta por persona (la más antigua registrada)\n"
        f"  - Fecha_Pago = fecha de pago/inscripción\n"
        f"  - Si una persona consultó múltiples veces, se usa SIEMPRE la primera fecha registrada\n"
        f"Filtros aplicados: Solo Match_Tipo 'Exacto' | Consulta >= 2024-01-01 | Pago <= hoy\n"
        f"Rango aceptado: 0 a 180 días (> 180 se descarta como outlier)\n"
        f"Personas que pasan los filtros: {len(exactos_t):,}\n"
        f"Promedio: {avg_dias_exacto:.1f} días | Mediana: {mediana_exacto:.1f} días | Moda: {moda_exacto:.0f} días\n"
        f"Mínimo: {exactos_t.min():.0f} días | Máximo: {exactos_t.max():.0f} días\n\n"
        f"INTERPRETACIÓN: ¿Cuánto tiempo desde que primero se interesó hasta que efectivamente se inscribió?, "
        f"independientemente de cuántas veces volvió a consultar.")
    mt.ln(3)
    mt.set_font("Helvetica", "B", 9)
    mt.cell(0, 6, "Muestreo de 20 registros individuales (datos crudos):", ln=True)
    mt.set_font("Helvetica", size=8)
    mt.cell(0, 3, "-" * 80, ln=True)
    mt.cell(0, 4, "--- Top 10 tiempos más largos (Maximos) ---", ln=True)
    top_10 = persona_time_valid.sort_values('Dias_Resolucion', ascending=False).head(10)
    for _, r in top_10.iterrows():
        pid = str(r['Persona_ID'])[:33]
        fc = r['Primera_Consulta'].strftime('%Y-%m-%d') if pd.notna(r['Primera_Consulta']) else 'N/A'
        fp = r['Fecha_Pago'].strftime('%Y-%m-%d') if pd.notna(r['Fecha_Pago']) else 'N/A'
        dias = f"{r['Dias_Resolucion']:.0f}"
        mt.cell(0, 4, f"  {pid:<33} {fc:>18} {fp:>18} {dias:>6}", ln=True)
        
    mt.cell(0, 4, "--- Top 10 tiempos más cortos (Minimos) ---", ln=True)
    bottom_10 = persona_time_valid.sort_values('Dias_Resolucion', ascending=True).head(10)
    for _, r in bottom_10.iterrows():
        pid = str(r['Persona_ID'])[:33]
        fc = r['Primera_Consulta'].strftime('%Y-%m-%d') if pd.notna(r['Primera_Consulta']) else 'N/A'
        fp = r['Fecha_Pago'].strftime('%Y-%m-%d') if pd.notna(r['Fecha_Pago']) else 'N/A'
        dias = f"{r['Dias_Resolucion']:.0f}"
        mt.cell(0, 4, f"  {pid:<33} {fc:>18} {fp:>18} {dias:>6}", ln=True)
    
    mt.ln(3)
    mt.set_font("Helvetica", "B", 9)
    mt.cell(0, 6, "Distribución por rangos de días:", ln=True)
    mt.set_font("Helvetica", size=8)
    try:
        mt.cell(0, 4, f"{'Rango':<20} {'Personas':>10} {'%':>8} {'% Acum':>8}", ln=True)
        mt.cell(0, 3, "-" * 50, ln=True)
        for _, r in df_dist_dias.iterrows():
            mt.cell(0, 4, f"  {r['Rango']:<18} {r['Personas']:>10} {r['%']:>7.1f}% {r['% Acumulado']:>7.1f}%", ln=True)
    except Exception:
        mt.cell(0, 4, "  (Datos de distribución por días no disponibles)", ln=True)
    
    mt.ln(3)
    mt.set_font("Helvetica", "B", 9)
    mt.cell(0, 6, "Tabla de deciles:", ln=True)
    mt.set_font("Helvetica", size=8)
    for _, r in df_deciles.iterrows():
        mt.cell(0, 4, f"  {r['Decil']:<20} {r['Dias']:>6} días", ln=True)

# --- Sección 3: Dominios ---
mt.add_page()
mt.set_font("Helvetica", "B", 11)
mt.cell(0, 8, "3. VERIFICACIÓN: Tasa de Inscripción por Dominio", ln=True)
mt.set_font("Helvetica", size=9)
mt.multi_cell(0, 5,
    f"Se extrajo el dominio del correo de cada persona (parte después del @).\n"
    f"Se contó: Total de leads y cuántos matchearon por dominio.\n"
    f"Se filtró a dominios con >= 100 leads para evitar ruido estadístico.")
mt.ln(3)
mt.set_font("Helvetica", "B", 9)
mt.cell(0, 6, "Top 15 dominios (datos completos):", ln=True)
mt.set_font("Helvetica", size=8)
mt.cell(0, 4, f"{'Dominio':<25} {'Total Leads':>12} {'Exactos':>12} {'Tasa %':>8}", ln=True)
mt.cell(0, 3, "-" * 60, ln=True)
for _, r in domain_top.iterrows():
    mt.cell(0, 4, f"  {r['Domain']:<23} {r['Total_Leads']:>12,} {r['Exactos']:>12,} {r['Tasa_Inscripcion_%']:>7.2f}%", ln=True)

# --- Sección 4: Tasas de Conversión (Meta, Google, General) ---
mt.add_page()
mt.set_font("Helvetica", "B", 11)
mt.cell(0, 8, "4. VERIFICACIÓN: Tasas de Conversión (Exactas - Histórico)", ln=True)
mt.set_font("Helvetica", size=9)

df['UtmSource_Clean'] = df['UtmSource'].astype(str).str.lower().str.strip()
df['FuenteLead_Num'] = pd.to_numeric(df['FuenteLead'], errors='coerce')

# Cálculos General Histórico
t_leads = len(df)
c_exactos_gen = len(df[df['Grupo_Match'] == 'Exacto'])
tasa_gen = (c_exactos_gen / t_leads) * 100 if t_leads > 0 else 0

# Cálculos Meta
meta_keywords = ['fb', 'facebook', 'ig', 'instagram', 'meta']
mask_meta = df['UtmSource_Clean'].str.contains('|'.join(meta_keywords), na=False) | (df['FuenteLead_Num'] == 18)
df_meta = df[mask_meta]
t_meta = len(df_meta)
c_exactos_meta = len(df_meta[df_meta['Grupo_Match'] == 'Exacto'])
tasa_meta = (c_exactos_meta / t_meta) * 100 if t_meta > 0 else 0

# Cálculos Google
google_keywords = ['google', 'gads']
mask_google = df['UtmSource_Clean'].str.contains('|'.join(google_keywords), na=False)
df_google = df[mask_google]
t_google = len(df_google)
c_exactos_google = len(df_google[df_google['Grupo_Match'] == 'Exacto'])
tasa_google = (c_exactos_google / t_google) * 100 if t_google > 0 else 0

mt.multi_cell(0, 5,
    f"Se aislaron las fuentes (Meta y Google) y se filtraron estrictamente por 'Match_Tipo' igual a 'Exacto'.\n"
    f"- Total Leads General (Histórico): {t_leads:,} | Convertidos: {c_exactos_gen:,} -> Tasa: {tasa_gen:.2f}%\n"
    f"- Total Leads Meta: {t_meta:,} | Convertidos Exactos Meta: {c_exactos_meta:,} -> Tasa: {tasa_meta:.2f}%\n"
    f"- Total Leads Google: {t_google:,} | Convertidos Exactos Google: {c_exactos_google:,} -> Tasa: {tasa_google:.2f}%")

mt.ln(3)

# ==============================================================
# SECCION MUESTRA PARA CONVERSION (GRADO/PREGRADO > SEP 2024)
# ==============================================================
if segmento == 'Grado_Pregrado':
    mt.set_font("Helvetica", "B", 11)
    mt.cell(0, 8, "5. VERIFICACIÓN: Tasas de Conversión (Muestra Cohorte Sept 2025)", ln=True)
    mt.set_font("Helvetica", size=9)
    
    df['Fecha_Limpia'] = pd.to_datetime(
        df['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')
    df_conv = df[
        (df['Fecha_Limpia'] >= '2025-09-01') &
        (df['Fecha_Limpia'] <= max_insc_ts)
    ].copy()

    t_leads_c = len(df_conv)
    c_exactos_gen_c = len(df_conv[df_conv['Grupo_Match'] == 'Exacto'])
    tasa_gen_c = (c_exactos_gen_c / t_leads_c) * 100 if t_leads_c > 0 else 0
    
    df_meta_c = df_conv[df_conv['UtmSource_Clean'].str.contains('|'.join(meta_keywords), na=False) | (df_conv['FuenteLead_Num'] == 18)]
    t_meta_c = len(df_meta_c)
    c_exactos_meta_c = len(df_meta_c[df_meta_c['Grupo_Match'] == 'Exacto'])
    tasa_meta_c = (c_exactos_meta_c / t_meta_c) * 100 if t_meta_c > 0 else 0
    
    df_google_c = df_conv[df_conv['UtmSource_Clean'].str.contains('|'.join(google_keywords), na=False)]
    t_google_c = len(df_google_c)
    c_exactos_google_c = len(df_google_c[df_google_c['Grupo_Match'] == 'Exacto'])
    tasa_google_c = (c_exactos_google_c / t_google_c) * 100 if t_google_c > 0 else 0
    
    mt.multi_cell(0, 5,
        f"Ventana de conversion: 01/09/2025 al {max_date_str} (ultima inscripcion registrada).\n"
        f"Leads posteriores a esa fecha se excluyen del denominador (no tuvieron tiempo de convertirse).\n"
        f"- Total Leads General (Muestra): {t_leads_c:,} | Convertidos: {c_exactos_gen_c:,} -> Tasa: {tasa_gen_c:.2f}%\n"
        f"- Leads Meta (Muestra): {t_meta_c:,} | Convertidos Meta: {c_exactos_meta_c:,} -> Tasa: {tasa_meta_c:.2f}%\n"
        f"- Leads Google (Muestra): {t_google_c:,} | Convertidos Google: {c_exactos_google_c:,} -> Tasa: {tasa_google_c:.2f}%")


mt.ln(3)
mt.set_font("Helvetica", "B", 9)
mt.cell(0, 6, "Muestreo: 10 Leads Convertidos en Meta (Exactos):", ln=True)
mt.set_font("Helvetica", size=8)
sample_meta = df_meta[df_meta['Grupo_Match'] == 'Exacto'].head(10)
for _, r in sample_meta.iterrows():
    pid = str(r['Correo'])[:30] if pd.notna(r['Correo']) else str(r['DNI'])[:30]
    mt.cell(0, 4, f"  ID/Correo: {pid:<30} | FuenteLead: {r['FuenteLead']} | UTM: {r['UtmSource']}", ln=True)

mt.output(os.path.join(output_dir, 'Memoria_Tecnica.pdf'))
print("Memoria Técnica generada: outputs/Analisis_No_Matcheados/Memoria_Tecnica.pdf")

print("Proceso Finalizado. Archivos guardados en outputs/Analisis_No_Matcheados/")
