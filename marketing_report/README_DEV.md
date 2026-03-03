# 🚀 Marketing Report Automation - DEV HANDOVER

**Última actualización:** 28 de Febrero de 2026
**Estado del Proyecto:** ✅ **Estable y Funcional (Fase 3 Completada)**

## 📌 Estado Actual del Desarrollo
El esquema de reportes está 100% automatizado, procesando bases de datos de Leads e Inscriptos mediante 12 scripts secuenciales.
Se ha completado la integración de todos los componentes gráficos, PDF y Excel, así como los reportes avanzados de **UTMs, Google Ads, Fuzzy Matching y Análisis de Leads No Matcheados**. Toda la salida de datos ahora se organiza dinámicamente en subcarpetas dentro de `outputs/`.

---

## 📁 Arquitectura de Carpetas
```text
h:\Test-Antigravity\marketing_report\
├── data/
│   └── 1_raw/          <- (Datasets originales Excel de Salesforce/Sistemas)
│       ├── leads_salesforce/
│       └── inscriptos/
├── outputs/            <- (GENERADO POR LOS SCRIPTS. No tocar manualmente salvo para auditoria)
│   ├── Data_Base/
│   ├── Informe_Analitico/
│   ├── Analisis_UTM/
│   ├── Google_Ads_Deep_Dive/
│   ├── Facebook_Deep_Dive/
│   ├── Bot_Deep_Dive/
│   ├── Analisis_No_Matcheados/
│   └── Calidad_Datos/
└── scripts/            <- (Lógica Core)
    ├── 01_... a 15_... .py
```

---

## ⚙️ Dependencias Clave (pip install)
Para ejecutar la pipeline de principio a fin, asegúrate de tener instaladas las siguientes librerías:
- `pandas` y `numpy`
- `thefuzz` y `Levenshtein` (Para lógica de strings y Fuzzy Matches)
- `matplotlib`, `seaborn` y `plotly.graph_objects` (Para Sankey y visuales)
- `fpdf2` (¡Importante! Usar `fpdf2` y no `fpdf` heredado para soporte de tablas complejas y UTF-8)
- `tabulate` (Para conversión rápida de pandas a Markdown)

---

## 📜 Secuencia de Ejecución (Pipeline)

La ejecución debe darse en orden numérico para evitar fallas por falta de datos maestros:

1. **`02_cruce_datos.py`**: Limpia y unifica las bases raw. Genera las bases maestras en `outputs/Data_Base/`. Aplica cruce exacto y fuzzy-multiprocessing inicial.
2. **`03_journey_sankey.py` a `06_sankeys_extras.py`**: Generadores de visualizaciones Sankey (Generales, Bot, Flow de Ventas, etc).
3. **`04_reporte_final.py` y `05_mapeo_y_reportes.py`**: Generan tablas intermedias y Markdown ejecutivos.
4. **`07_pdf_completo.py`**: Compila el Gran Informe Analítico general de 24 páginas en formato Apaisado (Landscape).
5. **`08_fuzzy_correos.py`**: Script de auditoría de Data Quality. Chequea correos huérfanos con 1 caracter de diferencia y guarda en `outputs/Calidad_Datos/control_manual_correos.xlsx`. *Nota: Tiene lógica de Skip persistente si detecta filas ya validadas por humanos.*
6. **`09_utm_conversion.py` y `10_google_ads_deep_dive.py`**: Aislan el rendimiento UTM y de Google Ads enviándolo a carpetas separadas con sus propios PDFs.
7. **`11_exportar_tablas_excel.py`**: Consolidación batch de todos los dataframes.
8. **`12_analisis_no_matcheados.py`**: Estudia demográfica y estadísticamente el residuo de ventas (leads sin inscripción) vs leads de éxito. PDF horizontal.
9. **`13_facebook_deep_dive.py`**: Informe exclusivo de tráfico Meta (Facebook/Instagram). Filtra por UTM de Meta + `FuenteLead = 18` (Facebook Lead Ads).
10. **`14_bot_deep_dive.py`**: Informe exclusivo del Bot/Chatbot. Filtra por `FuenteLead = 907`. Genera PDF horizontal, gráficos y Excel.
11. **`15_dominios_invalidos.py`**: Detecta dominios de correo con errores de tipeo (ej: `gmail.con`, `gmail.com.ar`) y estima cuántos matches se recuperarían.

---

## 🔑 IDs de FuenteLead Importantes

| FuenteLead | Descripción |
|------------|-------------|
| 18 | Facebook Lead Ads (campañas de Meta) |
| 907 | Bot / Chatbot |

---

## 📅 Formato de Fechas por Columna y Tabla

> **IMPORTANTE:** Todas las fechas en los CSVs de salida están almacenadas como strings en formato `YYYY-MM-DD` (ISO 8601). Sin embargo, al parsearlas con `pd.to_datetime()`, usar `dayfirst=True` puede generar errores silenciosos cuando el formato ya es ISO. Se recomienda usar `format='mixed'` o parsear sin `dayfirst`.

### Tabla: `reporte_marketing_leads_completos.csv` (Leads)

| Columna | Formato en CSV | Ejemplo | Origen | Observaciones |
|---------|---------------|---------|--------|---------------|
| `Consulta: Fecha de creación` | `YYYY-MM-DD` | `2024-12-01` | Salesforce (Leads `.xlsx`) | Fecha en que se creó la consulta del lead |
| `Fecha Pago` | `YYYY-MM-DD` | `2025-10-23` | Inscriptos (`.xls`) | Solo presente si el lead matcheó con un inscripto. Es la fecha de pago del inscripto matcheado |
| `Fecha Aplicación` | `YYYY-MM-DD` | `2026-03-10` | Inscriptos (`.xls`) | Fecha de inicio de cursado. Puede ser futura si el alumno se anotó para un ciclo próximo |
| `Insc_Fecha Pago` | `YYYY-MM-DD` | `2025-10-23` | Inscriptos (`.xls`) | Idéntica a `Fecha Pago` pero con prefijo `Insc_`. Generada por el cruce `02_cruce_datos.py` |
| `Insc_Fecha Aplicación` | `YYYY-MM-DD` | `2026-03-10` | Inscriptos (`.xls`) | Idéntica a `Fecha Aplicación` con prefijo `Insc_` |

### Tabla: `reporte_marketing_inscriptos_origenes.csv` (Inscriptos con Origen)

| Columna | Formato en CSV | Ejemplo | Origen | Observaciones |
|---------|---------------|---------|--------|---------------|
| `Consulta: Fecha de creación` | `YYYY-MM-DD` | `2024-12-01` | Salesforce | La consulta que originó al inscripto |
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
# ✅ CORRECTO: usar format='mixed' para manejar variaciones
pd.to_datetime(df['Columna'], format='mixed', dayfirst=True, errors='coerce')

# ⚠️ PRECAUCIÓN: dayfirst=True con formato YYYY-MM-DD genera un Warning
# porque pandas detecta que el formato ya es ISO y lo ignora igualmente.

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

### 1. ⚠️ `Fecha Aplicación` ≠ fecha histórica — ES FUTURA
**Descubrimiento:** La columna `Fecha Aplicación` / `Insc_Fecha Aplicación` NO es una fecha pasada. Representa la **fecha de inicio de cursado** del alumno, que puede estar hasta **10 meses en el futuro** (ej: un alumno paga en febrero 2026 pero empieza a cursar en diciembre 2026).

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
