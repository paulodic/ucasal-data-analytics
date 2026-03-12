# Auditoria de Indicadores - UCASAL Marketing
**Generado:** 2026-03-12 10:36:47  
**Script:** `22_auditoria_indicadores.py`  
**Checks:** 16 OK | 2 con problemas  
**Alertas:** 2  

## KPIs por Segmento

| Metrica                 | Grado_Pregrado   | Cursos     | Posgrados   |
|:------------------------|:-----------------|:-----------|:------------|
| Leads_Raw               | 388042           | 1069       | 180         |
| Exacto_Raw              | 12158            | 1052       | 133         |
| Fuzzy_Raw               | 140              | 17         | 47          |
| Sin_Match_Raw           | 375744           | 0          | 0           |
| Check_Raw_Sum           | 388042           | 1069       | 180         |
| Personas_Dedup          | 298855           | 683        | 147         |
| Exacto_Dedup            | 7354             | 666        | 100         |
| Fuzzy_Dedup             | 140              | 17         | 47          |
| Sin_Match_Dedup         | 291361           | 0          | 0           |
| Check_Dedup_Sum         | 298855           | 683        | 147         |
| Ventana_Inicio          | 2025-09-01       | Todos      | Todos       |
| Ventana_Fin             | 2026-02-17       | 2026-02-14 | 2026-02-14  |
| Leads_Ventana_Dedup     | 165515           | 671        | 125         |
| Conv_Ventana_Exacto     | 6347             | 657        | 84          |
| Tasa_Conv_%             | 3.8347           | 97.9136    | 67.2        |
| Inscriptos_Base         | 8755             | 864        | 325         |
| Inscriptos_Exacto_Base  | 7364             | 648        | 58          |
| Inscriptos_Directo_Base | 1251             | 199        | 220         |
| Leads_Google_Ventana    | 20566            | 36         | 19          |
| Conv_Google_Ventana     | 1097             | 33         | 10          |
| Leads_Facebook_Ventana  | 119385           | 137        | 78          |
| Conv_Facebook_Ventana   | 761              | 130        | 48          |
| Google_Spend_ARS        | 47387402.9       | 0.0        | 0.0         |
| Facebook_Spend_ARS      | 115200000.0      | 7100000.0  | 14500000.0  |
| CPL_Google              | 2304.16          | 0.0        | 0.0         |
| CPA_Google              | 43197.27         | 0.0        | 0.0         |
| CPL_Facebook            | 964.95           | 51824.82   | 185897.44   |
| CPA_Facebook            | 151379.76        | 54615.38   | 302083.33   |
| Rev_Atrib_Google        | 197341490.0      | 5281500.0  | 2030750.0   |
| ROI_Google_%            | 316.44           | nan        | nan         |
| Rev_Atrib_Facebook      | 131467610.0      | 20401800.0 | 10706650.0  |
| ROI_Facebook_%          | 14.12            | 187.35     | -26.16      |

## Checks de Consistencia

| Segmento       | Check                                         | Esperado   | Obtenido   | Diferencia   | OK     |
|:---------------|:----------------------------------------------|:-----------|:-----------|:-------------|:-------|
| Grado_Pregrado | Exacto+Fuzzy+SinMatch == Leads_Raw            | 388042     | 388042     | 0            | SI     |
| Grado_Pregrado | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 298855     | 298855     | 0            | SI     |
| Grado_Pregrado | Leads_Ventana_Dedup <= Personas_Dedup         | <= 298855  | 165515     | 0            | SI     |
| Grado_Pregrado | Conv_Ventana <= Leads_Ventana_Dedup           | <= 165515  | 6347       | 0            | SI     |
| Grado_Pregrado | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 3.83%      |              | SI     |
| Grado_Pregrado | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 6347    | 8755       | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch == Leads_Raw            | 1069       | 1069       | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 683        | 683        | 0            | SI     |
| Cursos         | Leads_Ventana_Dedup <= Personas_Dedup         | <= 683     | 671        | 0            | SI     |
| Cursos         | Conv_Ventana <= Leads_Ventana_Dedup           | <= 671     | 657        | 0            | SI     |
| Cursos         | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 97.91%     |              | ALERTA |
| Cursos         | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 657     | 864        | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch == Leads_Raw            | 180        | 180        | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 147        | 147        | 0            | SI     |
| Posgrados      | Leads_Ventana_Dedup <= Personas_Dedup         | <= 147     | 125        | 0            | SI     |
| Posgrados      | Conv_Ventana <= Leads_Ventana_Dedup           | <= 125     | 84         | 0            | SI     |
| Posgrados      | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 67.20%     |              | ALERTA |
| Posgrados      | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 84      | 325        | 0            | SI     |

## Alertas

| Segmento   | Indicador   | Valor   | Alerta                               |
|:-----------|:------------|:--------|:-------------------------------------|
| Cursos     | Tasa_Conv_% | 97.91%  | Tasa > 30% — revisar ventana cohorte |
| Posgrados  | Tasa_Conv_% | 67.20%  | Tasa > 30% — revisar ventana cohorte |

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `Auditoria_Indicadores.xlsx` | Excel con 5 hojas (KPIs, canales, checks, alertas) |
| `Auditoria_Indicadores.pdf` | Informe visual con KPIs y checks |
| `Auditoria_Indicadores.md` | Este archivo |
