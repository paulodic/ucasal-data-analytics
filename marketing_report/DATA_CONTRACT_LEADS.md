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

### Apéndice A — Columnas raw observadas
Ver: `marketing_report/scripts/columnas_raw.txt`