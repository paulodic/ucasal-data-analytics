# 🚀 Marketing Report Automation - DEV HANDOVER

**Última actualización:** 6 de Marzo de 2026
**Estado del Proyecto:** ✅ **Estable y Funcional (Fase 4 — Boletas + Embudo)**

## 📌 Estado Actual del Desarrollo
El esquema de reportes está 100% automatizado, procesando bases de datos de Leads, Inscriptos y Boletas mediante ~20 scripts secuenciales.
Se ha completado la integración de todos los componentes gráficos, PDF y Excel, incluyendo reportes avanzados de **UTMs, Google Ads, Fuzzy Matching, Análisis de Leads No Matcheados, Presupuesto/ROI, Atribución Causal, Bot Consolidado y Embudo de Conversión con Sankeys**. Toda la salida de datos se organiza dinámicamente en subcarpetas dentro de `outputs/`.

---

## 📁 Arquitectura de Carpetas
```text
h:\Test-Antigravity\marketing_report\
├── data/
│   └── 1_raw/          <- (Datasets originales Excel de Salesforce/Sistemas)
│       ├── leads_salesforce/
│       ├── inscriptos/
│       └── boletas/        <- Boletas generadas sin pago (paso previo a inscripción)
├── outputs/            <- (GENERADO POR LOS SCRIPTS. No tocar manualmente salvo para auditoria)
│   ├── Data_Base/
│   ├── Informe_Analitico/
│   ├── Analisis_UTM/
│   ├── Google_Ads_Deep_Dive/
│   ├── Facebook_Deep_Dive/
│   ├── Bot_Deep_Dive/
│   ├── Analisis_No_Matcheados/
│   ├── Calidad_Datos/
│   ├── Bot_Consolidado/
│   ├── Presupuesto_ROI/
│   ├── Presupuesto_ROI_Causal/
│   ├── Embudo_Conversion/
│   ├── Reporte_Asesores/
│   └── Reporte_Promociones/
└── scripts/            <- (Lógica Core)
    ├── 00_run_all.py ... 23_embudo_conversion.py
```

---

## ⚙️ Dependencias Clave (pip install)
Para ejecutar la pipeline de principio a fin, asegúrate de tener instaladas las siguientes librerías:
- `pandas` y `numpy`
- `thefuzz` y `Levenshtein` (Para lógica de strings y Fuzzy Matches)
- `matplotlib`, `seaborn` y `plotly.graph_objects` (Para Sankey y visuales)
- `kaleido` (Para exportar gráficos Plotly a PNG — requerido por `23_embudo_conversion.py`)
- `fpdf2` (¡Importante! Usar `fpdf2` y no `fpdf` heredado para soporte de tablas complejas y UTF-8)
- `tabulate` (Para conversión rápida de pandas a Markdown)
- `openpyxl` y `xlrd` (Para lectura/escritura de Excel `.xlsx` y `.xls`)

---

## 📜 Secuencia de Ejecución (Pipeline)

La ejecución consta de dos fases:

### Fase 0 — Generación de bases maestras (manual)

**`02_cruce_datos.py`** — Se ejecuta PRIMERO, manualmente. Limpia y unifica las bases raw de leads, inscriptos y boletas. Genera CSVs maestros en `outputs/Data_Base/`. Aplica cruce exacto (DNI→Email→Tel×6) + fuzzy email + fuzzy nombre con multiprocessing. También cruza leads sin inscripto contra boletas sin pago.

> **IMPORTANTE:** `00_run_all.py` NO ejecuta `02_cruce_datos.py`. Siempre correrlo primero.

### Fase 1 — Scripts analíticos por segmento (via `00_run_all.py`)

Cada script recibe el nombre del segmento como argumento y se ejecuta 3 veces (Grado_Pregrado, Cursos, Posgrados):

1. **`03_journey_sankey.py`**: Journey del estudiante — agrupa leads por persona, construye ruta de fuentes y tiempos hasta inscripción.
2. **`16_analisis_matriculadas.py`**: Análisis de leads matriculadas por segmento.
3. **`18_analisis_promociones.py`**: Análisis de promociones (**solo Grado_Pregrado**, se omite para otros segmentos).
4. **`17_reporte_asesores.py`**: Reporte de rendimiento por asesor/propietario de consulta.
5. **`04_reporte_final.py`**: Tablas resumen, análisis multi-touch, composición de inscriptos, gráficos comparativos por campaña.
6. **`07_pdf_completo.py`**: Compila el Gran Informe Analítico general (~24 páginas, landscape).
7. **`09_utm_conversion.py`**: Análisis de conversión por UTM Source/Medium/Campaign.
8. **`10_google_ads_deep_dive.py`**: Informe exclusivo de rendimiento Google Ads.
9. **`13_facebook_deep_dive.py`**: Informe exclusivo de tráfico Meta (Facebook/Instagram). Filtra por UTM + `FuenteLead = 18`.
10. **`14_bot_deep_dive.py`**: Informe exclusivo del Bot/Chatbot. Filtra por `FuenteLead = 907`.
11. **`11_exportar_tablas_excel.py`**: Consolidación batch de dataframes a Excel.
12. **`05_mapeo_y_reportes.py`**: Tablas intermedias y Markdown ejecutivos.
13. **`08_tabla_utm.py`**: Tabla detallada de UTMs y sus conversiones.
14. **`12_analisis_no_matcheados.py`**: Análisis demográfico/estadístico de leads sin inscripción vs leads exitosos.
15. **`21_exportar_matcheo_completo.py`**: Resumen del matcheo completo a Excel con métricas por tipo de match.

### Fase 2 — Scripts globales (via `00_run_all.py`)

Se ejecutan una sola vez, sin argumento de segmento:

16. **`19_bot_consolidado.py`**: Informe consolidado del Bot. Cruza todas las fuentes, verifica causalidad (consulta previa a inscripción). PDF/Excel/MD.
17. **`06_sankeys_extras.py`**: Sankeys adicionales (Bot, Flow de Ventas, etc.).
18. **`08_fuzzy_correos.py`**: Auditoría de Data Quality. Chequea correos huérfanos con 1 caracter de diferencia. Tiene lógica de Skip persistente para filas ya validadas.
19. **`15_dominios_invalidos.py`**: Detecta dominios de correo con errores de tipeo (ej: `gmail.con`, `gmail.com.ar`).
20. **`15_carreras.py`**: Análisis de carreras.
21. **`generate_eda_pdf.py`**: PDF de análisis exploratorio de datos (EDA).
22. **`20_presupuesto_roi.py`**: Inversión publicitaria y ROI. Cruza costos de Google Ads (hardcodeado) y Facebook Ads (archivos) con conversiones. KPIs: CPL, CPA, Revenue, ROI. Modelos Last-Touch y First-Touch.
23. **`21_atribucion_causal.py`**: Variante causal del ROI: solo cuenta como conversión consultas ANTERIORES al pago. Genera comparativa Estándar vs Causal, incluyendo modelo Any-Touch Causal.
24. **`22_auditoria_indicadores.py`**: Auditoría de indicadores de calidad del pipeline.
25. **`23_embudo_conversion.py`**: Embudo Consulta → Boleta → Inscripción. Lee boletas raw, cruza por DNI. Genera embudo por segmento, desglose por canal/campaña, y **diagramas Sankey** (canal → boleta → pago) con Plotly.

---

## 🔑 IDs de FuenteLead Importantes

| FuenteLead | Descripción |
|------------|-------------|
| 18 | Facebook Lead Ads (campañas de Meta) |
| 907 | Bot / Chatbot |

---

## 📅 Formato de Fechas por Columna y Tabla

> **IMPORTANTE — FORMATOS MIXTOS:** Las columnas de fecha en los CSVs de salida **NO comparten un único formato**. La columna `Consulta: Fecha de creación` mantiene el formato raw `D/M/YYYY` de Salesforce (ej: `2/3/2026` = 2 de marzo), mientras que las columnas `Insc_*`, `Fecha Pago` y `Fecha Aplicación` usan `YYYY-MM-DD` (ISO 8601). Ver tabla abajo para detalle por columna.
>
> **Riesgo si no se maneja:** Parsear `Consulta: Fecha de creación` sin `dayfirst=True` pierde el 87% de las filas donde el día > 12 (pandas las interpreta como mes inválido y devuelve `NaT`).

### Tabla: `reporte_marketing_leads_completos.csv` (Leads)

| Columna | Formato en CSV | Ejemplo | Origen | Observaciones |
|---------|---------------|---------|--------|---------------|
| `Consulta: Fecha de creación` | **`D/M/YYYY`** | `2/3/2026` | Salesforce (Leads `.xlsx`) | **⚠️ FORMATO NO ISO.** Se exporta tal cual llega de Salesforce, sin conversión. Parsear siempre con `dayfirst=True` |
| `Fecha Pago` | `YYYY-MM-DD` | `2025-10-23` | Inscriptos (`.xls`) | Solo presente si el lead matcheó con un inscripto. Es la fecha de pago del inscripto matcheado |
| `Fecha Aplicación` | `YYYY-MM-DD` | `2026-03-10` | Inscriptos (`.xls`) | Fecha de inicio de cursado. Puede ser futura si el alumno se anotó para un ciclo próximo |
| `Insc_Fecha Pago` | `YYYY-MM-DD` | `2025-10-23` | Inscriptos (`.xls`) | Idéntica a `Fecha Pago` pero con prefijo `Insc_`. Generada por el cruce `02_cruce_datos.py` |
| `Insc_Fecha Aplicación` | `YYYY-MM-DD` | `2026-03-10` | Inscriptos (`.xls`) | Idéntica a `Fecha Aplicación` con prefijo `Insc_` |

### Tabla: `reporte_marketing_inscriptos_origenes.csv` (Inscriptos con Origen)

| Columna | Formato en CSV | Ejemplo | Origen | Observaciones |
|---------|---------------|---------|--------|---------------|
| `Consulta: Fecha de creación` | **`D/M/YYYY`** | `2/3/2026` | Salesforce | **⚠️ FORMATO NO ISO.** La consulta que originó al inscripto. Parsear con `dayfirst=True` |
| `Fecha Pago` | `YYYY-MM-DD` | `2025-10-23` | Sistema de Inscriptos | Cuándo pagó la boleta |
| `Fecha Aplicación` | `YYYY-MM-DD` | `2026-03-10` | Sistema de Inscriptos | Cuándo empieza a cursar |
| `Insc_Fecha Pago` | `YYYY-MM-DD` | `2025-10-23` | Cruce `02` | Copia de `Fecha Pago` generada por merge |
| `Insc_Fecha Aplicación` | `YYYY-MM-DD` | `2026-03-10` | Cruce `02` | Copia de `Fecha Aplicación` generada por merge |

### Archivos Fuente (Raw)

| Archivo | Ubicación | Formato Nativo |
|---------|-----------|----------------|
| `Leads *.xlsx` | `data/1_raw/leads_salesforce/` | Excel `datetime64` (pandas lo lee como `YYYY-MM-DD HH:MM:SS`) |
| `*_20XX.xls` | `data/1_raw/inscriptos/` | Excel `datetime64` (pandas lo lee como `YYYY-MM-DD HH:MM:SS`) |

### Cómo parsear correctamente

```python
# ✅ CORRECTO para Consulta: Fecha de creación (formato D/M/YYYY raw de Salesforce)
pd.to_datetime(df['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

# ✅ CORRECTO para columnas Insc_Fecha Pago, Fecha Pago (formato ISO YYYY-MM-DD)
pd.to_datetime(df['Insc_Fecha Pago'], format='mixed', errors='coerce')

# ❌ MAL — pierde el 87% de las fechas de Consulta donde día > 12
pd.to_datetime(df['Consulta: Fecha de creación'], errors='coerce')

# ⚠️ NOTA: usar dayfirst=True con columnas ISO genera un UserWarning
# (pandas detecta el formato ISO y lo ignora), pero NO causa errores de datos.
# Por seguridad se puede usar format='mixed' con dayfirst=True en TODAS las columnas.

# ✅ VALIDACIÓN DE RANGO: siempre filtrar fechas fuera de rango razonable
fecha_min = pd.Timestamp('2024-01-01')
fecha_max = pd.Timestamp.now() + pd.Timedelta(days=365)
df.loc[df['col_fecha'] < fecha_min, 'col_fecha'] = pd.NaT
df.loc[df['col_fecha'] > fecha_max, 'col_fecha'] = pd.NaT
```

### Fecha Máxima para los Informes

La fecha que se inyecta en los encabezados de los reportes PDF proviene de la **tabla de inscriptos** (no de leads), ya que la fecha límite de corte la dicta el último inscripto registrado.
Se formatea como texto en español: `"DD de [Mes] de YYYY"` (ej: `"26 de diciembre de 2026"`).

---

## 🧠 Lecciones Aprendidas / Aclaraciones Críticas para Futuros Devs

### 1. ⚠️ `Fecha Aplicación` ≠ fecha histórica — ES FUTURA, el año de cursado de la carrera.
**Descubrimiento:** La columna `Fecha Aplicación` / `Insc_Fecha Aplicación` NO es una fecha pasada. Representa la **fecha de inicio de cursado** del alumno, que puede estar hasta **7 meses en el futuro** (ej: un alumno paga en septiembre 2025 pero empieza a cursar en marzo 2026).

**Consecuencia directa:** Si usas `max()` sobre todas las columnas "fecha" incluyendo `Fecha Aplicación`, obtendrás una fecha futura incorrecta (ej: "diciembre 2026" cuando estamos en febrero 2026). **Siempre usar solo `Fecha Pago` / `Insc_Fecha Pago`** para determinar la fecha de corte del informe, y además filtrar `<= hoy` por seguridad.

### 2. 🔢 `FuenteLead` es un código numérico, NO texto
**Descubrimiento:** La columna `FuenteLead` contiene IDs numéricos (float), no nombres de fuente como "Facebook" o "Bot". Para filtrar por origen se debe usar comparación numérica:
- `FuenteLead == 907` → Bot / Chatbot
- `FuenteLead == 18` → Facebook Lead Ads
- Otros valores comunes: `3.0`, `4.0`, `18.0`, `40.0`, `51.0`

**Mejor práctica:** Usar `pd.to_numeric(df['FuenteLead'], errors='coerce')` antes de comparar, porque pandas puede leerlo como float con `.0`.

### 3. 🐢 Los CSV maestros son MUY grandes — pandas se cuelga fácilmente
**Descubrimiento:** `reporte_marketing_leads_completos.csv` pesa cientos de MB. Leer todas las columnas con `pd.read_csv()` sin `usecols` hace que pandas se cuelgue indefinidamente en máquinas con < 16GB RAM.

**Mejor práctica:**
```python
# ✅ Siempre especificar las columnas que se necesitan
usecols = ['Correo', 'Match_Tipo', 'FuenteLead']
df = pd.read_csv(leads_csv, usecols=usecols, low_memory=False)

# ✅ Para exploración rápida, limitarse a las primeras filas
df_sample = pd.read_csv(leads_csv, nrows=200)
```

### 4. 🔤 `fpdf2` — Usar Helvetica, no Arial
**Descubrimiento:** `fpdf2` (versión moderna de `fpdf`) emite `DeprecationWarning` cuando se usan fuentes como `Arial` con el parámetro `ln=True`. Las fuentes heredadas siguen funcionando pero generan ruido en los logs.

**Corrección aplicada:** Se reemplazó `Arial` por `Helvetica` en todos los scripts PDF (`07`, `09`, `12`, `13`, `14`). `Helvetica` es la fuente core sin warnings.

### 5. 📊 Pie charts de `matplotlib` — labels y sizes DEBEN tener la misma longitud
**Descubrimiento:** Al filtrar categorías con valor 0 para un pie chart, si se filtran `labels` y `sizes` por separado, pueden quedar con longitud diferente y causar `ValueError: 'label' must be of length 'x'`.

**Corrección:**
```python
# ❌ MAL: filtrar por separado genera longitudes diferentes
labels = [l for l, p in zip(order, pcts) if p > 0]
sizes = [v for v in values if v > 0]

# ✅ BIEN: filtrar en pares (zip) para mantener misma longitud
pairs = [(l, v, p) for l, v, p in zip(order, values, pcts) if v > 0]
labels = [f'{l}\n({p}%)' for l, v, p in pairs]
sizes = [v for l, v, p in pairs]
```

### 6. 📅 `Consulta: Fecha de creación` — Formato D/M/YYYY (¡CRÍTICO!)
**Descubrimiento:** La columna `Consulta: Fecha de creación` en los CSVs maestros está almacenada en formato **`D/M/YYYY`** (ej: `2/3/2026` = 2 de marzo de 2026). Esto es distinto a todas las columnas `Insc_*` que usan `YYYY-MM-DD` (ISO).

**Impacto si NO se corrige:** `pd.to_datetime(col, errors='coerce')` sin `dayfirst=True` falla para el 87% de las filas (todas con día > 12), dejándolas como `NaT`. Los gráficos de curva de consultas por mes solo muestran 35K de 270K registros.

**Corrección obligatoria en todos los scripts:**
```python
# ✅ CORRECTO para Consulta: Fecha de creación
pd.to_datetime(df['Consulta: Fecha de creación'], format='mixed', dayfirst=True, errors='coerce')

# ✅ CORRECTO para columnas Insc_Fecha Pago, Fecha Pago (formato ISO YYYY-MM-DD)
pd.to_datetime(df['Insc_Fecha Pago'], format='mixed', errors='coerce')

# ❌ MAL — falla para fechas con día > 12
pd.to_datetime(df['Consulta: Fecha de creación'], errors='coerce')
```

**Scripts corregidos:** `04_reporte_final.py`, `07_pdf_completo.py`, `19_bot_consolidado.py`.

### 7. 🤖 Tasa de Conversión del Bot — Criterio Canónico
**Descubrimiento:** Dos métodos de cálculo producían tasas diferentes para el mismo canal (Bot):
- **Método A (incorrecto):** Deduplicar TODOS los leads → filtrar por `FuenteLead=907` → calcular tasa. Resultado: ~7.89%. Undercounts porque personas que consultaron por otro canal primero y luego por bot quedan excluidas.
- **Método B (correcto):** Filtrar por `FuenteLead=907` → deduplicar personas del bot → aplicar filtro cohorte → calcular tasa. Resultado: 6.12%.

**Regla de negocio:** El informe bot consolidado (`19`) y el informe general (`07`) deben usar el **Método B** para que las tasas del bot sean idénticas en ambos informes.

**Fórmula canónica:**
```python
df_bot = df_main[df_main['_fl'] == '907']           # todos los registros bot
df_bot_dedup = df_bot.drop_duplicates(subset='_pk')  # personas únicas del bot
if segmento == 'Grado_Pregrado':
    df_bot_dedup = df_bot_dedup[df_bot_dedup['fecha'] >= '2024-09-01']  # cohorte
tasa = bot_inscriptos / len(df_bot_dedup) * 100
```

### 8. 📧 Dominios de correo inválidos comunes
**Descubrimiento:** Una cantidad significativa de leads (1,378) tienen dominios con errores de tipeo. Los más frecuentes:
- `gmail.com.ar` (434 leads) — **NO EXISTE**, es un error común de argentinos
- `gmail.con` (354 leads) — falta la "m"
- `gamil.com` (171 leads) — inversión de letras
- Otros: `gmai.com`, `gmail.comm`, `gmail.co`, `hotmail.con`

Se estima que corregir estos dominios recuperaría ~43 matches adicionales.

---

## ⚠️ Known Issues / Próximos pasos para el siguiente Dev

1. **Retroalimentación de Fuzzy Matches Humanos:** El script `08` genera un Excel de control manual. Falta programar un script intermediario (ej. `02_b_integrar_fuzzy_manual.py`) que recoja los "Sí" de ese Excel en futuras ejecuciones y force a considerarlos "Exacto" en el cruce principal del script `02_cruce_datos.py`.
2. **Alertas de Linter / Typos en Type Hints:** Algunos scripts en Python (`04`, `07`, `09`) arrojan warnings de linter por compatibilidad de tipos (ej. Pandas Dataframes operando con Literales), o el uso de *DeprecationWarnings* en `fpdf2` respecto del parámetro `ln=True`. Funcionan perfectamente, pero para subir a producción estricta se debería migrar a `new_x=XPos.LMARGIN, new_y=YPos.NEXT`.
3. **Optimización OOM (Out Of Memory):** El archivo `reporte_marketing_leads_completos.csv` llega a pesar cientos de megas. Todos los scripts nuevos (`12`, `13`, `14`, `15`) fueron optimizados con `usecols` para no explotar la memoria RAM. Mantener esta buena práctica.
4. **Formateo de Fechas:** Las fechas detectadas dinámicamente ahora se inyectan como "DD de [Mes] de YYYY". El mapeo de meses se hace mediante un diccionario de Python. **NUNCA usar `Fecha Aplicación` para la fecha de corte** (ver Lección 1).
5. **Integración de Dominios Inválidos:** El script `15` detecta los typos pero no los corrige automáticamente. Para integrar las correcciones, se debería agregar un paso en `02_cruce_datos.py` que normalice los dominios antes del cruce.
6. **Mapeo completo de FuenteLead:** Solo se conocen los IDs 18 (Facebook Lead Ads) y 907 (Bot). Sería útil documentar el mapeo completo de todos los IDs de `FuenteLead` que existen en Salesforce.

---
*Fin del reporte de Handover.*
