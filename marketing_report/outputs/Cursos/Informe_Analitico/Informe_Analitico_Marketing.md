# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 14 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se analizaron un total de **608** leads únicos y **700** inscriptos únicos para identificar qué campañas e interacciones previas generaron las inscripciones finales.

| Métrica | Valor |
|---------|-------|
| Total Leads | 608 |
| Total Inscriptos | 700 |
| Inscriptos Atribuidos a un Lead (Exacto) | 358 (51.1% del total) |
| Inscriptos sin trazabilidad | 287 |
| **Tasa de Conversión General Leads (Exacta)** | **90.95%** |

### Desglose por Ecosistema Principal
*(Nota: Las tasas de conversión reflejan estrictamente cruces exactos sin contemplar coincidencias difusas)*

| Ecosistema | Total Leads Analizados | Inscriptos Atribuidos | Tasa de Conversión |
|------------|------------------------|-----------------------|--------------------|
| **Google Ads** | 40 | 26 | **65.00%** |
| **Meta (FB/IG)** | 205 | 182 | **88.78%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 608 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 246 leads (40.5%)
- **Otros (Orgánico / Sin Tracking ID):** 362 leads (59.5%)

De igual manera, al observar solo las **553 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 208 (37.6%)
- **Inscripciones Orgánicas/Directas:** 345 (62.4%)

*(Nota sobre Fuzzys: Existen 55 leads sospechosos de ser inscriptos (55 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Visualización de Tasas y Atribución
![Conversión Leads](chart_1_conversion_leads.png)
![Composición Inscriptos](chart_2_composicion_inscriptos.png)
![Pagados vs Otros Leads](chart_5_leads_pagos_vs_otros.png)
![Pagados vs Otros Inscriptos](chart_7_inscriptos_pagos_vs_otros.png)

### Análisis de Tiempos de Resolución (Inscriptos Exactos)
Comparativa gráfica de cuánto demora en inscribirse un prospecto según su origen (filtrado de 0 a 180 días).

| Origen_Agrupado    |   Promedio |   Mediana |   Moda |
|:-------------------|-----------:|----------:|-------:|
| Orgánicos/Directos |       40.3 |        30 |      0 |
| Pagados (Meta/UTM) |       67.2 |        67 |     67 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.4 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **114.3 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Desconocido**: 158 inscriptos
- **Facebook Lead Ads**: 141 inscriptos
- **Web Orgánico (3)**: 39 inscriptos
- **Portales (4)**: 36 inscriptos
- **Origen 51**: 18 inscriptos
- **Chatbot (907)**: 15 inscriptos
- **Origen 285**: 7 inscriptos
- **Origen 283**: 5 inscriptos
- **Origen 103**: 4 inscriptos
- **Origen 41**: 2 inscriptos

## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 02/02/2026 | Lunes | 27 |
| 29/01/2026 | Jueves | 24 |
| 30/01/2026 | Viernes | 20 |
| 19/12/2025 | Viernes | 17 |


### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 05/10/2025 | Domingo | 0 |
| 08/10/2025 | Miércoles | 0 |
| 11/10/2025 | Sábado | 0 |
| 12/10/2025 | Domingo | 0 |
| 19/10/2025 | Domingo | 0 |
| 25/10/2025 | Sábado | 0 |
| 26/10/2025 | Domingo | 0 |
| 02/11/2025 | Domingo | 0 |
| 03/11/2025 | Lunes | 0 |
| 08/11/2025 | Sábado | 0 |
| 13/11/2025 | Jueves | 0 |
| 16/11/2025 | Domingo | 0 |
| 21/11/2025 | Viernes | 0 |
| 23/11/2025 | Domingo | 0 |
| 06/12/2025 | Sábado | 0 |


**Observación sobre los valles:** El 73.3% de los días con menor volumen de inscripciones del histórico analizado coinciden directamente con fines de semana (Sábado/Domingo).

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.

