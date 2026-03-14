# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-14 20:35:54
**Segmento:** Posgrados
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads (historico) | 91 |
| Consultas en ventana de conversion | 90 |
| Personas unicas en ventana de conversion | 62 |
| Personas convertidas (Exacto, dedup) | 62 |
| Tasa conversion s/Consultas | 68.89% |
| **Tasa conversion s/Personas (KPI)** | **100.00%** |
| Matches Fuzzy (excluidos de tasa) | 48 |
| Inscriptos exactos deduplicados | 56 |
|   - Match por DNI | 24 |
|   - Match por Email | 18 |
|   - Match por Telefono | 7 |
|   - Match por Celular | 7 |
| Inscriptos directos (sin lead) | 221 |

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
| Leads CON UTM | 13 |
| Leads SIN UTM | 78 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** No — todos los leads
- **Fecha de corte:** `14 de febrero de 2026`
- **Páginas PDF generadas:** 27

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
