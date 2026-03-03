# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-03 08:18:29
**Segmento:** Cursos
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 965 |
| Total Inscriptos físicos | 864 |
| Leads en Contact Center | 114 (11.8%) |
| Leads con Estado "Abierto" | 165 (17.1%) |

## Distribución de Estados (Top 10)
| Estado           |   Cantidad |   Porcentaje |
|:-----------------|-----------:|-------------:|
| Solicitud creada |        326 |      33.7824 |
| No interesado    |        316 |      32.7461 |
| Abierto          |        165 |      17.0984 |
| Interesado       |        158 |      16.3731 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |        651 |    75.3472   |
| Sistemas / Automatizado   |        211 |    24.4213   |
| Sedes / Delegaciones      |          2 |     0.231481 |

## Reglas de Negocio
- **Propietario del lead:** Columna `Consulta: Nombre del propietario` (o equivalente), usada para agrupar por asesor
- **Inscripciones atribuidas:** Leads con `Match_Tipo` que contenga `"Exacto"` se consideran inscripciones confirmadas
- **Ranking de vendedores:** Basado en columna `Insc_Vendedor` de la base contable de inscriptos
- **Montos en ARS:** Sumados desde la columna `Insc_Haber` de inscriptos matcheados

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Reporte_Asesores\17_reporte_asesores.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Reporte_Asesores\17_reporte_asesores.md`
- CSV ranking asesores: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Reporte_Asesores\17_ranking_asesores.csv`
- CSV estados: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Reporte_Asesores\17_informe_estados_asesor.csv`
- CSV vendedores: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Reporte_Asesores\17_ranking_vendedores_inscriptos.csv`
