# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-14 20:35:49
**Segmento:** Posgrados
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 139 |
| Total Inscriptos físicos | 325 |
| Leads en Contact Center | 51 (36.7%) |
| Leads con Estado "Abierto" | 46 (33.1%) |

## Distribución de Estados (Top 10)
| Estado           |   Cantidad |   Porcentaje |
|:-----------------|-----------:|-------------:|
| No interesado    |         58 |     41.7266  |
| Abierto          |         46 |     33.0935  |
| Interesado       |         24 |     17.2662  |
| Solicitud creada |         11 |      7.91367 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |        299 |    92        |
| Sistemas / Automatizado   |         23 |     7.07692  |
| Sedes / Delegaciones      |          3 |     0.923077 |

## Reglas de Negocio
- **Propietario del lead:** Columna `Consulta: Nombre del propietario` (o equivalente), usada para agrupar por asesor
- **Inscripciones atribuidas:** Leads con `Match_Tipo` que contenga `"Exacto"` se consideran inscripciones confirmadas
- **Ranking de vendedores:** Basado en columna `Insc_Vendedor` de la base contable de inscriptos
- **Montos en ARS:** Sumados desde la columna `Insc_Haber` de inscriptos matcheados

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `17_reporte_asesores.pdf` | Informe visual multi-pagina |
| `17_reporte_asesores.xlsx` | Datos consolidados (5-6 hojas) |
| `17_reporte_asesores.md` | Documentacion textual (top rankings) |
| `17_ranking_asesores.csv` | Ranking asesores CRM |
| `17_informe_estados_asesor.csv` | Estados por grupo de asesor |
| `17_ranking_vendedores_inscriptos.csv` | Ranking vendedores financieros |
| `memoria_tecnica.md` | Este archivo |

## Nota Metodologica
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Para atribucion multi-canal, referirse al Informe Analitico (04_reporte_final).
- **Match Exacto:** DNI (23), Email (18), Telefono (15), Celular (7). Total: 63.
