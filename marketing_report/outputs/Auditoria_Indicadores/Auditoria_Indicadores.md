# Auditoria de Indicadores - UCASAL Marketing
**Generado:** 2026-03-04 17:37:32  
**Script:** `22_auditoria_indicadores.py`  
**Checks:** 16 OK | 2 con problemas  
**Alertas:** 2  

## KPIs por Segmento

| Metrica                 | Grado_Pregrado   | Cursos     | Posgrados   |
|:------------------------|:-----------------|:-----------|:------------|
| Leads_Raw               | 369148           | 965        | 157         |
| Exacto_Raw              | 11468            | 941        | 123         |
| Fuzzy_Raw               | 188              | 24         | 34          |
| Sin_Match_Raw           | 357492           | 0          | 0           |
| Check_Raw_Sum           | 369148           | 965        | 157         |
| Personas_Dedup          | 286660           | 616        | 127         |
| Exacto_Dedup            | 7020             | 592        | 93          |
| Fuzzy_Dedup             | 188              | 24         | 34          |
| Sin_Match_Dedup         | 279452           | 0          | 0           |
| Check_Dedup_Sum         | 286660           | 616        | 127         |
| Ventana_Inicio          | 2025-09-01       | Todos      | Todos       |
| Ventana_Fin             | 2026-02-17       | 2026-02-14 | 2026-02-14  |
| Leads_Ventana_Dedup     | 152231           | 600        | 105         |
| Conv_Ventana_Exacto     | 5892             | 581        | 77          |
| Tasa_Conv_%             | 3.8704           | 96.8333    | 73.3333     |
| Inscriptos_Base         | 8755             | 864        | 325         |
| Inscriptos_Exacto_Base  | 6926             | 572        | 52          |
| Inscriptos_Directo_Base | 1641             | 268        | 239         |
| Leads_Google_Ventana    | 18436            | 39         | 17          |
| Conv_Google_Ventana     | 970              | 35         | 9           |
| Leads_Facebook_Ventana  | 111503           | 139        | 61          |
| Conv_Facebook_Ventana   | 821              | 132        | 44          |
| Google_Spend_ARS        | 47387402.9       | 0.0        | 0.0         |
| Facebook_Spend_ARS      | 115200000.0      | 7100000.0  | 14500000.0  |
| CPL_Google              | 2570.37          | 0.0        | 0.0         |
| CPA_Google              | 48852.99         | 0.0        | 0.0         |
| CPL_Facebook            | 1033.16          | 51079.14   | 237704.92   |
| CPA_Facebook            | 140316.69        | 53787.88   | 329545.45   |
| Rev_Atrib_Google        | 171785360.0      | 5706000.0  | 1993150.0   |
| ROI_Google_%            | 262.51           | nan        | nan         |
| Rev_Atrib_Facebook      | 140717445.0      | 20668800.0 | 9992590.0   |
| ROI_Facebook_%          | 22.15            | 191.11     | -31.09      |

## Checks de Consistencia

| Segmento       | Check                                         | Esperado   | Obtenido   | Diferencia   | OK     |
|:---------------|:----------------------------------------------|:-----------|:-----------|:-------------|:-------|
| Grado_Pregrado | Exacto+Fuzzy+SinMatch == Leads_Raw            | 369148     | 369148     | 0            | SI     |
| Grado_Pregrado | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 286660     | 286660     | 0            | SI     |
| Grado_Pregrado | Leads_Ventana_Dedup <= Personas_Dedup         | <= 286660  | 152231     | 0            | SI     |
| Grado_Pregrado | Conv_Ventana <= Leads_Ventana_Dedup           | <= 152231  | 5892       | 0            | SI     |
| Grado_Pregrado | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 3.87%      |              | SI     |
| Grado_Pregrado | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 5892    | 8755       | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch == Leads_Raw            | 965        | 965        | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 616        | 616        | 0            | SI     |
| Cursos         | Leads_Ventana_Dedup <= Personas_Dedup         | <= 616     | 600        | 0            | SI     |
| Cursos         | Conv_Ventana <= Leads_Ventana_Dedup           | <= 600     | 581        | 0            | SI     |
| Cursos         | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 96.83%     |              | ALERTA |
| Cursos         | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 581     | 864        | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch == Leads_Raw            | 157        | 157        | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 127        | 127        | 0            | SI     |
| Posgrados      | Leads_Ventana_Dedup <= Personas_Dedup         | <= 127     | 105        | 0            | SI     |
| Posgrados      | Conv_Ventana <= Leads_Ventana_Dedup           | <= 105     | 77         | 0            | SI     |
| Posgrados      | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 73.33%     |              | ALERTA |
| Posgrados      | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 77      | 325        | 0            | SI     |

## Alertas

| Segmento   | Indicador   | Valor   | Alerta                               |
|:-----------|:------------|:--------|:-------------------------------------|
| Cursos     | Tasa_Conv_% | 96.83%  | Tasa > 30% — revisar ventana cohorte |
| Posgrados  | Tasa_Conv_% | 73.33%  | Tasa > 30% — revisar ventana cohorte |

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `Auditoria_Indicadores.xlsx` | Excel con 5 hojas (KPIs, canales, checks, alertas) |
| `Auditoria_Indicadores.pdf` | Informe visual con KPIs y checks |
| `Auditoria_Indicadores.md` | Este archivo |
