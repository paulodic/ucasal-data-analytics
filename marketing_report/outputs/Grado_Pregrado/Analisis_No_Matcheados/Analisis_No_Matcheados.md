# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 17 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **281,849** personas únicas (sin repetidos) en la base de datos.
- **Personas Matcheadas (Exacto):** 7,157 (2.5%)
- **Personas No Matcheadas:** 274,692 (97.5%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |              3110 |           62.2 |               192244 |              82.6 |
| 2 consultas   |              1063 |           21.2 |                29711 |              12.8 |
| 3 consultas   |               457 |            9.1 |                 7084 |               3   |
| 4 consultas   |               178 |            3.6 |                 2191 |               0.9 |
| 5 consultas   |                97 |            1.9 |                  793 |               0.3 |
| 6 consultas   |                33 |            0.7 |                  330 |               0.1 |
| 7 consultas   |                23 |            0.5 |                  172 |               0.1 |
| 8 consultas   |                11 |            0.2 |                   85 |               0   |
| 9 consultas   |                14 |            0.3 |                   52 |               0   |
| 10 consultas  |                 6 |            0.1 |                   30 |               0   |
| 10+ consultas |                12 |            0.2 |                   88 |               0   |

## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)

Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.

Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).

**Personas analizadas:** 3,169
- **Promedio:** 71 días
- **Mediana:** 22 días
- **Moda (Valor Más Frecuente):** 0 días

### 2b. Distribución por Rangos de Días hasta Inscripción

| Rango           |   Personas |    % |   % Acumulado |
|:----------------|-----------:|-----:|--------------:|
| Mismo día       |        622 | 19.6 |          19.6 |
| 1-3 días        |        235 |  7.4 |          27   |
| 4-7 días        |        308 |  9.7 |          36.7 |
| 8-14 días       |        252 |  8   |          44.7 |
| 15-30 días      |        326 | 10.3 |          55   |
| 31-60 días      |        279 |  8.8 |          63.8 |
| 61-90 días      |        131 |  4.1 |          67.9 |
| 91-120 días     |        157 |  5   |          72.9 |
| 121-150 días    |        180 |  5.7 |          78.6 |
| 151-180 días    |        192 |  6.1 |          84.7 |
| 181-210 días    |        170 |  5.4 |          90.1 |
| 211-240 días    |        109 |  3.4 |          93.5 |
| 241-270 días    |         82 |  2.6 |          96.1 |
| Más de 270 días |        126 |  4   |         100.1 |

*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*

### 2c. Referencia Estadística: Deciles

| Decil         |   Dias |
|:--------------|-------:|
| D10           |      0 |
| D20           |      2 |
| D30           |      4 |
| D40           |      9 |
| D50 (Mediana) |     22 |
| D60           |     43 |
| D70           |    103 |
| D80           |    158 |
| D90           |    210 |
| D100 (Máx)    |    342 |

*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain         |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:---------------|--------------:|----------:|-------------:|---------------------:|
| gmail.com      |        225057 |     10288 |       265929 |                 4.57 |
| hotmail.com    |         47951 |       628 |        59373 |                 1.31 |
| yahoo.com.ar   |          4371 |        70 |         5440 |                 1.6  |
| ucasal.edu.ar  |          3550 |        51 |         3571 |                 1.44 |
| hotmail.com.ar |          3394 |        44 |         4082 |                 1.3  |
| outlook.com    |          2549 |        62 |         3049 |                 2.43 |
| live.com.ar    |          1680 |        20 |         2063 |                 1.19 |
| icloud.com     |          1428 |       116 |         1675 |                 8.12 |
| yahoo.com      |          1189 |        31 |         1439 |                 2.61 |
| live.com       |           966 |        10 |         1180 |                 1.04 |
| hotmail.es     |           765 |         3 |          932 |                 0.39 |
| outlook.es     |           686 |        11 |          808 |                 1.6  |
| gmail.com.ar   |           655 |        10 |          778 |                 1.53 |
| gmail.con      |           524 |        15 |          595 |                 2.86 |
| outlook.com.ar |           371 |        11 |          449 |                 2.96 |

