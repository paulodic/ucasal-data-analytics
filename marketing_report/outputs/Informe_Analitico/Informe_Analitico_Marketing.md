# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 17 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se analizaron un total de **217,633** leads únicos y **7,843** inscriptos únicos para identificar qué campañas e interacciones previas generaron las inscripciones finales.

| Métrica | Valor |
|---------|-------|
| Total Leads | 217,633 |
| Total Inscriptos | 7,843 |
| Inscriptos Atribuidos a un Lead (Exacto) | 4,296 (54.8% del total) |
| Inscriptos Directos (Sin Lead Previo) | 2,714 |
| **Tasa de Conversión General Leads (Exacta)** | **3.19%** |

### Desglose por Ecosistema Principal
*(Nota: Las tasas de conversión reflejan estrictamente cruces exactos sin contemplar coincidencias difusas)*
| Ecosistema | Total Leads | Inscriptos Atribuidos | Tasa de Conversión |
|------------|-------------|-----------------------|--------------------|
| **Google Ads** | 27,794 | 1,250 | **4.50%** |
| **Meta (FB/IG)** | 147,864 | 1,591 | **1.08%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 217,633 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 175,982 leads (80.9%)
- **Otros (Orgánico / Sin Tracking ID):** 41,651 leads (19.1%)

De igual manera, al observar solo las **6,945 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 2,847 (41.0%)
- **Inscripciones Orgánicas/Directas:** 4,098 (59.0%)

*(Nota sobre Fuzzys: Existen 833 leads sospechosos de ser inscriptos (833 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Visualización de Tasas y Atribución
![Conversión Leads](chart_1_conversion_leads.png)
![Composición Inscriptos](chart_2_composicion_inscriptos.png)
![Pagados vs Otros Leads](chart_5_leads_pagos_vs_otros.png)
![Pagados vs Otros Inscriptos](chart_7_inscriptos_pagos_vs_otros.png)

### Análisis de Tiempos de Resolución (Inscriptos Exactos)
Comparativa gráfica de cuánto demora en inscribirse un prospecto según su origen (filtrado de 0 a 180 días).

| Origen_Agrupado    |   Promedio |   Mediana |   Moda |
|:-------------------|-----------:|----------:|-------:|
| Orgánicos/Directos |       72.3 |        65 |      0 |
| Pagados (Meta/UTM) |       80.4 |        75 |      8 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día
![Volumen Consultas](chart_9_consultas_por_dia.png)



## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.2 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **191.5 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Desconocido**: 1644 inscriptos
- **Facebook Lead Ads**: 1526 inscriptos
- **Portales (4)**: 1401 inscriptos
- **Web Orgánico (3)**: 1392 inscriptos
- **Origen 103**: 345 inscriptos
- **Chatbot (907)**: 112 inscriptos
- **Origen 27**: 81 inscriptos
- **Origen 51**: 71 inscriptos
- **Origen 6**: 60 inscriptos
- **Origen 74**: 51 inscriptos

## 3. Curva de Inscripciones a lo largo del tiempo
La siguiente curva muestra el volumen de pagos confirmados por fecha, destacando los picos de inscripciones.

![Curva Inscripciones](chart_6_inscripciones_por_dia.png)

### Análisis de Picos de Inscripción
Los 4 días con mayor volumen de inscripciones confirmadas fueron:

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 30/01/2026 | Viernes | 324 |
| 24/10/2025 | Viernes | 302 |
| 23/12/2025 | Martes | 270 |
| 19/01/2026 | Lunes | 223 |


### Análisis de Valles de Inscripción (Días de menor actividad)
Analizando los días con las caídas más fuertes de inscripciones, podemos observar el patrón de comportamiento (mostrando los 15 días más bajos):

| Fecha | Día de la Semana | Cantidad de Inscripciones |
|-------|------------------|---------------------------|
| 08/11/2025 | Sábado | 2 |
| 11/10/2025 | Sábado | 3 |
| 02/11/2025 | Domingo | 3 |
| 09/11/2025 | Domingo | 3 |
| 16/11/2025 | Domingo | 3 |
| 04/01/2026 | Domingo | 3 |
| 05/10/2025 | Domingo | 4 |
| 07/12/2025 | Domingo | 4 |
| 24/12/2025 | Miércoles | 4 |
| 25/12/2025 | Jueves | 4 |
| 01/01/2026 | Jueves | 4 |
| 03/01/2026 | Sábado | 4 |
| 12/10/2025 | Domingo | 5 |
| 25/10/2025 | Sábado | 5 |
| 26/10/2025 | Domingo | 5 |


**Observación sobre los valles:** El 80.0% de los días con menor volumen de inscripciones del histórico analizado coinciden directamente con fines de semana (Sábado/Domingo).

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.

