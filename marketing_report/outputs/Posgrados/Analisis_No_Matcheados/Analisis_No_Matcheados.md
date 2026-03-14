# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 14 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **111** personas únicas (agrupadas por persona) en la base de datos.
El tipo de match mostrado es el de mayor prioridad por persona (DNI > Email > Telefono > Celular).

- **Personas Matcheadas (Exacto):** 63 (56.8%)
  - por DNI: 23
  - por Email: 18
  - por Telefono: 15
  - por Celular: 7
- **Personas No Matcheadas:** 48 (43.2%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |                33 |           70.2 |                   45 |               100 |
| 2 consultas   |                13 |           27.7 |                    0 |                 0 |
| 3 consultas   |                 1 |            2.1 |                    0 |                 0 |
| 4 consultas   |                 0 |            0   |                    0 |                 0 |
| 5 consultas   |                 0 |            0   |                    0 |                 0 |
| 6 consultas   |                 0 |            0   |                    0 |                 0 |
| 7 consultas   |                 0 |            0   |                    0 |                 0 |
| 8 consultas   |                 0 |            0   |                    0 |                 0 |
| 9 consultas   |                 0 |            0   |                    0 |                 0 |
| 10 consultas  |                 0 |            0   |                    0 |                 0 |
| 10+ consultas |                 0 |            0   |                    0 |                 0 |

## 2. Tiempo de Resolución
No se hallaron suficientes registros con fechas válidas para calcular esta métrica.

## 3. Tasa de Inscripción por Dominio de Correo Electrónico

Esta tabla muestra, para los 15 dominios con más volumen de leads, qué porcentaje de estos leads terminó inscribiéndose. Esto permite identificar si ciertos proveedores de correo tienen tasas de inscripción más altas o más bajas que el promedio.

| Domain    |   Total_Leads |   Exactos |   No_Exactos |   Tasa_Inscripcion_% |
|:----------|--------------:|----------:|-------------:|---------------------:|
| gmail.com |            80 |        72 |           33 |                   90 |


## Nota Metodológica

- **Modelo de atribución:** Deduplicado por persona (Correo o DNI). Match por prioridad: DNI > Email > Teléfono > Celular.
- **Personas Matcheadas (Exacto):** 63 — por DNI: 23, por Email: 18, por Teléfono: 15, por Celular: 7.
- **Any-Touch ESTANDAR (este informe):** Incluye todas las consultas sin filtro de fecha vs pago.
- **Modelo CAUSAL (informe separado):** Solo consultas con fecha <= fecha de pago. Ver Presupuesto_ROI_Causal.
- **Ventana de conversión:** Año calendario 2026.

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

