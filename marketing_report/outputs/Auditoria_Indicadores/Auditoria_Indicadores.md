# Auditoria de Indicadores - UCASAL Marketing
**Generado:** 2026-03-12 21:31:33  
**Script:** `22_auditoria_indicadores.py`  
**Checks:** 16 OK | 2 con problemas  
**Alertas:** 2  

## KPIs por Segmento

| Metrica                 | Grado_Pregrado   | Cursos     | Posgrados   |
|:------------------------|:-----------------|:-----------|:------------|
| Leads_Raw               | 398556           | 44         | 178         |
| Exacto_Raw              | 13170            | 40         | 133         |
| Fuzzy_Raw               | 155              | 4          | 45          |
| Sin_Match_Raw           | 385231           | 0          | 0           |
| Check_Raw_Sum           | 398556           | 44         | 178         |
| Personas_Dedup          | 305249           | 25         | 145         |
| Exacto_Dedup            | 7980             | 21         | 100         |
| Fuzzy_Dedup             | 155              | 4          | 45          |
| Sin_Match_Dedup         | 297114           | 0          | 0           |
| Check_Dedup_Sum         | 305249           | 25         | 145         |
| Ventana_Inicio          | 2025-09-01       | Todos      | Todos       |
| Ventana_Fin             | 2026-02-17       | 2026-02-14 | 2026-02-14  |
| Leads_Ventana_Dedup     | 170085           | 21         | 123         |
| Conv_Ventana_Exacto     | 6911             | 18         | 84          |
| Tasa_Conv_%             | 4.0633           | 85.7143    | 68.2927     |
| Inscriptos_Base         | 9525             | 94         | 325         |
| Inscriptos_Exacto_Base  | 7993             | 19         | 58          |
| Inscriptos_Directo_Base | 1377             | 71         | 222         |
| Leads_Google_Ventana    | 20504            | 3          | 19          |
| Conv_Google_Ventana     | 1117             | 2          | 10          |
| Leads_Facebook_Ventana  | 123201           | 9          | 76          |
| Conv_Facebook_Ventana   | 880              | 8          | 48          |
| Google_Spend_ARS        | 47387402.9       | 0.0        | 0.0         |
| Facebook_Spend_ARS      | 115200000.0      | 7100000.0  | 14500000.0  |
| CPL_Google              | 2311.13          | 0.0        | 0.0         |
| CPA_Google              | 42423.82         | 0.0        | 0.0         |
| CPL_Facebook            | 935.06           | 788888.89  | 190789.47   |
| CPA_Facebook            | 130909.09        | 887500.0   | 302083.33   |
| Rev_Atrib_Google        | 201110465.0      | 146800.0   | 2030750.0   |
| ROI_Google_%            | 324.4            | nan        | nan         |
| Rev_Atrib_Facebook      | 151078375.0      | 431000.0   | 10706650.0  |
| ROI_Facebook_%          | 31.14            | -93.93     | -26.16      |

## Checks de Consistencia

| Segmento       | Check                                         | Esperado   | Obtenido   | Diferencia   | OK     |
|:---------------|:----------------------------------------------|:-----------|:-----------|:-------------|:-------|
| Grado_Pregrado | Exacto+Fuzzy+SinMatch == Leads_Raw            | 398556     | 398556     | 0            | SI     |
| Grado_Pregrado | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 305249     | 305249     | 0            | SI     |
| Grado_Pregrado | Leads_Ventana_Dedup <= Personas_Dedup         | <= 305249  | 170085     | 0            | SI     |
| Grado_Pregrado | Conv_Ventana <= Leads_Ventana_Dedup           | <= 170085  | 6911       | 0            | SI     |
| Grado_Pregrado | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 4.06%      |              | SI     |
| Grado_Pregrado | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 6911    | 9525       | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch == Leads_Raw            | 44         | 44         | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 25         | 25         | 0            | SI     |
| Cursos         | Leads_Ventana_Dedup <= Personas_Dedup         | <= 25      | 21         | 0            | SI     |
| Cursos         | Conv_Ventana <= Leads_Ventana_Dedup           | <= 21      | 18         | 0            | SI     |
| Cursos         | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 85.71%     |              | ALERTA |
| Cursos         | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 18      | 94         | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch == Leads_Raw            | 178        | 178        | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 145        | 145        | 0            | SI     |
| Posgrados      | Leads_Ventana_Dedup <= Personas_Dedup         | <= 145     | 123        | 0            | SI     |
| Posgrados      | Conv_Ventana <= Leads_Ventana_Dedup           | <= 123     | 84         | 0            | SI     |
| Posgrados      | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 68.29%     |              | ALERTA |
| Posgrados      | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 84      | 325        | 0            | SI     |

## Alertas

| Segmento   | Indicador   | Valor   | Alerta                               |
|:-----------|:------------|:--------|:-------------------------------------|
| Cursos     | Tasa_Conv_% | 85.71%  | Tasa > 30% — revisar ventana cohorte |
| Posgrados  | Tasa_Conv_% | 68.29%  | Tasa > 30% — revisar ventana cohorte |

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `Auditoria_Indicadores.xlsx` | Excel con 5 hojas (KPIs, canales, checks, alertas) |
| `Auditoria_Indicadores.pdf` | Informe visual con KPIs y checks |
| `Auditoria_Indicadores.md` | Este archivo |
