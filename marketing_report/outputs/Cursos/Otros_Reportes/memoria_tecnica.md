# Memoria Técnica: Journey del Estudiante (Sankey)

**Generado:** 2026-03-03 08:18:25
**Segmento:** Cursos
**Script:** `03_journey_sankey.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Personas únicas analizadas | 616 |
| Personas inscriptas (con pago confirmado) | 24 |
| Personas no inscriptas | 592 |
| Promedio consultas por persona | 1.6 |
| Promedio días hasta inscripción | 91.0 |

## Lógica del Journey
- **Agrupación:** Se agrupan leads por `DNI` (persona única)
- **Ruta de fuentes:** Se concatenan los valores de `FuenteLead` por orden cronológico de consulta
- **Touch 1/2/3:** Primeros tres contactos con fuentes diferentes
- **Inscripto:** `"Sí"` si la persona tiene al menos un match Exacto con un inscripto
- **Días hasta inscripción:** Diferencia entre primera consulta (`Consulta: Fecha de creación`) y `Fecha Pago`/`Insc_Fecha Pago`

## Archivos de Salida
- Excel: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Otros_Reportes\reporte_journey_tiempos.xlsx`
