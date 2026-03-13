# Memoria Técnica — 19_bot_consolidado.py

**Generado automáticamente el 2026-03-12 21:28:10**
**Datos actualizados al 17 de febrero de 2026** *(fecha del último inscripto registrado)*

---

## 1. Fuentes de Datos

| Concepto | Valor |
|----------|-------|
| Segmentos procesados | Grado_Pregrado, Cursos, Posgrados |
| Archivos leads cargados | 3 |
| Archivos inscriptos cargados | 3 |
| Total leads consolidados | 398,778 |
| Total inscriptos consolidados | 9,944 |

## 2. Métricas del Bot (FuenteLead = 907)

| Métrica | Valor |
|---------|-------|
| Total Consultas (registros sin dedup) | 10,247 |
| Personas Únicas vía Bot | 7,668 |
| Inscriptos del Bot | 507 |
| Tasa de Conversión Total | 6.61% |

### Desglose por Segmento

| Segmento       |   Consultas_Total |   Personas_Unicas |   Inscriptos |   Match_DNI |   Match_Email |   Match_Telefono |   Match_Celular |   Tasa_% |
|:---------------|------------------:|------------------:|-------------:|------------:|--------------:|-----------------:|----------------:|---------:|
| Grado_Pregrado |             10240 |              7663 |          502 |         271 |           167 |               33 |              31 |     6.55 |
| Cursos         |                 1 |                 0 |            0 |           0 |             0 |                0 |               0 |     0    |
| Posgrados      |                 6 |                 5 |            5 |           2 |             2 |                1 |               0 |   100    |

## 3. Auditoría de DNI — Inscriptos del Bot

### 3.1 Cobertura de DNI

| Indicador | Cantidad | % del Total |
|-----------|----------|-------------|
| Total inscriptos del bot | 555 | 100.0% |
| DNI presente (final, post-recuperación) | 555 | 100.0% |
| DNI vacío (final, post-recuperación) | 0 | 0.0% |
| Insc_DNI presente (fuente inscriptos) | 555 | 100.0% |

### 3.2 DNIs Recuperados desde Inscriptos

Los leads que matchearon por **Email, Teléfono o Celular** no traían DNI del CRM de Salesforce.
Sin embargo, la tabla de inscriptos sí contiene el DNI (`Insc_DNI`) de cada persona.

**Proceso de recuperación:**
1. Se detectan filas donde `DNI` está vacío/NaN
2. Se verifica si `Insc_DNI` tiene valor para esas filas
3. Se copia `Insc_DNI` → `DNI` para completar el dato

**Resultado:** Se recuperaron **244** DNIs desde la tabla de inscriptos.

### 3.3 Distribución por Tipo de Match

| Tipo de Match | Cantidad | Tenía DNI en CRM |
|---------------|----------|-------------------|
| Exacto (DNI) | 303 | Sí |
| Exacto (Email) | 183 | No (recuperado de Insc) |
| Exacto (Teléfono) | 37 | No (recuperado de Insc) |
| Exacto (Celular) | 32 | No (recuperado de Insc) |

### 3.4 Muestreo — Registros matcheados por Email (DNI recuperado de inscriptos)

|     | Nombre_Completo                          |      DNI |   Insc_DNI | Match_Tipo     | Correo                           |
|----:|:-----------------------------------------|---------:|-----------:|:---------------|:---------------------------------|
| 302 | Soria Briones , Juan Pablo               | 48338866 |   48338866 | Exacto (Email) | jpsoria2016@gmail.com            |
| 303 | Limardo, Lucía Belén                     | 43918536 |   43918536 | Exacto (Email) | limardolb@gmail.com              |
| 304 | FUENTES SANMILLAN, CAMILA                | 47818826 |   47818826 | Exacto (Email) | camilafuentessanmillan@gmail.com |
| 305 | Montañez, Brisa de los Ángeles           | 48210845 |   48210845 | Exacto (Email) | brisamontanez77@gmail.com        |
| 306 | TEJERINA, ALVARO BENJAMIN                | 45976665 |   45976665 | Exacto (Email) | benjatejerina16@gmail.com        |
| 307 | Valdez, Abigail De Los Angeles Guadalupe | 48804837 |   48804837 | Exacto (Email) | abi.v2804@gmail.com              |
| 308 | SOLALIGA , EMILIA MICAELA                | 48777049 |   48777049 | Exacto (Email) | solaligaemilia7@gmail.com        |
| 309 | HERRERA, VICTORIA CAROLINA               | 48412717 |   48412717 | Exacto (Email) | vickyyyvh@gmail.com              |
| 310 | Puca , Sarón Briana                      | 46471828 |   46471828 | Exacto (Email) | sharon.puca04@gmail.com          |
| 311 | NESTOR JOEL MAIDANA, NESTOR JOEL MAIDANA | 48209694 |   48209694 | Exacto (Email) | joelmaidana07098@gmail.com       |

### 3.5 Muestreo — Registros matcheados por DNI (siempre tuvieron DNI)

|    | Nombre_Completo                    |      DNI |   Insc_DNI | Match_Tipo   | Correo                                  |
|---:|:-----------------------------------|---------:|-----------:|:-------------|:----------------------------------------|
|  1 | ESPINOZA LAMAS, BIANCA ROCÍO       | 49341445 |   49341445 | Exacto (DNI) | biancaespinoza1234t@gmail.com           |
|  2 | Lezama Oropeza , Andrés Elias      | 96126505 |   96126505 | Exacto (DNI) | lezamaandres007@gmail.com               |
|  3 | TORRES, ZOE                        | 48918566 |   48918566 | Exacto (DNI) | aleezoe7777@gmail.com                   |
|  4 | CALISAYA MARTINEZ, SANTIAGO MIGUEL | 48656231 |   48656231 | Exacto (DNI) | saantiicalisaya@gmail.com               |
|  5 | ROMERO, MORENA ANTONELLA           | 48082711 |   48082711 | Exacto (DNI) | noresponder+5493873114444@ucasal.edu.ar |

### 3.6 Verificación: ¿Existen inscriptos sin DNI en ninguna fuente?

**Resultado: NO.** De los 555 inscriptos del bot, el 100% tiene DNI disponible
en al menos una fuente (CRM o tabla de inscriptos). Tras la recuperación, 555 de 555
tienen DNI completo en la columna `DNI` del listado final.

## 4. Verificación Temporal — Consulta Previa o Simultánea a Inscripción

**Criterio:** `Sí` = fecha de consulta al bot ≤ fecha de inscripción (incluye mismo día).
Las fechas se normalizan a medianoche antes de comparar para que consultas y pagos del mismo
día sean correctamente identificados como "Sí", sin importar la hora de la consulta.

| Indicador | Cantidad |
|-----------|----------|
| Consulta ANTERIOR o MISMA FECHA que inscripción (Sí) | 291 |
| Consulta POSTERIOR a inscripción (No) | 264 |
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
