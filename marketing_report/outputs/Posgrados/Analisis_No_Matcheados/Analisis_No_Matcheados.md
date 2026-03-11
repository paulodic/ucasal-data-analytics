# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 14 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **131** personas únicas (sin repetidos) en la base de datos.
- **Personas Matcheadas (Exacto):** 95 (72.5%)
- **Personas No Matcheadas:** 36 (27.5%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |                62 |           82.7 |                   34 |               100 |
| 2 consultas   |                12 |           16   |                    0 |                 0 |
| 3 consultas   |                 1 |            1.3 |                    0 |                 0 |
| 4 consultas   |                 0 |            0   |                    0 |                 0 |
| 5 consultas   |                 0 |            0   |                    0 |                 0 |
| 6 consultas   |                 0 |            0   |                    0 |                 0 |
| 7 consultas   |                 0 |            0   |                    0 |                 0 |
| 8 consultas   |                 0 |            0   |                    0 |                 0 |
| 9 consultas   |                 0 |            0   |                    0 |                 0 |
| 10 consultas  |                 0 |            0   |                    0 |                 0 |
| 10+ consultas |                 0 |            0   |                    0 |                 0 |

## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)

Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.

Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).

**Personas analizadas:** 18
- **Promedio:** 86 días
- **Mediana:** 39 días
- **Moda (Valor Más Frecuente):** 3 días

**Nota:** Las gráficas 2a y 2b utilizan los mismos rangos de días para garantizar coherencia. La gráfica 2a muestra la distribución como histograma continuo, mientras que 2b presenta los datos como barras categóricas con porcentajes y acumulados.

### 2b. Distribución por Rangos de Días hasta Inscripción

**Nota Metodológica:** Este análisis calcula los días desde la **PRIMERA CONSULTA REGISTRADA** hasta el pago/inscripción. Si una persona consultó múltiples veces, el reloj comienza en el primer contacto registrado, independientemente de cuántas veces volvió a consultar después.

Esta métrica busca responder: **"¿Cuánto tiempo desde que primero se interesó hasta que efectivamente se inscribió?"** de forma conservadora y realista, midiendo la velocidad de conversión desde el primer contacto.

**Definición de rangos:** 'Mismo día' incluye personas que se inscribieron el mismo día o el día siguiente de su primera consulta (0-1 días). Los demás rangos son acumulativos hasta cada límite superior.

| Rango           |   Personas |    % |   % Acumulado |
|:----------------|-----------:|-----:|--------------:|
| Mismo día       |          0 |  0   |           0   |
| 1-3 días        |          2 | 11.1 |          11.1 |
| 4-7 días        |          2 | 11.1 |          22.2 |
| 8-14 días       |          2 | 11.1 |          33.3 |
| 15-30 días      |          1 |  5.6 |          38.9 |
| 31-60 días      |          5 | 27.8 |          66.7 |
| 61-90 días      |          0 |  0   |          66.7 |
| 91-120 días     |          1 |  5.6 |          72.3 |
| 121-150 días    |          0 |  0   |          72.3 |
| 151-180 días    |          0 |  0   |          72.3 |
| 181-210 días    |          0 |  0   |          72.3 |
| 211-240 días    |          4 | 22.2 |          94.5 |
| 241-270 días    |          0 |  0   |          94.5 |
| Más de 270 días |          1 |  5.6 |         100.1 |

*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*

### 2c. Referencia Estadística: Deciles

| Decil         |   Dias |
|:--------------|-------:|
| D10           |      4 |
| D20           |      8 |
| D30           |     11 |
| D40           |     30 |
| D50 (Mediana) |     39 |
| D60           |     46 |
| D70           |     97 |
| D80           |    214 |
| D90           |    225 |
| D100 (Máx)    |    299 |

*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain    |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:----------|--------------:|----------:|-------------:|---------------------:|
| gmail.com |            93 |        96 |           26 |               103.23 |

## 3b. Distribución Granular: Día a Día hasta Inscripción

Esta gráfica complementa la sección 2b mostrando un **histograma continuo día a día**, donde cada barra representa un intervalo pequeño de días. Permite visualizar con mayor detalle los picos y la forma de la distribución, especialmente en los primeros días donde se concentra la mayor cantidad de inscripciones.

**Personas analizadas:** 18 (mismas que sección 2)

