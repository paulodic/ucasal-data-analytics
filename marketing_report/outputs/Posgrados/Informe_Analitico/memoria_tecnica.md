# Memoria Técnica: Informe Analítico de Marketing

**Generado:** 2026-03-14 20:35:53
**Segmento:** Posgrados
**Script:** `04_reporte_final.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`
- Journey: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Otros_Reportes\reporte_journey_tiempos.xlsx`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total Consultas (ID Consulta único) | 139 |
| Personas únicas que consultaron | 111 |
| Consultas en período de conversión | 132 |
| Personas en período de conversión | 104 |
| Total Inscriptos | 325 |
| Personas convertidas (Exacto) | 62 |
| Personas convertidas (Fuzzy) | 48 |
| Personas no convertidas | 0 |
| Inscriptos atribuidos a Lead (Exacto) | 56 |
| Inscriptos sin trazabilidad | 221 |

> **Nota:** Cada consulta tiene un ID unico de Salesforce y un origen especifico. Una persona puede tener multiples consultas desde diferentes canales. Se presentan DOS tasas de conversion: sobre consultas (eficiencia por interaccion) y sobre personas (eficiencia por individuo, KPI principal). Embudo: Consultas -> Personas -> Inscriptos.

## Tasas de Conversion Calculadas
| Ecosistema | Consultas | Personas | Convertidas | Tasa s/Consultas | Tasa s/Personas |
|---|---|---|---|---|---|
| **General** | 132 | 104 | 62 | 46.97% | 59.62% |
| **Google Ads** | 21 | 19 | 9 | 42.86% | 47.37% |
| **Meta (FB/IG)** | 72 | 60 | 31 | 43.06% | 51.67% |

## Procedencia de Leads
| Categoría | Cantidad | Porcentaje |
|---|---|---|
| Plataformas Pagas (UTM/Ads) | 96 | 69.1% |
| Otros (Orgánico/Sin Tracking) | 43 | 30.9% |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (2026) | 8 |
| Inscriptos campaña anterior (match histórico) | 55 |

La columna `Campana_Lead` en el CSV maestro indica si la fecha de consulta del lead
cae dentro de la ventana de la campaña actual o es anterior. Generada por `02_cruce_datos.py`.
- Grado_Pregrado: >= 2025-09-01 = "Ingreso 2026", antes = "Campaña Anterior"
- Cursos/Posgrados: >= 2026-01-01 = "2026", antes = "Campaña Anterior"

## Reglas de Negocio Aplicadas
- **Filtro de cohorte (Grado_Pregrado):** No — se usan todos los leads
- **Match_Tipo para conversión exacta:** Se filtran registros cuyo `Match_Tipo` contenga la cadena `"Exacto"` (incluye: Exacto DNI, Email, Teléfono, Celular)
- **Fuzzy excluidos de tasa:** Los matches fuzzy (nombre/email) NO se cuentan como conversión
- **Fecha de corte del informe:** `14 de febrero de 2026` (extraída de inscriptos, columna `Insc_Fecha Pago`)

## Gráficos Generados
1. `chart_1_conversion_leads.png` — Barras: Total Leads vs Conv. Exactas vs Fuzzy
2. `chart_2_composicion_inscriptos.png` — Pie: Atribuidos vs Sin trazabilidad
3. `chart_5_leads_pagos_vs_otros.png` — Pie: Leads pagados vs orgánicos
4. `chart_7_inscriptos_pagos_vs_otros.png` — Pie: Inscripciones pagas vs orgánicas
5. `chart_8_tiempos_resolucion.png` — Barras: Días resolución pagados vs orgánicos
6. `chart_9_consultas_por_dia.png` — Línea: Volumen consultas diario
7. `chart_9b_consultas_por_mes.png` — Línea: Volumen consultas mensual
8. `chart_6_inscripciones_por_dia.png` — Línea: Curva inscripciones por día
