"""
08_fuzzy_correos.py
Búsqueda de matches fuzzy entre correos de leads no matcheados e inscriptos no matcheados.
Utiliza distancia de Levenshtein = 1 (un solo carácter de diferencia).

PROPÓSITO: Generar una lista para revisión HUMANA de potenciales correos mal escritos
que no fueron capturados por el matcheo exacto. La columna 'Validado' en el Excel
debe ser completada manualmente (SI / NO) para confirmar si el match es correcto.

Nota: Es incremental — si ya existe el archivo Excel, solo agrega pares nuevos sin pisar
las validaciones humanas previas.

SALIDA (output_dir = outputs/General/Calidad_Datos/):
  - control_manual_correos.xlsx   -> Pares candidatos (lleva columna Validado para revisión)
  - control_manual_correos.md     -> Documentación del proceso y estadísticas
"""
import pandas as pd
import os
import Levenshtein
import numpy as np
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "General", "Calidad_Datos")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")

leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")
output_excel = os.path.join(output_dir, "control_manual_correos.xlsx")

print("Cargando bases de datos para busqueda Fuzzy de Correos...")
df_leads = pd.read_csv(leads_csv, low_memory=False)
df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

# ============================================================
# FILTRADO: SOLO NO MATCHEADOS
# ============================================================
# Solo tiene sentido buscar fuzzy entre leads que NO matchearon exactamente,
# ya que si ya matchearon no necesitan revisión
def classify_mc(v):
    s = str(v)
    if 'Si' in s and 'Exacto' in s: return 'exacto'
    return 'no_match'

df_leads['_mc'] = df_leads['Match_Tipo'].apply(classify_mc)
leads_unmatched = df_leads[df_leads['_mc'] != 'exacto'].dropna(subset=['Correo']).copy()
leads_unmatched['Correo_low'] = leads_unmatched['Correo'].astype(str).str.lower().str.strip()

# Inscriptos sin match exacto: si Match_Tipo está vacío, no matcheó
df_insc['Match_Tipo'] = df_insc['Match_Tipo'].fillna('')
insc_unmatched = df_insc[~df_insc['Match_Tipo'].str.contains('Exacto')].copy()

# El correo del inscripto puede estar en diferentes columnas según la versión del CSV
col_email_insc = 'Insc_Email' if 'Insc_Email' in df_insc.columns else 'Email'
insc_unmatched = insc_unmatched.dropna(subset=[col_email_insc]).copy()
insc_unmatched['Email_low'] = insc_unmatched[col_email_insc].astype(str).str.lower().str.strip()

print(f"Buscando matches fuzzy entre {len(insc_unmatched)} inscriptos y {len(leads_unmatched)} leads no matcheados...")

# ============================================================
# MODO INCREMENTAL: CARGAR VALIDACIONES PREVIAS
# ============================================================
# Si ya existe el archivo, se cargan los pares previos para no duplicarlos ni pisar
# las validaciones humanas que ya completaron la columna "Validado"
existing_pairs = set()
df_existing = pd.DataFrame()

if os.path.exists(output_excel):
    print("Detectado archivo previo. Cargando validaciones previas para no pisarlas...")
    df_existing = pd.read_excel(output_excel)
    for _, row in df_existing.iterrows():
        l_mail = str(row.get('Lead_Correo', '')).lower().strip()
        i_mail = str(row.get('Insc_Correo', '')).lower().strip()
        if l_mail and i_mail:
            existing_pairs.add((l_mail, i_mail))
else:
    df_existing = pd.DataFrame(columns=[
        'Validado', 'Distancia', 'Lead_DNI', 'Lead_Nombre', 'Lead_Correo',
        'Insc_DNI', 'Insc_Nombre', 'Insc_Correo'
    ])

# ============================================================
# BÚSQUEDA FUZZY POR DISTANCIA LEVENSHTEIN = 1
# ============================================================
# Optimización: agrupar leads por longitud de correo para comparar solo candidatos
# de la misma longitud ± 1 (distancia 1 no puede ocurrir con diferencia > 1 en longitud)
from collections import defaultdict
leads_by_len = defaultdict(list)
for l in leads_unmatched[['DNI', 'Nombre', 'Correo', 'Correo_low']].to_dict('records'):
    leads_by_len[len(l['Correo_low'])].append(l)

nuevos_matches = []
count_new = 0
total_insc = len(insc_unmatched)

for i_idx, (idx, insc) in enumerate(insc_unmatched.iterrows(), 1):
    e_insc = insc['Email_low']
    if len(e_insc) < 5: continue    # correos muy cortos suelen ser inválidos
    if "nan" in e_insc: continue    # excluir valores nulos representados como string

    if i_idx % 500 == 0:
        print(f"  ...Procesando inscriptos: {i_idx}/{total_insc}")

    i_name = insc.get('Insc_Apellido y Nombre', insc.get('Apellido y Nombre', ''))
    i_dni = insc.get('Insc_DNI', insc.get('DNI', ''))

    # Solo comparar con leads de longitud similar (±1) para eficiencia
    L = len(e_insc)
    candidates = leads_by_len.get(L-1, []) + leads_by_len.get(L, []) + leads_by_len.get(L+1, [])

    for l in candidates:
        e_lead = l['Correo_low']
        if len(e_lead) < 5: continue

        # Saltar pares ya revisados en corridas anteriores
        if (e_lead, e_insc) in existing_pairs:
            continue

        dist = Levenshtein.distance(e_insc, e_lead)
        if dist == 1:  # solo 1 carácter de diferencia
            nuevos_matches.append({
                'Validado': '',            # columna para revisión humana: completar SI / NO
                'Distancia': dist,
                'Lead_DNI': l.get('DNI', ''),
                'Lead_Nombre': l.get('Nombre', ''),
                'Lead_Correo': l.get('Correo', ''),
                'Insc_DNI': i_dni,
                'Insc_Nombre': i_name,
                'Insc_Correo': insc.get(col_email_insc, '')
            })
            existing_pairs.add((e_lead, e_insc))
            count_new += 1

# ============================================================
# GUARDAR EXCEL ACTUALIZADO
# ============================================================
if count_new > 0:
    print(f"Se hallaron {count_new} nuevos posibles matches de correo!")
    df_nuevos = pd.DataFrame(nuevos_matches)
    df_final = pd.concat([df_existing, df_nuevos], ignore_index=True)
else:
    print("No se encontraron nuevos matches fuzzy.")
    df_final = df_existing

df_final.to_excel(output_excel, index=False)
print(f"Archivo de control guardado en: {output_excel}")
print("Puedes editar la columna 'Validado' indicando 'SI' o 'NO' para dejar constancia humana.")

# ============================================================
# DOCUMENTACIÓN MARKDOWN
# ============================================================
# Genera un resumen del proceso para referencia en el directorio Calidad_Datos/
n_validados_si  = int((df_final['Validado'].astype(str).str.upper() == 'SI').sum())  if not df_final.empty else 0
n_validados_no  = int((df_final['Validado'].astype(str).str.upper() == 'NO').sum())  if not df_final.empty else 0
n_sin_validar   = int((df_final['Validado'].astype(str).str.strip() == '').sum())    if not df_final.empty else 0

md_content = f"""# Control Manual de Correos Fuzzy

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Script:** `08_fuzzy_correos.py`

## Descripcion
Busca pares de (lead no matcheado, inscripto no matcheado) cuyos correos difieren en
exactamente 1 caracter (distancia Levenshtein = 1). El resultado es una lista para
**revision humana**: la columna `Validado` debe completarse manualmente con SI o NO.

## Estadisticas del Proceso
| Metrica | Valor |
|---|---|
| Leads sin match analizados | {len(leads_unmatched):,} |
| Inscriptos sin match analizados | {len(insc_unmatched):,} |
| Pares candidatos nuevos encontrados | {count_new:,} |
| Total acumulado de pares | {len(df_final):,} |
| Validados SI | {n_validados_si:,} |
| Validados NO | {n_validados_no:,} |
| Sin validar aun | {n_sin_validar:,} |

## Como Usar el Excel
1. Abrir `control_manual_correos.xlsx`
2. Para cada fila: comparar Lead_Nombre + Lead_Correo con Insc_Nombre + Insc_Correo
3. Si son la misma persona con error de tipeo: escribir **SI** en la columna Validado
4. Si son personas diferentes: escribir **NO** en la columna Validado
5. Guardar el archivo — la proxima corrida del script respetara estas validaciones

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `control_manual_correos.xlsx` | Pares candidatos para revision humana (incremental) |
| `control_manual_correos.md` | Este archivo de documentacion |
"""
md_path = os.path.join(output_dir, 'control_manual_correos.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)
print(f"-> MD generado: {md_path}")
