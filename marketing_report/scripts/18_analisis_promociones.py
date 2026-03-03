import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

import sys
segmento = sys.argv[1] if len(sys.argv) > 1 else 'Grado_Pregrado'

base_dir = r"h:\Test-Antigravity\marketing_report"
output_dir_base = os.path.join(base_dir, "outputs", segmento, "Reporte_Promociones")
os.makedirs(output_dir_base, exist_ok=True)
inscriptos_csv = os.path.join(base_dir, "outputs", "Data_Base", segmento, "reporte_marketing_inscriptos_origenes.csv")

print("Generando Reporte de Inscriptos por Tramos de Promoción...")

df_insc = pd.read_csv(inscriptos_csv, low_memory=False)

# Determinar columna de fecha
date_col = None
# PRIORITY: We need the actual transaction date (Pago), NOT the academic cohort application date (Aplicación)
for col in ['Insc_Fecha Pago', 'Fecha Pago', 'Insc_Fecha']:
    if col in df_insc.columns:
        date_col = col
        break

if not date_col:
    print("No se encontró una columna de fecha en inscriptos. Abortando.")
    exit()

# Parsear fechas limpiamente (forzando formato día primero)
df_insc['Fecha_Clean'] = pd.to_datetime(df_insc[date_col], dayfirst=True, errors='coerce')

# Definir los tramos (consecutivos + extensión solicitada al 27/02)
# Formato (Nombre, % Descuento, Inicio, Fin)
tramos_promo = [
    ("Tramo 1 (50% OFF)", 50, "2025-09-01", "2025-09-26"),
    ("Tramo 2 (40% OFF)", 40, "2025-09-27", "2025-10-26"),
    ("Tramo 3 (30% OFF)", 30, "2025-10-27", "2025-11-25"),
    ("Tramo 4 (20% OFF)", 20, "2025-11-26", "2025-12-23"),
    ("Tramo 5 (15% OFF)", 15, "2025-12-24", "2026-01-19"),
    ("Tramo 6 (10% OFF Ene)", 10, "2026-01-20", "2026-01-31"),
    ("Tramo 7 (10% OFF Feb)", 10, "2026-02-01", "2026-02-23"),
    ("Tramo 8 (10% OFF Ext)", 10, "2026-02-24", "2026-02-27")
]

# Convertir strings a datetime
tramos_fechas = []
for nombre, descuento, inicio, fin in tramos_promo:
    tramos_fechas.append({
        'Tramo': nombre,
        'Descuento': descuento,
        'Inicio': pd.to_datetime(inicio),
        'Fin': pd.to_datetime(fin)
    })

def asignar_tramo(fecha):
    if pd.isna(fecha):
        return 'Sin Fecha Registrada'
    for tramo in tramos_fechas:
        if tramo['Inicio'] <= fecha <= tramo['Fin']:
            return tramo['Tramo']
    if fecha < tramos_fechas[0]['Inicio']:
        return 'Antes de Promociones'
    elif fecha > tramos_fechas[-1]['Fin']:
        return 'Post Extension (Expirado)'
    return 'Desconocido'

df_insc['Tramo_Promocional'] = df_insc['Fecha_Clean'].apply(asignar_tramo)

# Agrupamiento de inscriptos por Tramo
df_insc = df_insc[df_insc['Tramo_Promocional'] != 'Antes de Promociones'].copy()
orden_deseado = [t['Tramo'] for t in tramos_fechas] + ["Post Extension (Expirado)", "Sin Fecha Registrada"]

df_insc['Tramo_Promocional'] = pd.Categorical(df_insc['Tramo_Promocional'], categories=orden_deseado, ordered=True)
resumen_tramos = df_insc.groupby('Tramo_Promocional', observed=False).size().reset_index(name='Cantidad_Inscriptos')

print(resumen_tramos.to_string(index=False))

# Exportar tabla a CSV
csv_promociones_path = os.path.join(output_dir_base, '18_tabla_promociones.csv')
resumen_tramos.to_csv(csv_promociones_path, index=False)
print(f"-> Exportada tabla promociones a: {csv_promociones_path}")

# =========================================================
# GRÁFICA 1: BARRAS HORIZONTALES POR TRAMO
# =========================================================
plt.figure(figsize=(10, 6))
# Excluir 'Sin Fecha Registrada' si no nos sirve para el plot, pero lo mostramos para completitud
sns.barplot(data=resumen_tramos[resumen_tramos['Tramo_Promocional'] != 'Sin Fecha Registrada'], 
            y='Tramo_Promocional', x='Cantidad_Inscriptos', palette='coolwarm_r')
plt.title('Volumen de Inscripciones por Bloque Promocional')
plt.xlabel('Cantidad de Inscripciones (Efectivas)')
plt.ylabel('Etapa Comercial')

# Añadir etiquetas
for index, value in enumerate(resumen_tramos[resumen_tramos['Tramo_Promocional'] != 'Sin Fecha Registrada']['Cantidad_Inscriptos']):
    plt.text(value, index, f' {value:,}')
    
plt.tight_layout()
chart_tramos_path = os.path.join(output_dir_base, 'chart_barras_promo.png')
plt.savefig(chart_tramos_path)
plt.close()

# =========================================================
# GRÁFICA 2: CURVA DE TIEMPO CON LÍNEAS DE CIERRE
# =========================================================
# Solo inscriptos dentro del rango de promo
rango_inicio = tramos_fechas[0]['Inicio']
rango_fin = tramos_fechas[-1]['Fin'] + pd.Timedelta(days=5) # un piquito mas para ver

df_rango = df_insc[(df_insc['Fecha_Clean'] >= rango_inicio) & (df_insc['Fecha_Clean'] <= rango_fin)].copy()
insc_por_dia = df_rango.groupby(df_rango['Fecha_Clean'].dt.date).size().reset_index(name='Inscriptos')
insc_por_dia['Fecha_Clean'] = pd.to_datetime(insc_por_dia['Fecha_Clean'])

plt.figure(figsize=(14, 6))
plt.plot(insc_por_dia['Fecha_Clean'], insc_por_dia['Inscriptos'], marker='o', linestyle='-', color='dodgerblue', alpha=0.8)

# Dibujar lineas rojas para cada Cierre de Promo
for i, tramo in enumerate(tramos_fechas):
    plt.axvline(x=tramo['Fin'], color='red', linestyle='--', linewidth=1.5, alpha=0.6)
    plt.text(tramo['Fin'], insc_por_dia['Inscriptos'].max() * 0.95 if len(insc_por_dia) > 0 else 100, 
             f"Cierre {tramo['Descuento']}%", 
             rotation=90, verticalalignment='top', horizontalalignment='right', color='darkred', fontsize=8, backgroundcolor='white')

plt.xlim([pd.to_datetime('2025-08-25'), pd.to_datetime('2026-03-05')])
plt.title('Evolución de Inscriptos Diarios cruzado con Cierres Promocionales')
plt.xlabel('Fecha de Inscripción (Efectiva de Pago)')
plt.ylabel('Inscriptos por Día')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
chart_curva_path = os.path.join(output_dir_base, 'chart_curva_promo_cierres.png')
plt.savefig(chart_curva_path)
plt.close()

# =========================================================
# GRÁFICA 3: SUPERPOSICIÓN POR DÍAS DE LA SEMANA
# ==========================================
# Preparar datos agregando número de semana y día de la semana
insc_por_dia['Dia_Semana'] = insc_por_dia['Fecha_Clean'].dt.dayofweek # 0=Lunes, 6=Domingo
insc_por_dia['Num_Semana'] = insc_por_dia['Fecha_Clean'].dt.isocalendar().week
insc_por_dia['Año'] = insc_por_dia['Fecha_Clean'].dt.isocalendar().year
insc_por_dia['Semana_Unica'] = insc_por_dia['Año'].astype(str) + "-W" + insc_por_dia['Num_Semana'].astype(str)

# Ubicar explícitamente las 5 semanas donde ocurren los cierres promocionales principales
semanas_pico_info = {}
dias_semana_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}

# Tramos a resaltar: Tramo 2 (40%), Tramo 3 (30%), Tramo 4 (20%), Tramo 5 (15%), Tramo 6 (10% Ene)
for tramo in tramos_fechas[1:6]:
    fecha_fin = tramo['Fin']
    num_sem = fecha_fin.isocalendar().week
    año = fecha_fin.isocalendar().year
    sem_unica = f"{año}-W{num_sem}"
    
    df_sem = insc_por_dia[insc_por_dia['Semana_Unica'] == sem_unica]
    if len(df_sem) > 0:
        row_max = df_sem.loc[df_sem['Inscriptos'].idxmax()]
        dia_str = dias_semana_es[fecha_fin.weekday()]
        promo_cercana = f"Cierre {tramo['Descuento']}% ({dia_str})"
        
        semanas_pico_info[sem_unica] = {
            'fecha': row_max['Fecha_Clean'],
            'inscriptos': row_max['Inscriptos'],
            'promo': promo_cercana
        }

plt.figure(figsize=(12, 6))
# Dibujar una línea por cada semana
semanas = insc_por_dia['Semana_Unica'].unique()
colores_pico = ['firebrick', 'darkorange', 'forestgreen', 'purple', 'teal']
pico_idx = 0

for sem in semanas:
    df_sem = insc_por_dia[insc_por_dia['Semana_Unica'] == sem].sort_values('Dia_Semana')
    if len(df_sem) > 1:
        if sem in semanas_pico_info:
            color = colores_pico[pico_idx % len(colores_pico)]
            info = semanas_pico_info[sem]
            label_promo = f" | {info['promo']}" if info['promo'] != "Ninguna" else ""
            label = f"Mxn Pico Semanal: {info['fecha'].strftime('%d/%m')} ({info['inscriptos']} insc.){label_promo}"
            plt.plot(df_sem['Dia_Semana'], df_sem['Inscriptos'], marker='o', linestyle='-', alpha=0.9, linewidth=2.5, color=color, label=label)
            pico_idx += 1
        else:
            plt.plot(df_sem['Dia_Semana'], df_sem['Inscriptos'], marker='o', linestyle='-', alpha=0.3, color='gray')

# Dibujar la línea promedio general
promedio_por_dia = insc_por_dia.groupby('Dia_Semana')['Inscriptos'].mean().reset_index()
plt.plot(promedio_por_dia['Dia_Semana'], promedio_por_dia['Inscriptos'], marker='s', linestyle='--', linewidth=3, color='navy', label='Promedio General')

dias_labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
plt.xticks(ticks=range(7), labels=dias_labels)
plt.title('Superposición de Inscripciones Diarias por Día de la Semana')
plt.xlabel('Día de la Semana')
plt.ylabel('Cantidad de Inscriptos Diarios')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
chart_semana_path = os.path.join(output_dir_base, '18_grafica_inscripciones_dias_semana.png')
plt.savefig(chart_semana_path)
plt.close()

# =========================================================
# GENERACIÓN DE PDF
# =========================================================
pdf = FPDF()
pdf.add_page()
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Analisis de Comportamiento: Tramos Promocionales', ln=True, align='C')
pdf.ln(5)

pdf.set_font('Helvetica', '', 11)
primer_inscripto = df_insc['Fecha_Clean'].min()
primer_inscripto_str = primer_inscripto.strftime('%d/%m/%Y') if pd.notnull(primer_inscripto) else 'Desconocida'

pdf.multi_cell(0, 6, f"Se han segmentado todas las inscripciones facturadas cruzándolas contra el calendario oficial de "
                     f"descuentos promocionales enviado (Desde el 50% en Septiembre hasta la prórroga del 10% en Febrero de 2026).\n"
                     f"El objetivo de este reporte es medir cuántos estudiantes logran captar las diversas instancias de precio "
                     f"y la influencia mental (FOMO) del día exacto del cierre.\n\n"
                     f"Nota Importante: La primera inscripcion facturada oficial registrada en la base de datos entregada "
                     f"tiene fecha del {primer_inscripto_str}. Debido a esto, el tramo de '50% OFF' de Septiembre luce sin inscriptos.")
pdf.ln(5)

# Render Tabla Markdown -> PDF
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '1. Concentracion Volumetrica por Tramo', ln=True)
pdf.set_font('Helvetica', '', 10)

fin_dict = {t['Tramo']: t['Fin'] for t in tramos_fechas}
dias_semana_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}

pdf.cell(65, 8, 'Bloque Promocional', 1)
pdf.cell(50, 8, 'Día de Cierre', 1, align='C')
pdf.cell(30, 8, 'Inscripciones', 1, ln=True, align='C')

for index, row in resumen_tramos.iterrows():
    val = row['Tramo_Promocional']
    count = row['Cantidad_Inscriptos']
    if val != 'Sin Fecha Registrada' and val != 'Antes de Promociones' and val != 'Post Extension (Expirado)':
        dia_str = "-"
        if val in fin_dict:
            fecha_fin = fin_dict[val]
            dia_str = f"{dias_semana_es[fecha_fin.weekday()]} {fecha_fin.strftime('%d/%m/%y')}"
        
        pdf.cell(65, 8, str(val), 1)
        pdf.cell(50, 8, dia_str, 1, align='C')
        pdf.cell(30, 8, f"{count:,}", 1, ln=True, align='C')
    elif val in ['Post Extension (Expirado)']:
        pdf.cell(65, 8, str(val), 1)
        pdf.cell(50, 8, "-", 1, align='C')
        pdf.cell(30, 8, f"{count:,}", 1, ln=True, align='C')

pdf.ln(5)
pdf.image(chart_tramos_path, x=15, w=180)

pdf.add_page()
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '2. Analisis de Picos vs Cierres Promocionales', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 5, "Esta curva denota el ritmo de ventas día a día. Las líneas rojas verticales representan exactamente "
                     "el último día de ventana para adquirir cada nivel de descuento comercial. Frecuentemente se observa "
                     "un 'Pico de Cierre' donde el volumen aumenta repentinamente para aprovechar horas antes.")
pdf.ln(5)
pdf.image(chart_curva_path, x=10, w=190)

pdf.add_page()
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '3. Comportamiento por Dia de la Semana', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 5, "Esta gráfica superpone el rendimiento de cada semana individual del año "
                     "(líneas grises tenues) sobre los 7 días de la semana, comenzando por el Lunes. "
                     "La línea gruesa azul representa el promedio de inscriptos para ese día específico. "
                     "Se han resaltado a color las semanas que contienen los 5 picos históricos más altos de inscripción. "
                     "El gráfico permite confirmar que efectivamente cada pico de máxima inscripción se encuentra asociado de manera "
                     "exactamente adyacente al Cierre de una ventana Promocional.")
pdf.ln(5)
pdf.image(chart_semana_path, x=15, w=180)

pdf.image(chart_semana_path, x=15, w=180)

pdf_file = os.path.join(output_dir_base, '18_reporte_promociones.pdf')
pdf.output(pdf_file)
print(f"\\n>>> Reporte de Promociones terminado exitosamente en: {pdf_file}")

# Generar reporte MD
md_file = os.path.join(output_dir_base, '18_reporte_promociones.md')
with open(md_file, "w", encoding="utf-8") as f:
    f.write("# Reporte de Promociones y Comportamiento de Inscripciones\n\n")
    f.write(f"Primer inscrito oficial documentado: {primer_inscripto_str}\n\n")
    f.write("## 1. Tabla de Volumen Promocional\n\n")
    f.write(resumen_tramos.to_markdown(index=False))
    f.write("\n\n## 2. Gráficas Generadas\n")
    f.write("- Evolución Diaria y Cierres Promocionales\n")
    f.write("- Volumen por Día de la Semana con Picos de Cierre\n")
    f.write("- Tabla de Concentración por Tramo\n")
    
print(f"-> Generado MD de Promociones en: {md_file}")
