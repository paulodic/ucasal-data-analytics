# Memoria Técnica: Journey del Estudiante (Sankey)

**Generado:** 2026-03-02 23:16:43
**Segmento:** Posgrados
**Script:** `03_journey_sankey.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Personas únicas analizadas | 127 |
| Personas inscriptas (con pago confirmado) | 34 |
| Personas no inscriptas | 93 |
| Promedio consultas por persona | 1.2 |
| Promedio días hasta inscripción | 62.4 |

## Lógica del Journey
- **Agrupación:** Se agrupan leads por `DNI` (persona única)
- **Ruta de fuentes:** Se concatenan los valores de `FuenteLead` por orden cronológico de consulta
- **Touch 1/2/3:** Primeros tres contactos con fuentes diferentes
- **Inscripto:** `"Sí"` si la persona tiene al menos un match Exacto con un inscripto
- **Días hasta inscripción:** Diferencia entre primera consulta (`Consulta: Fecha de creación`) y `Fecha Pago`/`Insc_Fecha Pago`

## Archivos de Salida
- Excel: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Otros_Reportes\reporte_journey_tiempos.xlsx`
