# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-06 23:40:41
**Segmento:** Posgrados
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads | 123 |
| Personas únicas evaluadas (cohorte) | 77 |
| Personas convertidas (Exacto, dedup) | 77 |
| Tasa conversión deduplicada | 100.00% |
| Matches Fuzzy (excluidos de tasa) | 36 |
| Inscriptos exactos (desde tabla inscriptos) | 52 |
| Inscriptos directos (sin lead) | 237 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 5 |
| Leads Bot en cohorte evaluada | 3 |
| Inscripciones confirmadas (Bot) | 3 |
| Tasa conversión Bot | 100.00% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 14 |
| Leads SIN UTM | 109 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** No — todos los leads
- **Fecha de corte:** `14 de febrero de 2026`
- **Páginas PDF generadas:** 26

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
