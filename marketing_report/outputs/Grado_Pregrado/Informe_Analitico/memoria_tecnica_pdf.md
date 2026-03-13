# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-12 21:18:05
**Segmento:** Grado_Pregrado
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads | 398,401 |
| Personas únicas evaluadas (cohorte) | 169,894 |
| Personas convertidas (Exacto, dedup) | 6,911 |
| Tasa conversión deduplicada | 4.07% |
| Matches Fuzzy (excluidos de tasa) | 155 |
| Inscriptos exactos deduplicados | 7,993 |
|   - Match por DNI | 5,423 |
|   - Match por Email | 2,151 |
|   - Match por Telefono | 227 |
|   - Match por Celular | 192 |
| Inscriptos directos (sin lead) | 1,377 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 10,240 |
| Leads Bot en cohorte evaluada | 7,663 |
| Inscripciones confirmadas (Bot) | 502 |
| Tasa conversión Bot | 6.55% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 69,035 |
| Leads SIN UTM | 329,366 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** Sí — leads desde 2025-09-01
- **Fecha de corte:** `17 de febrero de 2026`
- **Páginas PDF generadas:** 26

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
