# Memoria Técnica: Auditoría CRM Matriculadas

**Generado:** 2026-03-14 20:25:20
**Segmento:** Grado_Pregrado
**Script:** `16_analisis_matriculadas.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Auditoría CRM vs Base Contable
| Métrica | Valor |
|---|---|
| Total Leads analizados | 398,442 |
| Leads con Matriculadas=1 en CRM | 8,294 |
| Inscriptos reales cruzados (verificados) | 153 |
| **Falsos positivos CRM** (marcados pero no inscriptos) | 8,289 |
| **Falsos negativos CRM** (inscriptos pero no marcados) | 148 |
| Diferencia bruta (CRM - Real) | 8,141 |

## Atribución de Inscriptos Reales
| Tipo de Match | Cantidad |
|---|---|
| Total inscriptos físicos (base contable) | 9,525 |
| Rastreados por match Exacto | 7,984 |
| Rastreados por match Fuzzy (nombre) | 110 |
| Rastreados por match Fuzzy (email) | 43 |
| Huérfanos (sin traza en CRM) | 1,388 |

## Reglas de Negocio
- **Matriculadas CRM:** Columna `Matriculadas` con valor `1.0` en los leads
- **Inscriptos reales:** Cualquier lead con `Match_Tipo` que contenga `"Exacto"` o `"Fuzzy"`
- **Falso positivo:** `Matriculadas=1` pero sin match en base contable
- **Falso negativo:** Inscripto real verificado sin `Matriculadas=1` en CRM

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Analisis_CRM\auditoria_crm_matriculadas.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Grado_Pregrado\Analisis_CRM\16_analisis_matriculadas.md`
