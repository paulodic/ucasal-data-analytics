# Memoria Técnica: Informe Analítico de Marketing

**Generado:** 2026-03-12 21:17:57
**Segmento:** Grado_Pregrado
**Script:** `04_reporte_final.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`
- Journey: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Otros_Reportes\reporte_journey_tiempos.xlsx`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total Leads cargados | 398,556 |
| Leads en período de conversión | 212,826 |
| Total Inscriptos | 9,525 |
| Leads convertidos (Exacto) | 10,225 |
| Leads convertidos (Fuzzy) | 155 |
| Leads no convertidos | 385,231 |
| Inscriptos atribuidos a Lead (Exacto) | 7,993 |
| Inscriptos sin trazabilidad | 1,377 |

## Tasas de Conversión Calculadas
| Ecosistema | Universo | Convertidos | Tasa |
|---|---|---|---|
| **General** | 212,826 | 10,225 | 4.80% |
| **Google Ads** | 27,170 | 1,756 | 6.46% |
| **Meta (FB/IG)** | 148,479 | 1,494 | 1.01% |

## Procedencia de Leads
| Categoría | Cantidad | Porcentaje |
|---|---|---|
| Plataformas Pagas (UTM/Ads) | 321,665 | 80.7% |
| Otros (Orgánico/Sin Tracking) | 76,891 | 19.3% |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (Ingreso 2026) | 10,448 |
| Inscriptos campaña anterior (match histórico) | 2,722 |

La columna `Campana_Lead` en el CSV maestro indica si la fecha de consulta del lead
cae dentro de la ventana de la campaña actual o es anterior. Generada por `02_cruce_datos.py`.
- Grado_Pregrado: >= 2025-09-01 = "Ingreso 2026", antes = "Campaña Anterior"
- Cursos/Posgrados: >= 2026-01-01 = "2026", antes = "Campaña Anterior"

## Reglas de Negocio Aplicadas
- **Filtro de cohorte (Grado_Pregrado):** Sí — leads desde 2025-09-01
- **Match_Tipo para conversión exacta:** Se filtran registros cuyo `Match_Tipo` contenga la cadena `"Exacto"` (incluye: Exacto DNI, Email, Teléfono, Celular)
- **Fuzzy excluidos de tasa:** Los matches fuzzy (nombre/email) NO se cuentan como conversión
- **Fecha de corte del informe:** `17 de febrero de 2026` (extraída de inscriptos, columna `Insc_Fecha Pago`)

## Gráficos Generados
1. `chart_1_conversion_leads.png` — Barras: Total Leads vs Conv. Exactas vs Fuzzy
2. `chart_2_composicion_inscriptos.png` — Pie: Atribuidos vs Sin trazabilidad
3. `chart_5_leads_pagos_vs_otros.png` — Pie: Leads pagados vs orgánicos
4. `chart_7_inscriptos_pagos_vs_otros.png` — Pie: Inscripciones pagas vs orgánicas
5. `chart_8_tiempos_resolucion.png` — Barras: Días resolución pagados vs orgánicos
6. `chart_9_consultas_por_dia.png` — Línea: Volumen consultas diario
7. `chart_9b_consultas_por_mes.png` — Línea: Volumen consultas mensual
8. `chart_6_inscripciones_por_dia.png` — Línea: Curva inscripciones por día
