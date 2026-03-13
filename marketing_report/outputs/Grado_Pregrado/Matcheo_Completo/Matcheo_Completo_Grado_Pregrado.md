# Matcheo Completo: Grado_Pregrado

**Generado:** 2026-03-12 21:26:52
**Segmento:** Grado_Pregrado
**Script:** `21_exportar_matcheo_completo.py`

## Fuentes de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_leads_completos.csv`
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Totales Históricos
| Métrica | Valor |
|---|---|
| Total registros leads (con duplicados) | 398,556 |
| Personas únicas (deduplicadas) | 305,249 |
| Match Exacto (DNI/Email/Teléfono) | 7,980 |
| Match Fuzzy (revisión pendiente) | 155 |
| Sin match (solo lead) | 385,231 |

## Atribución por Campaña
| Métrica | Valor |
|---|---|
| Inscriptos campaña actual (Ingreso 2026) | 6,465 |
| Inscriptos campaña anterior (match histórico) | 1,515 |

## Ventana de Conversión (Cohorte)
| Métrica | Valor |
|---|---|
| Ventana de análisis | 01/09/2025 - 17/02/2026 |
| Leads en ventana (dedup) | 170,085 |
| Inscriptos en ventana | 6,911 |
| Tasa de conversión | 4.06% |

## Archivos de Salida
| Archivo | Filas | Descripcion |
|---|---|---|
| `Resumen_Grado_Pregrado.xlsx` | — | Métricas y estadísticas |
| `Con_Duplicados_Grado_Pregrado.xlsx` | 398,556 | Todos los registros de leads |
| `Deduplicados_Grado_Pregrado.xlsx` | 305,249 | 1 fila por persona (mejor match) |
| `Solo_Matcheados_Grado_Pregrado.xlsx` | 7,980 | Solo matcheos exactos |

## Reglas de Negocio
- **Deduplicación:** prioridad Exacto > Fuzzy > Sin_Match (misma clave pk)
- **Clave pk:** DNI (sin decimal) > Correo > ID Consulta > índice
- **Ventana cohorte Grado_Pregrado:** desde 2025-09-01 (ingreso 2026)
- **Ventana cohorte Cursos/Posgrados:** todos los registros hasta hoy

## Nota Metodologica
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consulto. Para atribucion multi-canal, referirse al Informe Analitico (04_reporte_final).
- **Match:** Exacto por DNI, Email, Telefono y Celular.
