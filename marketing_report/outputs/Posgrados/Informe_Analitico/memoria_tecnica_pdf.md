# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-12 21:27:35
**Segmento:** Posgrados
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads | 133 |
| Personas únicas evaluadas (cohorte) | 84 |
| Personas convertidas (Exacto, dedup) | 84 |
| Tasa conversión deduplicada | 100.00% |
| Matches Fuzzy (excluidos de tasa) | 45 |
| Inscriptos exactos deduplicados | 58 |
|   - Match por DNI | 24 |
|   - Match por Email | 18 |
|   - Match por Telefono | 9 |
|   - Match por Celular | 7 |
| Inscriptos directos (sin lead) | 222 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 6 |
| Leads Bot en cohorte evaluada | 4 |
| Inscripciones confirmadas (Bot) | 4 |
| Tasa conversión Bot | 100.00% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 15 |
| Leads SIN UTM | 118 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** No — todos los leads
- **Fecha de corte:** `14 de febrero de 2026`
- **Páginas PDF generadas:** 26

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
