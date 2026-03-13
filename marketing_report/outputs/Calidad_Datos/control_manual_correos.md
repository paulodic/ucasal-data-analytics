# Control Manual de Correos Fuzzy

**Generado:** 2026-03-12 21:30:53
**Script:** `08_fuzzy_correos.py`

## Descripcion
Busca pares de (lead no matcheado, inscripto no matcheado) cuyos correos difieren en
exactamente 1 caracter (distancia Levenshtein = 1). El resultado es una lista para
**revision humana**: la columna `Validado` debe completarse manualmente con SI o NO.

## Estadisticas del Proceso
| Metrica | Valor |
|---|---|
| Leads sin match analizados | 208,612 |
| Inscriptos sin match analizados | 3,520 |
| Pares candidatos nuevos encontrados | 0 |
| Total acumulado de pares | 6 |
| Validados SI | 0 |
| Validados NO | 0 |
| Sin validar aun | 0 |

## Como Usar el Excel
1. Abrir `control_manual_correos.xlsx`
2. Para cada fila: comparar Lead_Nombre + Lead_Correo con Insc_Nombre + Insc_Correo
3. Si son la misma persona con error de tipeo: escribir **SI** en la columna Validado
4. Si son personas diferentes: escribir **NO** en la columna Validado
5. Guardar el archivo — la proxima corrida del script respetara estas validaciones

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `control_manual_correos.xlsx` | Pares candidatos para revision humana (incremental) |
| `control_manual_correos.md` | Este archivo de documentacion |
