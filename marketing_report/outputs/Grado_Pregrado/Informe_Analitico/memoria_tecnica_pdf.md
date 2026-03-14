# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-14 20:26:28
**Segmento:** Grado_Pregrado
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads (historico) | 398,289 |
| Consultas en ventana de conversion | 212,693 |
| Personas unicas en ventana de conversion | 170,007 |
| Personas convertidas (Exacto, dedup) | 6,895 |
| Tasa conversion s/Consultas | 3.24% |
| **Tasa conversion s/Personas (KPI)** | **4.06%** |
| Matches Fuzzy (excluidos de tasa) | 153 |
| Inscriptos exactos deduplicados | 7,984 |
|   - Match por DNI | 5,423 |
|   - Match por Email | 2,151 |
|   - Match por Telefono | 215 |
|   - Match por Celular | 195 |
| Inscriptos directos (sin lead) | 1,388 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 10,240 |
| Leads Bot en cohorte evaluada | 7,772 |
| Inscripciones confirmadas (Bot) | 503 |
| Tasa conversión Bot | 6.47% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 69,028 |
| Leads SIN UTM | 329,261 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** Sí — leads desde 2025-09-01
- **Fecha de corte:** `17 de febrero de 2026`
- **Páginas PDF generadas:** 27

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
