# Informe Analítico de Marketing y Trazabilidad

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aquí están pendientes de verificación.**

*(Datos actualizados al 17 de febrero de 2026)*

Este informe consolida el análisis generado a partir del cruce de bases de datos de **Consultas (Leads en Salesforce)** e **Inscriptos**, unificando los orígenes y calculando el "Journey" de las personas. Durante la lectura de las bases de datos originales se aplicaron procesos de **deduplicación** para garantizar que los solapamientos de archivos no duplicaran los registros.

## 1. Resumen Ejecutivo
Se procesaron **398,442** consultas únicas de Salesforce (cada una con su propio ID y origen), correspondientes a **305,232** personas distintas. Se cruzaron contra **9,525** inscriptos únicos.

| Métrica | Valor |
|---------|-------|
| Total Consultas (ID Consulta único) | 398,442 |
| Personas que consultaron | 305,232 |
| Total Inscriptos | 9,525 |
| Personas convertidas (Exacto) | 6,895 |
| Inscriptos atribuidos a Lead (Exacto) | 7,984 (83.8% del total) |
| Inscriptos sin trazabilidad | 1,388 |
| **Tasa de Conversion sobre Consultas** | **3.24%** *(inscriptos / consultas en ventana)* |
| **Tasa de Conversion sobre Personas** | **4.05%** *(inscriptos / personas en ventana)* |

> **Consultas vs Personas (Embudo):** Cada consulta tiene un ID unico de Salesforce y proviene de un canal especifico. Una persona puede generar multiples consultas desde distintos canales. Se presentan DOS tasas de conversion: sobre consultas (eficiencia por interaccion) y sobre personas (eficiencia por individuo). La tasa sobre personas es el KPI principal del embudo: Consultas -> Personas -> Inscriptos.

### Desglose por Ecosistema Principal (Any-Touch)
*(Nota: Las tasas de conversión reflejan cruces exactos. Modelo Any-Touch: una persona que consultó por Google Y por Meta se cuenta en ambos canales.)*
*(Nota Cohortes: Para Grado_Pregrado, las tasas de conversión asumen como denominador las personas que consultaron a partir de Septiembre 2025, coincidiendo con el inicio de inscripción a la primera cohorte. En mayo se abren a la segunda.)*
| Ecosistema | Consultas | Personas | Convertidas | Tasa s/Consultas | Tasa s/Personas |
|------------|-----------|----------|-------------|------------------|-----------------|
| **Google Ads** | 27,163 | 23,722 | 1,399 | 5.15% | **5.90%** |
| **Meta (FB/IG)** | 148,445 | 125,561 | 1,080 | 0.73% | **0.86%** |

### Procedencia de Leads (Pagado vs Orgánico/Desconocido)
De los 398,442 leads capturados, se analizó cuántos poseen parámetros tracking (UTM) o provienen directamente de formularios dentro de redes (ej. Facebook Lead Ads), frente a los que no tienen este tracking:
- **Plataformas Pagadas Confirmadas:** 321,617 leads (80.7%)
- **Otros (Orgánico / Sin Tracking ID):** 76,825 leads (19.3%)

De igual manera, al observar solo las **7,937 inscripciones (cruces exactos)** logradas a partir de leads, la distribución de origen es:
- **Inscripciones Pagadas (Meta/UTM):** 2,286 (28.8%)
- **Inscripciones Orgánicas/Directas:** 5,651 (71.2%)

*(Nota sobre Fuzzys: Existen 153 leads sospechosos de ser inscriptos (153 inscriptos) que fueron encontrados mediante algoritmos de similitud de nombres y requieren verificación manual. NO han sido incluidos en ninguna tasa de conversión).*

### Atribución por Campaña
La columna `Campana_Lead` identifica si el lead que generó la inscripción pertenece a la campaña actual o a una anterior.
| Campaña | Inscriptos Exactos |
|---|---|
| Campaña actual (Ingreso 2026) | 6,381 |
| Campaña anterior (match histórico) | 1,556 |

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
| Orgánicos/Directos |       24.6 |         7 |      0 |
| Pagados (Meta/UTM) |       33.8 |        15 |      0 |

![Tiempos Resolucion](chart_8_tiempos_resolucion.png)
### Volumen de Consultas por Día y Mes
![Volumen Consultas Mes](chart_9b_consultas_por_mes.png)

![Volumen Consultas Dia](chart_9_consultas_por_dia.png)



### Analisis Multi-Touch de Inscriptos
Cada inscripto puede haber consultado por multiples canales antes de inscribirse.

| Metrica | Total | Ingreso 2026 | Campana Anterior |
|---|---|---|---|
| Inscriptos con 1 sola consulta | 5,160 (65.0%) | 4,454 (64.2%) | 706 (70.8%) |
| Promedio consultas por inscripto | 1.6 | 1.7 | 1.5 |
| Inscriptos con 1 canal | 6,614 (83.3%) | 5,716 (82.4%) | 898 (90.1%) |
| Inscriptos con 2+ canales | 1,323 (16.7%) | 1,224 (17.6%) | 99 (9.9%) |
| **Total inscriptos** | **7,937** | **6,940** | **997** |

#### Top Combinaciones (Total)
| Combinacion           |   Inscriptos |
|:----------------------|-------------:|
| Otros                 |         4655 |
| Google                |         1024 |
| Meta                  |          732 |
| Google + Otros        |          555 |
| Meta + Otros          |          266 |
| Bot                   |          203 |
| Bot + Otros           |          170 |
| Google + Meta         |           88 |
| Google + Meta + Otros |           66 |
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
| **Google Ads** | 1,852 (23.3%) | 1,594 (23.0%) | 258 (25.9%) |
| **Meta (FB/IG)** | 1,238 (15.6%) | 1,126 (16.2%) | 112 (11.2%) |
| **Otros** | 5,793 (73.0%) | 5,068 (73.0%) | 725 (72.7%) |

#### Desglose por Tipo de Match (mejor match por persona, prioridad DNI > Email > Tel > Cel)
| Tipo Match | Total | Ingreso 2026 | Campana Anterior |
|---|---|---|---|
| **Exacto (DNI)** | 5,333 (67.2%) | 4,526 (65.2%) | 807 (80.9%) |
| **Exacto (Email)** | 2,150 (27.1%) | 2,018 (29.1%) | 132 (13.2%) |
| **Exacto (Telefono)** | 237 (3.0%) | 200 (2.9%) | 37 (3.7%) |
| **Exacto (Celular)** | 217 (2.7%) | 196 (2.8%) | 21 (2.1%) |

![Any-Touch Participacion](chart_anytouch_participacion.png)
![Any-Touch por Campana](chart_anytouch_por_campana.png)


## 2. Journey del Estudiante (Comportamiento)
Analizando el número de veces que un usuario consulta antes de pagar su matrícula, observamos los siguientes patrones:

- **Promedio de Consultas por Persona:** 1.3 veces.
- **Tiempo de Decisión Promedio:** Un usuario tarda en promedio **59.4 días** desde su primera consulta hasta que formaliza el pago.

### Principales Fuentes que Inician el Recorrido (1er Touch) en Usuarios Inscriptos:
![Top Fuentes](chart_3_top_fuentes.png)
- **Desconocido**: 2997 inscriptos
- **Web Orgánico (3)**: 1439 inscriptos
- **Portales (4)**: 1383 inscriptos
- **Facebook Lead Ads**: 833 inscriptos
- **Origen 103**: 328 inscriptos
- **Chatbot (907)**: 252 inscriptos
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
- **Modelo de este informe: Any-Touch ESTANDAR** - Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Incluye todas las consultas, sin filtro de fecha vs pago.
- **Modelo Causal (informe separado):** Solo cuenta consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago (Consulta <= Insc_Fecha Pago). Consultas post-pago excluidas. Ver `Presupuesto_ROI_Causal`.
- **Tasas de conversion:** Se presentan dos tasas complementarias: (1) **sobre consultas** = inscriptos / consultas en ventana, mide eficiencia por interaccion; (2) **sobre personas** = inscriptos / personas unicas en ventana, mide eficiencia por individuo (KPI principal). Embudo: Consultas -> Personas -> Inscriptos. Ventana: leads desde Sep 2025.
- **Fuente:** Consultas exportadas de Salesforce, inscriptos del sistema academico.

## Conclusiones y Recomendaciones

1. **Atribución de Marketing:** Se logró trazar el origen de un alto porcentaje de inscriptos, lo que demuestra que los esfuerzos de captación inicial en Salesforce tienen un impacto directo comprobable.
2. **Tiempo de Maduración:** Dado que el tiempo promedio de decisión supera el contacto inicial, las estrategias de "Remarketing" o "Nutrición de Leads" por email/teléfono durante estas semanas intermedias son vitales.
3. **Calidad de Datos:** Una porción de los registros se inscribió de manera directa o ingresó usando correos/teléfonos muy distintos. Se recomienda continuar fortaleciendo la trazabilidad mediante canales digitales.


## Atribucion Causal (consulta <= fecha de pago)

*Ventana: 01/09/2025 - 17/02/2026 | desde Sep 2025 (Cohorte Ingreso 2026)*

Consultas post-pago excluidas: 823

| Canal | Inscriptos (Any-Touch Causal) | % Participacion |
|-------|---:|---:|
| Google | 1,354 | 20.6% |
| Facebook | 1,009 | 15.4% |
| Bot | 315 | 4.8% |
| Otros | 4,715 | 71.8% |
| **Total Unico** | **6,565** | **100%** |

Multi-canal: 1 canal=5,824, 2 canales=659, 3+=82

Inscriptos sin lead/match: 1,145 de 5,553 (20.6%)

*Nota: El modelo causal solo cuenta consultas cuya fecha es ANTERIOR O IGUAL a la fecha de pago. Consultas post-pago (soporte, seguimiento) excluidas.*

