# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-06 23:31:15
**Segmento:** Grado_Pregrado
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 369,146 |
| Total Inscriptos físicos | 8,755 |
| Leads en Contact Center | 87,216 (23.6%) |
| Leads con Estado "Abierto" | 137,322 (37.2%) |

## Distribución de Estados (Top 10)
| Estado            |   Cantidad |   Porcentaje |
|:------------------|-----------:|-------------:|
| Abierto           |     137322 |  37.1999     |
| No interesado     |     120678 |  32.6911     |
| Interesado        |      87939 |  23.8223     |
| Solicitud creada  |      22541 |   6.10626    |
| Desuscripto       |        643 |   0.174186   |
| Pre Inscripción   |         17 |   0.00460522 |
| Solicita Admisión |          6 |   0.00162537 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |       5578 |     63.7122  |
| Sistemas / Automatizado   |       3003 |     34.3004  |
| Sedes / Delegaciones      |        174 |      1.98744 |

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
