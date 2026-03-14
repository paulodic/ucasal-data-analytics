"""
02_cruce_datos.py — Script maestro de cruce Leads ↔ Inscriptos ↔ Boletas

Pipeline principal que:
  1. Lee y deduplica leads de Salesforce (por Consulta: ID Consulta)
  2. Lee y deduplica inscriptos del sistema académico
  3. Cruza leads con inscriptos: exacto (DNI→Email→Tel×6) + fuzzy email + fuzzy nombre
  4. Cruza leads sin inscripto contra boletas sin pago (mismo cruce exacto)
  5. Clasifica cada lead por campaña según fecha de consulta vs ventana del segmento
  6. Segmenta por nivel académico (Grado_Pregrado/Cursos/Posgrados) y exporta CSVs

Outputs por segmento en outputs/Data_Base/<Segmento>/:
  - reporte_marketing_leads_completos.csv      (todos los leads + columnas Insc_* y Bol_*)
  - reporte_marketing_inscriptos_origenes.csv   (inscriptos + datos del lead que matcheó)
  - reporte_marketing_boletas_sin_pago.csv      (boletas que no pagaron, para embudo)

Dependencias: pandas, rapidfuzz (o thefuzz), Levenshtein, multiprocessing
Ver DATA_CONTRACT_LEADS.md para documentación completa del contrato de datos.
"""

import pandas as pd
import glob
import os
import re
try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    RAPIDFUZZ = True
except ImportError:
    from thefuzz import fuzz, process
    RAPIDFUZZ = False
import multiprocessing as mp
from functools import partial
import Levenshtein
from collections import defaultdict

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
raw_dir = os.path.join(base_dir, "data", "1_raw")
output_dir_base = os.path.join(base_dir, "outputs")
output_dir = os.path.join(output_dir_base, "Data_Base")
os.makedirs(output_dir, exist_ok=True)

leads_dir = os.path.join(raw_dir, "leads_salesforce")
inscriptos_dir = os.path.join(raw_dir, "inscriptos")

# ==========================================
# FUNCIONES DE LIMPIEZA
# ==========================================
def clean_dni(val):
    if pd.isna(val) or val == '':
        return pd.NA
    s = str(val).split('.')[0].strip().replace('.', '').replace('-', '').replace(' ', '')
    return s if s else pd.NA

def clean_email(val):
    if pd.isna(val) or val == '':
        return pd.NA
    s = str(val).strip().lower()
    return s if s else pd.NA

def clean_phone(val):
    """
    Normaliza teléfonos argentinos a un formato comparable de ~10 dígitos.
    Maneja: prefijos duplicados (54-549...), código de área duplicado (2901-2901...),
    prefijo internacional (54/549), cero inicial, '15' móvil intercalado,
    y trunca a últimos 10 dígitos si excede.
    """
    if pd.isna(val) or val == '':
        return pd.NA

    s = str(val).split('.')[0].strip()

    # Manejar posibles codigos duplos separados por guion:
    # e.g. "54 - 549388...", "2901 - 2901407680", "3444 - 3444423965"
    if '-' in s:
        parts = [p.strip() for p in s.split('-')]
        if len(parts) >= 2:
            p0 = re.sub(r'\D', '', parts[0])
            p1 = re.sub(r'\D', '', "".join(parts[1:]))
            
            # Caso 1: Duplicado exacto (ej. "2901 - 2901...", "3444 - 3444...")
            if p0 and p1.startswith(p0):
                s = p1 # Retenemos solo la segunda parte que contiene el resto del numero
            # Caso 2: Duplicado con country code inflado (ej. "54 - 5493...")
            elif p0 == '54' and p1.startswith('549'):
                s = p1[3:] # Removemos el 549 redundante
            elif p0 == '54' and p1.startswith('54'):
                s = p1[2:]
            else:
                s = p0 + p1
    
    s = re.sub(r'\D', '', s)
    
    if not s:
        return pd.NA
        
    if s.startswith('549'):
        s = s[3:]
    elif s.startswith('54'):
        s = s[2:]
        
    if s.startswith('0'):
        s = s[1:]
        
    s = re.sub(r'(^\d{2,4})15(\d{6,8}$)', r'\1\2', s)

    if len(s) > 10:
        s = s[-10:]

    # Mínimo 7 dígitos para evitar falsos positivos con prefijos sueltos
    # (ej: "11", "387", "388" que matchean accidentalmente)
    if len(s) < 7:
        return pd.NA

    return s if s else pd.NA

def clean_name(val):
    if pd.isna(val):
        return ""
    return str(val).strip().lower()

# ==========================================
# ESTANDARIZACIÓN DE COLUMNAS DE LEADS
# ==========================================
def standardize_leads_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza el DataFrame de leads al esquema canónico del pipeline.

    Problema resuelto: el "Informe General" de Salesforce exporta la columna
    de nombre como 'Nombre' (sin 'Candidato'), mientras que los archivos
    mensuales tienen ambas. Esta función garantiza que SIEMPRE existan
    'Candidato' y 'Nombre' antes del cruce, evitando crashes en el dropna.

    - Si falta 'Candidato', se crea como copia de 'Nombre'.
    - Si falta 'Nombre', se crea como copia de 'Candidato'.
    - Todas las columnas nuevas (Gestionados, Application, etc.) se preservan sin cambios.

    Ver DATA_CONTRACT_LEADS.md sección 15 para mapeo completo del nuevo formato.
    """
    df = df.copy()
    if 'Candidato' not in df.columns and 'Nombre' in df.columns:
        df['Candidato'] = df['Nombre']
    if 'Nombre' not in df.columns and 'Candidato' in df.columns:
        df['Nombre'] = df['Candidato']
    return df

# ==========================================
# MULTIPROCESSING WORKER PARA FUZZY MATCH
# ==========================================
def _fuzzy_worker(insc_tuple, choices_dict):
    """
    Worker para procesar un solo inscripto contra el diccionario de leads en paralelo.
    Usa rapidfuzz si está disponible (10-100x más rápido que thefuzz).
    insc_tuple es (insc_id, insc_name)
    """
    insc_id, insc_name = insc_tuple
    if not insc_name:
        return None

    if RAPIDFUZZ:
        result = rf_process.extractOne(
            insc_name, choices_dict,
            scorer=rf_fuzz.WRatio,
            score_cutoff=95
        )
        if result:
            _, score, best_match_key = result
            return (insc_id, best_match_key, score)
    else:
        best_match = process.extractOne(insc_name, choices_dict)
        if best_match:
            if len(best_match) == 3:
                _, score, best_match_key = best_match
            elif len(best_match) == 2:
                match_str, score = best_match
                best_match_key = None
                for k, v in choices_dict.items():
                     if v == match_str:
                          best_match_key = k
                          break
            else:
                return None
            if best_match_key and score >= 95:
                return (insc_id, best_match_key, score)
    return None

def cruce_exacto(df_leads, df_target, prefix, lead_id='Lead_Tmp_ID', target_id=None, match_col='Match_Tipo'):
    """
    Cruce exacto genérico Lead ↔ Target (Inscripto o Boleta).
    Matching secuencial: DNI → Email → Tel×4 combinaciones.
    Cada paso excluye IDs ya matcheados.

    Args:
        df_leads: DataFrame de leads con columnas *_match
        df_target: DataFrame target con columnas {prefix}_*_match
        prefix: 'Insc' o 'Bol'
        lead_id: columna ID en leads
        target_id: columna ID en target
        match_col: nombre de la columna donde escribir el tipo de match

    Returns: (df_matched, matched_lead_ids, matched_target_ids)
    """
    if target_id is None:
        target_id = f'{prefix}_Tmp_ID'

    steps = [
        ('DNI_match',      f'{prefix}_DNI_match',   'Exacto (DNI)'),
        ('Email_match',    f'{prefix}_Email_match',  'Exacto (Email)'),
        ('Phone_match',    f'{prefix}_Phone_match',  'Exacto (Teléfono)'),
        ('Phone_match',    f'{prefix}_Cel_match',    'Exacto (Celular)'),
        ('Cel_lead_match', f'{prefix}_Phone_match',  'Exacto (Celular)'),
        ('Cel_lead_match', f'{prefix}_Cel_match',    'Exacto (Celular)'),
    ]

    matched_leads = set()
    matched_targets = set()
    all_merges = []

    for left_on, right_on, label in steps:
        if left_on not in df_leads.columns or right_on not in df_target.columns:
            continue
        rem_l = df_leads[~df_leads[lead_id].isin(matched_leads)]
        rem_t = df_target[~df_target[target_id].isin(matched_targets)]
        l = rem_l[rem_l[left_on].notna()]
        t = rem_t[rem_t[right_on].notna()]
        if l.empty or t.empty:
            continue
        m = pd.merge(l, t, left_on=left_on, right_on=right_on, how='inner')
        m[match_col] = label
        matched_leads.update(m[lead_id])
        matched_targets.update(m[target_id])
        all_merges.append(m)

    df_matched = pd.concat(all_merges, ignore_index=True) if all_merges else pd.DataFrame()
    return df_matched, matched_leads, matched_targets


if __name__ == '__main__':
    # ==========================================
    # 1. LECTURA Y DEDUPLICACIÓN DE DATOS
    # ==========================================
    print("Leyendo archivos...")

    leads_files = glob.glob(os.path.join(leads_dir, "*.xlsx")) + \
                  glob.glob(os.path.join(leads_dir, "*.xls"))
    df_leads_list = []
    for f in leads_files:
        try:
            engine = 'xlrd' if f.endswith('.xls') else None
            df = pd.read_excel(f, engine=engine)
            df = standardize_leads_columns(df)  # garantiza 'Candidato' y 'Nombre'
            df_leads_list.append(df)
            print(f"  Cargado: {os.path.basename(f)} ({len(df)} filas)")
        except Exception as e:
            print(f"Error cargando {f}: {e}")
    df_leads = pd.concat(df_leads_list, ignore_index=True) if df_leads_list else pd.DataFrame()

    if not df_leads.empty:
        initial_len = len(df_leads)
        if 'Consulta: ID Consulta' in df_leads.columns:
            # Dedup inteligente por clave única de Salesforce.
            # groupby().first() toma el primer valor no-NaN por columna en cada grupo,
            # complementando datos entre archivos con distinto schema (ej: mensual vs Informe General).
            df_leads = (
                df_leads
                .groupby('Consulta: ID Consulta', sort=False)
                .first()
                .reset_index()
            )
        else:
            df_leads = df_leads.drop_duplicates()
        print(f"Leads después de dedup/complementación: {len(df_leads)} (removidos/fusionados: {initial_len - len(df_leads)})")

    inscriptos_files = glob.glob(os.path.join(inscriptos_dir, "*.xlsx")) + \
                       glob.glob(os.path.join(inscriptos_dir, "*.xls"))
    df_inscriptos_list = []
    for f in inscriptos_files:
        try:
            engine = 'xlrd' if f.endswith('.xls') else None
            df = pd.read_excel(f, engine=engine)
            df_inscriptos_list.append(df)
        except Exception as e:
            print(f"Error cargando {f}: {e}")
    df_inscriptos = pd.concat(df_inscriptos_list, ignore_index=True) if df_inscriptos_list else pd.DataFrame()

    if not df_inscriptos.empty:
        initial_len = len(df_inscriptos)
        df_inscriptos = df_inscriptos.drop_duplicates()
        print(f"Inscriptos duplicados removidos: {initial_len - len(df_inscriptos)}")

    if df_leads.empty or df_inscriptos.empty:
        print("Faltan datos de leads o de inscriptos.")
        exit()

    print(f"Leads únicos totales: {len(df_leads)}. Inscriptos únicos totales: {len(df_inscriptos)}.")

    # Limpieza Básica
    df_leads = df_leads.dropna(subset=['Candidato', 'DNI', 'Telefono'], how='all')
    df_inscriptos = df_inscriptos.dropna(subset=['Apellido y Nombre', 'DNI', 'Telefono'], how='all')

    print(f"Leads únicos totales: {len(df_leads)}. Inscriptos únicos totales: {len(df_inscriptos)}.")

    # -------------------------------------------------------------
    # SEPARACIÓN CONFIRMADA DE APELLIDO Y NOMBRE (Base Contable)
    # Tras auditoría, el 100% de la base inscriptos usa formato "Apellido, Nombres"
    # Separamos en dos columnas puras ANTES de añadir el prefijo general "Insc_"
    # -------------------------------------------------------------
    if 'Apellido y Nombre' in df_inscriptos.columns:
        sep_df = df_inscriptos['Apellido y Nombre'].str.split(',', n=1, expand=True)
        if len(sep_df.columns) == 2:
            df_inscriptos['Apellido'] = sep_df[0].str.strip()
            df_inscriptos['Nombres'] = sep_df[1].str.strip()
        else:
            # Fallback en caso extremadamente raro de error en split
            df_inscriptos['Apellido'] = df_inscriptos['Apellido y Nombre']
            df_inscriptos['Nombres'] = ''
    # -------------------------------------------------------------

    # ==========================================
    # 2. LIMPIEZA DE CLAVES
    # ==========================================
    print("Limpiando claves de cruce...")

    # Leads: generar claves de matching normalizadas
    # Nota: los leads tienen 'Correo' (no 'Email') y pueden tener 'Celular' (Informe General)
    df_leads['DNI_match'] = df_leads.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
    df_leads['Email_match'] = df_leads.get('Correo', pd.Series(dtype='object')).apply(clean_email)
    df_leads['Phone_match']   = df_leads.get('Telefono', pd.Series(dtype='object')).apply(clean_phone)
    df_leads['Cel_lead_match'] = df_leads.get('Celular', pd.Series(dtype='object')).apply(clean_phone)
    df_leads['Nombre_match']  = df_leads.get('Nombre', pd.Series(dtype='object')).apply(clean_name)

    # IDs temporales para tracking durante el cruce (se eliminan al final)
    df_inscriptos['Inscripto_Tmp_ID'] = df_inscriptos.index.astype(str)
    df_leads['Lead_Tmp_ID'] = df_leads.index.astype(str)

    # Inscriptos: generar claves de matching normalizadas
    # Nota: inscriptos tienen 'Email' (no 'Correo'), 'Telefono' y 'Celular'
    df_inscriptos['DNI_match'] = df_inscriptos.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
    df_inscriptos['Email_match'] = df_inscriptos.get('Email', pd.Series(dtype='object')).apply(clean_email)
    df_inscriptos['Phone_match'] = df_inscriptos.get('Telefono', pd.Series(dtype='object')).apply(clean_phone)
    df_inscriptos['Cel_match'] = df_inscriptos.get('Celular', pd.Series(dtype='object')).apply(clean_phone)
    df_inscriptos['Nombre_match'] = df_inscriptos.get('Apellido y Nombre', pd.Series(dtype='object')).apply(clean_name)

    # Renombrar columnas de inscriptos con prefijo Insc_ para evitar colisiones en el merge
    # (excepto Inscripto_Tmp_ID que se usa como clave de tracking)
    rename_dict = {col: f"Insc_{col}" for col in df_inscriptos.columns if col not in ['Inscripto_Tmp_ID']}
    df_inscriptos_renamed = df_inscriptos.rename(columns=rename_dict)

    # ==========================================
    # 3. CRUCE EXACTO LEAD ↔ INSCRIPTO
    # ==========================================
    # Secuencia de matching (en orden de prioridad, cada paso excluye ya matcheados):
    #   1. DNI lead vs DNI inscripto                    → Exacto (DNI)
    #   2. Email lead vs Email inscripto                → Exacto (Email)
    #   3. Telefono lead vs Telefono inscripto          → Exacto (Teléfono)
    #   4. Telefono lead vs Celular inscripto           → Exacto (Celular)
    #   5. Celular lead vs Telefono inscripto           → Exacto (Celular)
    #   6. Celular lead vs Celular inscripto            → Exacto (Celular)
    print("Realizando cruce exacto de datos (DNI, Email, Teléfono)...")
    df_matched_exact, matched_leads_ids, matched_insc_ids = cruce_exacto(
        df_leads, df_inscriptos_renamed, 'Insc', target_id='Inscripto_Tmp_ID')

    n_dni = len(df_matched_exact[df_matched_exact['Match_Tipo'] == 'Exacto (DNI)']) if not df_matched_exact.empty else 0
    n_email = len(df_matched_exact[df_matched_exact['Match_Tipo'] == 'Exacto (Email)']) if not df_matched_exact.empty else 0
    n_tel = len(df_matched_exact[df_matched_exact['Match_Tipo'].isin(['Exacto (Teléfono)', 'Exacto (Celular)'])]) if not df_matched_exact.empty else 0
    print(f"  DNI: {n_dni} | Email: {n_email} | Tel/Cel: {n_tel} | Total exactos: {len(df_matched_exact)}")

    # ==========================================
    # 3.5 LÓGICA DE CRUCE FUZZY EMAIL (OPTIMIZADO CON INDICES DE LONGITUD)
    # ==========================================
    print("Realizando búsqueda Fuzzy de 1-2 caracteres de diferencia en Emails (optimizado)...")
    df_unmatched_leads = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)].copy()
    df_unmatched_inscriptos = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)].copy()

    leads_email_rem = df_unmatched_leads[df_unmatched_leads['Email_match'].notna()]
    insc_email_rem = df_unmatched_inscriptos[df_unmatched_inscriptos['Insc_Email_match'].notna()]

    # Indexar leads por longitud de email para evitar O(n×m) --- clave del fix de velocidad
    leads_by_len_email = defaultdict(list)
    for _, l_row in leads_email_rem.iterrows():
        e = str(l_row['Email_match'])
        if len(e) >= 5 and 'nan' not in e:
            leads_by_len_email[len(e)].append(l_row)

    email_fuzzy_matches = []
    total_insc_email = len(insc_email_rem)

    for i_idx, (_, i_row) in enumerate(insc_email_rem.iterrows(), 1):
        insc_em = str(i_row['Insc_Email_match'])
        insc_id = i_row['Inscripto_Tmp_ID']

        if i_idx % 200 == 0:
            print(f"  ...email fuzzy: {i_idx}/{total_insc_email}")

        if insc_id in matched_insc_ids:
            continue
        if len(insc_em) < 5 or 'nan' in insc_em:
            continue

        L = len(insc_em)
        # Solo comparar leads con longitud similar (±2 caracteres)
        candidates = (leads_by_len_email.get(L-2, []) +
                      leads_by_len_email.get(L-1, []) +
                      leads_by_len_email.get(L,   []) +
                      leads_by_len_email.get(L+1, []) +
                      leads_by_len_email.get(L+2, []))

        for l_row in candidates:
            lead_id = l_row['Lead_Tmp_ID']
            if lead_id in matched_leads_ids:
                continue
            dist = Levenshtein.distance(insc_em, str(l_row['Email_match']))
            if 0 < dist <= 2:
                matched_leads_ids.add(lead_id)
                matched_insc_ids.add(insc_id)
                combined = {**l_row.to_dict(), **i_row.to_dict()}
                combined['Match_Tipo'] = f'Posible Match Fuzzy Email (Dist {dist})'
                email_fuzzy_matches.append(combined)
                break

    df_fuzzy_email = pd.DataFrame(email_fuzzy_matches) if email_fuzzy_matches else pd.DataFrame()
    print(f"-> Se encontraron {len(df_fuzzy_email)} coincidencias fuzzy por error en email.")

    # ==========================================
    # 4. BÚSQUEDA FUZZY (MULTITHREADING)
    # ==========================================
    print("Realizando búsqueda Fuzzy con Multiprocesamiento para acelerar...")
    df_unmatched_leads = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)].copy()
    df_unmatched_inscriptos = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)].copy()

    inscriptos_names = dict(zip(df_unmatched_inscriptos['Inscripto_Tmp_ID'], df_unmatched_inscriptos['Insc_Nombre_match']))
    leads_names = dict(zip(df_unmatched_leads['Lead_Tmp_ID'], df_unmatched_leads['Nombre_match']))

    choices = {k: v for k, v in leads_names.items() if v}
    total_unmatched_insc = len(inscriptos_names)
    print(f"Buscando {total_unmatched_insc} inscriptos sin match contra los leads restantes ({len(choices)}).")

    # Ejecutar pool de workers (usando CPUs disponibles)
    num_cores = mp.cpu_count()
    print(f"-> Utilizando {num_cores} núcleos de tu procesador AMD.")
    
    fuzzy_results = []
    if choices and inscriptos_names:
        # Preparamos los items a procesar
        items_to_process = list(inscriptos_names.items())
        
        # Ojo: la búsqueda en paralelo puede hacer que 2 inscriptos matcheen el mismo lead.
        # No sucede con frecuencia extrema y es un match fuzzy para revisión humana, 
        # pero para optimizarlo se permite este escenario en paralelo y luego se limpian duplicados exactos.
        worker_func = partial(_fuzzy_worker, choices_dict=choices)
        
        with mp.Pool(num_cores) as pool:
            for i, result in enumerate(pool.imap_unordered(worker_func, items_to_process, chunksize=50)):
                if result:
                    fuzzy_results.append(result)
                
                if (i+1) % 500 == 0:
                    print(f"  ...Fuzzy Progress: {i+1}/{total_unmatched_insc}")
                    
    # Reconstruir dataframe a base de los resultados procesados en paralelo
    fuzzy_matches_rows = []
    used_fuzzy_leads = set() # Track para evitar que el mismo lead se asigne 2 veces en la foto final
    
    # Ordenar por score descendente para que los mejores matches (ej. 100) reclamen el lead primero
    fuzzy_results.sort(key=lambda x: x[2], reverse=True)
    
    for insc_id, lead_id, score in fuzzy_results:
         if lead_id not in used_fuzzy_leads:
             used_fuzzy_leads.add(lead_id)
             lead_row = df_unmatched_leads[df_unmatched_leads['Lead_Tmp_ID'] == lead_id].iloc[0]
             insc_row = df_unmatched_inscriptos[df_unmatched_inscriptos['Inscripto_Tmp_ID'] == insc_id].iloc[0]
             
             combined = {**lead_row.to_dict(), **insc_row.to_dict()}
             combined['Match_Tipo'] = f'Posible Match Fuzzy (Score: {score})'
             fuzzy_matches_rows.append(combined)

             matched_leads_ids.add(lead_id)
             matched_insc_ids.add(insc_id)

    df_fuzzy = pd.DataFrame(fuzzy_matches_rows) if fuzzy_matches_rows else pd.DataFrame()
    print(f"-> Se encontraron {len(df_fuzzy)} coincidencias fuzzy.")

    # ==========================================
    # 5. CONSOLIDACIÓN FINAL
    # ==========================================
    # Se arman dos reportes:
    #   a) df_final_leads: TODOS los leads (matcheados + solos) con columnas Insc_* si matchearon
    #   b) df_final_inscriptos: TODOS los inscriptos (matcheados + solos) con datos del lead si matchearon
    print("Consolidando resultados...")

    # Juntar exactos + fuzzy
    frames_matched = [df_matched_exact]
    if not df_fuzzy_email.empty:
        frames_matched.append(df_fuzzy_email)
    if not df_fuzzy.empty:
        frames_matched.append(df_fuzzy)

    df_all_matched = pd.concat(frames_matched, ignore_index=True) if frames_matched else pd.DataFrame()
    if not df_all_matched.empty:
        df_all_matched = df_all_matched.drop_duplicates(subset=['Lead_Tmp_ID', 'Inscripto_Tmp_ID'])

    # Leads sobrantes totales (después de fuzzy)
    df_final_unmatched_leads = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)].copy()
    df_final_unmatched_leads['Match_Tipo'] = 'No (Solo Lead)'

    # Reporte Leads Completos (Exactos + Fuzzy + Solos)
    df_final_leads = pd.concat([df_all_matched, df_final_unmatched_leads], ignore_index=True)

    # Inscriptos sobrantes totales (después de fuzzy)
    df_final_unmatched_inscriptos = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)].copy()
    df_final_unmatched_inscriptos['Match_Tipo'] = 'No (Solo Inscripto Directo)'

    # Reporte Inscriptos y sus orígenes (Exactos + Fuzzy + Inscriptos Solos)
    df_final_inscriptos = pd.concat([df_all_matched, df_final_unmatched_inscriptos], ignore_index=True)
    df_final_inscriptos = df_final_inscriptos.drop_duplicates(subset=['Inscripto_Tmp_ID'])

    # ==========================================
    # 5b. CRUCE LEADS ↔ BOLETAS (PREINSCRIPTOS SIN PAGO)
    # ==========================================
    # Las boletas son el paso intermedio: Lead → Boleta → Inscripto.
    # Solo se cruzan contra leads SIN inscripto (Match_Tipo == 'No (Solo Lead)').
    # Boletas cuyo DNI ya aparece en inscriptos se excluyen (ya pagaron).
    # El cruce usa la misma función cruce_exacto() con prefijo 'Bol_'.
    # Resultado: columnas Bol_* se agregan al df_final_leads vía merge.
    boletas_dir = os.path.join(raw_dir, "boletas")
    boletas_files = glob.glob(os.path.join(boletas_dir, "*.xlsx")) + \
                    glob.glob(os.path.join(boletas_dir, "*.xls"))

    df_final_boletas = pd.DataFrame()  # para exportación

    if boletas_files:
        print("\n--- Procesando Boletas (preinscriptos sin pago) ---")
        df_boletas_list = []
        for f in boletas_files:
            try:
                engine = 'xlrd' if f.endswith('.xls') else None
                df = pd.read_excel(f, engine=engine)
                df_boletas_list.append(df)
                print(f"  Cargado: {os.path.basename(f)} ({len(df)} filas)")
            except Exception as e:
                print(f"Error cargando {f}: {e}")

        df_boletas = pd.concat(df_boletas_list, ignore_index=True) if df_boletas_list else pd.DataFrame()

        if not df_boletas.empty:
            # Dedup por Nro Transac
            initial_len = len(df_boletas)
            if 'Nro Transac' in df_boletas.columns:
                df_boletas = df_boletas.drop_duplicates(subset=['Nro Transac'])
            else:
                df_boletas = df_boletas.drop_duplicates()
            print(f"Boletas después de dedup: {len(df_boletas)} (removidas: {initial_len - len(df_boletas)})")

            # Separar Apellido y Nombre (mismo formato que inscriptos)
            if 'Apellido y Nombre' in df_boletas.columns:
                sep = df_boletas['Apellido y Nombre'].str.split(',', n=1, expand=True)
                if len(sep.columns) == 2:
                    df_boletas['Apellido'] = sep[0].str.strip()
                    df_boletas['Nombres'] = sep[1].str.strip()
                else:
                    df_boletas['Apellido'] = df_boletas['Apellido y Nombre']
                    df_boletas['Nombres'] = ''

            # Limpiar claves de cruce (mismas funciones que inscriptos)
            df_boletas['DNI_match'] = df_boletas.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
            df_boletas['Email_match'] = df_boletas.get('Email', pd.Series(dtype='object')).apply(clean_email)
            df_boletas['Phone_match'] = df_boletas.get('Telefono', pd.Series(dtype='object')).apply(clean_phone)
            df_boletas['Cel_match'] = df_boletas.get('Celular', pd.Series(dtype='object')).apply(clean_phone)
            df_boletas['Nombre_match'] = df_boletas.get('Apellido y Nombre', pd.Series(dtype='object')).apply(clean_name)
            df_boletas['Boleta_Tmp_ID'] = df_boletas.index.astype(str)

            # Excluir boletas de personas que YA son inscriptos (ya pagaron)
            inscripto_dnis = set(df_inscriptos['DNI_match'].dropna())
            mask_ya_pago = df_boletas['DNI_match'].isin(inscripto_dnis)
            n_ya_pago = int(mask_ya_pago.sum())
            df_boletas_sin_pago = df_boletas[~mask_ya_pago].copy()
            print(f"Boletas excluidas (ya pagaron): {n_ya_pago} | Boletas sin pago: {len(df_boletas_sin_pago)}")

            # Renombrar con prefijo Bol_
            rename_bol = {col: f"Bol_{col}" for col in df_boletas_sin_pago.columns
                          if col not in ['Boleta_Tmp_ID', 'DNI_match', 'Email_match',
                                         'Phone_match', 'Cel_match', 'Nombre_match']}
            df_boletas_renamed = df_boletas_sin_pago.rename(columns=rename_bol)
            # Agregar prefijo a las columnas _match del target
            df_boletas_renamed = df_boletas_renamed.rename(columns={
                'DNI_match': 'Bol_DNI_match', 'Email_match': 'Bol_Email_match',
                'Phone_match': 'Bol_Phone_match', 'Cel_match': 'Bol_Cel_match',
                'Nombre_match': 'Bol_Nombre_match'})

            # Cruzar leads no matcheados contra boletas (misma función de cruce exacto)
            df_leads_sin_match = df_final_leads[df_final_leads['Match_Tipo'] == 'No (Solo Lead)'].copy()
            print(f"Cruzando {len(df_leads_sin_match)} leads sin inscripto contra {len(df_boletas_renamed)} boletas...")

            df_boleta_matched, boleta_lead_ids, _ = cruce_exacto(
                df_leads_sin_match, df_boletas_renamed, 'Bol',
                target_id='Boleta_Tmp_ID', match_col='Bol_Match_Tipo')

            if not df_boleta_matched.empty:
                df_boleta_matched = df_boleta_matched.drop_duplicates(subset=['Lead_Tmp_ID'])
                # Seleccionar columnas Bol_ para merge al df_final_leads
                bol_data_cols = [c for c in df_boleta_matched.columns if c.startswith('Bol_')]
                bol_info = df_boleta_matched[['Lead_Tmp_ID'] + bol_data_cols].copy()
                df_final_leads = df_final_leads.merge(bol_info, on='Lead_Tmp_ID', how='left')
                n_bol_dni = len(df_boleta_matched[df_boleta_matched['Bol_Match_Tipo'] == 'Exacto (DNI)'])
                n_bol_email = len(df_boleta_matched[df_boleta_matched['Bol_Match_Tipo'] == 'Exacto (Email)'])
                n_bol_tel = len(df_boleta_matched[df_boleta_matched['Bol_Match_Tipo'].isin(['Exacto (Teléfono)', 'Exacto (Celular)'])])
                print(f"  Boleta matches: DNI={n_bol_dni} | Email={n_bol_email} | Tel/Cel={n_bol_tel} | Total={len(df_boleta_matched)}")
            else:
                print("  No se encontraron matches con boletas.")

            # Preparar df de boletas para exportación por segmento
            df_final_boletas = df_boletas_sin_pago.copy()
            # Limpiar columnas internas de match
            bol_match_cols = ['DNI_match', 'Email_match', 'Phone_match', 'Cel_match', 'Nombre_match', 'Boleta_Tmp_ID']
            df_final_boletas.drop(columns=[c for c in bol_match_cols if c in df_final_boletas.columns], inplace=True, errors='ignore')
    else:
        print("\nNo se encontraron archivos de boletas en data/1_raw/boletas/")

    # Limpieza de columnas internas de matching (no se exportan al CSV final)
    cols_to_drop = [
        'DNI_match', 'Email_match', 'Phone_match', 'Cel_lead_match', 'Nombre_match', 'Lead_Tmp_ID', 'Inscripto_Tmp_ID',
        'Insc_DNI_match', 'Insc_Email_match', 'Insc_Phone_match', 'Insc_Cel_match', 'Insc_Nombre_match',
        'Bol_DNI_match', 'Bol_Email_match', 'Bol_Phone_match', 'Bol_Cel_match', 'Bol_Nombre_match', 'Boleta_Tmp_ID'
    ]

    df_final_leads.drop(columns=[c for c in cols_to_drop if c in df_final_leads.columns], inplace=True, errors='ignore')
    df_final_inscriptos.drop(columns=[c for c in cols_to_drop if c in df_final_inscriptos.columns], inplace=True, errors='ignore')

    # ==========================================
    # 6. CLASIFICACIÓN POR CAMPAÑA (FECHA DE CONSULTA)
    # ==========================================
    # Cada lead se clasifica según si su fecha de consulta cae dentro de la
    # ventana de la campaña actual o corresponde a una campaña anterior.
    # La ventana depende del segmento académico:
    #   - Grado_Pregrado: desde 2025-09-01 (Cohorte Ingreso 2026)
    #   - Cursos/Posgrados: desde 2026-01-01 (Año Calendario 2026)
    # Esta columna permite a los informes downstream separar inscriptos
    # que convirtieron desde la campaña actual vs campañas anteriores.

    PERIODO_INICIO_CAMPANA = {
        'Grado_Pregrado': pd.Timestamp('2025-09-01'),
        'Cursos':         pd.Timestamp('2026-01-01'),
        'Posgrados':      pd.Timestamp('2026-01-01'),
        'Desconocido':    pd.Timestamp('2025-09-01'),  # fallback conservador
    }

    CAMPANA_LABEL = {
        'Grado_Pregrado': 'Ingreso 2026',
        'Cursos':         '2026',
        'Posgrados':      '2026',
        'Desconocido':    'Ingreso 2026',
    }

    # Parsear fecha de consulta una sola vez (formato D/M/YYYY)
    df_final_leads['_fecha_consulta'] = pd.to_datetime(
        df_final_leads['Consulta: Fecha de creación'],
        format='mixed', dayfirst=True, errors='coerce')

    # ==========================================
    # 7. SEGMENTACIÓN Y EXPORTACIÓN POR NIVEL ACADÉMICO
    # ==========================================
    print("Segmentando y exportando informes a CSV según Nivel Académico...")

    # Códigos de carrera que son "Cursos de Ingreso" a carreras de grado
    # → deben reportar en Grado_Pregrado, no en Cursos
    CODCAR_INGRESO_GRADO = {1169, 1200, 1201, 1202, 1203, 1204}

    # Función para estandarizar la clasificación
    def segmentar_tipcar(tipcar_val, codcar_val=None):
        # Si el código de carrera es de curso de ingreso a grado, reclasificar
        if codcar_val is not None:
            try:
                if int(float(codcar_val)) in CODCAR_INGRESO_GRADO:
                    return 'Grado_Pregrado'
            except (ValueError, TypeError):
                pass
        val = str(tipcar_val).lower()
        if 'curso' in val:
            return 'Cursos'
        elif 'postgrado' in val or 'maestría' in val or 'maestria' in val or 'posgrado' in val:
            return 'Posgrados'
        elif 'grado' in val or 'pregrado' in val:
            return 'Grado_Pregrado'
        else:
            return 'Desconocido'

    # Clasificar inscriptos (usan Insc_Tipcar + Insc_Cod. Carrera)
    df_final_inscriptos['Segmento_Acad'] = df_final_inscriptos.apply(
        lambda r: segmentar_tipcar(r.get('Insc_Tipcar', ''), r.get('Insc_Cod. Carrera')), axis=1)

    # Clasificar leads: si matchearon con inscripto, heredan Insc_Tipcar para
    # consistencia exacta con el segmento del inscripto. Si no matchearon,
    # usan 'Tipo de Carrera' del CRM (puede tener nomenclatura diferente).
    def get_lead_segment(row):
        insc_tip = str(row.get('Insc_Tipcar', 'nan'))
        if insc_tip != 'nan' and insc_tip.strip() != '' and insc_tip != 'None':
             return segmentar_tipcar(insc_tip, row.get('Insc_Cod. Carrera'))

        local_tip = str(row.get('Tipo de Carrera', 'nan'))
        return segmentar_tipcar(local_tip, row.get('Código Carrera'))

    df_final_leads['Segmento_Acad'] = df_final_leads.apply(get_lead_segment, axis=1)

    # Clasificar boletas por segmento (usan Tipcar + Cod. Carrera)
    if not df_final_boletas.empty:
        df_final_boletas['Segmento_Acad'] = df_final_boletas.apply(
            lambda r: segmentar_tipcar(r.get('Tipcar', ''), r.get('Cod. Carrera')), axis=1)

    # Exportar cada grupo a su propio directorio
    for segmento in ['Grado_Pregrado', 'Cursos', 'Posgrados', 'Desconocido']:
         # Crear subcarpeta para la DB de ese segmento
         segment_dir = os.path.join(output_dir, segmento)
         os.makedirs(segment_dir, exist_ok=True)
         
         sub_inscriptos = df_final_inscriptos[df_final_inscriptos['Segmento_Acad'] == segmento]
         sub_leads = df_final_leads[df_final_leads['Segmento_Acad'] == segmento]
         
         # Si el segmento es "Desconocido" y está vacío, lo salteamos
         if segmento == 'Desconocido' and sub_inscriptos.empty and sub_leads.empty:
             continue

         # Clasificar cada lead según la campaña de su fecha de consulta
         inicio = PERIODO_INICIO_CAMPANA[segmento]
         label_actual = CAMPANA_LABEL[segmento]
         sub_leads = sub_leads.copy()
         sub_leads['Campana_Lead'] = sub_leads['_fecha_consulta'].apply(
             lambda d: label_actual if pd.notna(d) and d >= inicio else 'Campaña Anterior'
         )

         # Estadísticas de campaña para este segmento
         n_actual = int((sub_leads['Campana_Lead'] == label_actual).sum())
         n_anterior = int((sub_leads['Campana_Lead'] == 'Campaña Anterior').sum())
         # Contar inscriptos matcheados por campaña
         matcheados = sub_leads[sub_leads['Match_Tipo'].str.contains('Exacto', na=False)]
         n_insc_actual = int((matcheados['Campana_Lead'] == label_actual).sum())
         n_insc_anterior = int((matcheados['Campana_Lead'] == 'Campaña Anterior').sum())
         print(f"  [{segmento}] Campaña: {label_actual}={n_actual:,} | Anterior={n_anterior:,} | "
               f"Inscriptos matcheados: {label_actual}={n_insc_actual:,}, Anterior={n_insc_anterior:,}")

         out_insc = os.path.join(segment_dir, "reporte_marketing_inscriptos_origenes.csv")
         out_leads = os.path.join(segment_dir, "reporte_marketing_leads_completos.csv")

         sub_inscriptos.drop(columns=['Segmento_Acad']).to_csv(out_insc, index=False)
         sub_leads.drop(columns=['Segmento_Acad', '_fecha_consulta']).to_csv(out_leads, index=False)

         # Exportar boletas sin pago (si existen)
         msg_boletas = ""
         if not df_final_boletas.empty:
             sub_boletas = df_final_boletas[df_final_boletas['Segmento_Acad'] == segmento]
             if not sub_boletas.empty:
                 out_bol = os.path.join(segment_dir, "reporte_marketing_boletas_sin_pago.csv")
                 sub_boletas.drop(columns=['Segmento_Acad']).to_csv(out_bol, index=False)
                 msg_boletas = f" y {len(sub_boletas)} boletas sin pago"

         print(f"[{segmento}] -> Exportados: {len(sub_inscriptos)} inscriptos, {len(sub_leads)} leads{msg_boletas}.")

    print("¡Proceso finalizado con éxito! Datos distribuidos correctamente.")
