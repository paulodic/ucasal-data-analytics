# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 14 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **623** personas únicas (sin repetidos) en la base de datos.
- **Personas Matcheadas (Exacto):** 599 (96.1%)
- **Personas No Matcheadas:** 24 (3.9%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |               274 |           71.5 |                   23 |               100 |
| 2 consultas   |                71 |           18.5 |                    0 |                 0 |
| 3 consultas   |                22 |            5.7 |                    0 |                 0 |
| 4 consultas   |                 9 |            2.3 |                    0 |                 0 |
| 5 consultas   |                 3 |            0.8 |                    0 |                 0 |
| 6 consultas   |                 1 |            0.3 |                    0 |                 0 |
| 7 consultas   |                 2 |            0.5 |                    0 |                 0 |
| 8 consultas   |                 0 |            0   |                    0 |                 0 |
| 9 consultas   |                 0 |            0   |                    0 |                 0 |
| 10 consultas  |                 0 |            0   |                    0 |                 0 |
| 10+ consultas |                 1 |            0.3 |                    0 |                 0 |

## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)

Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.

Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).

**Personas analizadas:** 181
- **Promedio:** 91 días
- **Mediana:** 31 días
- **Moda (Valor Más Frecuente):** 1 días

### 2b. Distribución por Rangos de Días hasta Inscripción

| Rango           |   Personas |    % |   % Acumulado |
|:----------------|-----------:|-----:|--------------:|
| Mismo día       |         28 | 15.5 |          15.5 |
| 1-3 días        |          5 |  2.8 |          18.3 |
| 4-7 días        |         14 |  7.7 |          26   |
| 8-14 días       |         14 |  7.7 |          33.7 |
| 15-30 días      |         25 | 13.8 |          47.5 |
| 31-60 días      |         19 | 10.5 |          58   |
| 61-90 días      |          4 |  2.2 |          60.2 |
| 91-120 días     |          7 |  3.9 |          64.1 |
| 121-150 días    |          8 |  4.4 |          68.5 |
| 151-180 días    |         14 |  7.7 |          76.2 |
| 181-210 días    |         11 |  6.1 |          82.3 |
| 211-240 días    |         11 |  6.1 |          88.4 |
| 241-270 días    |         12 |  6.6 |          95   |
| Más de 270 días |          9 |  5   |         100   |

*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*

### 2c. Referencia Estadística: Deciles

| Decil         |   Dias |
|:--------------|-------:|
| D10           |      1 |
| D20           |      4 |
| D30           |     12 |
| D40           |     23 |
| D50 (Mediana) |     31 |
| D60           |     67 |
| D70           |    156 |
| D80           |    191 |
| D90           |    251 |
| D100 (Máx)    |    325 |

*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain    |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:----------|--------------:|----------:|-------------:|---------------------:|
| gmail.com |           524 |       851 |           22 |                162.4 |

