# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 14 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se procesaron **139** consultas únicas de Salesforce (cada una con su propio ID y origen), correspondientes a **111** personas distintas. Se cruzaron contra **325** inscriptos únicos.

| Métrica | Valor |
|---------|-------|
| Total Consultas (ID Consulta único) | 139 |
| Personas que consultaron | 111 |
| Total Inscriptos | 325 |
| Personas convertidas (Exacto) | 62 |
| Inscriptos atribuidos a Lead (Exacto) | 56 (17.2% del total) |
| Inscriptos sin trazabilidad | 221 |
| **Tasa de Conversion sobre Consultas** | **46.97%** *(inscriptos / consultas en ventana)* |
| **Tasa de Conversion sobre Personas** | **59.62%** *(inscriptos / personas en ventana)* |

> **Consultas vs Personas (Embudo):** Cada consulta tiene un ID unico de Salesforce y proviene de un canal especifico. Una persona puede generar multiples consultas desde distintos canales. Se presentan DOS tasas de conversion: sobre consultas (eficiencia por interaccion) y sobre personas (eficiencia por individuo). La tasa sobre personas es el KPI principal del embudo: Consultas -> Personas -> Inscriptos.

### Desglose por Ecosistema Principal (Any-Touch)
*(Nota: Las tasas de conversión reflejan cruces exactos. Modelo Any-Touch: una persona que consultó por Google Y por Meta se cuenta en ambos canales.)*

| Ecosistema | Consultas | Personas | Convertidas | Tasa s/Consultas | Tasa s/Personas |
|------------|-----------|----------|-------------|------------------|-----------------|
| **Google Ads** | 21 | 19 | 9 | 42.86% | **47.37%** |
| **Meta (FB/IG)** | 72 | 60 | 31 | 43.06% | **51.67%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 139 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 96 leads (69.1%)
- **Otros (Orgánico / Sin Tracking ID):** 43 leads (30.9%)

De igual manera, al observar solo las **63 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 37 (58.7%)
- **Inscripciones Orgánicas/Directas:** 26 (41.3%)

*(Nota sobre Fuzzys: Existen 48 leads sospechosos de ser inscriptos (48 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Atribución por Campaña
La columna `Campana_Lead` identifica si el lead que generó la inscripción pertenece a la campaña actual o a una anterior.
| Campaña | Inscriptos Exactos |
|---|---|
| Campaña actual (2026) | 8 |
| Campaña anterior (match histórico) | 55 |

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
| Orgánicos/Directos |       67.6 |        64 |     92 |
| Pagados (Meta/UTM) |       74.8 |        68 |      3 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



### Analisis Multi-Touch de Inscriptos
Cada inscripto puede haber consultado por multiples canales antes de inscribirse.

| Metrica | Total | 2026 | Campana Anterior |
|---|---|---|---|
| Inscriptos con 1 sola consulta | 41 (65.1%) | 5 (62.5%) | 36 (65.5%) |
| Promedio consultas por inscripto | 1.4 | 1.5 | 1.4 |
| Inscriptos con 1 canal | 58 (92.1%) | 7 (87.5%) | 51 (92.7%) |
| Inscriptos con 2+ canales | 5 (7.9%) | 1 (12.5%) | 4 (7.3%) |
| **Total inscriptos** | **63** | **8** | **55** |

#### Top Combinaciones (Total)
| Combinacion    |   Inscriptos |
|:---------------|-------------:|
| Meta           |           29 |
| Otros          |           19 |
| Google         |            6 |
| Bot            |            4 |
| Google + Otros |            2 |
| Meta + Otros   |            2 |
| Bot + Google   |            1 |

![Multi-Touch Canales](chart_multitouch_canales.png)
![Multi-Touch Combinaciones](chart_multitouch_combinaciones.png)
![Multi-Touch por Campana](chart_multitouch_por_campana.png)

### Analisis Any-Touch: Participacion por Canal
Para cada inscripto se verifica si tuvo **al menos 1 contacto** con cada canal.
Un inscripto puede aparecer en varios canales a la vez (la suma supera 100%).

| Canal | Total | 2026 | Campana Anterior |
|---|---|---|---|
| **Bot** | 5 (7.9%) | 4 (50.0%) | 1 (1.8%) |
| **Google Ads** | 9 (14.3%) | 2 (25.0%) | 7 (12.7%) |
| **Meta (FB/IG)** | 31 (49.2%) | 0 (0.0%) | 31 (56.4%) |
| **Otros** | 23 (36.5%) | 3 (37.5%) | 20 (36.4%) |

#### Desglose por Tipo de Match (mejor match por persona, prioridad DNI > Email > Tel > Cel)
| Tipo Match | Total | 2026 | Campana Anterior |
|---|---|---|---|
| **Exacto (DNI)** | 23 (36.5%) | 4 (50.0%) | 19 (34.5%) |
| **Exacto (Email)** | 18 (28.6%) | 3 (37.5%) | 15 (27.3%) |
| **Exacto (Telefono)** | 15 (23.8%) | 1 (12.5%) | 14 (25.5%) |
| **Exacto (Celular)** | 7 (11.1%) | 0 (0.0%) | 7 (12.7%) |

![Any-Touch Participacion](chart_anytouch_participacion.png)
![Any-Touch por Campana](chart_anytouch_por_campana.png)


## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.3 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **161.8 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Facebook Lead Ads**: 28 inscriptos
- **Web Orgánico (3)**: 17 inscriptos
- **Chatbot (907)**: 4 inscriptos
- **Portales (4)**: 3 inscriptos
- **Origen 103**: 3 inscriptos
- **Desconocido**: 2 inscriptos
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
- **Modelo de este informe: Any-Touch ESTANDAR** - Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Incluye todas las consultas, sin filtro de fecha vs pago.
- **Modelo Causal (informe separado):** Solo cuenta consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago (Consulta <= Insc_Fecha Pago). Consultas post-pago excluidas. Ver `Presupuesto_ROI_Causal`.
- **Tasas de conversion:** Se presentan dos tasas complementarias: (1) **sobre consultas** = inscriptos / consultas en ventana, mide eficiencia por interaccion; (2) **sobre personas** = inscriptos / personas unicas en ventana, mide eficiencia por individuo (KPI principal). Embudo: Consultas -> Personas -> Inscriptos. Ventana: leads del ano calendario.
- **Fuente:** Consultas exportadas de Salesforce, inscriptos del sistema academico.

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.


## Atribucion Causal (consulta <= fecha de pago)

*Ventana: 01/01/2026 - 13/02/2026 | desde Ene 2026 (ano calendario)*

Consultas post-pago excluidas: 2

| Canal | Inscriptos (Any-Touch Causal) | % Participacion |
|-------|---:|---:|
| Google | 0 | 0.0% |
| Facebook | 0 | 0.0% |
| Bot | 2 | 40.0% |
| Otros | 3 | 60.0% |
| **Total Unico** | **5** | **100%** |

Multi-canal: 1 canal=5, 2 canales=0, 3+=0

Inscriptos sin lead/match: 29 de 33 (87.9%)

*Nota: El modelo causal solo cuenta consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago. Consultas post-pago (soporte, seguimiento) excluidas.*

