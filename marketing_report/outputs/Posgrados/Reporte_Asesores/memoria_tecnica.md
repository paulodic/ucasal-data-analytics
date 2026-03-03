# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-02 23:16:46
**Segmento:** Posgrados
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 157 |
| Total Inscriptos físicos | 325 |
| Leads en Contact Center | 50 (31.8%) |
| Leads con Estado "Abierto" | 57 (36.3%) |

## Distribución de Estados (Top 10)
| Estado           |   Cantidad |   Porcentaje |
|:-----------------|-----------:|-------------:|
| No interesado    |         69 |     43.949   |
| Abierto          |         57 |     36.3057  |
| Interesado       |         20 |     12.7389  |
| Solicitud creada |         11 |      7.00637 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |        283 |    87.0769   |
| Sistemas / Automatizado   |         41 |    12.6154   |
| Sedes / Delegaciones      |          1 |     0.307692 |

## Reglas de Negocio
- **Propietario del lead:** Columna `Consulta: Nombre del propietario` (o equivalente), usada para agrupar por asesor
- **Inscripciones atribuidas:** Leads con `Match_Tipo` que contenga `"Exacto"` se consideran inscripciones confirmadas
- **Ranking de vendedores:** Basado en columna `Insc_Vendedor` de la base contable de inscriptos
- **Montos en ARS:** Sumados desde la columna `Insc_Haber` de inscriptos matcheados

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Reporte_Asesores\17_reporte_asesores.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Reporte_Asesores\17_reporte_asesores.md`
- CSV ranking asesores: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Reporte_Asesores\17_ranking_asesores.csv`
- CSV estados: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Reporte_Asesores\17_informe_estados_asesor.csv`
- CSV vendedores: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Reporte_Asesores\17_ranking_vendedores_inscriptos.csv`
