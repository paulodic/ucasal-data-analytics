"""
03_journey_sankey.py
Análisis de journeys (rutas de consulta) de leads por segmento.

Agrupa leads por persona (DNI > Email > Nombre+Tel), reconstruye los primeros
3 touchpoints de cada journey, calcula días hasta inscripción, y genera un
Sankey diagram del flujo + tabla de tiempos en Excel.

ENTRADA: outputs/Data_Base/<Segmento>/reporte_marketing_leads_completos.csv
SALIDA (outputs/<Segmento>/Otros_Reportes/):
  - reporte_journey_tiempos.xlsx  -> Tabla de journeys con touchpoints y tiempos
  - memoria_tecnica.md            -> Documentación del proceso
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================
base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir = os.path.join(base_dir, "outputs", segmento, "Otros_Reportes")
os.makedirs(output_dir, exist_ok=True)
base_output_dir = os.path.join(base_dir, "outputs", "Data_Base", segmento)

leads_file = os.path.join(base_output_dir, "reporte_marketing_leads_completos.csv")
inscriptos_file = os.path.join(base_output_dir, "reporte_marketing_inscriptos_origenes.csv")

print("Leyendo reporte de leads completo...")
df = pd.read_csv(leads_file, low_memory=False)

# ==========================================
# PREPARACIÓN DE DATOS PARA JOURNEY
# ==========================================
print("Procesando journeys (rutas de consulta de leads)...")

# Identificar a una "Persona" única. Usaremos DNI, si no hay, Correo. Si no, Nombre+Tel.
# Para simplificar, creamos una clave única concatenando los valores que existan.
def get_person_id(row):
    dni = str(row.get('DNI', '')).strip()
    correo = str(row.get('Correo', '')).strip().lower()
    if dni and dni != 'nan':
        return f"DNI_{dni}"
    if correo and correo != 'nan':
        return f"EMAIL_{correo}"
    
    tel = str(row.get('Telefono', '')).strip()
    nom = str(row.get('Nombre', '')).strip().lower()
    return f"NOMTEL_{nom}_{tel}"

df['Persona_ID'] = df.apply(get_person_id, axis=1)

# Asegurar que Fecha de creación sea datetime
df['Consulta_Fecha'] = pd.to_datetime(df['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

# Ordenar por Persona y Fecha de Consulta
df = df.sort_values(by=['Persona_ID', 'Consulta_Fecha'])

# Agrupar por Persona
journey_data = []

for persona_id, group in df.groupby('Persona_ID'):
    # ignora los que no tengan datos válidos
    if persona_id == "NOMTEL_nan_nan":
        continue
        
    total_consultas = len(group)
    primera_fecha = group['Consulta_Fecha'].min()
    ultima_fecha = group['Consulta_Fecha'].max()
    
    # Determinar si se inscribió analizando el Match_Tipo de cualquiera de sus registros
    inscripto = any(group['Match_Tipo'].astype(str).str.contains('Exacto', case=False, na=False))
    
    # Intentar obtener la Fecha de Pago si existe en alguna de las filas
    if 'Insc_Fecha Pago' in group.columns:
        fechas_pago = pd.to_datetime(group['Insc_Fecha Pago'], errors='coerce').dropna()
        fecha_pago = fechas_pago.min() if not fechas_pago.empty else pd.NaT
    else:
        fecha_pago = pd.NaT

    # Alternativa: Fecha Aplicación
    if pd.isna(fecha_pago) and 'Insc_Fecha Aplicación' in group.columns:
         fechas_app = pd.to_datetime(group['Insc_Fecha Aplicación'], errors='coerce').dropna()
         fecha_pago = fechas_app.min() if not fechas_app.empty else pd.NaT

    dias_hasta_inscripcion = np.nan
    if inscripto and pd.notna(fecha_pago) and pd.notna(primera_fecha):
        dias_hasta_inscripcion = (fecha_pago - primera_fecha).days
        # Si la fecha de pago es anterior a la consulta (datos sucios), la dejamos en 0
        if dias_hasta_inscripcion < 0:
            dias_hasta_inscripcion = 0
            
    # Trailing sources (rutas de canales/fuentes)
    # Ejemplo: "Google -> Meta -> Directo"
    fuentes = group['FuenteLead'].fillna('Desconocido').astype(str).tolist()
    
    # Representación limitada para el Sankey (hasta 3 toques)
    t1 = fuentes[0] if len(fuentes) > 0 else "None"
    t2 = fuentes[1] if len(fuentes) > 1 else "None"
    t3 = fuentes[2] if len(fuentes) > 2 else "None"
    
    journey_data.append({
        'Persona_ID': persona_id,
        'Nombre_Ejemplo': group['Nombre'].iloc[0],
        'DNI_Ejemplo': group['DNI'].iloc[0],
        'Total_Consultas': total_consultas,
        'Primera_Consulta': primera_fecha,
        'Fecha_Inscripcion': fecha_pago,
        'Dias_hasta_Inscripcion': dias_hasta_inscripcion,
        'Inscripto': "Sí" if inscripto else "No",
        'Ruta_Fuentes': " -> ".join(fuentes),
        'Touch_1': t1,
        'Touch_2': t2,
        'Touch_3': t3
    })

df_journey = pd.DataFrame(journey_data)

# Exportar el Excel
output_excel = os.path.join(output_dir, "reporte_journey_tiempos.xlsx")
df_journey.to_excel(output_excel, index=False)
print(f"-> Reporte Journey guardado en: {output_excel}")


print("¡Proceso de Journey finalizado!")

# ==========================================
# MEMORIA TÉCNICA
# ==========================================
from datetime import datetime as _dt
total_personas = len(df_journey)
total_inscriptos_j = len(df_journey[df_journey['Inscripto'] == 'Sí'])
total_no_inscriptos = len(df_journey[df_journey['Inscripto'] == 'No'])
avg_consultas = df_journey['Total_Consultas'].mean() if not df_journey.empty else 0
avg_dias = df_journey.loc[df_journey['Inscripto'] == 'Sí', 'Dias_hasta_Inscripcion'].mean() if total_inscriptos_j > 0 else 0

memoria = f"""# Memoria Técnica: Journey del Estudiante (Sankey)

**Generado:** {_dt.now().strftime('%Y-%m-%d %H:%M:%S')}
**Segmento:** {segmento}
**Script:** `03_journey_sankey.py`

## Fuentes de Datos
- Leads: `{leads_file}`
- Inscriptos: `{inscriptos_file}`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Personas únicas analizadas | {total_personas:,} |
| Personas inscriptas (con pago confirmado) | {total_inscriptos_j:,} |
| Personas no inscriptas | {total_no_inscriptos:,} |
| Promedio consultas por persona | {avg_consultas:.1f} |
| Promedio días hasta inscripción | {avg_dias:.1f} |

## Lógica del Journey
- **Agrupación:** Se agrupan leads por `DNI` (persona única)
- **Ruta de fuentes:** Se concatenan los valores de `FuenteLead` por orden cronológico de consulta
- **Touch 1/2/3:** Primeros tres contactos con fuentes diferentes
- **Inscripto:** `"Sí"` si la persona tiene al menos un match Exacto con un inscripto
- **Días hasta inscripción:** Diferencia entre primera consulta (`Consulta: Fecha de creación`) y `Fecha Pago`/`Insc_Fecha Pago`

## Archivos de Salida
- Excel: `{output_excel}`
"""
with open(os.path.join(output_dir, 'memoria_tecnica.md'), 'w', encoding='utf-8') as f:
    f.write(memoria)
print(f"-> Memoria técnica generada en: {output_dir}")
