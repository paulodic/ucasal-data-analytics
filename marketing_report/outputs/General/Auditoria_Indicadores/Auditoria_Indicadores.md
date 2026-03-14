# Auditoria de Indicadores - UCASAL Marketing
**Generado:** 2026-03-14 20:39:54  
**Script:** `22_auditoria_indicadores.py`  
**Checks:** 16 OK | 2 con problemas  
**Alertas:** 2  

## KPIs por Segmento

| Metrica                 | Grado_Pregrado   | Cursos     | Posgrados   |
|:------------------------|:-----------------|:-----------|:------------|
| Leads_Raw               | 398442           | 41         | 139         |
| Exacto_Raw              | 13009            | 36         | 91          |
| Fuzzy_Raw               | 153              | 5          | 48          |
| Sin_Match_Raw           | 385280           | 0          | 0           |
| Check_Raw_Sum           | 398442           | 41         | 139         |
| Personas_Dedup          | 305232           | 22         | 111         |
| Exacto_Dedup            | 7937             | 17         | 63          |
| Exacto_DNI              | 5333             | 9          | 23          |
| Exacto_Email            | 2150             | 4          | 18          |
| Exacto_Telefono         | 237              | 2          | 15          |
| Exacto_Celular          | 217              | 2          | 7           |
| Fuzzy_Dedup             | 153              | 5          | 48          |
| Sin_Match_Dedup         | 297142           | 0          | 0           |
| Check_Dedup_Sum         | 305232           | 22         | 111         |
| Ventana_Inicio          | 2025-09-01       | Todos      | Todos       |
| Ventana_Fin             | 2026-02-17       | 2026-02-14 | 2026-02-14  |
| Leads_Ventana_Dedup     | 170073           | 19         | 104         |
| Conv_Ventana_Exacto     | 6895             | 15         | 62          |
| Tasa_Conv_%             | 4.0541           | 78.9474    | 59.6154     |
| Inscriptos_Base         | 9525             | 94         | 325         |
| Inscriptos_Exacto_Base  | 7984             | 18         | 56          |
| Inscriptos_Directo_Base | 1388             | 71         | 221         |
| Leads_Google_Ventana    | 20478            | 3          | 18          |
| Conv_Google_Ventana     | 1109             | 2          | 9           |
| Leads_Facebook_Ventana  | 123195           | 7          | 60          |
| Conv_Facebook_Ventana   | 854              | 5          | 30          |
| Google_Spend_ARS        | 47387402.9       | 0.0        | 0.0         |
| Facebook_Spend_ARS      | 115200000.0      | 7100000.0  | 14500000.0  |
| CPL_Google              | 2314.06          | 0.0        | 0.0         |
| CPA_Google              | 42729.85         | 0.0        | 0.0         |
| CPL_Facebook            | 935.1            | 1014285.71 | 241666.67   |
| CPA_Facebook            | 134894.61        | 1420000.0  | 483333.33   |
| Rev_Atrib_Google        | 199506405.0      | 146800.0   | 1723850.0   |
| ROI_Google_%            | 321.01           | nan        | nan         |
| Rev_Atrib_Facebook      | 145620560.0      | 261500.0   | 5501950.0   |
| ROI_Facebook_%          | 26.41            | -96.32     | -62.06      |

## Checks de Consistencia

| Segmento       | Check                                         | Esperado   | Obtenido   | Diferencia   | OK     |
|:---------------|:----------------------------------------------|:-----------|:-----------|:-------------|:-------|
| Grado_Pregrado | Exacto+Fuzzy+SinMatch == Leads_Raw            | 398442     | 398442     | 0            | SI     |
| Grado_Pregrado | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 305232     | 305232     | 0            | SI     |
| Grado_Pregrado | Leads_Ventana_Dedup <= Personas_Dedup         | <= 305232  | 170073     | 0            | SI     |
| Grado_Pregrado | Conv_Ventana <= Leads_Ventana_Dedup           | <= 170073  | 6895       | 0            | SI     |
| Grado_Pregrado | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 4.05%      |              | SI     |
| Grado_Pregrado | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 6895    | 9525       | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch == Leads_Raw            | 41         | 41         | 0            | SI     |
| Cursos         | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 22         | 22         | 0            | SI     |
| Cursos         | Leads_Ventana_Dedup <= Personas_Dedup         | <= 22      | 19         | 0            | SI     |
| Cursos         | Conv_Ventana <= Leads_Ventana_Dedup           | <= 19      | 15         | 0            | SI     |
| Cursos         | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 78.95%     |              | ALERTA |
| Cursos         | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 15      | 94         | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch == Leads_Raw            | 139        | 139        | 0            | SI     |
| Posgrados      | Exacto+Fuzzy+SinMatch_dedup == Personas_Dedup | 111        | 111        | 0            | SI     |
| Posgrados      | Leads_Ventana_Dedup <= Personas_Dedup         | <= 111     | 104        | 0            | SI     |
| Posgrados      | Conv_Ventana <= Leads_Ventana_Dedup           | <= 104     | 62         | 0            | SI     |
| Posgrados      | Tasa_Conv en rango [0%, 30%]                  | 0%-30%     | 59.62%     |              | ALERTA |
| Posgrados      | Inscriptos_Base >= Conv_Ventana_Exacto        | >= 62      | 325        | 0            | SI     |

## Alertas

| Segmento   | Indicador   | Valor   | Alerta                               |
|:-----------|:------------|:--------|:-------------------------------------|
| Cursos     | Tasa_Conv_% | 78.95%  | Tasa > 30% — revisar ventana cohorte |
| Posgrados  | Tasa_Conv_% | 59.62%  | Tasa > 30% — revisar ventana cohorte |

## Archivos de Salida
| Archivo | Descripcion |
|---|---|
| `Auditoria_Indicadores.xlsx` | Excel con 5 hojas (KPIs, canales, checks, alertas) |
| `Auditoria_Indicadores.pdf` | Informe visual con KPIs y checks |
| `Auditoria_Indicadores.md` | Este archivo |
