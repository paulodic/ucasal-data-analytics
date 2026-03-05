# 📄 Data Contract & Guía DEV — Leads + Inscriptos (UCASAL Marketing Report)

**Repo:** `paulodic/ucasal-data-analytics`

**Última actualización:** 2026-03-02

## 1. Objetivo
Este documento define el **contrato de datos** (data contract) y la **guía de desarrollo** del pipeline que:

1. Ingiere múltiples archivos raw de **Leads** (CRM/Salesforce) y **Inscriptos** (sistema académico/contable).
2. Normaliza identificadores personales (DNI, correo, teléfonos, nombre).
3. Realiza **matching Leads ↔ Inscriptos** (exacto + fuzzy) para determinar conversiones.
4. Genera **bases maestras** (`outputs/Data_Base/`) y luego reportes (PDF/MD/XLSX/CSV) consumibles por otras plataformas.

La intención es poder **agregar nuevos formatos de archivo de leads** (con columnas distintas) sin romper el matching y manteniendo consistencia.

---

## 2. Fuente de verdad (scripts core)

- Matching y unificación: `marketing_report/scripts/02_cruce_datos.py`
- Listado de columnas raw observadas (referencia): `marketing_report/scripts/columnas_raw.txt`
- Orquestación de reportes: `marketing_report/scripts/00_run_all.py`

---

## 3. Estructura de carpetas (contrato de IO)

> **IMPORTANTE:** El script `02_cruce_datos.py` usa rutas absolutas (Windows) en `base_dir = r"h:\Test-Antigravity\marketing_report"`. En el repo la estructura es la misma, pero para correrlo en otro entorno se recomienda parametrizar `base_dir` o ejecutar desde una carpeta que replique esa estructura.

**Entradas raw (no estandarizadas):**
- `marketing_report/data/1_raw/leads_salesforce/*.xlsx` y/o `*.xls`
- `marketing_report/data/1_raw/inscriptos/*.xlsx` y/o `*.xls`

**Salidas maestras (estandarizadas):**
- `marketing_report/outputs/Data_Base/<Segmento>/reporte_marketing_leads_completos.csv`
- `marketing_report/outputs/Data_Base/<Segmento>/reporte_marketing_inscriptos_origenes.csv`

Donde `<Segmento>` ∈ `{Grado_Pregrado, Cursos, Posgrados}` (y potencialmente `Desconocido`, aunque se omite si está vacío).

---

## 4. Inputs soportados (raw)

### 4.1 Leads (CRM / Salesforce)
Se concatenan todos los archivos en `leads_salesforce/`.

Columnas observadas (ver `columnas_raw.txt`):
- `Correo`, `Nombre`, `DNI`, `Telefono`, `Candidato`, `Tipo de Carrera`, `FuenteLead`, campos UTM, etc.

**Mínimo recomendado para matching confiable:**
- Alguno de: `DNI` o `Correo` o `Telefono` (idealmente más de uno)
- Algún campo de nombre: `Nombre` y/o `Candidato`

### 4.2 Inscriptos (Sistema académico/contable)
Se concatenan todos los archivos en `inscriptos/`.

Columnas observadas (ver `columnas_raw.txt`):
- `Apellido y Nombre`, `DNI`, `Email`, `Telefono`, `Celular`, `Tipcar`, etc.

El script asume que `Apellido y Nombre` está en formato **"Apellido, Nombres"** y lo separa.

---

## 5. Modelo canónico (schemas de salida)

### 5.1 Lead canónico (conceptual)
No existe una clase/tabla formal, sino un DataFrame. A nivel contrato, un lead (persona + consulta) debería poder representarse con:

**Identidad / matching**
- `DNI` (raw)
- `Correo` (raw)
- `Telefono` (raw)
- `Nombre` o `Candidato` (raw)

**Marketing / atribución (si existe)**
- `FuenteLead`
- `UtmSource`, `UtmMedium`, `UtmCampaign`, `UtmTerm`, `UtmContent`

**Estado / pipeline**
- `ColaNombre`, `PrimeraCola`, `Estado`, `Matriculadas`, etc.

**Campos agregados por el pipeline (internos):**
- `Match_Tipo` (resultado del cruce)
- Campos `Insc_*` cuando el lead matchea con un inscripto (se anexan columnas del inscripto renombradas con prefijo)

### 5.2 Inscripto canónico (conceptual)
- `DNI`
- `Email`
- `Telefono`
- `Celular`
- `Apellido y Nombre` (raw) + `Apellido` y `Nombres` (derivados)
- `Tipcar` (usado para segmentación)

**Campos agregados por el pipeline:**
- Prefijo `Insc_` para casi todas las columnas (ver sección 6)

---

## 6. Normalización de claves (implementación actual)

El script crea claves de matching con funciones `clean_*`:

### 6.1 DNI (`clean_dni`)
- Convierte a string
- Remueve decimales `.0`, puntos, guiones, espacios
- Devuelve `pd.NA` si vacío

**Implicancia:** DNIs como `44564512.0` se normalizan a `44564512`.

### 6.2 Email (`clean_email`)
- `strip()` + `lower()`
- `pd.NA` si vacío

### 6.3 Teléfono/Celular (`clean_phone`)
Normalización agresiva orientada a Argentina:
- Elimina caracteres no numéricos
- Maneja casos con guiones y prefijos duplicados
- Remueve prefijos `54` / `549` si aparecen
- Remueve `0` inicial
- Remueve el `15` móvil en patrones tipo `38715xxxxxxx`
- Trunca a últimos 10 dígitos si excede

**Resultado esperado:** un número "comparable" entre sistemas, con longitud típica 10.

### 6.4 Nombre (`clean_name`)
- `strip().lower()`
- Si NA → "" (string vacío)

---

## 7. Renombrado de columnas de inscriptos (`Insc_`)

Para evitar colisiones de nombres al mergear, el script renombra columnas del DF de inscriptos con prefijo `Insc_`:

- Se crea `Inscripto_Tmp_ID` (sin prefijo)
- Para el resto: `Insc_<columna_original>`

Ejemplos:
- `DNI_match` en inscriptos se vuelve `Insc_DNI_match`
- `Tipcar` se vuelve `Insc_Tipcar`

---

## 8. Matching Leads ↔ Inscriptos (algoritmo actual)

### 8.1 Etapa 0 — Preconditions
El script aborta si falta alguna de las dos bases:
- sin leads o sin inscriptos → `exit()`

Además filtra filas completamente vacías de claves:
- Leads: `dropna(subset=['Candidato','DNI','Telefono'], how='all')`
- Inscriptos: `dropna(subset=['Apellido y Nombre','DNI','Telefono'], how='all')`

### 8.2 Etapa 1 — Match exacto por DNI
`Match_Tipo = 'Exacto (DNI)'`

### 8.3 Etapa 2 — Match exacto por Email
`Match_Tipo = 'Exacto (Email)'`

### 8.4 Etapa 3 — Match exacto por Teléfono/Celular
- Insc `Telefono` vs lead `Telefono` → `Exacto (Teléfono)`
- Insc `Celular` vs lead `Telefono` → `Exacto (Celular)`

> Nota: el lead usa `Phone_match` que proviene de la columna raw `Telefono`. Si en el futuro hay leads con `Celular` separado, habrá que mapearlo.

### 8.5 Etapa 3.5 — Fuzzy Email (distancia Levenshtein 1-2)
- Solo para registros aún sin match
- Indexa leads por longitud de email
- Para cada inscripto, compara con leads de longitudes `L±2`
- Si `Levenshtein.distance(insc_email, lead_email)` está en `{1,2}` → match

`Match_Tipo = 'Posible Match Fuzzy Email (Dist X)'`

### 8.6 Etapa 4 — Fuzzy por Nombre (RapidFuzz/TheFuzz) + multiprocessing
- Usa `WRatio` con `score_cutoff=95`
- Corre en paralelo con `multiprocessing.Pool(mp.cpu_count())`

`Match_Tipo = 'Posible Match Fuzzy (Score: <score>)'`

**Regla anti-colisión (postproceso):**
- Ordena resultados por score desc
- Un lead solo puede ser asignado a 1 inscripto en fuzzy (set `used_fuzzy_leads`).

---

## 9. Consolidación y outputs

Se construyen dos datasets:

### 9.1 `reporte_marketing_leads_completos.csv`
Incluye:
- Leads que matchearon (exacto/fuzzy) con columnas `Insc_*` anexadas
- Leads sin match: `Match_Tipo = 'No (Solo Lead)'`

### 9.2 `reporte_marketing_inscriptos_origenes.csv`
Incluye:
- Inscriptos que matchearon (exacto/fuzzy) con columnas del lead anexadas
- Inscriptos sin match: `Match_Tipo = 'No (Solo Inscripto Directo)'`

### 9.3 Limpieza final
Se eliminan columnas técnicas: `*_Tmp_ID`, `*_match`.

---

## 10. Segmentación (Nivel Académico)

La exportación final se hace por `Segmento_Acad`:

### 10.1 Función de segmentación (`segmentar_tipcar`)
Reglas sobre string lower:
- contiene `curso` → `Cursos`
- contiene `postgrado`/`posgrado`/`maestría`/`maestria` → `Posgrados`
- contiene `grado` o `pregrado` → `Grado_Pregrado`
- else → `Desconocido`

### 10.2 Fuente del dato
- Inscriptos: `Insc_Tipcar`
- Leads: si matchearon y existe `Insc_Tipcar`, lo heredan; si no, usan `Tipo de Carrera` del CRM.

---

## 10b. Clasificación por Campaña (`Campana_Lead`)

Columna agregada por `02_cruce_datos.py` al CSV de leads (`reporte_marketing_leads_completos.csv`).
Identifica si la consulta del lead cae dentro de la ventana de la campaña actual o es anterior.

### 10b.1 Regla de clasificación

| Segmento | Ventana Campaña Actual | Label | Antes de ventana |
|---|---|---|---|
| `Grado_Pregrado` | >= 2025-09-01 | `Ingreso 2026` | `Campaña Anterior` |
| `Cursos` | >= 2026-01-01 | `2026` | `Campaña Anterior` |
| `Posgrados` | >= 2026-01-01 | `2026` | `Campaña Anterior` |

La fecha usada es `Consulta: Fecha de creación` (parseada con `dayfirst=True`).

### 10b.2 Propósito

Permite a los informes downstream separar:
- **Inscriptos de campaña actual**: personas cuyo lead (consulta) surgió durante la campaña vigente
- **Inscriptos de campaña anterior**: personas que consultaron ANTES del inicio de la campaña actual,
  pero cuyo match con inscripto se produjo igualmente (por ejemplo, leads de 2024 que recién se inscribieron)

### 10b.3 Uso en informes

| Script | Cómo lo usa |
|---|---|
| `04_reporte_final.py` | Torta de orígenes filtrada a campaña actual; gráfico comparativo 2026 vs anterior |
| `07_pdf_completo.py` | Sección "Atribución por Campaña" en Resumen Ejecutivo del PDF |
| `20_presupuesto_roi.py` | Diagnóstico en consola de inscriptos por campaña |
| `21_exportar_matcheo_completo.py` | Sección en resumen Excel y MD |

### 10b.4 Análisis Multi-Touch

El script `04_reporte_final.py` genera además un análisis multi-touch que muestra:
- **Cuántos canales** consultó cada inscripto antes de inscribirse (1, 2, 3 o 4 canales)
- **Qué combinaciones** de canales son más frecuentes (ej: "Google + Otros", "Meta + Bot")

Los canales se clasifican como: `Google`, `Meta`, `Bot`, `Otros`.

Gráficos generados:
- `chart_multitouch_canales.png` — Distribución de cantidad de canales por inscripto
- `chart_multitouch_combinaciones.png` — Top 10 combinaciones de canales
- `chart_2b_campana_comparativa.png` — Barras comparando inscriptos por canal entre campañas

---

## 11. Checklist QA (antes y después de correr)

### 11.1 Antes de correr (raw)
- Verificar que los excels abren bien (no protegidos, no corruptos).
- Validar encoding/formatos: emails como string, DNIs sin letras.
- Confirmar nombres de columnas (ver sección 12 para nuevos archivos).

### 11.2 Después de correr (outputs)
- Validar que existen archivos por segmento:
  - `outputs/Data_Base/<seg>/reporte_marketing_leads_completos.csv`
  - `outputs/Data_Base/<seg>/reporte_marketing_inscriptos_origenes.csv`
- Revisar distribución de `Match_Tipo` (porcentaje de exactos vs fuzzy vs no match).
- Auditar fuzzy (muestras manuales):
  - Fuzzy Email dist 1-2
  - Fuzzy nombre score ≥ 95

---

## 12. Cómo incorporar un NUEVO archivo de leads con columnas diferentes (guía práctica)

### 12.1 Problema actual
`02_cruce_datos.py` asume columnas específicas en leads:
- DNI: `DNI`
- Email: `Correo`
- Teléfono: `Telefono`
- Nombre: `Nombre`

Si llega un archivo nuevo con columnas distintas (ej. `Email`, `Mail`, `Celular`, `Nombre Completo`, etc.) el matching puede degradar o fallar silenciosamente (muchos NA).

### 12.2 Estrategia recomendada (no implementada aún)
Agregar una etapa de **mapeo/estandarización de columnas de leads** antes de generar `*_match`.

**Propuesta de contrato:** todos los leads deben mapearse a estas columnas canónicas internas:
- `DNI`
- `Correo` (email)
- `Telefono`
- `Nombre`

Luego se aplican `clean_dni/clean_email/clean_phone/clean_name` siempre sobre las canónicas.

### 12.3 Template de mapeo (para el equipo)
Cuando ingrese un archivo nuevo, completar una tabla así:

| Campo canónico | Columna en archivo nuevo | Transformación | Notas |
|---|---|---|---|
| `DNI` |  | `str` + limpiar separadores | |
| `Correo` |  | lower/strip | |
| `Telefono` |  | limpiar a dígitos | |
| `Nombre` |  | concatenar nombre+apellido si aplica | |
| `Tipo de Carrera` |  | opcional | |
| `FuenteLead` |  | opcional | |

### 12.4 Validación rápida
Usar `marketing_report/scripts/inspect_data.py` o crear un script similar para:
- listar columnas
- mostrar 5 filas
- medir % de nulos en `DNI/Correo/Telefono/Nombre`

---

## 13. Troubleshooting

### 13.1 "Faltan datos de leads o de inscriptos"
- Verificar que haya archivos en `data/1_raw/leads_salesforce/` y `data/1_raw/inscriptos/`.
- Verificar extensiones soportadas: `.xlsx` y `.xls`.

### 13.2 Muchos `No (Solo Lead)`
Causas típicas:
- El nuevo archivo tiene columnas con nombres distintos (no se mapeó a `Correo/Telefono/Nombre/DNI`).
- Teléfonos no normalizan bien (formatos raros).
- Emails vacíos o con typos severos.

### 13.3 Fuzzy con falsos positivos
- Revisar umbral `score_cutoff=95`.
- Considerar agregar reglas de bloqueo (ej. mismo DNI parcial, misma provincia, etc.).

---

## 14. Próximos pasos recomendados

1. ~~Extraer a una función `standardize_leads_columns(df_leads)`~~ — **IMPLEMENTADO** (ver sección 15).
2. Agregar logging de cobertura:
   - % filas con `DNI_match` no nulo
   - % filas con `Email_match` no nulo
   - % filas con `Phone_match` no nulo
3. Guardar un reporte de QA por corrida en `outputs/Calidad_Datos/`.

---

## 15. Formato "Informe General" de Salesforce (incorporado 2026-03-02)

### 15.1 Archivo gatillante
`data/1_raw/leads_salesforce/Informe General Mkt-2026-03-02-10-26-52.xlsx`

Este tipo de reporte es un **export completo de Salesforce** que difiere de los exports mensuales en schema y alcance.

### 15.2 Diferencias de columnas vs formato mensual

**Columnas AUSENTES en "Informe General" (presentes en mensuales):**

| Columna ausente | Solución implementada |
|---|---|
| `Candidato` | Se crea automáticamente copiando `Nombre` via `standardize_leads_columns()` |
| `PrimeraCola` | Queda como NaN — no disponible en este formato |
| `Matriculadas` | Queda como NaN — no disponible en este formato |
| `Consulta: Nombre del propietario` | Reemplazado por `Consulta: Creado por` en el nuevo formato |

**Columnas NUEVAS en "Informe General" (ausentes en mensuales):**

| Columna nueva | Tipo | Descripción |
|---|---|---|
| `Gestionados` | string | Indica si el lead fue gestionado (`Si`/`No` o similar) |
| `Grado de Consulta` | string | Temperatura del lead (ej: `2.Tibio`, `3.Frío`, `1.Caliente`) |
| `Fecha de última interacción` | datetime | Última vez que hubo contacto con el lead |
| `Application` | string | ID de la aplicación/solicitud en Salesforce (ej: `APP-181952`) |
| `Consulta: Creado por` | string | Usuario de Salesforce que creó la consulta (reemplaza `Consulta: Nombre del propietario`) |

**Columnas comunes (presentes en ambos formatos):**
`Correo`, `Nombre`, `DNI`, `Telefono`, `Tipo de Carrera`, `Modo`, `Código Carrera`, `Carrera`, `CódigoSede`, `Sede Nombre`, `FuenteLead`, `UtmSource`, `UtmCampaign`, `UtmMedium`, `UtmTerm`, `UtmContent`, `ColaNombre`, `Estado`, `Consulta: Fecha de creación`, `Id. candidato/contacto`, `Consulta: ID Consulta`

### 15.3 Estrategia de deduplicación y complementación

**Clave única:** `Consulta: ID Consulta` — presente en TODOS los archivos de leads de Salesforce.

**Algoritmo implementado en `02_cruce_datos.py`:**

```python
df_leads = (
    df_leads
    .groupby('Consulta: ID Consulta', sort=False)
    .first()
    .reset_index()
)
```

`groupby().first()` usa `skipna=True` por defecto → toma el primer valor **no-NaN** por columna en cada grupo. Esto complementa automáticamente datos entre archivos:
- Si el mensual tiene `Candidato` y el General no → se usa el del mensual
- Si el General tiene `Gestionados` y el mensual no → se usa el del General

### 15.4 Análisis de solapamiento (2026-03-02)

| Archivo | Filas | Rango ID Consulta | Solapamiento con General |
|---|---|---|---|
| **Informe General** (nuevo) | 100,004 | 1,663,529 – 1,795,300 | — |
| `provisorio febrero 2026.xlsx` | 36,718 | ≈ mismo rango | **36,644 IDs compartidos** |
| `Leads enero 2026.xlsx` | 39,137 | diferente rango | 0 |
| `Leads diciembre 2025.xlsx` | 31,565 | diferente rango | 0 |
| `Leads noviembre 2025.xlsx` | 35,271 | diferente rango | 0 |
| `Leads octubre 2025.xlsx` | 38,525 | diferente rango | 0 |
| `Leads septiembre 2025.xlsx` | 33,721 | diferente rango | 0 |

**63,356 IDs del General son registros completamente nuevos** (no estaban en ningún archivo mensual previo).

### 15.5 Nota sobre `Septiembre_2025.xlsx`

Este archivo NO es un export de leads de Salesforce — tiene un schema diferente (datos contables/académicos) y **no tiene** `Consulta: ID Consulta`. El pipeline lo lee pero no afecta el cruce porque sus columnas no coinciden con las claves canónicas del matching.

---

## 16. Presupuesto, Costos e Indicadores de ROI (Reglas de Negocio)

> **Script fuente:** `marketing_report/scripts/20_presupuesto_roi.py`
> **Output:** `outputs/Presupuesto_ROI/Presupuesto_ROI_Ingreso2026.pdf` + `Presupuesto_ROI_Datos.xlsx`

Este informe cruza datos de inversión publicitaria con datos de leads y conversiones para calcular KPIs financieros por segmento y canal.

### 16.1 Períodos de análisis por segmento

Cada segmento tiene una ventana de análisis diferente:

| Segmento | Tipo de período | Fecha inicio | Fecha fin | Justificación |
|---|---|---|---|---|
| **Grado_Pregrado** | Cohorte Ingreso 2026 | `2025-09-01` | Última inscripción registrada | La captación para la cohorte de ingreso 2026 comienza en septiembre del año anterior |
| **Cursos** | Año calendario 2026 | `2026-01-01` | Última inscripción registrada | Los cursos se inscriben por año calendario |
| **Posgrados** | Año calendario 2026 | `2026-01-01` | Última inscripción registrada | Los posgrados se inscriben por año calendario |

**Fecha fin dinámica:** El límite superior siempre es `max(Insc_Fecha Pago)` filtrado por `<= hoy`. Esto evita contar leads muy recientes que aún no tuvieron tiempo de convertir.

**Para el matching se usan TODOS los leads históricos** (sin restricción de fecha). La ventana solo se aplica para el denominador de las tasas de conversión y los KPIs financieros.

### 16.2 Fuentes de inversión (datos de costos)

#### 16.2.1 Google Ads

- **Fuente:** Valores hardcodeados en el script (variable `GOOGLE_SPEND`).
- **Moneda:** ARS (pesos argentinos), **sin impuestos**.
- **Período reportado:** `01/09/2025 - 17/02/2026` (variable `GOOGLE_PERIODO`).
- **Responsable de actualización:** El equipo de marketing debe actualizar estos valores manualmente cuando tenga nuevos datos de Google Ads.

| Segmento | Inversión Google Ads (ARS) | Período |
|---|---|---|
| Grado_Pregrado | `$ 47,387,402.90` | 01/09/2025 - 17/02/2026 (cohorte) |
| Cursos | `$ 0` (sin campaña activa) | - |
| Posgrados | `$ 976,308.10` | 01/01/2026 - 17/02/2026 (calendario) |

> **IMPORTANTE:** Los valores de Google Ads son hardcodeados por segmento. Si el equipo de marketing tiene datos actualizados de Google Ads, debe actualizar el diccionario `GOOGLE_SPEND` en el script.

#### 16.2.2 Facebook Ads (Meta)

- **Fuente:** Archivos Excel/CSV en `data/1_raw/presupuestos/`.
- **Formato esperado:** Export directo de Meta Business Manager.
- **Moneda:** ARS (pesos argentinos), según plataforma.
- **Columnas requeridas del export de Facebook:**

| Columna | Tipo | Uso |
|---|---|---|
| `Nombre de la campaña` | string | Clasificación por segmento |
| `Importe gastado (ARS)` | numérico | Inversión |
| `Clientes potenciales` | numérico | Leads generados en plataforma |
| `Impresiones` | numérico | Alcance |
| `Clics en el enlace` | numérico | Tráfico |
| `Inicio del informe` | fecha | Período del export |
| `Fin del informe` | fecha | Período del export |
| `Nombre del conjunto de anuncios` | string | Conteo de conjuntos |

#### 16.2.3 Clasificación de campañas Facebook por segmento

Las campañas de Facebook se clasifican automáticamente según el **nombre de la campaña** con la siguiente lógica (función `classify_fb_segment`):

```
Si el nombre contiene 'posgrado', 'postgrado', 'maestr' o 'especiali' → Posgrados
Si el nombre contiene 'curso' → Cursos
Todo lo demás → Grado_Pregrado
```

> **NOTA:** La clasificación es case-insensitive. Si una campaña tiene un nombre ambiguo, se clasifica como Grado_Pregrado por defecto. El equipo de marketing debe usar nombres descriptivos en las campañas para una clasificación correcta.

> **IMPORTANTE — "Campaña2026" = Grado_Pregrado:** Cuando el nombre de una campaña dice `Campaña2026` (sin la palabra "curso" ni "posgrado"), se refiere a la **campaña de Grado y Pregrado cuya captación comienza en septiembre 2025** para el ingreso 2026. El año en el nombre indica el año de ingreso/cohorte, NO el año en que se lanza la campaña.

#### 16.2.3b Convención de nombres de campañas Facebook

El equipo de marketing usa la siguiente estructura en los nombres de campañas de Meta Business Manager:

```
<CodCar>-<CodModalidad>-<Descripción>_<FLA|otro>
```

| Componente | Posición | Descripción | Valores |
|---|---|---|---|
| **CodCar** | 1er valor (antes del primer `-`) | Código de carrera | `0` = comodín (todas las carreras), otros = código específico de carrera |
| **CodModalidad** | 2do valor (entre guiones) | Código de modalidad | `1` = presencial, `2` = semipresencial, `7` = distancia |
| **Grupo** | En descripción | Agrupación de carreras | `GRUPO_A`, `GRUPO_B`, `GRUPO_C`, `GRUPO_CCC` = grupos de carreras |
| **FLA** | Sufijo | Tipo de campaña | `Fla` = Facebook Lead Ads (formularios nativos) |
| **Año** | En descripción | Año de cohorte/ingreso | `2026` = campaña para ingreso 2026 |

**Ejemplos reales:**

| Nombre de campaña | CodCar | Modalidad | Significado |
|---|---|---|---|
| `0-7-Campaña2026_Primer_GRUPO_A_Fla` | 0 (todas) | 7 (distancia) | FLA para carreras Grupo A, distancia, ingreso 2026 |
| `0-1-Campaña2026_Primer_GRUPO_B_Fla` | 0 (todas) | 1 (presencial) | FLA para carreras Grupo B, presencial, ingreso 2026 |
| `1452-7-Curso2026_IA_Digitales_Fla` | 1452 | 7 (distancia) | FLA para curso específico 1452, distancia |
| `228-7-Posgrado2026_Valoración_Patrimonial_Fla` | 228 | 7 (distancia) | FLA para posgrado específico 228, distancia |

#### 16.2.4 Filtrado de campañas Facebook por año de cohorte

Las campañas de Facebook se filtran por el **año de la cohorte/período que se está analizando** (variable `COHORTE_YEAR = 2026`). El año se extrae del nombre de la campaña usando una regex `20\d{2}`.

**Regla:**
- Campañas con `"2026"` en el nombre → **Incluidas** en el cálculo de inversión
- Campañas sin año en el nombre → **Incluidas** (se asumen del año actual)
- Campañas con otros años (`"2025"`, `"2024"`, etc.) → **Excluidas** del cálculo de inversión

**Ejemplo con datos reales (análisis Ingreso 2026):**

| Segmento | Campañas 2026 (incluidas) | Campañas otros años (excluidas) |
|---|---|---|
| Grado_Pregrado | $ 103.4M (ej: `Campaña2026_Primer_GRUPO_A`) | $ 11.8M (ej: `Branding2025_Alcance`) |
| Cursos | $ 1.7M (ej: `Curso2026_...`) | $ 5.4M (ej: `Curso2025_Protección_Niños`) |
| Posgrados | $ 9.8M (ej: `Posgrado2026_...`) | $ 4.7M (ej: `Posgrado2025_Gestión_Ambiental`) |

> **IMPORTANTE para el equipo de marketing:** El nombre de la campaña en Meta Business Manager **debe contener el año** para el que está destinada (ej: `Campaña2026_...`). Si una campaña no tiene año en el nombre, se incluirá en el análisis del año actual por defecto. El detalle de campañas excluidas se puede auditar en la hoja `FB_Excluidas_Resumen` del Excel de respaldo.

> **Para cambiar el año de análisis:** Modificar `COHORTE_YEAR = 2026` en el script.

### 16.3 Atribución de canal (leads CRM)

Los leads del CRM se clasifican en 4 canales usando las columnas `UtmSource` y `FuenteLead`:

| Canal | Regla de atribución | Prioridad |
|---|---|---|
| **Google Ads** | `UtmSource` contiene `'google'` (case-insensitive) | 1ra evaluación |
| **Facebook Ads** | `UtmSource` contiene `'fb'`, `'facebook'`, `'ig'`, `'instagram'` o `'meta'` **O** `FuenteLead == 18` | 2da evaluación |
| **Bot/Chatbot** | `FuenteLead == 907` | 3ra evaluación |
| **Otros/Orgánico** | Todo lo que no cae en los anteriores | Residual |

**Reglas de exclusión mutua:** Las masks se evalúan de modo que un lead puede caer en solo un canal:
- `mask_otros = ~mask_google & ~mask_fb & ~mask_bot`
- Si un lead tiene `UtmSource = 'google'` Y `FuenteLead = 907`, se clasifica como Google (la primera mask que matchea).

**Valores de `FuenteLead` importantes:**
- `18` → Facebook Lead Ads (formularios nativos de Facebook)
- `907` → Bot/Chatbot (chatbot de la universidad)

### 16.4 Definición de KPIs (fórmulas exactas)

#### 16.4.1 Leads CRM (deduplicados)

- **Definición:** Cantidad de personas únicas que consultaron en la ventana del segmento.
- **Deduplicación:** Se usa una clave `_pk` compuesta:
  - Prioridad 1: `DNI` (sin decimales ni puntos)
  - Prioridad 2: `Correo` (si DNI es nulo/vacío)
- **Filtro de matcheo:** Se excluyen matches fuzzy — solo se cuentan leads con match `Exacto` o `No (Solo Lead)`.
- **Ordenamiento dedup:** `sort_values('_mc')` → `exacto` < `no_match`, por lo que `drop_duplicates(subset='_pk', keep='first')` prioriza el registro que tiene match exacto.

#### 16.4.2 Inscriptos (conversiones)

- **Definición:** Cantidad de personas que se inscribieron Y cuyo lead tiene `Match_Tipo` con la palabra `'Exacto'`.
- **Solo se cuentan matches exactos** (DNI, Email, Teléfono, Celular). Los matches fuzzy **NO** se incluyen en la tasa de conversión ni en el ROI.
- **Fórmula:** `n_conv = (sub['_mc'] == 'exacto').sum()`

#### 16.4.3 CPL — Costo por Lead

```
CPL = Inversión del canal / Leads CRM (personas únicas deduplicadas en ventana)
```

- Se calcula por canal y por segmento.
- **CPL CRM:** Usa los leads que llegaron al CRM (Salesforce).
- **CPL Plataforma (solo Facebook):** Usa los leads reportados por la plataforma de Facebook (`Clientes potenciales`). Este número puede diferir del CRM porque no todos los leads de Facebook llegan al CRM.

#### 16.4.4 CPA — Costo por Adquisición (Inscripto)

```
CPA = Inversión del canal / Inscriptos con Match Exacto
```

- Solo se cuentan inscriptos cuyo lead fue atribuido a ese canal.
- Un CPA más alto indica menor eficiencia de conversión.

**Manejo de múltiples consultas por persona — Modelos de atribución:**

El informe calcula **dos modelos de atribución** en paralelo para comparar:

| Modelo | Criterio de dedup | Descripción |
|---|---|---|
| **Last-Touch (principal)** | `sort(['_mc', '_fecha'], ascending=[True, False])` → `drop_duplicates('_pk', keep='first')` | Toma la consulta exacta **más reciente**. Atribuye al canal que "cerró" la conversión. |
| **First-Touch (alternativo)** | `sort(['_mc', '_fecha'], ascending=[True, True])` → `drop_duplicates('_pk', keep='first')` | Toma la consulta exacta **más antigua**. Atribuye al canal que originó el contacto inicial. |

En ambos modelos:
1. Se prioriza el match más exacto: `Exacto (DNI)` > `Exacto (Email)` > `Exacto (Teléfono)` > `No match`
2. Dentro del mismo nivel de match, se desempata por `Consulta: Fecha de creación` (más reciente para LT, más antigua para FT)
3. Se asigna la persona **SOLO al canal de esa consulta** (UtmSource/FuenteLead)
4. Se cuenta como **1 conversión** en ese canal (aunque tuvo múltiples consultas)
5. **El total de inscriptos es idéntico en ambos modelos** — solo cambia la distribución entre canales

**El modelo principal (Last-Touch) se usa en todas las tablas de KPIs.** La página 3 del PDF muestra la comparativa lado a lado para evaluar la sensibilidad de los resultados al criterio de atribución.

#### 16.4.5 Revenue Atribuida

```
Revenue Atribuida = SUM(Insc_Haber) de inscriptos con Match Exacto cuyo lead pertenece a ese canal
```

- **`Insc_Haber`** es el monto registrado al momento de inscripción (cuota/arancel).
- **NO es el LTV (Lifetime Value)** completo del alumno. Es solo el haber registrado en el momento de la inscripción.
- Solo se suma el haber de inscriptos con match exacto.

#### 16.4.6 ROI — Retorno sobre Inversión

```
ROI (%) = (Revenue Atribuida - Inversión) / Inversión × 100
```

- ROI > 0% indica ganancia; ROI < 0% indica pérdida.
- **Canales sin inversión (Bot, Otros):** No se calcula ROI (se muestra `-`).
- **Limitación:** El ROI subestima el retorno real porque `Insc_Haber` solo captura el primer pago/cuota, no la totalidad de los ingresos futuros del alumno.

#### 16.4.7 Tasa de Conversión

```
Tasa de Conversión (%) = Inscriptos con Match Exacto / Leads CRM deduplicados × 100
```

### 16.5 Outputs generados

| Archivo | Contenido |
|---|---|
| `Presupuesto_ROI_Ingreso2026.pdf` | PDF landscape (~12 páginas) con tablas y gráficos |
| `Presupuesto_ROI_Datos.xlsx` | Excel con 7 hojas (ver detalle abajo) |

#### Estructura del PDF:
1. **Pág. 1 — Resumen Ejecutivo:** Inversión total por segmento + KPIs consolidados (todos los canales)
2. **Pág. 2 — KPIs Consolidados Segmento × Canal:** Tabla cruzada con todos los segmentos y canales, incluyendo período de leads, inversión, CPL, CPA, Revenue y ROI por cada combinación
3. **Pág. 3 — Comparativa de Atribución LT vs FT:** Tabla lado a lado mostrando inscriptos y revenue por canal según Last-Touch (principal) y First-Touch (alternativo), con diferencias absolutas y porcentuales
4. **Pág. 4 — KPIs por Grupo de Carreras:** Desglose de inversión y métricas de Facebook para **Grado_Pregrado** por grupos (A, B, C, CCC, etc.): spend, leads plataforma, impresiones, clics, CPL
5. **Pág. 5-7 — Detalle por Segmento:** KPIs por canal (Google, Facebook, Bot, Otros) + Top campañas Facebook para cada segmento
6. **Pág. 8+ — Gráficos:** CPL/CPA comparativo, distribución de inversión Facebook, top campañas por segmento

#### Hojas del Excel:
| Hoja | Contenido |
|---|---|
| `KPIs_Por_Canal` | KPIs por segmento y canal (inversión, leads, inscriptos, CPL, CPA, ROI) — modelo Last-Touch |
| `Atribucion_LT_vs_FT` | Comparativa Last-Touch vs First-Touch: inscriptos y revenue por segmento × canal |
| `Facebook_Detalle` | Detalle de todas las campañas Facebook **incluidas** (solo cohorte 2026) |
| `Top_FB_<segmento>` | Top 15 campañas Facebook por segmento |
| `FB_Excluidas_Resumen` | Campañas excluidas (años anteriores) con spend y leads, para auditoría |
| `FB_Por_Segmento_Anio` | Tabla cruzada Facebook: segmento × año de campaña, con columna `Incluida_en_ROI` |

### 16.6 Criterios y advertencias importantes para el equipo

1. **Google Ads es hardcodeado:** No se lee automáticamente. El equipo debe actualizar `GOOGLE_SPEND` en el script cuando tenga datos nuevos.
2. **Facebook se lee de archivos:** Colocar los exports de Meta en `data/1_raw/presupuestos/`. Se aceptan `.xlsx` y `.csv`.
3. **Revenue ≠ LTV:** `Insc_Haber` es el monto de inscripción, no el ingreso total esperado del alumno. El ROI real es mayor.
4. **Fuzzy excluido de conversiones:** Solo matches exactos (DNI, Email, Teléfono, Celular) cuentan como conversiones. Esto es conservador pero preciso.
5. **Muestras pequeñas:** Cursos y Posgrados pueden tener pocas inscripciones en los primeros meses del año, generando tasas de conversión volátiles. Interpretar con cautela.
6. **Sin impuestos (Google):** El gasto de Google reportado no incluye IVA ni retenciones. Para comparar con el costo real, el equipo financiero debe aplicar el factor impositivo correspondiente.
7. **Campañas mal clasificadas:** Si una campaña de Facebook tiene un nombre que no contiene las keywords correctas, caerá en Grado_Pregrado por defecto. Revisar la clasificación en la hoja `Facebook_Detalle` del Excel.

---

### Apéndice A — Columnas raw observadas
Ver: `marketing_report/scripts/columnas_raw.txt`