# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 17 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se analizaron un total de **398,556** leads únicos y **9,525** inscriptos únicos para identificar qué campañas e interacciones previas generaron las inscripciones finales.

| Métrica | Valor |
|---------|-------|
| Total Leads | 398,556 |
| Total Inscriptos | 9,525 |
| Inscriptos Atribuidos a un Lead (Exacto) | 7,993 (83.9% del total) |
| Inscriptos sin trazabilidad | 1,377 |
| **Tasa de Conversión General Leads (Exacta)** | **4.80%** |

### Desglose por Ecosistema Principal
*(Nota: Las tasas de conversión reflejan estrictamente cruces exactos sin contemplar coincidencias difusas)*
*(Nota Cohortes: Para Grado_Pregrado, las tasas de conversión asumen como denominador los leads ingresados a partir de Septiembre 2025, coincidiendo con el inicio de inscripción a la primera cohorte. En mayo se abren a la segunda.)*
| Ecosistema | Total Leads Analizados | Inscriptos Atribuidos | Tasa de Conversión |
|------------|------------------------|-----------------------|--------------------|
| **Google Ads** | 27,170 | 1,756 | **6.46%** |
| **Meta (FB/IG)** | 148,479 | 1,494 | **1.01%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 398,556 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 321,665 leads (80.7%)
- **Otros (Orgánico / Sin Tracking ID):** 76,891 leads (19.3%)

De igual manera, al observar solo las **13,170 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 4,281 (32.5%)
- **Inscripciones Orgánicas/Directas:** 8,889 (67.5%)

*(Nota sobre Fuzzys: Existen 155 leads sospechosos de ser inscriptos (155 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Atribución por Campaña
La columna `Campana_Lead` identifica si el lead que generó la inscripción pertenece a la campaña actual o a una anterior.
| Campaña | Inscriptos Exactos |
|---|---|
| Campaña actual (Ingreso 2026) | 10,448 |
| Campaña anterior (match histórico) | 2,722 |

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
| Orgánicos/Directos |       28.6 |         9 |      0 |
| Pagados (Meta/UTM) |       39.2 |        19 |      0 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



### Analisis Multi-Touch de Inscriptos
Cada inscripto puede haber consultado por multiples canales antes de inscribirse.

| Metrica | Total | Ingreso 2026 | Campana Anterior |
|---|---|---|---|
| Inscriptos con 1 sola consulta | 5,181 (64.9%) | 4,469 (64.1%) | 712 (70.9%) |
| Promedio consultas por inscripto | 1.7 | 1.7 | 1.5 |
| Inscriptos con 1 canal | 6,653 (83.4%) | 5,748 (82.4%) | 905 (90.1%) |
| Inscriptos con 2+ canales | 1,327 (16.6%) | 1,228 (17.6%) | 99 (9.9%) |
| **Total inscriptos** | **7,980** | **6,976** | **1,004** |

#### Top Combinaciones (Total)
| Combinacion           |   Inscriptos |
|:----------------------|-------------:|
| Otros                 |         4678 |
| Google                |         1024 |
| Meta                  |          749 |
| Google + Otros        |          556 |
| Meta + Otros          |          266 |
| Bot                   |          202 |
| Bot + Otros           |          170 |
| Google + Meta         |           89 |
| Google + Meta + Otros |           67 |
| Bot + Google + Otros  |           46 |

![Multi-Touch Canales](chart_multitouch_canales.png)
![Multi-Touch Combinaciones](chart_multitouch_combinaciones.png)
![Multi-Touch por Campana](chart_multitouch_por_campana.png)

### Analisis Any-Touch: Participacion por Canal
Para cada inscripto se verifica si tuvo **al menos 1 contacto** con cada canal.
Un inscripto puede aparecer en varios canales a la vez (la suma supera 100%).

| Canal | Total | Ingreso 2026 | Campana Anterior |
|---|---|---|---|
| **Bot** | 551 (6.9%) | 550 (7.9%) | 1 (0.1%) |
| **Google Ads** | 1,855 (23.2%) | 1,597 (22.9%) | 258 (25.7%) |
| **Meta (FB/IG)** | 1,258 (15.8%) | 1,142 (16.4%) | 116 (11.6%) |
| **Otros** | 5,818 (72.9%) | 5,090 (73.0%) | 728 (72.5%) |

#### Desglose por Tipo de Match (mejor match por persona, prioridad DNI > Email > Tel > Cel)
| Tipo Match | Total | Ingreso 2026 | Campana Anterior |
|---|---|---|---|
| **Exacto (DNI)** | 5,333 (66.8%) | 4,526 (64.9%) | 807 (80.4%) |
| **Exacto (Email)** | 2,150 (26.9%) | 2,018 (28.9%) | 132 (13.1%) |
| **Exacto (Telefono)** | 284 (3.6%) | 239 (3.4%) | 45 (4.5%) |
| **Exacto (Celular)** | 213 (2.7%) | 193 (2.8%) | 20 (2.0%) |

![Any-Touch Participacion](chart_anytouch_participacion.png)
![Any-Touch por Campana](chart_anytouch_por_campana.png)


## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.3 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **59.5 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Desconocido**: 3000 inscriptos
- **Web Orgánico (3)**: 1458 inscriptos
- **Portales (4)**: 1383 inscriptos
- **Facebook Lead Ads**: 854 inscriptos
- **Origen 103**: 328 inscriptos
- **Chatbot (907)**: 251 inscriptos
- **Origen 51**: 71 inscriptos
- **Origen 6**: 70 inscriptos
- **Origen 74**: 42 inscriptos
- **Origen 493**: 34 inscriptos

## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 26/09/2025 | Viernes | 403 |
| 30/01/2026 | Viernes | 308 |
| 24/10/2025 | Viernes | 302 |
| 23/12/2025 | Martes | 268 |


### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 14/12/2025 | Domingo | 0 |
| 28/09/2025 | Domingo | 1 |
| 08/11/2025 | Sábado | 2 |
| 11/10/2025 | Sábado | 3 |
| 02/11/2025 | Domingo | 3 |
| 09/11/2025 | Domingo | 3 |
| 16/11/2025 | Domingo | 3 |
| 01/01/2026 | Jueves | 3 |
| 03/01/2026 | Sábado | 3 |
| 04/01/2026 | Domingo | 3 |
| 05/10/2025 | Domingo | 4 |
| 07/12/2025 | Domingo | 4 |
| 24/12/2025 | Miércoles | 4 |
| 25/12/2025 | Jueves | 4 |
| 14/09/2025 | Domingo | 5 |


**Observación sobre los valles:** El 80.0% de los días con menor volumen de inscripciones del histórico analizado coinciden directamente con fines de semana (Sábado/Domingo).

## Nota Metodologica
- **Cruce de datos:** Deduplicado por persona (DNI). Match exacto por DNI, Email, Telefono y Celular.
- **Modelo Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Detalle en secciones de Multi-Touch y Any-Touch de este informe.
- **Tasas de conversion:** Calculadas sobre la muestra de la campana actual (leads desde Sep 2025).
- **Fuente:** Consultas exportadas de Salesforce, inscriptos del sistema academico.

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.

