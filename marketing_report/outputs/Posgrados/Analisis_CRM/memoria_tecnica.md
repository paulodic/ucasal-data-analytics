# Memoria Técnica: Auditoría CRM Matriculadas

**Generado:** 2026-03-14 20:35:47
**Segmento:** Posgrados
**Script:** `16_analisis_matriculadas.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Auditoría CRM vs Base Contable
| Métrica | Valor |
|---|---|
| Total Leads analizados | 139 |
| Leads con Matriculadas=1 en CRM | 1 |
| Inscriptos reales cruzados (verificados) | 48 |
| **Falsos positivos CRM** (marcados pero no inscriptos) | 1 |
| **Falsos negativos CRM** (inscriptos pero no marcados) | 48 |
| Diferencia bruta (CRM - Real) | 47 |

## Atribución de Inscriptos Reales
| Tipo de Match | Cantidad |
|---|---|
| Total inscriptos físicos (base contable) | 325 |
| Rastreados por match Exacto | 56 |
| Rastreados por match Fuzzy (nombre) | 33 |
| Rastreados por match Fuzzy (email) | 15 |
| Huérfanos (sin traza en CRM) | 221 |

## Reglas de Negocio
- **Matriculadas CRM:** Columna `Matriculadas` con valor `1.0` en los leads
- **Inscriptos reales:** Cualquier lead con `Match_Tipo` que contenga `"Exacto"` o `"Fuzzy"`
- **Falso positivo:** `Matriculadas=1` pero sin match en base contable
- **Falso negativo:** Inscripto real verificado sin `Matriculadas=1` en CRM

## Archivos de Salida
- PDF: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Analisis_CRM\auditoria_crm_matriculadas.pdf`
- MD: `h:\Test-Antigravity\marketing_report\outputs\Posgrados\Analisis_CRM\16_analisis_matriculadas.md`
