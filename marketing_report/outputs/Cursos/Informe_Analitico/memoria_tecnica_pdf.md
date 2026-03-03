# Memoria Técnica: PDF Informe Analítico Completo

**Generado:** 2026-03-02 23:16:16
**Segmento:** Cursos
**Script:** `07_pdf_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total registros de leads | 941 |
| Personas únicas evaluadas (cohorte) | 581 |
| Personas convertidas (Exacto, dedup) | 581 |
| Tasa conversión deduplicada | 100.00% |
| Matches Fuzzy (excluidos de tasa) | 24 |
| Inscriptos exactos (desde tabla inscriptos) | 572 |
| Inscriptos directos (sin lead) | 268 |

## Bot / Chatbot (FuenteLead=907)
| Métrica | Valor |
|---|---|
| Leads capturados por Bot | 75 |
| Leads Bot en cohorte evaluada | 55 |
| Inscripciones confirmadas (Bot) | 55 |
| Tasa conversión Bot | 100.00% |

## Tracking UTM
| Categoría | Cantidad |
|---|---|
| Leads CON UTM | 83 |
| Leads SIN UTM | 858 |

## Reglas de Negocio
- **Clasificación Match_Tipo:** `'Exacto'` en el string = conversión confirmada; `'Posible Match Fuzzy'` = excluido de tasas
- **Deduplicación de personas:** por `DNI` (pk primaria), fallback `Correo`
- **Filtro cohorte:** No — todos los leads
- **Fecha de corte:** `14 de febrero de 2026`
- **Páginas PDF generadas:** 18

## Archivo de Salida
- `h:\Test-Antigravity\marketing_report\outputs\Cursos\Informe_Analitico\Informe_Analitico_Marketing_Completo.pdf`
