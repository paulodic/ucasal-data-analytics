# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-14 20:35:21
**Segmento:** Cursos
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads (historico) | 36 |
| Consultas en ventana de conversion | 34 |
| Personas unicas en ventana de conversion | 15 |
| Personas convertidas (Exacto, dedup) | 15 |
| Tasa conversion s/Consultas | 44.12% |
| **Tasa conversion s/Personas (KPI)** | **100.00%** |
| Matches Fuzzy (excluidos de tasa) | 5 |
| Inscriptos exactos deduplicados | 18 |
|   - Match por DNI | 10 |
|   - Match por Email | 4 |
|   - Match por Telefono | 2 |
|   - Match por Celular | 2 |
| Inscriptos directos (sin lead) | 71 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 1 |
| Leads Bot en cohorte evaluada | 0 |
| Inscripciones confirmadas (Bot) | 0 |
| Tasa conversión Bot | 0.00% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 5 |
| Leads SIN UTM | 31 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** No — todos los leads
- **Fecha de corte:** `14 de febrero de 2026`
- **Páginas PDF generadas:** 27

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Cursos\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
