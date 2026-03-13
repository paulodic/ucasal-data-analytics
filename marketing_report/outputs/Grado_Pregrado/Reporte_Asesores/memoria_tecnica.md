# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-12 21:17:18
**Segmento:** Grado_Pregrado
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 398,556 |
| Total Inscriptos físicos | 9,525 |
| Leads en Contact Center | 135,406 (34.0%) |
| Leads con Estado "Abierto" | 148,930 (37.4%) |

## Distribución de Estados (Top 10)
| Estado            |   Cantidad |   Porcentaje |
|:------------------|-----------:|-------------:|
| Abierto           |     148930 |  37.3674     |
| No interesado     |     128567 |  32.2582     |
| Interesado        |      95744 |  24.0227     |
| Solicitud creada  |      24634 |   6.18081    |
| Desuscripto       |        656 |   0.164594   |
| Pre Inscripción   |         18 |   0.0045163  |
| Solicita Admisión |          7 |   0.00175634 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |       7782 |     81.7008  |
| Sistemas / Automatizado   |       1348 |     14.1522  |
| Sedes / Delegaciones      |        395 |      4.14698 |

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
