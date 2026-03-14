# Memoria Técnica: Auditoría CRM Matriculadas

**Generado:** 2026-03-14 20:35:14
**Segmento:** Cursos
**Script:** `16_analisis_matriculadas.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Auditoría CRM vs Base Contable
| Métrica | Valor |
|---|---|
| Total Leads analizados | 41 |
| Leads con Matriculadas=1 en CRM | 5 |
| Inscriptos reales cruzados (verificados) | 5 |
| **Falsos positivos CRM** (marcados pero no inscriptos) | 5 |
| **Falsos negativos CRM** (inscriptos pero no marcados) | 5 |
| Diferencia bruta (CRM - Real) | 0 |

## Atribución de Inscriptos Reales
| Tipo de Match | Cantidad |
|---|---|
| Total inscriptos físicos (base contable) | 94 |
| Rastreados por match Exacto | 18 |
| Rastreados por match Fuzzy (nombre) | 3 |
| Rastreados por match Fuzzy (email) | 2 |
| Huérfanos (sin traza en CRM) | 71 |

## Reglas de Negocio
- **Matriculadas CRM:** Columna `Matriculadas` con valor `1.0` en los leads
- **Inscriptos reales:** Cualquier lead con `Match_Tipo` que contenga `"Exacto"` o `"Fuzzy"`
- **Falso positivo:** `Matriculadas=1` pero sin match en base contable
- **Falso negativo:** Inscripto real verificado sin `Matriculadas=1` en CRM

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Analisis_CRM\auditoria_crm_matriculadas.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Cursos\Analisis_CRM\16_analisis_matriculadas.md`
