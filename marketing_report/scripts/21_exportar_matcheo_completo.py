"""
21_exportar_matcheo_completo.py
Exporta la tabla maestra leads-inscriptos a 4 archivos Excel separados:
  Resumen_<seg>.xlsx | Con_Duplicados_<seg>.xlsx | Deduplicados_<seg>.xlsx | Solo_Matcheados_<seg>.xlsx
Motor: xlsxwriter (rápido para grandes volúmenes)
"""
import pandas as pd
import numpy as np
import os, sys

segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
db_dir   = os.path.join(base_dir, "outputs", "Data_Base", segmento)
out_dir  = os.path.join(base_dir, "outputs", segmento, "Matcheo_Completo")
os.makedirs(out_dir, exist_ok=True)

print(f"Cargando datos para {segmento}...")
df_raw  = pd.read_csv(os.path.join(db_dir, "reporte_marketing_leads_completos.csv"), low_memory=False)
df_insc = pd.read_csv(os.path.join(db_dir, "reporte_marketing_inscriptos_origenes.csv"), low_memory=False)
print(f"  Leads raw: {len(df_raw):,}  |  Inscriptos: {len(df_insc):,}")

# ------ LIMPIEZA Y CLASIFICACIÓN ------
def classify(v):
    s = str(v)
    if 'Exacto' in s: return 'Exacto'
    if 'Fuzzy'  in s: return 'Fuzzy'
    return 'Sin_Match'

df_raw['_mc'] = df_raw['Match_Tipo'].apply(classify)

# DNI sin decimal
for col in ['DNI', 'Insc_DNI']:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.split('.').str[0].str.strip().replace('nan', '')

# Clave de deduplicación
def make_pk(row):
    for field in ['DNI', 'Correo', 'Consulta: ID Consulta']:
        val = str(row.get(field, '')).strip()
        if val and val not in ('nan', 'None', ''):
            return val
    return str(row.name)

df_raw['_pk'] = df_raw.apply(make_pk, axis=1)

# Orden de prioridad para dedup (Exacto primero)
prio = {'Exacto': 0, 'Fuzzy': 1, 'Sin_Match': 2}
df_sorted = df_raw.assign(_prio=df_raw['_mc'].map(prio)).sort_values('_prio')

# Columnas a exportar (sin helpers internos)
export_cols = [c for c in df_raw.columns if c not in ('_mc', '_pk', '_prio')]

# ------ HOJAS ------
df_con_dup    = df_raw[export_cols].copy()
df_dedup      = df_sorted.drop_duplicates(subset='_pk')[export_cols].copy()
df_matcheados = df_sorted[df_sorted['_mc'] == 'Exacto'].drop_duplicates(subset='_pk')[export_cols].copy()

print(f"  Con_Duplicados:  {len(df_con_dup):,}")
print(f"  Deduplicados:    {len(df_dedup):,}")
print(f"  Solo_Matcheados: {len(df_matcheados):,}")

# ------ MÉTRICAS PARA RESUMEN ------
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

# ------ HELPER: ESCRIBIR UN ARCHIVO XLSX DE DATOS (xlsxwriter) ------
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


# ------ ESCRIBIR EXCEL CON XLSXWRITER (UN ARCHIVO POR TABLA) ------
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
print("Proceso finalizado.")
