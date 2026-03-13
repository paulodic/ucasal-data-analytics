# Memoria Tecnica: Ranking de Carreras

**Generado:** 2026-03-12 21:30:57
**Script:** `15_carreras.py`

## Fuentes de Datos
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\reporte_marketing_inscriptos_origenes.csv`

## Metodologia
- Solo se consideran registros con `Match_Tipo` que contenga 'Exacto'
- La columna de carrera usada es: `Insc_Carrera`
- Valores nulos/vacíos en carrera son excluidos del ranking

## Volúmenes
| Metrica | Valor |
|---|---|
| Total inscriptos exactos | 4,296 |
| Total carreras con inscriptos | 100 |
| Top carrera | ABOGACÍA (653 insc.) |

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `Reporte_Carreras_Ranking.pdf` | Informe visual con grafico y tabla |
| `Reporte_Carreras_Datos.xlsx` | Ranking completo en Excel (2 hojas) |
| `Reporte_Carreras.md` | Documentacion textual del ranking |
| `ranking_carreras.png` | Grafico PNG embebido en PDF |
| `memoria_tecnica.md` | Este archivo |
