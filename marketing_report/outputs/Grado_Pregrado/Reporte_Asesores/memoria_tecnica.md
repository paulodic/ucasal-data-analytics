# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-03 10:16:11
**Segmento:** Grado_Pregrado
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 369,148 |
| Total Inscriptos físicos | 8,755 |
| Leads en Contact Center | 87,217 (23.6%) |
| Leads con Estado "Abierto" | 137,323 (37.2%) |

## Distribución de Estados (Top 10)
| Estado            |   Cantidad |   Porcentaje |
|:------------------|-----------:|-------------:|
| Abierto           |     137323 |  37.2        |
| No interesado     |     120678 |  32.691      |
| Interesado        |      87940 |  23.8224     |
| Solicitud creada  |      22541 |   6.10622    |
| Desuscripto       |        643 |   0.174185   |
| Pre Inscripción   |         17 |   0.0046052  |
| Solicita Admisión |          6 |   0.00162536 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |       5577 |     63.7007  |
| Sistemas / Automatizado   |       3004 |     34.3118  |
| Sedes / Delegaciones      |        174 |      1.98744 |

## Reglas de Negocio
- **Propietario del lead:** Columna `Consulta: Nombre del propietario` (o equivalente), usada para agrupar por asesor
- **Inscripciones atribuidas:** Leads con `Match_Tipo` que contenga `"Exacto"` se consideran inscripciones confirmadas
- **Ranking de vendedores:** Basado en columna `Insc_Vendedor` de la base contable de inscriptos
- **Montos en ARS:** Sumados desde la columna `Insc_Haber` de inscriptos matcheados

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Reporte_Asesores\17_reporte_asesores.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Reporte_Asesores\17_reporte_asesores.md`
- CSV ranking asesores: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Reporte_Asesores\17_ranking_asesores.csv`
- CSV estados: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Reporte_Asesores\17_informe_estados_asesor.csv`
- CSV vendedores: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Reporte_Asesores\17_ranking_vendedores_inscriptos.csv`
