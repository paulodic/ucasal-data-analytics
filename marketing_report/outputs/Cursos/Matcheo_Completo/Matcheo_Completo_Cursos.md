# Matcheo Completo: Cursos

**Generado:** 2026-03-14 20:35:45
**Segmento:** Cursos
**Script:** `21_exportar_matcheo_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Cursos\reporte_marketing_inscriptos_origenes.csv`

## Totales Históricos
| Métrica | Valor |
|---|---|
| Total registros leads (con duplicados) | 41 |
| Personas únicas (deduplicadas) | 22 |
| Match Exacto (DNI/Email/Teléfono) | 17 |
| Match Fuzzy (revisión pendiente) | 5 |
| Sin match (solo lead) | 0 |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (2026) | 4 |
| Inscriptos campaña anterior (match histórico) | 13 |

## Ventana de Conversión (Cohorte)
| Métrica | Valor |
|---|---|
| Ventana de análisis | Todos hasta 14/02/2026 |
| Leads en ventana (dedup) | 19 |
| Inscriptos en ventana | 15 |
| Tasa de conversión | 78.95% |

## Archivos de Salida
| Archivo | Filas | Descripcion |
|---|---|---|
| `Resumen_Cursos.xlsx` | — | Métricas y estadísticas |
| `Con_Duplicados_Cursos.xlsx` | 41 | Todos los registros de leads |
| `Deduplicados_Cursos.xlsx` | 22 | 1 fila por persona (mejor match) |
| `Solo_Matcheados_Cursos.xlsx` | 17 | Solo matcheos exactos |

## Reglas de Negocio
- **Deduplicación:** prioridad Exacto > Fuzzy > Sin_Match (misma clave pk)
- **Clave pk:** DNI (sin decimal) > Correo > ID Consulta > índice
- **Ventana cohorte Grado_Pregrado:** desde 2025-09-01 (ingreso 2026)
- **Ventana cohorte Cursos/Posgrados:** todos los registros hasta hoy

## Nota Metodologica
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Para atribucion multi-canal, referirse al Informe Analitico (04_reporte_final).
- **Match:** Exacto por DNI, Email, Telefono y Celular.
