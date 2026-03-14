# Memoria Técnica: Reporte de Asesores y Canales de Venta

**Generado:** 2026-03-14 20:25:32
**Segmento:** Grado_Pregrado
**Script:** `17_reporte_asesores.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Macro
| Métrica | Valor |
|---|---|
| Total Leads históricos | 398,442 |
| Total Inscriptos físicos | 9,525 |
| Leads en Contact Center | 135,367 (34.0%) |
| Leads con Estado "Abierto" | 148,879 (37.4%) |

## Distribución de Estados (Top 10)
| Estado            |   Cantidad |   Porcentaje |
|:------------------|-----------:|-------------:|
| Abierto           |     148879 |  37.3653     |
| No interesado     |     128521 |  32.2559     |
| Interesado        |      95728 |  24.0256     |
| Solicitud creada  |      24633 |   6.18233    |
| Desuscripto       |        656 |   0.164641   |
| Pre Inscripción   |         18 |   0.0045176  |
| Solicita Admisión |          7 |   0.00175684 |

## Origen de Inscripciones (Atribución por Canal)
| Origen_Cierre             |   Cantidad |   Porcentaje |
|:--------------------------|-----------:|-------------:|
| Asesores UCASAL (Central) |       7790 |     81.7848  |
| Sistemas / Automatizado   |       1340 |     14.0682  |
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
- **Match Exacto:** DNI (5,333), Email (2,150), Telefono (237), Celular (217). Total: 7,937.
