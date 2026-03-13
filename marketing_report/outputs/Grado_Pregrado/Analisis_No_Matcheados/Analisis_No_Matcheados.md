# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 17 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **299,739** personas únicas (agrupadas por persona) en la base de datos.
El tipo de match mostrado es el de mayor prioridad por persona (DNI > Email > Telefono > Celular).

- **Personas Matcheadas (Exacto):** 8,132 (2.7%)
  - por DNI: 5,515
  - por Email: 2,127
  - por Telefono: 279
  - por Celular: 211
- **Personas No Matcheadas:** 291,607 (97.3%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |              3549 |           60.2 |               203449 |              81.8 |
| 2 consultas   |              1280 |           21.7 |                32694 |              13.1 |
| 3 consultas   |               570 |            9.7 |                 8081 |               3.2 |
| 4 consultas   |               232 |            3.9 |                 2570 |               1   |
| 5 consultas   |               134 |            2.3 |                  944 |               0.4 |
| 6 consultas   |                46 |            0.8 |                  414 |               0.2 |
| 7 consultas   |                29 |            0.5 |                  211 |               0.1 |
| 8 consultas   |                21 |            0.4 |                  103 |               0   |
| 9 consultas   |                13 |            0.2 |                   60 |               0   |
| 10 consultas  |                 9 |            0.2 |                   41 |               0   |
| 10+ consultas |                14 |            0.2 |                  101 |               0   |

## 2. Tiempo de Resolución: Primera Consulta → Inscripción (Solo Inscriptos)

Este análisis aplica **exclusivamente a personas que efectivamente se inscribieron** (Matcheados Exactos), ya que los No Matcheados por definición nunca completaron una inscripción.

Se filtran únicamente registros con fechas en el rango razonable (2024 en adelante).

**Personas analizadas:** 3,255
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
| Mismo día       |        642 | 19.7 |          19.7 |
| 1-3 días        |        236 |  7.3 |          27   |
| 4-7 días        |        319 |  9.8 |          36.8 |
| 8-14 días       |        260 |  8   |          44.8 |
| 15-30 días      |        345 | 10.6 |          55.4 |
| 31-60 días      |        292 |  9   |          64.4 |
| 61-90 días      |        134 |  4.1 |          68.5 |
| 91-120 días     |        162 |  5   |          73.5 |
| 121-150 días    |        176 |  5.4 |          78.9 |
| 151-180 días    |        185 |  5.7 |          84.6 |
| 181-210 días    |        171 |  5.3 |          89.9 |
| 211-240 días    |        119 |  3.7 |          93.6 |
| 241-270 días    |         83 |  2.5 |          96.1 |
| Más de 270 días |        131 |  4   |         100.1 |

*Lectura: La columna '% Acumulado' muestra el porcentaje de inscriptos que ya habían pagado dentro de ese rango de días. Ej: si '15-30 días' tiene 75% acumulado, significa que 3 de cada 4 inscriptos pagó dentro del primer mes.*

### 2c. Referencia Estadística: Deciles

| Decil         |   Dias |
|:--------------|-------:|
| D10           |      0 |
| D20           |      2 |
| D30           |      4 |
| D40           |      9 |
| D50 (Mediana) |     22 |
| D60           |     41 |
| D70           |     99 |
| D80           |    157 |
| D90           |    213 |
| D100 (Máx)    |    342 |

*Interpretación: D50 = el 50% pagó en esos días o menos. D90 = el 90% ya pagó.*

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain         |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:---------------|--------------:|----------:|-------------:|---------------------:|
| gmail.com      |        244013 |     11868 |       286219 |                 4.86 |
| hotmail.com    |         51951 |       676 |        63910 |                 1.3  |
| yahoo.com.ar   |          4668 |        70 |         5756 |                 1.5  |
| ucasal.edu.ar  |          4366 |        66 |         4372 |                 1.51 |
| hotmail.com.ar |          3671 |        45 |         4409 |                 1.23 |
| outlook.com    |          2760 |        64 |         3281 |                 2.32 |
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

**Personas analizadas:** 3,255 (mismas que sección 2)


## Nota Metodológica

- **Modelo de atribución:** Deduplicado por persona (Correo o DNI). Match por prioridad: DNI > Email > Teléfono > Celular.
- **Personas Matcheadas (Exacto):** 8,132 — por DNI: 5,515, por Email: 2,127, por Teléfono: 279, por Celular: 211.
- **Any-Touch:** Para atribución multi-canal (inscriptos que consultaron por más de un canal), referirse al Informe Analítico (04_reporte_final).
- **Ventana de conversión:** Leads desde 01/09/2025 (campaña ingreso 2026). Límite superior: última fecha de inscripción registrada.
