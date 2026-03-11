# Matcheo Completo: Grado_Pregrado

**Generado:** 2026-03-06 23:39:53
**Segmento:** Grado_Pregrado
**Script:** `21_exportar_matcheo_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Totales Históricos
| Métrica | Valor |
|---|---|
| Total registros leads (con duplicados) | 369,146 |
| Personas únicas (deduplicadas) | 286,658 |
| Match Exacto (DNI/Email/Teléfono) | 7,020 |
| Match Fuzzy (revisión pendiente) | 186 |
| Sin match (solo lead) | 357,492 |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (Ingreso 2026) | 5,538 |
| Inscriptos campaña anterior (match histórico) | 1,482 |

## Ventana de Conversión (Cohorte)
| Métrica | Valor |
|---|---|
| Ventana de análisis | 01/09/2025 - 17/02/2026 |
| Leads en ventana (dedup) | 152,231 |
| Inscriptos en ventana | 5,892 |
| Tasa de conversión | 3.87% |

## Archivos de Salida
| Archivo | Filas | Descripcion |
|---|---|---|
| `Resumen_Grado_Pregrado.xlsx` | — | Métricas y estadísticas |
| `Con_Duplicados_Grado_Pregrado.xlsx` | 369,146 | Todos los registros de leads |
| `Deduplicados_Grado_Pregrado.xlsx` | 286,658 | 1 fila por persona (mejor match) |
| `Solo_Matcheados_Grado_Pregrado.xlsx` | 7,020 | Solo matcheos exactos |

## Reglas de Negocio
- **Deduplicación:** prioridad Exacto > Fuzzy > Sin_Match (misma clave pk)
- **Clave pk:** DNI (sin decimal) > Correo > ID Consulta > índice
- **Ventana cohorte Grado_Pregrado:** desde 2025-09-01 (ingreso 2026)
- **Ventana cohorte Cursos/Posgrados:** todos los registros hasta hoy
