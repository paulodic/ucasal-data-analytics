# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 17 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se analizaron un total de **207,186** leads únicos y **6,818** inscriptos únicos para identificar qué campañas e interacciones previas generaron las inscripciones finales.

| Métrica | Valor |
|---------|-------|
| Total Leads | 207,186 |
| Total Inscriptos | 6,818 |
| Inscriptos Atribuidos a un Lead (Exacto) | 3,898 (57.2% del total) |
| Inscriptos sin trazabilidad | 2,216 |
| **Tasa de Conversión General Leads (Exacta)** | **2.94%** |

### Desglose por Ecosistema Principal
*(Nota: Las tasas de conversión reflejan estrictamente cruces exactos sin contemplar coincidencias difusas)*
*(Nota Cohortes: Para Grado_Pregrado, las tasas de conversión asumen como denominador los leads ingresados a partir de Septiembre 2024, coincidiendo con el inicio de inscripción a la primera cohorte. En mayo se abren a la segunda.)*
| Ecosistema | Total Leads Analizados | Inscriptos Atribuidos | Tasa de Conversión |
|------------|------------------------|-----------------------|--------------------|
| **Google Ads** | 27,721 | 1,215 | **4.38%** |
| **Meta (FB/IG)** | 140,561 | 1,362 | **0.97%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 207,186 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 168,605 leads (81.4%)
- **Otros (Orgánico / Sin Tracking ID):** 38,581 leads (18.6%)

De igual manera, al observar solo las **6,275 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 2,583 (41.2%)
- **Inscripciones Orgánicas/Directas:** 3,692 (58.8%)

*(Nota sobre Fuzzys: Existen 704 leads sospechosos de ser inscriptos (704 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Visualización de Tasas y Atribución
![Conversión Leads](chart_1_conversion_leads.png)
![Composición Inscriptos](chart_2_composicion_inscriptos.png)
![Pagados vs Otros Leads](chart_5_leads_pagos_vs_otros.png)
![Pagados vs Otros Inscriptos](chart_7_inscriptos_pagos_vs_otros.png)

### Análisis de Tiempos de Resolución (Inscriptos Exactos)
Comparativa gráfica de cuánto demora en inscribirse un prospecto según su origen (filtrado de 0 a 180 días).

| Origen_Agrupado    |   Promedio |   Mediana |   Moda |
|:-------------------|-----------:|----------:|-------:|
| Orgánicos/Directos |       31.8 |        12 |      0 |
| Pagados (Meta/UTM) |       51.8 |        41 |      0 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.2 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **106.3 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Desconocido**: 1267 inscriptos
- **Portales (4)**: 957 inscriptos
- **Facebook Lead Ads**: 916 inscriptos
- **Web Orgánico (3)**: 873 inscriptos
- **Origen 103**: 167 inscriptos
- **Chatbot (907)**: 95 inscriptos
- **Origen 6**: 30 inscriptos
- **Origen 74**: 26 inscriptos
- **Origen 493**: 26 inscriptos
- **Origen 731**: 24 inscriptos

## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 30/01/2026 | Viernes | 289 |
| 24/10/2025 | Viernes | 288 |
| 23/12/2025 | Martes | 258 |
| 19/01/2026 | Lunes | 207 |


### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 14/12/2025 | Domingo | 0 |
| 08/11/2025 | Sábado | 2 |
| 09/11/2025 | Domingo | 2 |
| 07/12/2025 | Domingo | 2 |
| 01/02/2026 | Domingo | 2 |
| 11/10/2025 | Sábado | 3 |
| 02/11/2025 | Domingo | 3 |
| 16/11/2025 | Domingo | 3 |
| 01/01/2026 | Jueves | 3 |
| 03/01/2026 | Sábado | 3 |
| 04/01/2026 | Domingo | 3 |
| 04/10/2025 | Sábado | 4 |
| 05/10/2025 | Domingo | 4 |
| 01/11/2025 | Sábado | 4 |
| 24/12/2025 | Miércoles | 4 |


**Observación sobre los valles:** El 86.7% de los días con menor volumen de inscripciones del histórico analizado coinciden directamente con fines de semana (Sábado/Domingo).

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.

