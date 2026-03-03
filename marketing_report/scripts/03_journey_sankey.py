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
try:
    df = pd.read_excel(leads_file)
except Exception as e:
    print(f"Error leyendo Excel ({e}). Probando fallback a CSV...")
    df = pd.read_csv(leads_file.replace('.xlsx', '.csv'))

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
df['Consulta_Fecha'] = pd.to_datetime(df['Consulta: Fecha de creación'], errors='coerce')

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
    inscripto = any(group['Match_Tipo'].astype(str).str.contains(r'Si \(Lead|Match Fuzzy', case=False, na=False))
    
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
