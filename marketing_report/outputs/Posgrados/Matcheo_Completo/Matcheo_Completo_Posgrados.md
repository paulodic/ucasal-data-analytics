# Matcheo Completo: Posgrados

**Generado:** 2026-03-06 23:41:06
**Segmento:** Posgrados
**Script:** `21_exportar_matcheo_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Posgrados\reporte_marketing_inscriptos_origenes.csv`

## Totales Históricos
| Métrica | Valor |
|---|---|
| Total registros leads (con duplicados) | 159 |
| Personas únicas (deduplicadas) | 129 |
| Match Exacto (DNI/Email/Teléfono) | 93 |
| Match Fuzzy (revisión pendiente) | 36 |
| Sin match (solo lead) | 0 |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (2026) | 28 |
| Inscriptos campaña anterior (match histórico) | 65 |

## Ventana de Conversión (Cohorte)
| Métrica | Valor |
|---|---|
| Ventana de análisis | Todos hasta 14/02/2026 |
| Leads en ventana (dedup) | 107 |
| Inscriptos en ventana | 77 |
| Tasa de conversión | 71.96% |

## Archivos de Salida
| Archivo | Filas | Descripcion |
|---|---|---|
| `Resumen_Posgrados.xlsx` | — | Métricas y estadísticas |
| `Con_Duplicados_Posgrados.xlsx` | 159 | Todos los registros de leads |
| `Deduplicados_Posgrados.xlsx` | 129 | 1 fila por persona (mejor match) |
| `Solo_Matcheados_Posgrados.xlsx` | 93 | Solo matcheos exactos |

## Reglas de Negocio
- **Deduplicación:** prioridad Exacto > Fuzzy > Sin_Match (misma clave pk)
- **Clave pk:** DNI (sin decimal) > Correo > ID Consulta > índice
- **Ventana cohorte Grado_Pregrado:** desde 2025-09-01 (ingreso 2026)
- **Ventana cohorte Cursos/Posgrados:** todos los registros hasta hoy
