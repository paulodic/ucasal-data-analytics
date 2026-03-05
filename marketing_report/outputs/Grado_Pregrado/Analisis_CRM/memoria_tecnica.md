# Memoria Técnica: Auditoría CRM Matriculadas

**Generado:** 2026-03-03 10:16:02
**Segmento:** Grado_Pregrado
**Script:** `16_analisis_matriculadas.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Auditoría CRM vs Base Contable
| Métrica | Valor |
|---|---|
| Total Leads analizados | 369,148 |
| Leads con Matriculadas=1 en CRM | 5,712 |
| Inscriptos reales cruzados (verificados) | 188 |
| **Falsos positivos CRM** (marcados pero no inscriptos) | 5,707 |
| **Falsos negativos CRM** (inscriptos pero no marcados) | 183 |
| Diferencia bruta (CRM - Real) | 5,524 |

## Atribución de Inscriptos Reales
| Tipo de Match | Cantidad |
|---|---|
| Total inscriptos físicos (base contable) | 8,755 |
| Rastreados por match Exacto | 6,926 |
| Rastreados por match Fuzzy (nombre) | 137 |
| Rastreados por match Fuzzy (email) | 51 |
| Huérfanos (sin traza en CRM) | 1,641 |

## Reglas de Negocio
- **Matriculadas CRM:** Columna `Matriculadas` con valor `1.0` en los leads
- **Inscriptos reales:** Cualquier lead con `Match_Tipo` que contenga `"Exacto"` o `"Fuzzy"`
- **Falso positivo:** `Matriculadas=1` pero sin match en base contable
- **Falso negativo:** Inscripto real verificado sin `Matriculadas=1` en CRM

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Analisis_CRM\auditoria_crm_matriculadas.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Analisis_CRM\16_analisis_matriculadas.md`
