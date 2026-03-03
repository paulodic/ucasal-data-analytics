# Benchmark: 02_cruce_datos.py — Comparación de Rendimiento

## Objetivo
Comparar el rendimiento del proceso de matching antes y después de las optimizaciones de velocidad aplicadas al fuzzy.

---

## RUN 1 — Código Original (Lento) ✅ Completado

| Métrica | Valor |
|---|---|
| **Fecha de ejecución** | 2026-03-01 ~22:45 a 2026-03-02 ~01:xx (ARG) |
| **Duración total estimada** | > 2 horas (proceso aún corriendo al registrar estos datos) |
| **Versión del código** | commit `160b0c4` — antes de optimizaciones fuzzy |
| **Leads únicos cargados** | 217,028 |
| **Inscriptos únicos cargados** | 7,843 |
| **Leads duplicados removidos** | 1 |
| **Inscriptos duplicados removidos** | 1 |

### Fases y tiempos aproximados

| Fase | Descripción | Tiempo estimado |
|---|---|---|
| Lectura y deduplicación | Carga de XLSXs + concat | < 2 min |
| Limpieza de claves | DNI, Email, Phone | < 1 min |
| Match exacto (DNI + Email + Tel + Cel) | Merge exacto | < 1 min |
| **3.5 — Fuzzy Email (LENTO)** | Loop O(n×m) sin paralelismo sobre ~150K leads × ~3.5K inscriptos | **> 2 horas** |
| 4 — Fuzzy Nombre (multiprocessing) | thefuzz + mp.Pool(24 cores) | A registrar |

### Resultados del matching (a completar cuando termine)
| Métrica | Valor |
|---|---|
| Matches exactos DNI | _pendiente_ |
| Matches exactos Email | _pendiente_ |
| Matches exactos Teléfono | _pendiente_ |
| Matches exactos Celular | _pendiente_ |
| **Matches fuzzy email** | _pendiente_ |
| **Matches fuzzy nombre** | _pendiente_ |
| Leads sin match | _pendiente_ |
| Inscriptos sin match | _pendiente_ |
| **Grado_Pregrado — Leads exportados** | _pendiente_ |
| **Grado_Pregrado — Inscriptos exportados** | _pendiente_ |

> 📝 Completar con los valores del output de consola cuando concluya.

---

## RUN 2 — Código Optimizado (Pendiente)

| Métrica | Valor |
|---|---|
| **Fecha de ejecución** | _a registrar_ |
| **Duración total** | _a registrar_ (estimado: 5-15 min) |
| **Versión del código** | post-optimización fuzzy — rapidfuzz + bucketed email |
| **Leads únicos cargados** | Se espera igual: ~217,028 |
| **Inscriptos únicos cargados** | Se espera igual: ~7,843 |

### Cambios aplicados en esta versión

| Fase | Cambio |
|---|---|
| **3.5 — Fuzzy Email** | Loop O(n×m) → `defaultdict` por longitud O(m × ~500 candidatos). Reducción: de 525M a ~1.75M comparaciones (~300x) |
| **4 — Fuzzy Nombre** | `thefuzz` (Python puro) → `rapidfuzz` (C++ nativo, 10-100x más rápido por core) con fallback automático |

### Resultados esperados (a completar)
| Métrica | Valor |
|---|---|
| Matches fuzzy email | _a registrar_ |
| Matches fuzzy nombre | _a registrar_ |
| Duración fase email fuzzy | _a registrar_ |
| Duración fase nombre fuzzy | _a registrar_ |
| **Duración total** | _a registrar_ |

---

## Comparación Final (a completar)

| Métrica | Run 1 (original) | Run 2 (optimizado) | Mejora |
|---|---|---|---|
| Duración total | _pendiente_ | _pendiente_ | _pendiente_ |
| Fase fuzzy email | > 2 horas | _pendiente_ | _pendiente_ |
| Fase fuzzy nombre | _pendiente_ | _pendiente_ | _pendiente_ |
| Fuzzy email encontrados | _pendiente_ | _pendiente_ | debe ser igual |
| Fuzzy nombre encontrados | _pendiente_ | _pendiente_ | debe ser igual |

> ⚠️ Los resultados (cantidad de matches) deben ser **idénticos** entre ambas versiones — solo cambia la velocidad, no la lógica de matching.
