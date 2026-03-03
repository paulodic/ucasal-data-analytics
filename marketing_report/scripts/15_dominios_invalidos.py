"""15_dominios_invalidos.py
Análisis de dominios de correo inválidos o sospechosos.
Identifica correos con dominios que no existen (ej: gmail.con, gmail.com.ar)
y estima cuánto aumentaría la tasa de match si se corrigieran.

LÓGICA:
  1. Carga solo las columnas 'Correo' y 'Match_Tipo' del CSV maestro (usecols).
  2. Extrae el dominio de cada correo (parte después del @).
  3. Cruza contra un diccionario de CORRECCIONES CONOCIDAS (typo → correcto).
  4. Para cada typo, calcula cuántos leads matchearon y cuántos no.
  5. Estima matches recuperables aplicando la tasa del dominio correcto.

DESCUBRIMIENTO CLAVE:
  gmail.com.ar NO EXISTE como dominio. Es el error más común en Argentina
  (434 leads afectados). Ver README_DEV.md Lección 6.

OUTPUT: outputs/Calidad_Datos/dominios_invalidos.[md/xlsx]
"""
import pandas as pd
import os
from datetime import datetime

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", "Calidad_Datos")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base")
leads_csv = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_csv = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

# Dominios válidos comunes (los que realmente existen)
DOMINIOS_VALIDOS = {
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'live.com',
    'hotmail.com.ar', 'yahoo.com.ar', 'outlook.com.ar', 'live.com.ar',
    'hotmail.es', 'yahoo.es', 'outlook.es',
    'icloud.com', 'protonmail.com', 'aol.com', 'msn.com',
    'ucasal.edu.ar'  # dominio institucional
}

# ======================================================
# DICCIONARIO DE CORRECCIONES CONOCIDAS
# ======================================================
# Mapeo de dominios con errores de tipeo → dominio correcto.
# Se agregan nuevos typos a medida que se descubren en la sección 2 del output.
# NOTA: gmail.com.ar NO EXISTE como servicio de Google. Es un error
#       común de usuarios argentinos que asumen que existe un dominio .com.ar
CORRECCIONES = {
    'gmail.con': 'gmail.com',
    'gmail.com.ar': 'gmail.com',  # NO EXISTE - error común en Argentina
    'gmai.com': 'gmail.com',
    'gmial.com': 'gmail.com',
    'gmal.com': 'gmail.com',
    'gamil.com': 'gmail.com',     # inversión de letras
    'gnail.com': 'gmail.com',
    'gmail.co': 'gmail.com',
    'gmail.cm': 'gmail.com',
    'gmail.om': 'gmail.com',
    'gmail.coom': 'gmail.com',    # doble 'o'
    'gmail.comm': 'gmail.com',    # doble 'm'
    'hotmail.con': 'hotmail.com',
    'hotamil.com': 'hotmail.com',
    'hotmal.com': 'hotmail.com',
    'hotmil.com': 'hotmail.com',
    'hotamail.com': 'hotmail.com',
    'outlook.con': 'outlook.com',
    'outllok.com': 'outlook.com',
    'outlok.com': 'outlook.com',
    'yahoo.con': 'yahoo.com',
    'yaho.com': 'yahoo.com',
    'yahooo.com': 'yahoo.com',
    'live.con': 'live.com',
    'iclud.com': 'icloud.com',
    'icloud.con': 'icloud.com',
}

# ======================================================
# CARGA Y PREPARACIÓN DE DATOS
# ======================================================
# Solo cargamos 3 columnas para evitar problemas de memoria con el CSV grande.
print("Cargando datos...")
try:
    df_leads = pd.read_csv(leads_csv, usecols=['Correo', 'Match_Tipo', 'Id. candidato/contacto'], low_memory=False)
except Exception:
    df_leads = pd.read_csv(leads_csv, low_memory=False)

# Limpiar correos: minúsculas, sin espacios
df_leads = df_leads.dropna(subset=['Correo'])
df_leads['Correo'] = df_leads['Correo'].astype(str).str.lower().str.strip()
# Extraer dominio: todo lo que está después del '@'
df_leads['Domain'] = df_leads['Correo'].apply(lambda x: x.split('@')[-1] if '@' in x else '')

# Columna binaria: 1 si matcheo exacto, 0 si no
df_leads['Es_Exacto'] = df_leads['Match_Tipo'].astype(str).str.contains('Exacto', case=False, na=False).astype(int)

# Obtener todos los dominios y su frecuencia
all_domains = df_leads['Domain'].value_counts().reset_index()
all_domains.columns = ['Domain', 'Total_Leads']

# Identificar dominios sospechosos (que son typos de dominios conocidos)
print("Detectando dominios inválidos y sospechosos...")

# Encontrar dominios que están en las correcciones conocidas
typo_domains = all_domains[all_domains['Domain'].isin(CORRECCIONES.keys())].copy()
typo_domains['Dominio_Correcto'] = typo_domains['Domain'].map(CORRECCIONES)

# También detectar dominios no comunes con pocas apariciones que se parezcan a comunes
# Buscar dominios con < 50 leads que no estén en los válidos
small_domains = all_domains[
    (all_domains['Total_Leads'] >= 5) & 
    (~all_domains['Domain'].isin(DOMINIOS_VALIDOS)) &
    (all_domains['Domain'] != '') &
    (~all_domains['Domain'].isin(CORRECCIONES.keys()))
].copy()

# Para los typos conocidos, analizar su impacto en el match
print("Calculando impacto potencial...")

md_content = "# Análisis de Dominios de Correo Inválidos\n\n"
md_content += "Este informe identifica dominios de correo electrónico que no existen o son errores de tipeo, "
md_content += "y estima cuántos leads podrían recuperarse si se corrigiesen.\n\n"

# Análisis detallado por typo
results = []
for _, row in typo_domains.iterrows():
    typo = row['Domain']
    correcto = row['Dominio_Correcto']
    total = row['Total_Leads']
    
    # Cuantos de este typo matchearon a pesar del error en el dominio
    leads_typo = df_leads[df_leads['Domain'] == typo]
    matcheados = leads_typo['Es_Exacto'].sum()
    no_matcheados = total - matcheados
    
    # Obtener la tasa de match del dominio CORRECTO como referencia
    # Ej: si gmail.com tiene tasa de 3.67%, asumimos que los leads con gmail.con
    # tendrían esa misma tasa si se les corrigiera el dominio
    leads_correcto = df_leads[df_leads['Domain'] == correcto]
    tasa_correcto = (leads_correcto['Es_Exacto'].sum() / len(leads_correcto) * 100) if len(leads_correcto) > 0 else 0
    
    # Estimación conservadora: aplicar tasa del dominio correcto a los no matcheados
    # Esto NO garantiza que matcheen, solo estima el potencial
    matches_esperados = int(no_matcheados * tasa_correcto / 100)
    
    results.append({
        'Dominio_Typo': typo,
        'Dominio_Correcto': correcto,
        'Total_Leads': total,
        'Matcheados_Actuales': matcheados,
        'No_Matcheados': no_matcheados,
        'Tasa_Dominio_Correcto_%': round(tasa_correcto, 2),
        'Matches_Recuperables_Est': matches_esperados
    })

df_results = pd.DataFrame(results).sort_values('Total_Leads', ascending=False)

total_recuperables = df_results['Matches_Recuperables_Est'].sum()
total_afectados = df_results['Total_Leads'].sum()

md_content += "## 1. Dominios con Errores de Tipeo Conocidos\n\n"
md_content += f"Se detectaron **{len(df_results)}** dominios con errores de tipeo, afectando **{total_afectados:,}** leads.\n"
md_content += f"**Estimación de matches recuperables si se corrigiesen:** {total_recuperables:,} nuevos matches potenciales.\n\n"
md_content += df_results.to_markdown(index=False) + "\n\n"

md_content += "### Cómo se calcula la estimación\n"
md_content += "Se toma la tasa de match del dominio correcto (ej: gmail.com tiene ~5.5%) "
md_content += "y se aplica a los leads no matcheados del dominio con typo. "
md_content += "Esto da una estimación conservadora de cuántos matches se recuperarían.\n\n"

# Dominios sospechosos no clasificados
md_content += "## 2. Otros Dominios Poco Comunes (Revisión Manual)\n\n"
md_content += "Los siguientes dominios tienen 5 o más leads pero no son proveedores de correo comunes. "
md_content += "Podrían ser dominios corporativos legítimos, institucionales, o errores.\n\n"

# Agregar stats de match para estos
susp_results = []
for _, row in small_domains.head(30).iterrows():
    dom = row['Domain']
    tot = row['Total_Leads']
    leads_dom = df_leads[df_leads['Domain'] == dom]
    matchs = leads_dom['Es_Exacto'].sum()
    tasa = round(matchs / tot * 100, 2) if tot > 0 else 0
    susp_results.append({
        'Domain': dom,
        'Total_Leads': tot,
        'Matcheados': matchs,
        'Tasa_Match_%': tasa
    })

df_sospechosos = pd.DataFrame(susp_results)
md_content += df_sospechosos.to_markdown(index=False) + "\n\n"

# Guardar
print("Guardando resultados...")
with open(os.path.join(output_dir, 'dominios_invalidos.md'), 'w', encoding='utf-8') as f:
    f.write(md_content)

with pd.ExcelWriter(os.path.join(output_dir, 'dominios_invalidos.xlsx')) as writer:
    df_results.to_excel(writer, sheet_name='Typos_Conocidos', index=False)
    df_sospechosos.to_excel(writer, sheet_name='Dominos_Sospechosos', index=False)

print(f"Proceso Finalizado. {len(df_results)} typos detectados, {total_recuperables:,} matches recuperables estimados.")
print(f"Archivos guardados en outputs/Calidad_Datos/")
