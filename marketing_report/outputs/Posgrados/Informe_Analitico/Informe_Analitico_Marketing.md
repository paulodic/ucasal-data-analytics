# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 14 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se analizaron un total de **178** leads únicos y **325** inscriptos únicos para identificar qué campañas e interacciones previas generaron las inscripciones finales.

| Métrica | Valor |
|---------|-------|
| Total Leads | 178 |
| Total Inscriptos | 325 |
| Inscriptos Atribuidos a un Lead (Exacto) | 58 (17.8% del total) |
| Inscriptos sin trazabilidad | 222 |
| **Tasa de Conversión General Leads (Exacta)** | **74.68%** |

### Desglose por Ecosistema Principal
*(Nota: Las tasas de conversión reflejan estrictamente cruces exactos sin contemplar coincidencias difusas)*

| Ecosistema | Total Leads Analizados | Inscriptos Atribuidos | Tasa de Conversión |
|------------|------------------------|-----------------------|--------------------|
| **Google Ads** | 23 | 13 | **56.52%** |
| **Meta (FB/IG)** | 90 | 63 | **70.00%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 178 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 119 leads (66.9%)
- **Otros (Orgánico / Sin Tracking ID):** 59 leads (33.1%)

De igual manera, al observar solo las **133 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 79 (59.4%)
- **Inscripciones Orgánicas/Directas:** 54 (40.6%)

*(Nota sobre Fuzzys: Existen 45 leads sospechosos de ser inscriptos (45 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Atribución por Campaña
La columna `Campana_Lead` identifica si el lead que generó la inscripción pertenece a la campaña actual o a una anterior.
| Campaña | Inscriptos Exactos |
|---|---|
| Campaña actual (2026) | 34 |
| Campaña anterior (match histórico) | 99 |

### Visualización de Tasas y Atribución
![Conversión Leads](chart_1_conversion_leads.png)
![Composición Inscriptos](chart_2_composicion_inscriptos.png)
![Pagados vs Otros Leads](chart_5_leads_pagos_vs_otros.png)
![Pagados vs Otros Inscriptos](chart_7_inscriptos_pagos_vs_otros.png)

![Comparativa por Campana](chart_2b_campana_comparativa.png)

### Análisis de Tiempos de Resolución (Inscriptos Exactos)
Comparativa gráfica de cuánto demora en inscribirse un prospecto según su origen (filtrado de 0 a 180 días).

| Origen_Agrupado    |   Promedio |   Mediana |   Moda |
|:-------------------|-----------:|----------:|-------:|
| Orgánicos/Directos |       60.9 |        29 |      2 |
| Pagados (Meta/UTM) |       81.1 |        89 |      3 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



### Analisis Multi-Touch de Inscriptos
Cada inscripto puede haber consultado por multiples canales antes de inscribirse.

| Metrica | Total | 2026 | Campana Anterior |
|---|---|---|---|
| Inscriptos con 1 sola consulta | 73 (73.0%) | 23 (76.7%) | 50 (71.4%) |
| Promedio consultas por inscripto | 1.3 | 1.3 | 1.4 |
| Inscriptos con 1 canal | 94 (94.0%) | 28 (93.3%) | 66 (94.3%) |
| Inscriptos con 2+ canales | 6 (6.0%) | 2 (6.7%) | 4 (5.7%) |
| **Total inscriptos** | **100** | **30** | **70** |

#### Top Combinaciones (Total)
| Combinacion    |   Inscriptos |
|:---------------|-------------:|
| Meta           |           48 |
| Otros          |           35 |
| Google         |            7 |
| Bot            |            4 |
| Google + Otros |            2 |
| Meta + Otros   |            2 |
| Bot + Google   |            1 |
| Google + Meta  |            1 |

![Multi-Touch Canales](chart_multitouch_canales.png)
![Multi-Touch Combinaciones](chart_multitouch_combinaciones.png)
![Multi-Touch por Campana](chart_multitouch_por_campana.png)

### Analisis Any-Touch: Participacion por Canal
Para cada inscripto se verifica si tuvo **al menos 1 contacto** con cada canal.
Un inscripto puede aparecer en varios canales a la vez (la suma supera 100%).

| Canal | Total | 2026 | Campana Anterior |
|---|---|---|---|
| **Bot** | 5 (5.0%) | 4 (13.3%) | 1 (1.4%) |
| **Google Ads** | 11 (11.0%) | 3 (10.0%) | 8 (11.4%) |
| **Meta (FB/IG)** | 51 (51.0%) | 8 (26.7%) | 43 (61.4%) |
| **Otros** | 39 (39.0%) | 17 (56.7%) | 22 (31.4%) |

#### Desglose por Tipo de Match (mejor match por persona, prioridad DNI > Email > Tel > Cel)
| Tipo Match | Total | 2026 | Campana Anterior |
|---|---|---|---|
| **Exacto (DNI)** | 23 (23.0%) | 4 (13.3%) | 19 (27.1%) |
| **Exacto (Email)** | 18 (18.0%) | 3 (10.0%) | 15 (21.4%) |
| **Exacto (Telefono)** | 52 (52.0%) | 23 (76.7%) | 29 (41.4%) |
| **Exacto (Celular)** | 7 (7.0%) | 0 (0.0%) | 7 (10.0%) |

![Any-Touch Participacion](chart_anytouch_participacion.png)
![Any-Touch por Campana](chart_anytouch_por_campana.png)


## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.2 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **133.0 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Facebook Lead Ads**: 48 inscriptos
- **Web Orgánico (3)**: 30 inscriptos
- **Chatbot (907)**: 4 inscriptos
- **Portales (4)**: 4 inscriptos
- **Desconocido**: 4 inscriptos
- **Origen 103**: 3 inscriptos
- **Origen 37**: 1 inscriptos
- **Origen 394**: 1 inscriptos
- **Origen 74**: 1 inscriptos
- **Origen 701**: 1 inscriptos

## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 19/12/2025 | Viernes | 16 |
| 28/11/2025 | Viernes | 15 |
| 30/01/2026 | Viernes | 15 |
| 17/12/2025 | Miércoles | 14 |


### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 01/11/2025 | Sábado | 0 |
| 02/11/2025 | Domingo | 0 |
| 03/11/2025 | Lunes | 0 |
| 04/11/2025 | Martes | 0 |
| 05/11/2025 | Miércoles | 0 |
| 06/11/2025 | Jueves | 0 |
| 07/11/2025 | Viernes | 0 |
| 08/11/2025 | Sábado | 0 |
| 09/11/2025 | Domingo | 0 |
| 10/11/2025 | Lunes | 0 |
| 11/11/2025 | Martes | 0 |
| 14/11/2025 | Viernes | 0 |
| 15/11/2025 | Sábado | 0 |
| 16/11/2025 | Domingo | 0 |
| 21/11/2025 | Viernes | 0 |


**Observación sobre los valles:** El 40.0% de los días con menor volumen de inscripciones del histórico analizado coinciden directamente con fines de semana (Sábado/Domingo).

## Nota Metodologica
- **Cruce de datos:** Deduplicado por persona (DNI). Match exacto por DNI, Email, Telefono y Celular.
- **Modelo Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Detalle en secciones de Multi-Touch y Any-Touch de este informe.
- **Tasas de conversion:** Calculadas sobre la muestra de la campana actual (leads del ano calendario).
- **Fuente:** Consultas exportadas de Salesforce, inscriptos del sistema academico.

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.

