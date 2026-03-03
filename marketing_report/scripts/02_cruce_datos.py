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

    df_leads['DNI_match'] = df_leads.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
    df_leads['Email_match'] = df_leads.get('Correo', pd.Series(dtype='object')).apply(clean_email)
    df_leads['Phone_match']   = df_leads.get('Telefono', pd.Series(dtype='object')).apply(clean_phone)
    df_leads['Cel_lead_match'] = df_leads.get('Celular', pd.Series(dtype='object')).apply(clean_phone)
    df_leads['Nombre_match']  = df_leads.get('Nombre', pd.Series(dtype='object')).apply(clean_name)

    df_inscriptos['Inscripto_Tmp_ID'] = df_inscriptos.index.astype(str)
    df_leads['Lead_Tmp_ID'] = df_leads.index.astype(str)

    df_inscriptos['DNI_match'] = df_inscriptos.get('DNI', pd.Series(dtype='object')).apply(clean_dni)
    df_inscriptos['Email_match'] = df_inscriptos.get('Email', pd.Series(dtype='object')).apply(clean_email)
    df_inscriptos['Phone_match'] = df_inscriptos.get('Telefono', pd.Series(dtype='object')).apply(clean_phone)
    df_inscriptos['Cel_match'] = df_inscriptos.get('Celular', pd.Series(dtype='object')).apply(clean_phone)
    df_inscriptos['Nombre_match'] = df_inscriptos.get('Apellido y Nombre', pd.Series(dtype='object')).apply(clean_name)

    rename_dict = {col: f"Insc_{col}" for col in df_inscriptos.columns if col not in ['Inscripto_Tmp_ID']}
    df_inscriptos_renamed = df_inscriptos.rename(columns=rename_dict)

    print("Realizando cruce exacto de datos (DNI, Email, Teléfono)...")

    # ==========================================
    # 3. LÓGICA DE CRUCE EXACTO
    # ==========================================
    matched_leads_ids = set()
    matched_insc_ids = set()

    # Match 1: DNI
    leads_dni = df_leads[df_leads['DNI_match'].notna()]
    insc_dni = df_inscriptos_renamed[df_inscriptos_renamed['Insc_DNI_match'].notna()]
    merge1 = pd.merge(leads_dni, insc_dni, left_on='DNI_match', right_on='Insc_DNI_match', how='inner')
    merge1['Match_Tipo'] = 'Exacto (DNI)'

    matched_leads_ids.update(merge1['Lead_Tmp_ID'])
    matched_insc_ids.update(merge1['Inscripto_Tmp_ID'])

    # Match 2: Email
    leads_rem_1 = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)]
    insc_rem_1 = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)]

    leads_email = leads_rem_1[leads_rem_1['Email_match'].notna()]
    insc_email = insc_rem_1[insc_rem_1['Insc_Email_match'].notna()]
    merge2 = pd.merge(leads_email, insc_email, left_on='Email_match', right_on='Insc_Email_match', how='inner')
    merge2['Match_Tipo'] = 'Exacto (Email)'

    matched_leads_ids.update(merge2['Lead_Tmp_ID'])
    matched_insc_ids.update(merge2['Inscripto_Tmp_ID'])

    # Match 3: Teléfono 
    # Insc Telefono
    leads_rem_2 = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)]
    insc_rem_2 = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)]

    leads_phone = leads_rem_2[leads_rem_2['Phone_match'].notna()]
    insc_phone = insc_rem_2[insc_rem_2['Insc_Phone_match'].notna()]
    merge3a = pd.merge(leads_phone, insc_phone, left_on='Phone_match', right_on='Insc_Phone_match', how='inner')
    merge3a['Match_Tipo'] = 'Exacto (Teléfono)'

    matched_leads_ids.update(merge3a['Lead_Tmp_ID'])
    matched_insc_ids.update(merge3a['Inscripto_Tmp_ID'])

    # Match 3b: lead Telefono vs insc Celular
    leads_rem_3 = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)]
    insc_rem_3 = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)]

    leads_cel = leads_rem_3[leads_rem_3['Phone_match'].notna()]
    insc_cel = insc_rem_3[insc_rem_3['Insc_Cel_match'].notna()]
    merge3b = pd.merge(leads_cel, insc_cel, left_on='Phone_match', right_on='Insc_Cel_match', how='inner')
    merge3b['Match_Tipo'] = 'Exacto (Celular)'

    matched_leads_ids.update(merge3b['Lead_Tmp_ID'])
    matched_insc_ids.update(merge3b['Inscripto_Tmp_ID'])

    # Match 3c: lead Celular vs insc Telefono
    leads_rem_4 = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)]
    insc_rem_4 = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)]

    leads_cel2 = leads_rem_4[leads_rem_4['Cel_lead_match'].notna()]
    insc_phone2 = insc_rem_4[insc_rem_4['Insc_Phone_match'].notna()]
    merge3c = pd.merge(leads_cel2, insc_phone2, left_on='Cel_lead_match', right_on='Insc_Phone_match', how='inner')
    merge3c['Match_Tipo'] = 'Exacto (Celular)'

    matched_leads_ids.update(merge3c['Lead_Tmp_ID'])
    matched_insc_ids.update(merge3c['Inscripto_Tmp_ID'])

    # Match 3d: lead Celular vs insc Celular
    leads_rem_5 = df_leads[~df_leads['Lead_Tmp_ID'].isin(matched_leads_ids)]
    insc_rem_5 = df_inscriptos_renamed[~df_inscriptos_renamed['Inscripto_Tmp_ID'].isin(matched_insc_ids)]

    leads_cel3 = leads_rem_5[leads_rem_5['Cel_lead_match'].notna()]
    insc_cel2 = insc_rem_5[insc_rem_5['Insc_Cel_match'].notna()]
    merge3d = pd.merge(leads_cel3, insc_cel2, left_on='Cel_lead_match', right_on='Insc_Cel_match', how='inner')
    merge3d['Match_Tipo'] = 'Exacto (Celular)'

    matched_leads_ids.update(merge3d['Lead_Tmp_ID'])
    matched_insc_ids.update(merge3d['Inscripto_Tmp_ID'])

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
    print("Consolidando resultados...")

    # Leads Exactos (DNI + Email + Teléfono×4 combinaciones)
    df_matched_exact = pd.concat([merge1, merge2, merge3a, merge3b, merge3c, merge3d], ignore_index=True)

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

    # Limpieza columnas
    cols_to_drop = [
        'DNI_match', 'Email_match', 'Phone_match', 'Cel_lead_match', 'Nombre_match', 'Lead_Tmp_ID', 'Inscripto_Tmp_ID',
        'Insc_DNI_match', 'Insc_Email_match', 'Insc_Phone_match', 'Insc_Cel_match', 'Insc_Nombre_match'
    ]

    df_final_leads.drop(columns=[c for c in cols_to_drop if c in df_final_leads.columns], inplace=True, errors='ignore')
    df_final_inscriptos.drop(columns=[c for c in cols_to_drop if c in df_final_inscriptos.columns], inplace=True, errors='ignore')

    # ==========================================
    # 6. SEGMENTACIÓN Y EXPORTACIÓN POR NIVEL ACADÉMICO
    # ==========================================
    print("Segmentando y exportando informes a CSV según Nivel Académico...")
    
    # Función para estandarizar la clasificación 
    def segmentar_tipcar(tipcar_val):
        val = str(tipcar_val).lower()
        if 'curso' in val: 
            return 'Cursos'
        elif 'postgrado' in val or 'maestría' in val or 'maestria' in val or 'posgrado' in val: 
            return 'Posgrados'
        elif 'grado' in val or 'pregrado' in val: 
            return 'Grado_Pregrado'
        else: 
            return 'Desconocido'

    # Clasificar inscriptos (usan Insc_Tipcar)
    df_final_inscriptos['Segmento_Acad'] = df_final_inscriptos['Insc_Tipcar'].apply(segmentar_tipcar)
    
    # Clasificar leads (Si matchearon, heredan Insc_Tipcar para estricta consistencia. Si no, usan 'Tipo de Carrera' original de CRM)
    def get_lead_segment(row):
        insc_tip = str(row.get('Insc_Tipcar', 'nan'))
        if insc_tip != 'nan' and insc_tip.strip() != '' and insc_tip != 'None':
             return segmentar_tipcar(insc_tip)
             
        local_tip = str(row.get('Tipo de Carrera', 'nan'))
        return segmentar_tipcar(local_tip)
        
    df_final_leads['Segmento_Acad'] = df_final_leads.apply(get_lead_segment, axis=1)

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
             
         out_insc = os.path.join(segment_dir, "reporte_marketing_inscriptos_origenes.csv")
         out_leads = os.path.join(segment_dir, "reporte_marketing_leads_completos.csv")
         
         sub_inscriptos.drop(columns=['Segmento_Acad']).to_csv(out_insc, index=False)
         sub_leads.drop(columns=['Segmento_Acad']).to_csv(out_leads, index=False)
         
         print(f"[{segmento}] -> Exportados: {len(sub_inscriptos)} inscriptos reales y {len(sub_leads)} leads.")
    
    print("¡Proceso finalizado con éxito! Datos distribuidos correctamente.")
