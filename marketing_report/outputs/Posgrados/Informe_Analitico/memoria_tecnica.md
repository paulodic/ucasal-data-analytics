# Memoria Técnica: Informe Analítico de Marketing

**Generado:** 2026-03-03 08:19:06
**Segmento:** Posgrados
**Script:** `04_reporte_final.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`
- Journey: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Otros_Reportes\reporte_journey_tiempos.xlsx`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total Leads cargados | 157 |
| Leads en período de conversión | 133 |
| Total Inscriptos | 325 |
| Leads convertidos (Exacto) | 105 |
| Leads convertidos (Fuzzy) | 34 |
| Leads no convertidos | 0 |
| Inscriptos atribuidos a Lead (Exacto) | 52 |
| Inscriptos sin trazabilidad | 239 |

## Tasas de Conversión Calculadas
| Ecosistema | Universo | Convertidos | Tasa |
|---|---|---|---|
| **General** | 133 | 105 | 78.95% |
| **Google Ads** | 21 | 12 | 57.14% |
| **Meta (FB/IG)** | 73 | 57 | 78.08% |

## Procedencia de Leads
| Categoría | Cantidad | Porcentaje |
|---|---|---|
| Plataformas Pagas (UTM/Ads) | 100 | 63.7% |
| Otros (Orgánico/Sin Tracking) | 57 | 36.3% |

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
