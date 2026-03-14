# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 17 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **305,247** personas únicas (agrupadas por persona) en la base de datos.
El tipo de match mostrado es el de mayor prioridad por persona (DNI > Email > Telefono > Celular).

- **Personas Matcheadas (Exacto):** 7,937 (2.6%)
  - por DNI: 5,333
  - por Email: 2,150
  - por Telefono: 237
  - por Celular: 217
- **Personas No Matcheadas:** 297,310 (97.4%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |              3838 |           68.1 |               208804 |              82.5 |
| 2 consultas   |              1105 |           19.6 |                32603 |              12.9 |
| 3 consultas   |               398 |            7.1 |                 7705 |               3   |
| 4 consultas   |               158 |            2.8 |                 2388 |               0.9 |
| 5 consultas   |                73 |            1.3 |                  815 |               0.3 |
| 6 consultas   |                27 |            0.5 |                  366 |               0.1 |
| 7 consultas   |                15 |            0.3 |                  187 |               0.1 |
| 8 consultas   |                 9 |            0.2 |                   80 |               0   |
| 9 consultas   |                 3 |            0.1 |                   57 |               0   |
| 10 consultas  |                 4 |            0.1 |                   36 |               0   |
| 10+ consultas |                 8 |            0.1 |                   85 |               0   |

## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)

Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.

Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).

**Personas analizadas:** 3,205
- **Promedio:** 70 días
- **Mediana:** 22 días
- **Moda (Valor Más Frecuente):** 0 días

**Nota:** Las gráficas 2a y 2b utilizan los mismos rangos de días para garantizar coherencia. La gráfica 2a muestra la distribución como histograma continuo, mientras que 2b presenta los datos como barras categóricas con porcentajes y acumulados.

### 2b. Distribución por Rangos de Días hasta Inscripción

**Nota Metodológica:** Este análisis calcula los días desde la **PRIMERA CONSULTA REGISTRADA** hasta el pago/inscripción. Si una persona consultó múltiples veces, el reloj comienza en el primer contacto registrado, independientemente de cuántas veces volvió a consultar después.

Esta métrica busca responder: **"¿Cuánto tiempo desde que primero se interesó hasta que efectivamente se inscribió?"** de forma conservadora y realista, midiendo la velocidad de conversión desde el primer contacto.

**Definición de rangos:** 'Mismo día' incluye personas que se inscribieron el mismo día o el día siguiente de su primera consulta (0-1 días). Los demás rangos son acumulativos hasta cada límite superior.

| Rango           |   Personas |    % |   % Acumulado |
|:----------------|-----------:|-----:|--------------:|
| Mismo día       |        626 | 19.5 |          19.5 |
| 1-3 días        |        228 |  7.1 |          26.6 |
| 4-7 días        |        316 |  9.9 |          36.5 |
| 8-14 días       |        255 |  8   |          44.5 |
| 15-30 días      |        343 | 10.7 |          55.2 |
| 31-60 días      |        292 |  9.1 |          64.3 |
| 61-90 días      |        132 |  4.1 |          68.4 |
| 91-120 días     |        161 |  5   |          73.4 |
| 121-150 días    |        176 |  5.5 |          78.9 |
| 151-180 días    |        181 |  5.6 |          84.5 |
| 181-210 días    |        169 |  5.3 |          89.8 |
| 211-240 días    |        118 |  3.7 |          93.5 |
| 241-270 días    |         82 |  2.6 |          96.1 |
| Más de 270 días |        126 |  3.9 |         100   |

*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*

### 2c. Referencia Estadística: Deciles

| Decil         |   Dias |
|:--------------|-------:|
| D10           |      0 |
| D20           |      2 |
| D30           |      5 |
| D40           |     10 |
| D50 (Mediana) |     22 |
| D60           |     42 |
| D70           |     99 |
| D80           |    156 |
| D90           |    212 |
| D100 (Máx)    |    342 |

*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain         |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:---------------|--------------:|----------:|-------------:|---------------------:|
| gmail.com      |        243926 |     11742 |       286251 |                 4.81 |
| hotmail.com    |         51939 |       653 |        63921 |                 1.26 |
| yahoo.com.ar   |          4668 |        69 |         5757 |                 1.48 |
| ucasal.edu.ar  |          4358 |        59 |         4371 |                 1.35 |
| hotmail.com.ar |          3671 |        44 |         4410 |                 1.2  |
| outlook.com    |          2760 |        62 |         3283 |                 2.25 |
| live.com.ar    |          1803 |        21 |         2202 |                 1.16 |
| icloud.com     |          1569 |       143 |         1804 |                 9.11 |
| yahoo.com      |          1287 |        32 |         1543 |                 2.49 |
| live.com       |          1031 |        12 |         1253 |                 1.16 |
| hotmail.es     |           847 |         3 |         1027 |                 0.35 |
| outlook.es     |           740 |        12 |          865 |                 1.62 |
| gmail.com.ar   |           705 |        16 |          829 |                 2.27 |
| gmail.con      |           571 |        19 |          643 |                 3.33 |
| outlook.com.ar |           388 |        11 |          466 |                 2.84 |

## 3b. Distribución Granular: Día a Día hasta Inscripción

Esta gráfica complementa la sección 2b mostrando un **histograma continuo día a día**, donde cada barra representa un intervalo pequeño de días. Permite visualizar con mayor detalle los picos y la forma de la distribución, especialmente en los primeros días donde se concentra la mayor cantidad de inscripciones.

**Personas analizadas:** 3,205 (mismas que sección 2)


## Nota Metodológica

- **Modelo de atribución:** Deduplicado por persona (Correo o DNI). Match por prioridad: DNI > Email > Teléfono > Celular.
- **Personas Matcheadas (Exacto):** 7,937 — por DNI: 5,333, por Email: 2,150, por Teléfono: 237, por Celular: 217.
- **Any-Touch ESTANDAR (este informe):** Incluye todas las consultas sin filtro de fecha vs pago.
- **Modelo CAUSAL (informe separado):** Solo consultas con fecha <= fecha de pago. Ver Presupuesto_ROI_Causal.
- **Ventana de conversión:** Leads desde 01/09/2025 (campaña ingreso 2026). Límite superior: última fecha de inscripción registrada.

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

