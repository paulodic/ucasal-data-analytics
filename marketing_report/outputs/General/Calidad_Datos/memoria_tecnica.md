# Memoria Tecnica: Analisis de Dominios Invalidos

**Generado:** 2026-03-14 20:39:13
**Script:** `15_dominios_invalidos.py`

## Fuente de Datos
- Leads: `h:\Test-Antigravity\marketing_report\outputs\Data_Base\reporte_marketing_leads_completos.csv` (215,322 registros con correo)

## Metodologia
- Se extrae el dominio del correo (parte despues del @)
- Se cruza contra el diccionario de CORRECCIONES (typos conocidos)
- Para cada typo, se estima cuantos matches se recuperarian corrigiendo el dominio
- Estimacion conservadora: tasa_match_dominio_correcto * leads_no_matcheados_con_typo

## Resultados Clave
| Metrica | Valor |
|---|---|
| Total leads con correo | 215,322 |
| Typos distintos detectados | 27 |
| Leads afectados | 1,617 |
| Matches recuperables estimados | 49 |
| Dominios sospechosos sin clasificar | 30 |

## Nota Importante
A la fecha (marzo 2026), las correcciones de dominios identificadas en este informe
**NO se aplican en el proceso de matching** de leads con inscriptos (`02_cruce_datos.py`).
Este reporte es exclusivamente de auditoria y diagnostico.

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `dominios_invalidos.pdf` | Informe visual con tablas |
| `dominios_invalidos.md` | Documentacion textual |
| `dominios_invalidos.xlsx` | Datos (Typos_Conocidos + Dominos_Sospechosos) |
| `memoria_tecnica.md` | Este archivo |
