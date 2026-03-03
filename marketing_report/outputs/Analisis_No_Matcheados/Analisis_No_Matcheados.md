# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 17 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **173,888** personas únicas (sin repetidos) en la base de datos.
- **Personas Matcheadas (Exacto):** 4,470 (2.6%)
- **Personas No Matcheadas:** 169,418 (97.4%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |              1641 |           68   |               100633 |              86.1 |
| 2 consultas   |               475 |           19.7 |                12587 |              10.8 |
| 3 consultas   |               170 |            7   |                 2470 |               2.1 |
| 4 consultas   |                63 |            2.6 |                  699 |               0.6 |
| 5 consultas   |                35 |            1.4 |                  219 |               0.2 |
| 6 consultas   |                10 |            0.4 |                  100 |               0.1 |
| 7 consultas   |                 6 |            0.2 |                   54 |               0   |
| 8 consultas   |                 4 |            0.2 |                   31 |               0   |
| 9 consultas   |                 2 |            0.1 |                   14 |               0   |
| 10 consultas  |                 2 |            0.1 |                    7 |               0   |
| 10+ consultas |                 7 |            0.3 |                   32 |               0   |

## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)

Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.

Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).

**Personas analizadas:** 1,611
- **Promedio:** 196 días
- **Mediana:** 185 días
- **Moda (Valor Más Frecuente):** 0 días

### 2b. Distribución por Rangos de Días hasta Inscripción

| Rango        |   Personas |    % |   % Acumulado |
|:-------------|-----------:|-----:|--------------:|
| Mismo día    |         50 |  3.1 |           3.1 |
| 1-3 días     |         27 |  1.7 |           4.8 |
| 4-7 días     |         21 |  1.3 |           6.1 |
| 8-14 días    |         62 |  3.8 |           9.9 |
| 15-30 días   |         55 |  3.4 |          13.3 |
| 31-60 días   |        143 |  8.9 |          22.2 |
| 61-90 días   |         93 |  5.8 |          28   |
| 91-120 días  |        108 |  6.7 |          34.7 |
| 121-180 días |        228 | 14.2 |          48.9 |
| 181-270 días |        384 | 23.8 |          72.7 |
| 271-365 días |        282 | 17.5 |          90.2 |
| Más de 1 año |        158 |  9.8 |         100   |

*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*

### 2c. Referencia Estadística: Deciles

| Decil         |   Dias |
|:--------------|-------:|
| D10           |     15 |
| D20           |     50 |
| D30           |    101 |
| D40           |    136 |
| D50 (Mediana) |    185 |
| D60           |    227 |
| D70           |    259 |
| D80           |    302 |
| D90           |    363 |
| D100 (Máx)    |    752 |

*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain         |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:---------------|--------------:|----------:|-------------:|---------------------:|
| gmail.com      |        107243 |      5927 |       155373 |                 5.53 |
| hotmail.com    |         22880 |       423 |        35106 |                 1.85 |
| yahoo.com.ar   |          1851 |        46 |         2963 |                 2.49 |
| ucasal.edu.ar  |          1699 |        17 |         1754 |                 1    |
| hotmail.com.ar |          1657 |        39 |         2403 |                 2.35 |
| outlook.com    |          1221 |        39 |         1758 |                 3.19 |
| live.com.ar    |           778 |        24 |         1174 |                 3.08 |
| icloud.com     |           675 |        66 |          980 |                 9.78 |
| yahoo.com      |           537 |        17 |          807 |                 3.17 |
| live.com       |           449 |         9 |          673 |                 2    |
| hotmail.es     |           397 |         3 |          577 |                 0.76 |
| outlook.es     |           334 |         5 |          466 |                 1.5  |
| gmail.com.ar   |           294 |         7 |          427 |                 2.38 |
| gmail.con      |           263 |        11 |          343 |                 4.18 |
| outlook.com.ar |           166 |         8 |          247 |                 4.82 |

