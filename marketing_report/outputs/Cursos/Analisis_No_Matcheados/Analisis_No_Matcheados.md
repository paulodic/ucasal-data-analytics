# Análisis Profundo: Leads No Matcheados

**Datos actualizados al 14 de febrero de 2026**

Este informe analiza el comportamiento de los Leads que **no** lograron concretar un cruce exitoso (No Matcheados) contra aquellos que sí lo hicieron (Exactos), explorando dimensiones de volumen de consultas, tiempos y dominios de correo electrónico.

## 0. Proporción General: Personas Matcheadas vs No Matcheadas

Se identificaron **25** personas únicas (agrupadas por persona) en la base de datos.
El tipo de match mostrado es el de mayor prioridad por persona (DNI > Email > Telefono > Celular).

- **Personas Matcheadas (Exacto):** 21 (84.0%)
  - por DNI: 9
  - por Email: 4
  - por Telefono: 6
  - por Celular: 2
- **Personas No Matcheadas:** 4 (16.0%)

## 1. Distribución de Consultas por Persona

La siguiente tabla muestra cómo se distribuyen las personas según cuántas consultas realizaron.
**Ejemplo de lectura:** *"El X% de los inscriptos hicieron solo 1 consulta antes de inscribirse."*

| Rango         |   Inscriptos_Cant |   Inscriptos_% |   No_Inscriptos_Cant |   No_Inscriptos_% |
|:--------------|------------------:|---------------:|---------------------:|------------------:|
| 1 consulta    |                10 |           58.8 |                    4 |               100 |
| 2 consultas   |                 4 |           23.5 |                    0 |                 0 |
| 3 consultas   |                 1 |            5.9 |                    0 |                 0 |
| 4 consultas   |                 2 |           11.8 |                    0 |                 0 |
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

| Domain   | Total_Leads   | Exactos   | No_Exactos   | Tasa_Inscripcion_%   |
|----------|---------------|-----------|--------------|----------------------|


## Nota Metodológica

- **Modelo de atribución:** Deduplicado por persona (Correo o DNI). Match por prioridad: DNI > Email > Teléfono > Celular.
- **Personas Matcheadas (Exacto):** 21 — por DNI: 9, por Email: 4, por Teléfono: 6, por Celular: 2.
- **Any-Touch:** Para atribución multi-canal (inscriptos que consultaron por más de un canal), referirse al Informe Analítico (04_reporte_final).
- **Ventana de conversión:** Año calendario 2026.
