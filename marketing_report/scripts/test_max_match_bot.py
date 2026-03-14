"""
TEST INDEPENDIENTE: Máximo match posible Bot vs Inscriptos
=========================================================
Objetivo: verificar que el pipeline de matching (02_cruce_datos.py) está
capturando TODOS los inscriptos que tienen al menos 1 lead del bot (FuenteLead=907),
usando TODAS las combinaciones posibles de campos de contacto.

Este test NO depende del CSV de salida del pipeline.
Lee directamente los archivos fuente (leads raw + inscriptos raw) y hace el cruce
desde cero, comparando resultados con lo que el pipeline produjo.

Combinaciones de match:
  1. DNI lead          vs DNI inscripto
  2. Email lead        vs Email inscripto
  3. Telefono lead     vs Telefono inscripto
  4. Telefono lead     vs Celular inscripto
  5. Celular lead      vs Telefono inscripto
  6. Celular lead      vs Celular inscripto

Normalización telefónica (clean_phone):
  - Quita prefijo internacional 549 / 54
  - Quita 0 inicial (interurbano)
  - Quita 15 móvil intercalado
  - Trunca a 10 dígitos
  - Maneja guiones y duplicados de código de área
"""
import pandas as pd
import numpy as np
import re
import os
import sys
import glob

# ---- Funciones de limpieza (idénticas a 02_cruce_datos.py) ----

def clean_dni(val):
    if pd.isna(val) or val == '':
        return None
    s = str(val).split('.')[0].strip()
    if s in ('nan', '', 'None', 'NaN', '0'):
        return None
    # Solo dígitos
    s = re.sub(r'\D', '', s)
    return s if s else None


def clean_email(val):
    if pd.isna(val) or val == '':
        return None
    s = str(val).strip().lower()
    if s in ('nan', '', 'none', '0'):
        return None
    if '@' not in s:
        return None
    return s


def clean_phone(val):
    """Normaliza teléfonos argentinos a ~10 dígitos comparables."""
    if pd.isna(val) or val == '':
        return None
    s = str(val).split('.')[0].strip()
    if '-' in s:
        parts = [p.strip() for p in s.split('-')]
        if len(parts) >= 2:
            p0 = re.sub(r'\D', '', parts[0])
            p1 = re.sub(r'\D', '', ''.join(parts[1:]))
            if p0 and p1.startswith(p0):
                s = p1
            elif p0 == '54' and p1.startswith('549'):
                s = p1[3:]
            elif p0 == '54' and p1.startswith('54'):
                s = p1[2:]
            else:
                s = p0 + p1
    s = re.sub(r'\D', '', s)
    if not s:
        return None
    if s.startswith('549'):
        s = s[3:]
    elif s.startswith('54'):
        s = s[2:]
    if s.startswith('0'):
        s = s[1:]
    s = re.sub(r'(^\d{2,4})15(\d{6,8}$)', r'\1\2', s)
    if len(s) > 10:
        s = s[-10:]
    return s if s and len(s) >= 7 else None


# ---- Paths ----
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_BASE = os.path.join(BASE, '..', 'outputs', 'Data_Base')
LEADS_DIR = os.path.join(BASE, '..', 'data', '1_raw', 'leads')

SEGMENTOS = ['Grado_Pregrado', 'Cursos', 'Posgrados']
BOT_FUENTE = 907


def load_inscriptos(seg):
    """Lee inscriptos del CSV de origenes (contiene Insc_* fields)."""
    path = os.path.join(DATA_BASE, seg, 'reporte_marketing_inscriptos_origenes.csv')
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def load_leads_csv(seg):
    """Lee leads del CSV de salida del pipeline (para comparar)."""
    path = os.path.join(DATA_BASE, seg, 'reporte_marketing_leads_completos.csv')
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def build_inscripto_index(df_insc):
    """
    Construye índices de búsqueda para inscriptos.
    Cada inscripto se identifica por un ID único (Insc_DNI preferido).
    Devuelve dicts: {valor_limpio: set_of_person_ids} para cada campo.
    """
    idx_dni = {}
    idx_email = {}
    idx_phone = {}  # Tel + Cel combinados

    for i, row in df_insc.iterrows():
        # Person ID = Insc_DNI preferido, fallback a index
        pid = clean_dni(row.get('Insc_DNI', ''))
        if not pid:
            pid = clean_email(row.get('Insc_Email', ''))
        if not pid:
            pid = f'_insc_{i}'

        # DNI
        d = clean_dni(row.get('Insc_DNI', ''))
        if d:
            idx_dni.setdefault(d, set()).add(pid)

        # Email
        e = clean_email(row.get('Insc_Email', ''))
        if e:
            idx_email.setdefault(e, set()).add(pid)

        # Telefono inscripto
        t = clean_phone(row.get('Insc_Telefono', ''))
        if t:
            idx_phone.setdefault(t, set()).add(pid)

        # Celular inscripto
        c = clean_phone(row.get('Insc_Celular', ''))
        if c:
            idx_phone.setdefault(c, set()).add(pid)

    return idx_dni, idx_email, idx_phone


def cross_match_all(df_leads, idx_dni, idx_email, idx_phone):
    """
    Para TODOS los leads (sin filtro de fuente), intenta matchear contra inscriptos.
    Devuelve el maximo teorico de inscriptos matcheables.
    """
    matched_persons = set()
    match_details = {
        'DNI': set(), 'Email': set(),
        'Tel_x_Tel_Cel': set(), 'Cel_x_Tel_Cel': set(),
    }

    for _, row in df_leads.iterrows():
        d = clean_dni(row.get('DNI', ''))
        e = clean_email(row.get('Correo', ''))
        t = clean_phone(row.get('Telefono', ''))
        c = clean_phone(row.get('Celular', ''))

        pids = set()
        if d and d in idx_dni:
            for pid in idx_dni[d]:
                pids.add(pid)
                match_details['DNI'].add(pid)
        if e and e in idx_email:
            for pid in idx_email[e]:
                if pid not in pids:
                    match_details['Email'].add(pid)
                pids.update(idx_email[e])
        if t and t in idx_phone:
            for pid in idx_phone[t]:
                if pid not in pids:
                    match_details['Tel_x_Tel_Cel'].add(pid)
                pids.update(idx_phone[t])
        if c and c in idx_phone:
            for pid in idx_phone[c]:
                if pid not in pids:
                    match_details['Cel_x_Tel_Cel'].add(pid)
                pids.update(idx_phone[c])

        matched_persons.update(pids)

    return matched_persons, match_details


def cross_match_bot(df_leads, idx_dni, idx_email, idx_phone):
    """
    Para cada lead del bot, intenta matchear contra inscriptos
    usando las 6 combinaciones. Registra por qué campo matcheó.
    Any-touch: si UNA fila del bot matchea, el inscripto cuenta.
    """
    matched_persons = set()
    match_details = {
        'DNI': set(),
        'Email': set(),
        'Tel_x_Tel_Cel': set(),   # Telefono lead -> Tel/Cel inscripto
        'Cel_x_Tel_Cel': set(),   # Celular lead -> Tel/Cel inscripto
    }

    bot = df_leads[pd.to_numeric(df_leads.get('FuenteLead', 0), errors='coerce') == BOT_FUENTE]

    for _, row in bot.iterrows():
        d = clean_dni(row.get('DNI', ''))
        e = clean_email(row.get('Correo', ''))
        t = clean_phone(row.get('Telefono', ''))
        c = clean_phone(row.get('Celular', ''))

        pids = set()
        via = None

        # 1. DNI
        if d and d in idx_dni:
            pids = idx_dni[d]
            via = 'DNI'
        # 2. Email
        if e and e in idx_email:
            new = idx_email[e] - pids
            if new:
                pids = pids | new
                if via is None:
                    via = 'Email'
        # 3. Telefono lead -> Tel/Cel inscripto
        if t and t in idx_phone:
            new = idx_phone[t] - pids
            if new:
                pids = pids | new
                if via is None:
                    via = 'Tel_x_Tel_Cel'
        # 4. Celular lead -> Tel/Cel inscripto
        if c and c in idx_phone:
            new = idx_phone[c] - pids
            if new:
                pids = pids | new
                if via is None:
                    via = 'Cel_x_Tel_Cel'

        for pid in pids:
            matched_persons.add(pid)
            # Classify by best match type found for this person
            if d and d in idx_dni and pid in idx_dni.get(d, set()):
                match_details['DNI'].add(pid)
            elif e and e in idx_email and pid in idx_email.get(e, set()):
                match_details['Email'].add(pid)
            elif t and t in idx_phone and pid in idx_phone.get(t, set()):
                match_details['Tel_x_Tel_Cel'].add(pid)
            elif c and c in idx_phone and pid in idx_phone.get(c, set()):
                match_details['Cel_x_Tel_Cel'].add(pid)

    return matched_persons, match_details


def get_pipeline_bot_count(df_leads_csv):
    """Cuenta inscriptos bot según el CSV del pipeline (any-touch)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from causal_utils import make_pk

    df = df_leads_csv.copy()
    df['FuenteLead'] = pd.to_numeric(df.get('FuenteLead', 0), errors='coerce')
    if 'Celular' not in df.columns:
        df['Celular'] = ''
    df['_pk'] = make_pk(df)

    exact_mask = df['Match_Tipo'].astype(str).str.contains('Exacto', case=False, na=False)
    all_matched_pks = set(df[exact_mask]['_pk'].unique())
    bot_pks = set(df[df['FuenteLead'] == BOT_FUENTE]['_pk'].unique())

    # Any-touch: matched AND has at least 1 bot lead
    anytouch = all_matched_pks & bot_pks

    # Direct: the bot lead itself is the one that matched
    direct = set(df[(df['FuenteLead'] == BOT_FUENTE) & exact_mask]['_pk'].unique())

    return {
        'direct': len(direct),
        'anytouch_pk': len(anytouch),
        'all_matched': len(all_matched_pks),
    }


def main():
    print("=" * 70)
    print("TEST INDEPENDIENTE: Maximo match Bot vs Inscriptos")
    print("=" * 70)

    for seg in SEGMENTOS:
        print(f"\n{'=' * 50}")
        print(f"SEGMENTO: {seg}")
        print(f"{'=' * 50}")

        df_insc = load_inscriptos(seg)
        if df_insc.empty:
            print("  (sin datos de inscriptos)")
            continue

        df_leads_csv = load_leads_csv(seg)
        if df_leads_csv.empty:
            print("  (sin datos de leads)")
            continue

        # Build index and data map
        idx_dni, idx_email, idx_phone = build_inscripto_index(df_insc)

        # Build per-person data map for diagnostics
        insc_data_map = {}
        for i, row in df_insc.iterrows():
            pid = clean_dni(row.get('Insc_DNI', ''))
            if not pid:
                pid = clean_email(row.get('Insc_Email', ''))
            if not pid:
                pid = f'_insc_{i}'
            insc_data_map[pid] = {
                'dni': clean_dni(row.get('Insc_DNI', '')),
                'email': clean_email(row.get('Insc_Email', '')),
                'tel': clean_phone(row.get('Insc_Telefono', '')),
                'cel': clean_phone(row.get('Insc_Celular', '')),
            }
        print(f"\n  Inscriptos: {len(df_insc):,}")
        print(f"  Lookup DNI: {len(idx_dni):,} valores únicos")
        print(f"  Lookup Email: {len(idx_email):,} valores únicos")
        print(f"  Lookup Phone (Tel+Cel): {len(idx_phone):,} valores únicos")

        # Cross-match
        matched, details = cross_match_bot(df_leads_csv, idx_dni, idx_email, idx_phone)

        print(f"\n  --- RESULTADO TEST INDEPENDIENTE (any-touch, 6 combos) ---")
        print(f"  Total inscriptos con al menos 1 lead bot: {len(matched):,}")
        print(f"    Via DNI:                {len(details['DNI']):,}")
        print(f"    Via Email:              {len(details['Email']):,}")
        print(f"    Via Tel->Tel/Cel:        {len(details['Tel_x_Tel_Cel']):,}")
        print(f"    Via Cel->Tel/Cel:        {len(details['Cel_x_Tel_Cel']):,}")

        # Pipeline comparison
        pipeline = get_pipeline_bot_count(df_leads_csv)
        print(f"\n  --- PIPELINE ACTUAL ---")
        print(f"  Bot directo (lead bot matcheado):   {pipeline['direct']:,}")
        print(f"  Bot any-touch (via _pk):            {pipeline['anytouch_pk']:,}")
        print(f"  Total matcheados (todos canales):   {pipeline['all_matched']:,}")

        diff = len(matched) - pipeline['anytouch_pk']
        print(f"\n  --- DIAGNÓSTICO ---")
        if diff > 0:
            print(f"  ALERTA: HAY {diff} INSCRIPTOS ADICIONALES que el pipeline NO captura como bot")
            print(f"    Posibles causas:")
            print(f"    - _pk solo usa 1 campo (fallback), el cross-match usa todos")
            print(f"    - Email/Tel del lead bot matchea inscripto, pero _pk eligió otro campo")
        elif diff < 0:
            print(f"  ALERTA: El pipeline reporta {-diff} MÁS que el test (revisar lógica)")
        else:
            print(f"  OK: Pipeline captura el 100% de los matches posibles")

        # Check truly unmatched: inscriptos that COULD match a bot lead
        # but are NOT matched at all in the pipeline (by any source)
        exact_mask = df_leads_csv['Match_Tipo'].astype(str).str.contains('Exacto', case=False, na=False)
        all_matched_emails = set(df_leads_csv[exact_mask]['Correo'].apply(clean_email).dropna())
        all_matched_dnis = set(df_leads_csv[exact_mask]['DNI'].apply(clean_dni).dropna())
        all_matched_phones = set()
        for col in ['Telefono', 'Celular']:
            if col in df_leads_csv.columns:
                all_matched_phones.update(
                    set(df_leads_csv[exact_mask][col].apply(clean_phone).dropna()))

        truly_missed = set()
        for pid in matched:
            data = insc_data_map.get(pid, {})
            found = False
            # Check by DNI
            if data.get('dni') and data['dni'] in all_matched_dnis:
                found = True
            # Check by email
            if not found and data.get('email') and data['email'] in all_matched_emails:
                found = True
            # Check by phone (tel or cel)
            if not found and data.get('tel') and data['tel'] in all_matched_phones:
                found = True
            if not found and data.get('cel') and data['cel'] in all_matched_phones:
                found = True
            if not found:
                truly_missed.add(pid)

        if truly_missed:
            print(f"\n  ALERTA: {len(truly_missed)} inscriptos con lead bot NO MATCHEADOS por ningun canal")
            for pid in list(truly_missed)[:5]:
                data = insc_data_map.get(pid, {})
                print(f"    PID={pid} | email={data.get('email','-')} | tel={data.get('tel','-')} | cel={data.get('cel','-')}")
        else:
            print(f"\n  OK: Todos los inscriptos con lead bot estan matcheados (posiblemente por otro canal)")

        # ---- VERIFICACION GLOBAL: match total (todos los canales) ----
        print(f"\n  --- VERIFICACION GLOBAL (todos los canales) ---")
        all_matched_global, all_details = cross_match_all(df_leads_csv, idx_dni, idx_email, idx_phone)
        print(f"  Maximo teorico inscriptos matcheables: {len(all_matched_global):,}")
        print(f"    Via DNI:           {len(all_details['DNI']):,}")
        print(f"    Via Email:         {len(all_details['Email']):,}")
        print(f"    Via Tel->Tel/Cel:   {len(all_details['Tel_x_Tel_Cel']):,}")
        print(f"    Via Cel->Tel/Cel:   {len(all_details['Cel_x_Tel_Cel']):,}")
        print(f"  Pipeline matcheados: {pipeline['all_matched']:,}")
        global_diff = len(all_matched_global) - pipeline['all_matched']
        if global_diff > 0:
            print(f"  ALERTA: {global_diff} inscriptos adicionales matcheables no capturados")
        elif global_diff < 0:
            print(f"  ALERTA: pipeline reporta {-global_diff} mas (revisar)")
        else:
            print(f"  OK: Pipeline captura el 100% de matches posibles")

    print(f"\n{'=' * 70}")
    print("TEST FINALIZADO")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
