# Memoria Técnica: Journey del Estudiante (Sankey)

**Generado:** 2026-03-12 21:16:48
**Segmento:** Grado_Pregrado
**Script:** `03_journey_sankey.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Personas únicas analizadas | 305,234 |
| Personas inscriptas (con pago confirmado) | 7,980 |
| Personas no inscriptas | 297,254 |
| Promedio consultas por persona | 1.3 |
| Promedio días hasta inscripción | 59.5 |

## Lógica del Journey
- **Agrupación:** Se agrupan leads por `DNI` (persona única)
- **Ruta de fuentes:** Se concatenan los valores de `FuenteLead` por orden cronológico de consulta
- **Touch 1/2/3:** Primeros tres contactos con fuentes diferentes
- **Inscripto:** `"Sí"` si la persona tiene al menos un match Exacto con un inscripto
- **Días hasta inscripción:** Diferencia entre primera consulta (`Consulta: Fecha de creación`) y `Fecha Pago`/`Insc_Fecha Pago`

## Archivos de Salida
- Excel: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Otros_Reportes\reporte_journey_tiempos.xlsx`

## Nota Metodologica
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Para atribucion multi-canal, referirse al Informe Analitico (04_reporte_final).
- **Match:** Exacto por DNI, Email, Telefono y Celular.
