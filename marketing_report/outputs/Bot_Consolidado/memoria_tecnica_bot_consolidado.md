# Memoria Técnica — 19_bot_consolidado.py

**Generado automáticamente el 2026-03-02 23:17:25**
**Datos actualizados al 17 de febrero de 2026** *(fecha del último inscripto registrado)*

---

## 1. Fuentes de Datos

| Concepto | Valor |
|----------|-------|
| Segmentos procesados | Grado_Pregrado, Cursos, Posgrados |
| Archivos leads cargados | 3 |
| Archivos inscriptos cargados | 3 |
| Total leads consolidados | 370,270 |
| Total inscriptos consolidados | 9,944 |

## 2. Métricas del Bot (FuenteLead = 907)

| Métrica | Valor |
|---------|-------|
| Total Consultas (registros sin dedup) | 8,527 |
| Personas Únicas vía Bot | 6,248 |
| Inscriptos del Bot | 455 |
| Tasa de Conversión Total | 7.28% |

### Desglose por Segmento

| Segmento       |   Consultas_Total |   Personas_Unicas |   Inscriptos |   Tasa_% |
|:---------------|------------------:|------------------:|-------------:|---------:|
| Grado_Pregrado |              8447 |              6189 |          396 |      6.4 |
| Cursos         |                75 |                55 |           55 |    100   |
| Posgrados      |                 5 |                 4 |            4 |    100   |

## 3. Auditoría de DNI — Inscriptos del Bot

### 3.1 Cobertura de DNI

| Indicador | Cantidad | % del Total |
|-----------|----------|-------------|
| Total inscriptos del bot | 505 | 100.0% |
| DNI presente (final, post-recuperación) | 505 | 100.0% |
| DNI vacío (final, post-recuperación) | 0 | 0.0% |
| Insc_DNI presente (fuente inscriptos) | 505 | 100.0% |

### 3.2 DNIs Recuperados desde Inscriptos

Los leads que matchearon por **Email, Teléfono o Celular** no traían DNI del CRM de Salesforce.
Sin embargo, la tabla de inscriptos sí contiene el DNI (`Insc_DNI`) de cada persona.

**Proceso de recuperación:**
1. Se detectan filas donde `DNI` está vacío/NaN
2. Se verifica si `Insc_DNI` tiene valor para esas filas
3. Se copia `Insc_DNI` → `DNI` para completar el dato

**Resultado:** Se recuperaron **237** DNIs desde la tabla de inscriptos.

### 3.3 Distribución por Tipo de Match

| Tipo de Match | Cantidad | Tenía DNI en CRM |
|---------------|----------|-------------------|
| Exacto (DNI) | 263 | Sí |
| Exacto (Email) | 176 | No (recuperado de Insc) |
| Exacto (Teléfono) | 35 | No (recuperado de Insc) |
| Exacto (Celular) | 31 | No (recuperado de Insc) |

### 3.4 Muestreo — Registros matcheados por Email (DNI recuperado de inscriptos)

|     | Nombre_Completo                          |      DNI |   Insc_DNI | Match_Tipo     | Correo                           |
|----:|:-----------------------------------------|---------:|-----------:|:---------------|:---------------------------------|
| 254 | Soria Briones , Juan Pablo               | 48338866 |   48338866 | Exacto (Email) | jpsoria2016@gmail.com            |
| 255 | Limardo, Lucía Belén                     | 43918536 |   43918536 | Exacto (Email) | limardolb@gmail.com              |
| 256 | FUENTES SANMILLAN, CAMILA                | 47818826 |   47818826 | Exacto (Email) | camilafuentessanmillan@gmail.com |
| 257 | Montañez, Brisa de los Ángeles           | 48210845 |   48210845 | Exacto (Email) | brisamontanez77@gmail.com        |
| 258 | SOLALIGA , EMILIA MICAELA                | 48777049 |   48777049 | Exacto (Email) | solaligaemilia7@gmail.com        |
| 259 | Fullana, Enso Walter                     | 16195987 |   16195987 | Exacto (Email) | ensofullana@gmail.com            |
| 260 | Puca , Sarón Briana                      | 46471828 |   46471828 | Exacto (Email) | sharon.puca04@gmail.com          |
| 261 | NESTOR JOEL MAIDANA, NESTOR JOEL MAIDANA | 48209694 |   48209694 | Exacto (Email) | joelmaidana07098@gmail.com       |
| 262 | Quilaqueo, Zulma Liwen                   | 29443778 |   29443778 | Exacto (Email) | liwen.weeen@gmail.com            |
| 263 | Homez Llanos , Valentina Luján           | 44564872 |   44564872 | Exacto (Email) | valenhomez2002@gmail.com         |

### 3.5 Muestreo — Registros matcheados por DNI (siempre tuvieron DNI)

|    | Nombre_Completo                    |      DNI |   Insc_DNI | Match_Tipo   | Correo                                  |
|---:|:-----------------------------------|---------:|-----------:|:-------------|:----------------------------------------|
|  1 | ESPINOZA LAMAS, BIANCA ROCÍO       | 49341445 |   49341445 | Exacto (DNI) | biancaespinoza1234t@gmail.com           |
|  2 | Lezama Oropeza , Andrés Elias      | 96126505 |   96126505 | Exacto (DNI) | lezamaandres007@gmail.com               |
|  3 | TORRES, ZOE                        | 48918566 |   48918566 | Exacto (DNI) | aleezoe7777@gmail.com                   |
|  4 | CALISAYA MARTINEZ, SANTIAGO MIGUEL | 48656231 |   48656231 | Exacto (DNI) | saantiicalisaya@gmail.com               |
|  5 | ROMERO, MORENA ANTONELLA           | 48082711 |   48082711 | Exacto (DNI) | noresponder+5493873114444@ucasal.edu.ar |

### 3.6 Verificación: ¿Existen inscriptos sin DNI en ninguna fuente?

**Resultado: NO.** De los 505 inscriptos del bot, el 100% tiene DNI disponible
en al menos una fuente (CRM o tabla de inscriptos). Tras la recuperación, 505 de 505
tienen DNI completo en la columna `DNI` del listado final.

## 4. Verificación Temporal — Consulta Previa o Simultánea a Inscripción

**Criterio:** `Sí` = fecha de consulta al bot ≤ fecha de inscripción (incluye mismo día).
Las fechas se normalizan a medianoche antes de comparar para que consultas y pagos del mismo
día sean correctamente identificados como "Sí", sin importar la hora de la consulta.

| Indicador | Cantidad |
|-----------|----------|
| Consulta ANTERIOR o MISMA FECHA que inscripción (Sí) | 236 |
| Consulta POSTERIOR a inscripción (No) | 269 |
| Sin datos de fecha (alguna fecha faltante) | 0 |

**Nota sobre los casos "No":** Representan re-consultas al bot de personas que ya se habían
inscrito (volvieron a consultar después de pagar). No son errores de atribución.

## 5. Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `Informe_Bot_Consolidado.md` | Markdown con informe completo |
| `Informe_Bot_Consolidado.pdf` | PDF apaisado con tablas y gráficos |
| `Bot_Resumen_Por_Nivel.csv` | CSV resumen por segmento |
| `Bot_Inscriptos_Listado.csv` | CSV listado de inscriptos |
| `Bot_Inscriptos_Detalle_Completo.xlsx` | Excel con 3 hojas (Resumen, Inscriptos, Todos Leads) |
| `bot_por_nivel.png` | Gráfico barras personas y tasas por nivel |
| `pie_inscriptos_bot_nivel.png` | Gráfico pie distribución inscriptos |
| `memoria_tecnica_bot_consolidado.md` | Este archivo |

---
*Fin de la Memoria Técnica.*
