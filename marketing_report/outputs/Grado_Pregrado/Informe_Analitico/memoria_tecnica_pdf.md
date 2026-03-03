# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-02 23:15:04
**Segmento:** Grado_Pregrado
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads | 368,960 |
| Personas únicas evaluadas (cohorte) | 152,095 |
| Personas convertidas (Exacto, dedup) | 5,892 |
| Tasa conversión deduplicada | 3.87% |
| Matches Fuzzy (excluidos de tasa) | 188 |
| Inscriptos exactos (desde tabla inscriptos) | 6,926 |
| Inscriptos directos (sin lead) | 1,641 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 8,447 |
| Leads Bot en cohorte evaluada | 6,189 |
| Inscripciones confirmadas (Bot) | 396 |
| Tasa conversión Bot | 6.40% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 64,953 |
| Leads SIN UTM | 304,007 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** Sí — leads desde 2025-09-01
- **Fecha de corte:** `17 de febrero de 2026`
- **Páginas PDF generadas:** 18

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
