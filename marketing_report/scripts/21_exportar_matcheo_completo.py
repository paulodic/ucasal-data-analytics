"""
21_exportar_matcheo_completo.py
Exporta la tabla maestra leads-inscriptos a 4 archivos Excel separados:
  Resumen_<seg>.xlsx       | Métricas y estadísticas del proceso de matcheo
  Con_Duplicados_<seg>.xlsx| Todos los registros de leads (incluyendo duplicados por persona)
  Deduplicados_<seg>.xlsx  | Una fila por persona (mejor match priorizado)
  Solo_Matcheados_<seg>.xlsx | Solo personas que matchearon exactamente (tienen inscripto)

Motor: xlsxwriter (más rápido que openpyxl para grandes volúmenes de datos)

SALIDA (output_dir = outputs/{segmento}/Matcheo_Completo/):
  - Resumen_{segmento}.xlsx          -> Métricas y estadísticas del proceso
  - Con_Duplicados_{segmento}.xlsx   -> Todos los registros de leads
  - Deduplicados_{segmento}.xlsx     -> Una fila por persona (mejor match)
  - Solo_Matcheados_{segmento}.xlsx  -> Solo matcheos exactos
  - Matcheo_Completo_{segmento}.md   -> Documentacion del proceso
"""
import pandas as pd
import numpy as np
import os, sys
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
db_dir   = os.path.join(base_dir, "outputs", "Data_Base", segmento)
out_dir  = os.path.join(base_dir, "outputs", segmento, "Matcheo_Completo")
os.makedirs(out_dir, exist_ok=True)

print(f"Cargando datos para {segmento}...")
df_raw  = pd.read_csv(os.path.join(db_dir, "reporte_marketing_leads_completos.csv"), low_memory=False)
df_insc = pd.read_csv(os.path.join(db_dir, "reporte_marketing_inscriptos_origenes.csv"), low_memory=False)
print(f"  Leads raw: {len(df_raw):,}  |  Inscriptos: {len(df_insc):,}")

# ============================================================
# LIMPIEZA Y CLASIFICACIÓN DE MATCH
# ============================================================
# Simplifica Match_Tipo a 3 categorías para procesamiento interno
def classify(v):
    s = str(v)
    if 'Exacto' in s: return 'Exacto'
    if 'Fuzzy'  in s: return 'Fuzzy'
    return 'Sin_Match'

df_raw['_mc'] = df_raw['Match_Tipo'].apply(classify)

# DNI sin decimal (los CSVs lo almacenan como float: "12345678.0" -> "12345678")
for col in ['DNI', 'Insc_DNI']:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.split('.').str[0].str.strip().replace('nan', '')

# Clave de deduplicación: identifica a una persona a partir del primer campo no vacío
# Prioridad: DNI > Correo > ID Consulta > índice de fila
def make_pk(row):
    for field in ['DNI', 'Correo', 'Consulta: ID Consulta']:
        val = str(row.get(field, '')).strip()
        if val and val not in ('nan', 'None', ''):
            return val
    return str(row.name)

df_raw['_pk'] = df_raw.apply(make_pk, axis=1)

# ============================================================
# DEDUPLICACIÓN PRIORIZADA
# ============================================================
# Orden Exacto > Fuzzy > Sin_Match: si una persona tiene múltiples registros,
# el que queda en "Deduplicados" es el de mejor calidad de match
prio = {'Exacto': 0, 'Fuzzy': 1, 'Sin_Match': 2}
df_sorted = df_raw.assign(_prio=df_raw['_mc'].map(prio)).sort_values('_prio')

# Excluir columnas auxiliares del export final (son solo para procesamiento)
export_cols = [c for c in df_raw.columns if c not in ('_mc', '_pk', '_prio')]

# Construir las 3 tablas de datos
df_con_dup    = df_raw[export_cols].copy()                                                         # todos los registros raw
df_dedup      = df_sorted.drop_duplicates(subset='_pk')[export_cols].copy()                        # 1 fila por persona (mejor match)
df_matcheados = df_sorted[df_sorted['_mc'] == 'Exacto'].drop_duplicates(subset='_pk')[export_cols].copy()  # solo exactos

print(f"  Con_Duplicados:  {len(df_con_dup):,}")
print(f"  Deduplicados:    {len(df_dedup):,}")
print(f"  Solo_Matcheados: {len(df_matcheados):,}")

# ============================================================
# MÉTRICAS PARA EL RESUMEN
# ============================================================
max_insc_ts = pd.Timestamp.now()
for col in ['Insc_Fecha Pago', 'Fecha Pago']:
    if col in df_insc.columns:
        d = pd.to_datetime(df_insc[col], format='mixed', errors='coerce')
        d = d[d <= pd.Timestamp.now()]
        if not d.isna().all():
            max_insc_ts = d.max()
            break

df_raw['_fecha'] = pd.to_datetime(
    df_raw['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

if segmento == 'Grado_Pregrado':
    mask_v = (df_raw['_fecha'] >= '2025-09-01') & (df_raw['_fecha'] <= max_insc_ts)
    ventana_txt = f"01/09/2025 - {max_insc_ts.strftime('%d/%m/%Y')}"
else:
    mask_v = df_raw['_fecha'] <= max_insc_ts
    ventana_txt = f"Todos hasta {max_insc_ts.strftime('%d/%m/%Y')}"

df_v = df_sorted[mask_v].drop_duplicates(subset='_pk')
n_v  = len(df_v)
n_cv = len(df_v[df_v['_mc'] == 'Exacto'])
tasa = n_cv / n_v * 100 if n_v > 0 else 0

# ============================================================
# MÉTRICAS POR CAMPAÑA
# ============================================================
# Si existe la columna Campana_Lead (generada por 02_cruce_datos.py),
# calcular cuántos inscriptos matchearon desde la campaña actual vs anterior.
label_campana = 'Ingreso 2026' if segmento == 'Grado_Pregrado' else '2026'
if 'Campana_Lead' in df_raw.columns:
    matcheados_all = df_sorted[df_sorted['_mc'] == 'Exacto'].drop_duplicates(subset='_pk')
    n_camp_actual = int((matcheados_all['Campana_Lead'] == label_campana).sum())
    n_camp_anterior = int((matcheados_all['Campana_Lead'] == 'Campaña Anterior').sum())
    print(f"  Campana actual ({label_campana}): {n_camp_actual:,} | Anterior: {n_camp_anterior:,}")
else:
    n_camp_actual = 0
    n_camp_anterior = 0

lead_cols = len([c for c in export_cols if not c.startswith('Insc_')])
insc_cols  = len([c for c in export_cols if c.startswith('Insc_')])

resumen = [
    ('SEGMENTO', segmento),
    ('Fecha generacion', pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')),
    ('', ''),
    ('=== TOTALES HISTORICOS ===', ''),
    ('Total registros leads (con duplicados)', len(df_con_dup)),
    ('Personas unicas (deduplicadas)', len(df_dedup)),
    ('  - Match Exacto (DNI/Email/Telefono)', len(df_matcheados)),
    ('  - Match Fuzzy (revision pendiente)', len(df_raw[df_raw['_mc']=='Fuzzy'])),
    ('  - Sin match (solo lead)', len(df_raw[df_raw['_mc']=='Sin_Match'])),
    ('', ''),
    ('=== ATRIBUCION POR CAMPANA ===', ''),
    (f'Inscriptos campana actual ({label_campana})', n_camp_actual),
    ('Inscriptos campana anterior (match historico)', n_camp_anterior),
    ('', ''),
    ('=== MUESTRA CONVERSION (cohorte) ===', ''),
    ('Ventana de analisis', ventana_txt),
    ('Leads en ventana (dedup)', n_v),
    ('Inscriptos en ventana', n_cv),
    ('Tasa de conversion', f'{tasa:.2f}%'),
    ('', ''),
    ('=== ESTRUCTURA ARCHIVO ===', ''),
    ('Hoja Con_Duplicados', f'{len(df_con_dup):,} filas - 1 por registro de lead'),
    ('Hoja Deduplicados', f'{len(df_dedup):,} filas - 1 por persona (mejor match)'),
    ('Hoja Solo_Matcheados', f'{len(df_matcheados):,} filas - solo personas con inscripto'),
    ('Columnas totales por hoja', len(export_cols)),
    ('  - Columnas lead', lead_cols),
    ('  - Columnas inscripto (Insc_*)', insc_cols),
]

# ============================================================
# HELPER: ESCRIBIR ARCHIVO XLSX CON FORMATO (xlsxwriter)
# ============================================================
def write_data_file(file_path, sheet_name, df):
    print(f"  Escribiendo '{sheet_name}' ({len(df):,} filas) -> {os.path.basename(file_path)}")
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt_header = wb.add_format({
            'bold': True, 'font_color': 'white', 'bg_color': '#1F4E79',
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 9
        })
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
        ws = writer.sheets[sheet_name]
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, 0, len(df.columns) - 1)
        for col_idx, col_name in enumerate(df.columns):
            ws.write(0, col_idx, col_name, fmt_header)
            col_width = max(10, min(len(str(col_name)) + 4, 32))
            ws.set_column(col_idx, col_idx, col_width)
    size_mb = os.path.getsize(file_path) / 1_048_576
    print(f"    Tamano: {size_mb:.1f} MB")


# ============================================================
# ESCRIBIR ARCHIVOS EXCEL (UN ARCHIVO POR TABLA)
# ============================================================
# Archivos separados para evitar problemas de memoria con volúmenes grandes.
# xlsxwriter es más rápido que openpyxl para escritura masiva.
print(f"\nEscribiendo archivos Excel separados en: {out_dir}")

# 1. Resumen
f_resumen = os.path.join(out_dir, f"Resumen_{segmento}.xlsx")
print(f"  Escribiendo 'Resumen' -> {os.path.basename(f_resumen)}")
with pd.ExcelWriter(f_resumen, engine='xlsxwriter') as writer:
    wb = writer.book
    fmt_header  = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4E79',
                                  'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 9})
    fmt_section = wb.add_format({'bold': True, 'font_color': '#1F4E79', 'font_size': 10})
    fmt_label   = wb.add_format({'bold': True, 'font_size': 9})
    fmt_value   = wb.add_format({'font_size': 9})
    fmt_num     = wb.add_format({'font_size': 9, 'num_format': '#,##0'})
    ws_res = wb.add_worksheet('Resumen')
    ws_res.set_column('A:A', 48)
    ws_res.set_column('B:B', 45)
    ws_res.write(0, 0, 'Metrica', fmt_header)
    ws_res.write(0, 1, 'Valor', fmt_header)
    ws_res.freeze_panes(1, 0)
    for r_idx, (label, value) in enumerate(resumen, start=1):
        if str(label).startswith('==='):
            ws_res.write(r_idx, 0, label, fmt_section)
            ws_res.write(r_idx, 1, '', fmt_section)
        elif label == '':
            ws_res.write(r_idx, 0, '', fmt_value)
            ws_res.write(r_idx, 1, '', fmt_value)
        else:
            ws_res.write(r_idx, 0, label, fmt_label)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                ws_res.write_number(r_idx, 1, value, fmt_num)
            else:
                ws_res.write(r_idx, 1, str(value), fmt_value)

# 2. Con_Duplicados
write_data_file(
    os.path.join(out_dir, f"Con_Duplicados_{segmento}.xlsx"),
    'Con_Duplicados', df_con_dup
)

# 3. Deduplicados
write_data_file(
    os.path.join(out_dir, f"Deduplicados_{segmento}.xlsx"),
    'Deduplicados', df_dedup
)

# 4. Solo_Matcheados
write_data_file(
    os.path.join(out_dir, f"Solo_Matcheados_{segmento}.xlsx"),
    'Solo_Matcheados', df_matcheados
)

print(f"\n-> Archivos generados en: {out_dir}")
print(f"   Resumen_{segmento}.xlsx")
print(f"   Con_Duplicados_{segmento}.xlsx   ({len(df_con_dup):,} filas)")
print(f"   Deduplicados_{segmento}.xlsx     ({len(df_dedup):,} filas)")
print(f"   Solo_Matcheados_{segmento}.xlsx  ({len(df_matcheados):,} filas)")

# ============================================================
# DOCUMENTACIÓN MARKDOWN
# ============================================================
# Resume el proceso y los volúmenes para referencia posterior
pct_exacto = n_cv / n_v * 100 if n_v > 0 else 0
md_content = f"""# Matcheo Completo: {segmento}

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Segmento:** {segmento}
**Script:** `21_exportar_matcheo_completo.py`

## Fuentes de Datos
- Leads: `{os.path.join(db_dir, 'reporte_marketing_leads_completos.csv')}`
- Inscriptos: `{os.path.join(db_dir, 'reporte_marketing_inscriptos_origenes.csv')}`

## Totales Históricos
| Métrica | Valor |
|---|---|
| Total registros leads (con duplicados) | {len(df_con_dup):,} |
| Personas únicas (deduplicadas) | {len(df_dedup):,} |
| Match Exacto (DNI/Email/Teléfono) | {len(df_matcheados):,} |
| Match Fuzzy (revisión pendiente) | {len(df_raw[df_raw['_mc']=='Fuzzy']):,} |
| Sin match (solo lead) | {len(df_raw[df_raw['_mc']=='Sin_Match']):,} |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual ({label_campana}) | {n_camp_actual:,} |
| Inscriptos campaña anterior (match histórico) | {n_camp_anterior:,} |

## Ventana de Conversión (Cohorte)
| Métrica | Valor |
|---|---|
| Ventana de análisis | {ventana_txt} |
| Leads en ventana (dedup) | {n_v:,} |
| Inscriptos en ventana | {n_cv:,} |
| Tasa de conversión | {tasa:.2f}% |

## Archivos de Salida
| Archivo | Filas | Descripcion |
|---|---|---|
| `Resumen_{segmento}.xlsx` | — | Métricas y estadísticas |
| `Con_Duplicados_{segmento}.xlsx` | {len(df_con_dup):,} | Todos los registros de leads |
| `Deduplicados_{segmento}.xlsx` | {len(df_dedup):,} | 1 fila por persona (mejor match) |
| `Solo_Matcheados_{segmento}.xlsx` | {len(df_matcheados):,} | Solo matcheos exactos |

## Reglas de Negocio
- **Deduplicación:** prioridad Exacto > Fuzzy > Sin_Match (misma clave pk)
- **Clave pk:** DNI (sin decimal) > Correo > ID Consulta > índice
- **Ventana cohorte Grado_Pregrado:** desde 2025-09-01 (ingreso 2026)
- **Ventana cohorte Cursos/Posgrados:** todos los registros hasta hoy

## Nota Metodologica
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Para atribucion multi-canal, referirse al Informe Analitico (04_reporte_final).
- **Match:** Exacto por DNI, Email, Telefono y Celular.
"""
md_path = os.path.join(out_dir, f'Matcheo_Completo_{segmento}.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)
print(f"-> MD generado: {md_path}")
print("Proceso finalizado.")
