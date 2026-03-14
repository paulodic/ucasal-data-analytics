"""
causal_utils.py
Funciones compartidas para el pipeline de marketing analytics.

CONTENIDO:
  make_pk(df)                  -> Clave de persona para deduplicación (DNI > Email > Tel > Cel)
  classify_canal(row)          -> Clasifica un lead en canal (Bot/Google/Meta/Otros)
  compute_anytouch_causal(...) -> Calcula atribución Any-Touch con filtro causal
  render_causal_md(...)        -> Genera sección Markdown de atribución causal
  render_causal_pdf(...)       -> Genera página PDF de atribución causal

MODELO CAUSAL: Solo se cuenta como conversión una consulta cuya fecha de creación
es ANTERIOR O IGUAL a la fecha de pago (Consulta: Fecha de creación <= Insc_Fecha Pago).
Consultas post-pago (soporte, reactivación) quedan excluidas.

DEDUPLICACIÓN (make_pk):
  Cadena de fallback: DNI > Correo > Telefono > Celular > indice de fila.
  - DNI/Telefono/Celular: se limpia el decimal (.0) con split('.')[0]
  - Correo: se normaliza a minúsculas (lower) conservando puntos del dominio
  - Si ningún campo tiene valor válido, se usa el índice de fila como último recurso
  - Todos los scripts de reporte (04-23) importan make_pk de este módulo
  - IMPORTANTE: Esta función SOLO se usa para deduplicación de personas en reportes.
    El matching real Lead↔Inscripto se hace en 02_cruce_datos.py con columnas
    limpias (*_match) y 6 pasos secuenciales: DNI, Email, Tel×Tel, Tel×Cel, Cel×Tel, Cel×Cel.

CRITERIOS DE MATCH (implementados en 02_cruce_datos.py -> cruce_exacto()):
  1. Exacto (DNI)       -- DNI del lead == DNI del inscripto (sin decimales, case-insensitive)
  2. Exacto (Email)     -- Correo del lead == Email del inscripto (lower, strip)
  3. Exacto (Telefono)  -- Phone_lead x Phone_inscripto (normalizado, sin prefijos)
  4. Exacto (Celular)   -- Phone_lead x Cel_inscripto, Cel_lead x Phone_inscripto, Cel_lead x Cel_inscripto
  Los pasos son secuenciales: cada paso excluye IDs ya matcheados en pasos anteriores.
  Todos los matches son case-insensitive y usan campos limpiados (clean_dni, clean_email, clean_phone).
  clean_phone: minimo 7 digitos (valores menores son prefijos sueltos -> falsos positivos).

CONSULTAS VS PERSONAS:
  - "Consulta" = fila unica por Consulta: ID Consulta (origen y canal especifico)
  - "Persona" = _pk unica (un individuo puede tener multiples consultas)
  - Tasas de conversion se calculan sobre PERSONAS, no sobre consultas
  - Ambas metricas son necesarias y deben aparecer en los informes

ANY-TOUCH (LEY):
  Un inscripto que consulto por Google, Meta Y Bot se cuenta en los TRES canales.
  NUNCA usar masks excluyentes entre canales (& ~bot_mask PROHIBIDO).
  La suma de canales puede superar el 100%. Solo "Otros" es residual.

USO: Importar desde cualquier script de reporte para generar la seccion
"Any-Touch Causal" de forma consistente (principio DRY).
  from causal_utils import make_pk, compute_anytouch_causal, render_causal_md, render_causal_pdf
"""
import pandas as pd
import numpy as np

# ============================================================
# CONSTANTES COMPARTIDAS
# ============================================================
PERIODO_INICIO = {
    'Grado_Pregrado': pd.Timestamp('2025-09-01'),
    'Cursos':         pd.Timestamp('2026-01-01'),
    'Posgrados':      pd.Timestamp('2026-01-01'),
}

PERIODO_LABEL = {
    'Grado_Pregrado': 'desde Sep 2025 (Cohorte Ingreso 2026)',
    'Cursos':         'desde Ene 2026 (ano calendario)',
    'Posgrados':      'desde Ene 2026 (ano calendario)',
}

META_KEYWORDS = ['fb', 'facebook', 'ig', 'instagram', 'meta']

_PK_INVALID = {'nan', '', 'None', 'NaN', 'none'}


def make_pk(df):
    """
    Clave de persona para deduplicar: DNI > Correo > Telefono > Celular > indice.

    Garantiza que cada persona tenga un identificador único incluso si
    el match fue por teléfono y no tiene DNI ni Email.

    Limpieza por tipo de campo:
      - DNI/Telefono/Celular: quitar decimales (.0) con split('.')[0]
      - Correo: lower().strip() sin split (el email tiene puntos válidos)
    """
    pk = (df['DNI'].astype(str).str.split('.').str[0].str.strip()
          if 'DNI' in df.columns else pd.Series('', index=df.index))
    pk = pk.replace({v: '' for v in _PK_INVALID})
    # Campos numéricos: quitar .0 decimal con split('.')
    _numeric_cols = {'Telefono', 'Celular'}
    for col in ['Correo', 'Telefono', 'Celular']:
        if col in df.columns:
            mask = pk.isin(_PK_INVALID) | (pk == '')
            if not mask.any():
                break
            if col in _numeric_cols:
                vals = df.loc[mask, col].astype(str).str.split('.').str[0].str.strip()
            else:
                # Email: conservar puntos, normalizar a minúsculas
                vals = df.loc[mask, col].astype(str).str.strip().str.lower()
            vals = vals.replace({v: '' for v in _PK_INVALID})
            pk.loc[mask] = vals
    # Último recurso: índice de fila (evita que múltiples personas colapsen en '')
    mask = pk.isin(_PK_INVALID) | (pk == '')
    if mask.any():
        pk.loc[mask] = '_idx_' + df.index[mask].astype(str)
    return pk

CANAL_COLORS = {
    'Google':   '#4285f4',
    'Facebook': '#1877f2',
    'Bot':      '#e74c3c',
    'Otros':    '#95a5a6',
}

CANALES_ORDER = ['Google', 'Facebook', 'Bot', 'Otros']


# ============================================================
# FUNCIONES
# ============================================================
def classify_canal(df, utm_col='_utm', fuente_col='_fuente'):
    """Clasifica cada fila en un canal: Google, Facebook, Bot, Otros.

    Args:
        df: DataFrame con columnas utm y fuente ya preparadas.
        utm_col: nombre de columna UTM (lowercase, stripped).
        fuente_col: nombre de columna FuenteLead numérica.

    Returns:
        Series con el canal asignado.
    """
    canal = pd.Series('Otros', index=df.index)
    canal[df[fuente_col] == 907] = 'Bot'
    canal[df[utm_col].str.contains('|'.join(META_KEYWORDS), na=False) |
          (df[fuente_col] == 18)] = 'Facebook'
    canal[df[utm_col].str.contains('google', na=False)] = 'Google'
    return canal


def compute_anytouch_causal(leads_csv, segmento, inscriptos_csv=None):
    """Calcula métricas Any-Touch Causal para un segmento.

    Lee el CSV de leads, aplica el filtro causal (consulta <= fecha pago),
    y devuelve métricas por canal bajo modelo Any-Touch.

    Args:
        leads_csv: path al CSV de leads completos del segmento.
        segmento: 'Grado_Pregrado', 'Cursos' o 'Posgrados'.
        inscriptos_csv: path al CSV de inscriptos (para contar huérfanos).

    Returns:
        dict con claves:
            'por_canal': {canal: {'conv': int, 'pct': float}} para Google, Facebook, Bot, Otros
            'total_unico': int (inscriptos únicos causales)
            'n_late': int (consultas post-pago excluidas)
            'ventana': str (periodo analizado)
            'inscriptos_sin_match': int (inscriptos sin lead)
            'total_inscriptos': int (total inscriptos físicos)
            'pct_sin_match': float
            'n_1canal': int, 'n_2canales': int, 'n_3plus': int
            'combos': DataFrame con top combinaciones
    """
    usecols_need = ['Match_Tipo', 'DNI', 'Correo', 'FuenteLead', 'UtmSource',
                    'Consulta: Fecha de creación', 'Insc_Fecha Pago']

    # Cargar solo columnas necesarias
    cols_avail = pd.read_csv(leads_csv, nrows=1).columns.tolist()
    usecols = [c for c in usecols_need if c in cols_avail]
    df = pd.read_csv(leads_csv, usecols=usecols, low_memory=False)

    # Preparar columnas
    df['_mc'] = df['Match_Tipo'].apply(
        lambda v: 'exacto' if 'Exacto' in str(v) else ('fuzzy' if 'Fuzzy' in str(v) else 'no_match'))
    df = df[df['_mc'] != 'fuzzy'].copy()

    df['_pk'] = make_pk(df)

    df['_utm'] = df.get('UtmSource', pd.Series('', index=df.index)).astype(str).str.lower().str.strip()
    df['_fuente'] = pd.to_numeric(df.get('FuenteLead', pd.Series(dtype='float')), errors='coerce')
    df['_fecha'] = pd.to_datetime(
        df['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

    # Ventana de conversión
    inicio = PERIODO_INICIO[segmento]
    hoy = pd.Timestamp.now()

    # Max fecha inscripción
    max_insc_ts = hoy
    if 'Insc_Fecha Pago' in df.columns:
        d = pd.to_datetime(df['Insc_Fecha Pago'], format='mixed', errors='coerce')
        d = d[d <= hoy]
        if not d.isna().all():
            max_insc_ts = d.max()

    df_conv = df[(df['_fecha'] >= inicio) & (df['_fecha'] <= max_insc_ts)].copy()
    ventana = f"{inicio.strftime('%d/%m/%Y')} - {max_insc_ts.strftime('%d/%m/%Y')}"

    # Filtro causal: consulta <= fecha de pago
    df_conv['_insc_fecha'] = pd.to_datetime(
        df_conv.get('Insc_Fecha Pago', pd.Series(dtype='str')),
        format='mixed', errors='coerce')

    late_mask = (df_conv['_mc'] == 'exacto') & (df_conv['_fecha'] > df_conv['_insc_fecha'])
    n_late = int(late_mask.sum())
    df_conv.loc[late_mask, '_mc'] = 'no_match'

    # Solo exactos causales
    df_exacto = df_conv[df_conv['_mc'] == 'exacto'].copy()
    df_exacto['_canal'] = classify_canal(df_exacto)

    total_unico = df_exacto['_pk'].nunique()

    # Any-Touch por canal (dedup dentro de cada canal)
    por_canal = {}
    for canal in CANALES_ORDER:
        sub = df_exacto[df_exacto['_canal'] == canal].drop_duplicates(subset='_pk', keep='first')
        conv = len(sub)
        pct = (conv / total_unico * 100) if total_unico > 0 else 0
        por_canal[canal] = {'conv': conv, 'pct': round(pct, 1)}

    # Multi-canal
    canales_por_persona = df_exacto.groupby('_pk')['_canal'].nunique()
    n_1canal = int((canales_por_persona == 1).sum())
    n_2canales = int((canales_por_persona == 2).sum())
    n_3plus = int((canales_por_persona >= 3).sum())

    # Top combinaciones
    combos = (df_exacto.groupby('_pk')['_canal']
              .apply(lambda x: ' + '.join(sorted(x.unique())))
              .value_counts().head(8).reset_index())
    combos.columns = ['Combinacion', 'Inscriptos']
    combos['%'] = (combos['Inscriptos'] / total_unico * 100).round(1) if total_unico > 0 else 0

    # Inscriptos sin match
    inscriptos_sin_match = 0
    total_inscriptos = 0
    pct_sin_match = 0.0
    if inscriptos_csv:
        try:
            df_insc = pd.read_csv(inscriptos_csv, usecols=['DNI'], low_memory=False)
            insc_dnis = set(df_insc['DNI'].astype(str).str.split('.').str[0].str.strip().unique()) - {'nan', '', 'None'}
            total_inscriptos = len(insc_dnis)
            matched_dnis = set(df_exacto['_pk'].unique()) & insc_dnis
            inscriptos_sin_match = total_inscriptos - len(matched_dnis)
            pct_sin_match = (inscriptos_sin_match / total_inscriptos * 100) if total_inscriptos > 0 else 0
        except Exception:
            pass

    return {
        'por_canal': por_canal,
        'total_unico': total_unico,
        'n_late': n_late,
        'ventana': ventana,
        'periodo_label': PERIODO_LABEL[segmento],
        'inscriptos_sin_match': inscriptos_sin_match,
        'total_inscriptos': total_inscriptos,
        'pct_sin_match': round(pct_sin_match, 1),
        'n_1canal': n_1canal,
        'n_2canales': n_2canales,
        'n_3plus': n_3plus,
        'combos': combos,
    }


def render_causal_md(causal_data, segmento):
    """Genera sección Markdown con datos Any-Touch Causal.

    Args:
        causal_data: dict retornado por compute_anytouch_causal().
        segmento: nombre del segmento.

    Returns:
        str con contenido Markdown.
    """
    d = causal_data
    md = "\n## Atribucion Causal (consulta <= fecha de pago)\n\n"
    md += f"*Ventana: {d['ventana']} | {d['periodo_label']}*\n\n"
    md += f"Consultas post-pago excluidas: {d['n_late']:,}\n\n"

    md += "| Canal | Inscriptos (Any-Touch Causal) | % Participacion |\n"
    md += "|-------|---:|---:|\n"
    for canal in CANALES_ORDER:
        c = d['por_canal'][canal]
        md += f"| {canal} | {c['conv']:,} | {c['pct']}% |\n"
    md += f"| **Total Unico** | **{d['total_unico']:,}** | **100%** |\n\n"

    md += f"Multi-canal: 1 canal={d['n_1canal']:,}, 2 canales={d['n_2canales']:,}, 3+={d['n_3plus']:,}\n\n"

    if d['total_inscriptos'] > 0:
        md += f"Inscriptos sin lead/match: {d['inscriptos_sin_match']:,} de {d['total_inscriptos']:,} ({d['pct_sin_match']}%)\n\n"

    md += "*Nota: El modelo causal solo cuenta consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago. "
    md += "Consultas post-pago (soporte, seguimiento) excluidas.*\n\n"

    return md


def render_causal_pdf(pdf, causal_data, segmento):
    """Renderiza sección Any-Touch Causal en un objeto FPDF.

    Args:
        pdf: instancia de FPDF (ya con add_page() o en página actual).
        causal_data: dict retornado por compute_anytouch_causal().
        segmento: nombre del segmento.
    """
    d = causal_data

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, 'Atribucion Causal (consulta <= fecha de pago)', new_x='LMARGIN', new_y='NEXT')

    pdf.set_fill_color(240, 248, 255)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 5,
        f'Ventana: {d["ventana"]} | Consultas post-pago excluidas: {d["n_late"]:,}',
        new_x='LMARGIN', new_y='NEXT', fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.ln(2)

    # Tabla por canal
    col_w = [40, 45, 30]
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(['Canal', 'Inscriptos (Causal)', '% Partic.'], col_w):
        pdf.cell(w, 7, h, border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 9)

    for i, canal in enumerate(CANALES_ORDER):
        c = d['por_canal'][canal]
        fill = (i % 2 == 0)
        if fill:
            pdf.set_fill_color(235, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w[0], 6, canal, border=1, fill=True)
        pdf.cell(col_w[1], 6, f'{c["conv"]:,}', border=1, fill=True, align='R')
        pdf.cell(col_w[2], 6, f'{c["pct"]}%', border=1, fill=True, align='R')
        pdf.ln()

    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(235, 245, 255)
    pdf.cell(col_w[0], 6, 'Total Unico', border=1, fill=True)
    pdf.cell(col_w[1], 6, f'{d["total_unico"]:,}', border=1, fill=True, align='R')
    pdf.cell(col_w[2], 6, '100%', border=1, fill=True, align='R')
    pdf.ln(4)

    pdf.set_fill_color(255, 255, 255)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(0, 5,
        f'Multi-canal: 1 canal={d["n_1canal"]:,} | 2 canales={d["n_2canales"]:,} | 3+={d["n_3plus"]:,}',
        new_x='LMARGIN', new_y='NEXT')

    if d['total_inscriptos'] > 0:
        pdf.cell(0, 5,
            f'Inscriptos sin lead/match: {d["inscriptos_sin_match"]:,} de {d["total_inscriptos"]:,} ({d["pct_sin_match"]}%)',
            new_x='LMARGIN', new_y='NEXT')

    pdf.ln(2)
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 4,
        'Modelo Causal: solo se cuentan consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago. '
        'Any-Touch: un inscripto se cuenta en CADA canal con contacto causal (suma > 100%).')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
