# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-12 21:26:58
**Segmento:** Cursos
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 44 |
| Total Inscriptos físicos | 94 |
| Leads en Contact Center | 20 (45.5%) |
| Leads con Estado "Abierto" | 13 (29.5%) |

## Distribución de Estados (Top 10)
| Estado           |   Cantidad |   Porcentaje |
|:-----------------|-----------:|-------------:|
| No interesado    |         18 |      40.9091 |
| Abierto          |         13 |      29.5455 |
| Interesado       |          8 |      18.1818 |
| Solicitud creada |          5 |      11.3636 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |         88 |     93.617   |
| Sistemas / Automatizado   |          6 |      6.38298 |

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
- **Match:** Exacto por DNI, Email, Telefono y Celular.
