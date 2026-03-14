# Memoria Técnica: Informe Analítico de Marketing

**Generado:** 2026-03-14 20:26:16
**Segmento:** Grado_Pregrado
**Script:** `04_reporte_final.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`
- Journey: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Otros_Reportes\reporte_journey_tiempos.xlsx`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total Consultas (ID Consulta único) | 398,442 |
| Personas únicas que consultaron | 305,232 |
| Consultas en período de conversión | 212,778 |
| Personas en período de conversión | 170,073 |
| Total Inscriptos | 9,525 |
| Personas convertidas (Exacto) | 6,895 |
| Personas convertidas (Fuzzy) | 153 |
| Personas no convertidas | 297,206 |
| Inscriptos atribuidos a Lead (Exacto) | 7,984 |
| Inscriptos sin trazabilidad | 1,388 |

> **Nota:** Cada consulta tiene un ID unico de Salesforce y un origen especifico. Una persona puede tener multiples consultas desde diferentes canales. Se presentan DOS tasas de conversion: sobre consultas (eficiencia por interaccion) y sobre personas (eficiencia por individuo, KPI principal). Embudo: Consultas -> Personas -> Inscriptos.

## Tasas de Conversion Calculadas
| Ecosistema | Consultas | Personas | Convertidas | Tasa s/Consultas | Tasa s/Personas |
|---|---|---|---|---|---|
| **General** | 212,778 | 170,073 | 6,895 | 3.24% | 4.05% |
| **Google Ads** | 27,163 | 23,722 | 1,399 | 5.15% | 5.90% |
| **Meta (FB/IG)** | 148,445 | 125,561 | 1,080 | 0.73% | 0.86% |

## Procedencia de Leads
| Categoría | Cantidad | Porcentaje |
|---|---|---|
| Plataformas Pagas (UTM/Ads) | 321,617 | 80.7% |
| Otros (Orgánico/Sin Tracking) | 76,825 | 19.3% |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (Ingreso 2026) | 6,381 |
| Inscriptos campaña anterior (match histórico) | 1,556 |

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
