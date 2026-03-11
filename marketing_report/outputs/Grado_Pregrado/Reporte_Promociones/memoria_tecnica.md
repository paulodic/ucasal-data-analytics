# Memoria Técnica: Reporte de Promociones

**Generado:** 2026-03-06 23:31:07
**Segmento:** Grado_Pregrado
**Script:** `18_analisis_promociones.py`

## Fuentes de Datos
- Inscriptos: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\Grado_Pregrado\reporte_marketing_inscriptos_origenes.csv`

## Volúmenes Procesados
| Métrica | Valor |
|---|---|
| Total inscriptos analizados | 8,755 |
| Primer inscripto registrado | 01/09/2025 |

## Distribución por Tramo Promocional
| Tramo_Promocional         |   Cantidad_Inscriptos |
|:--------------------------|----------------------:|
| Tramo 1 (50% OFF)         |                  1868 |
| Tramo 2 (40% OFF)         |                  1215 |
| Tramo 3 (30% OFF)         |                  1112 |
| Tramo 4 (20% OFF)         |                  1560 |
| Tramo 5 (15% OFF)         |                  1003 |
| Tramo 6 (10% OFF Ene)     |                   916 |
| Tramo 7 (10% OFF Feb)     |                  1081 |
| Tramo 8 (10% OFF Ext)     |                     0 |
| Post Extension (Expirado) |                     0 |
| Sin Fecha Registrada      |                     0 |

## Reglas de Negocio
- **Fecha utilizada:** `Insc_Fecha Pago` / `Fecha Pago` (fecha de transacción, NO Fecha Aplicación)
- **Tramos:** Definidos por rangos de fecha fijos según calendario de promociones UCASAL
- **Aplica solo a:** Segmento Grado_Pregrado

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `18_reporte_promociones.pdf` | Informe visual con 3 graficos |
| `18_reporte_promociones.xlsx` | Datos tramos + calendario |
| `18_reporte_promociones.md` | Documentacion textual |
| `18_tabla_promociones.csv` | Tabla cruda volumen por tramo |
| `memoria_tecnica.md` | Este archivo |
