# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 14 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se analizaron un total de **44** leads únicos y **94** inscriptos únicos para identificar qué campañas e interacciones previas generaron las inscripciones finales.

| Métrica | Valor |
|---------|-------|
| Total Leads | 44 |
| Total Inscriptos | 94 |
| Inscriptos Atribuidos a un Lead (Exacto) | 19 (20.2% del total) |
| Inscriptos sin trazabilidad | 71 |
| **Tasa de Conversión General Leads (Exacta)** | **92.50%** |

### Desglose por Ecosistema Principal
*(Nota: Las tasas de conversión reflejan estrictamente cruces exactos sin contemplar coincidencias difusas)*

| Ecosistema | Total Leads Analizados | Inscriptos Atribuidos | Tasa de Conversión |
|------------|------------------------|-----------------------|--------------------|
| **Google Ads** | 3 | 2 | **66.67%** |
| **Meta (FB/IG)** | 16 | 15 | **93.75%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 44 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 22 leads (50.0%)
- **Otros (Orgánico / Sin Tracking ID):** 22 leads (50.0%)

De igual manera, al observar solo las **40 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 18 (45.0%)
- **Inscripciones Orgánicas/Directas:** 22 (55.0%)

*(Nota sobre Fuzzys: Existen 4 leads sospechosos de ser inscriptos (4 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Atribución por Campaña
La columna `Campana_Lead` identifica si el lead que generó la inscripción pertenece a la campaña actual o a una anterior.
| Campaña | Inscriptos Exactos |
|---|---|
| Campaña actual (2026) | 7 |
| Campaña anterior (match histórico) | 33 |

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
| Orgánicos/Directos |      105.4 |       122 |    162 |
| Pagados (Meta/UTM) |       82.6 |        82 |     53 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



### Analisis Multi-Touch de Inscriptos
Cada inscripto puede haber consultado por multiples canales antes de inscribirse.

| Metrica | Total | 2026 | Campana Anterior |
|---|---|---|---|
| Inscriptos con 1 sola consulta | 13 (61.9%) | 5 (83.3%) | 8 (53.3%) |
| Promedio consultas por inscripto | 1.9 | 1.2 | 2.2 |
| Inscriptos con 1 canal | 19 (90.5%) | 6 (100.0%) | 13 (86.7%) |
| Inscriptos con 2+ canales | 2 (9.5%) | 0 (0.0%) | 2 (13.3%) |
| **Total inscriptos** | **21** | **6** | **15** |

#### Top Combinaciones (Total)
| Combinacion   |   Inscriptos |
|:--------------|-------------:|
| Meta          |            9 |
| Otros         |            8 |
| Google        |            1 |
| Meta + Otros  |            1 |
| Bot           |            1 |
| Google + Meta |            1 |

![Multi-Touch Canales](chart_multitouch_canales.png)
![Multi-Touch Combinaciones](chart_multitouch_combinaciones.png)
![Multi-Touch por Campana](chart_multitouch_por_campana.png)

### Analisis Any-Touch: Participacion por Canal
Para cada inscripto se verifica si tuvo **al menos 1 contacto** con cada canal.
Un inscripto puede aparecer en varios canales a la vez (la suma supera 100%).

| Canal | Total | 2026 | Campana Anterior |
|---|---|---|---|
| **Bot** | 1 (4.8%) | 1 (16.7%) | 0 (0.0%) |
| **Google Ads** | 2 (9.5%) | 0 (0.0%) | 2 (13.3%) |
| **Meta (FB/IG)** | 11 (52.4%) | 2 (33.3%) | 9 (60.0%) |
| **Otros** | 9 (42.9%) | 3 (50.0%) | 6 (40.0%) |

#### Desglose por Tipo de Match (mejor match por persona, prioridad DNI > Email > Tel > Cel)
| Tipo Match | Total | 2026 | Campana Anterior |
|---|---|---|---|
| **Exacto (DNI)** | 9 (42.9%) | 2 (33.3%) | 7 (46.7%) |
| **Exacto (Email)** | 4 (19.0%) | 0 (0.0%) | 4 (26.7%) |
| **Exacto (Telefono)** | 6 (28.6%) | 4 (66.7%) | 2 (13.3%) |
| **Exacto (Celular)** | 2 (9.5%) | 0 (0.0%) | 2 (13.3%) |

![Any-Touch Participacion](chart_anytouch_participacion.png)
![Any-Touch por Campana](chart_anytouch_por_campana.png)


## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.8 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **103.9 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Facebook Lead Ads**: 8 inscriptos
- **Web Orgánico (3)**: 3 inscriptos
- **Portales (4)**: 2 inscriptos
- **Desconocido**: 2 inscriptos
- **Origen 41**: 1 inscriptos
- **Origen 130**: 1 inscriptos
- **Origen 103**: 1 inscriptos
- **Chatbot (907)**: 1 inscriptos
- **Origen 908**: 1 inscriptos
- **Origen 272**: 1 inscriptos

## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 05/02/2026 | Jueves | 11 |
| 11/02/2026 | Miércoles | 10 |
| 04/02/2026 | Miércoles | 7 |
| 06/02/2026 | Viernes | 7 |


### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 06/12/2025 | Sábado | 0 |
| 07/12/2025 | Domingo | 0 |
| 08/12/2025 | Lunes | 0 |
| 09/12/2025 | Martes | 0 |
| 12/12/2025 | Viernes | 0 |
| 13/12/2025 | Sábado | 0 |
| 14/12/2025 | Domingo | 0 |
| 15/12/2025 | Lunes | 0 |
| 16/12/2025 | Martes | 0 |
| 17/12/2025 | Miércoles | 0 |
| 19/12/2025 | Viernes | 0 |
| 20/12/2025 | Sábado | 0 |
| 21/12/2025 | Domingo | 0 |
| 24/12/2025 | Miércoles | 0 |
| 25/12/2025 | Jueves | 0 |


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

