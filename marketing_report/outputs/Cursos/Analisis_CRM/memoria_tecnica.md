# Memoria Técnica: Auditoría CRM Matriculadas

**Generado:** 2026-03-06 23:39:56
**Segmento:** Cursos
**Script:** `16_analisis_matriculadas.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Auditoría CRM vs Base Contable
| Métrica | Valor |
|---|---|
| Total Leads analizados | 965 |
| Leads con Matriculadas=1 en CRM | 209 |
| Inscriptos reales cruzados (verificados) | 24 |
| **Falsos positivos CRM** (marcados pero no inscriptos) | 208 |
| **Falsos negativos CRM** (inscriptos pero no marcados) | 23 |
| Diferencia bruta (CRM - Real) | 185 |

## Atribución de Inscriptos Reales
| Tipo de Match | Cantidad |
|---|---|
| Total inscriptos físicos (base contable) | 864 |
| Rastreados por match Exacto | 572 |
| Rastreados por match Fuzzy (nombre) | 20 |
| Rastreados por match Fuzzy (email) | 4 |
| Huérfanos (sin traza en CRM) | 268 |

## Reglas de Negocio
- **Matriculadas CRM:** Columna `Matriculadas` con valor `1.0` en los leads
- **Inscriptos reales:** Cualquier lead con `Match_Tipo` que contenga `"Exacto"` o `"Fuzzy"`
- **Falso positivo:** `Matriculadas=1` pero sin match en base contable
- **Falso negativo:** Inscripto real verificado sin `Matriculadas=1` en CRM

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Analisis_CRM\auditoria_crm_matriculadas.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Analisis_CRM\16_analisis_matriculadas.md`
