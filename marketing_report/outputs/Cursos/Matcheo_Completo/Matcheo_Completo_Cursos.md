# Matcheo Completo: Cursos

**Generado:** 2026-03-06 23:40:32
**Segmento:** Cursos
**Script:** `21_exportar_matcheo_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Totales Históricos
| Métrica | Valor |
|---|---|
| Total registros leads (con duplicados) | 965 |
| Personas únicas (deduplicadas) | 616 |
| Match Exacto (DNI/Email/Teléfono) | 592 |
| Match Fuzzy (revisión pendiente) | 24 |
| Sin match (solo lead) | 0 |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (2026) | 129 |
| Inscriptos campaña anterior (match histórico) | 463 |

## Ventana de Conversión (Cohorte)
| Métrica | Valor |
|---|---|
| Ventana de análisis | Todos hasta 14/02/2026 |
| Leads en ventana (dedup) | 600 |
| Inscriptos en ventana | 581 |
| Tasa de conversión | 96.83% |

## Archivos de Salida
| Archivo | Filas | Descripcion |
|---|---|---|
| `Resumen_Cursos.xlsx` | — | Métricas y estadísticas |
| `Con_Duplicados_Cursos.xlsx` | 965 | Todos los registros de leads |
| `Deduplicados_Cursos.xlsx` | 616 | 1 fila por persona (mejor match) |
| `Solo_Matcheados_Cursos.xlsx` | 592 | Solo matcheos exactos |

## Reglas de Negocio
- **Deduplicación:** prioridad Exacto > Fuzzy > Sin_Match (misma clave pk)
- **Clave pk:** DNI (sin decimal) > Correo > ID Consulta > índice
- **Ventana cohorte Grado_Pregrado:** desde 2025-09-01 (ingreso 2026)
- **Ventana cohorte Cursos/Posgrados:** todos los registros hasta hoy
