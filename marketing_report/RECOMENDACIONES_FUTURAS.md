# Recomendaciones Técnicas — Pendientes para Futuras Iteraciones

## 1. Git — Manejo de Archivos Grandes

El repositorio actual incluye archivos CSV y Excel que superan el límite recomendado de 50 MB de GitHub:

- `outputs/Data_Base/reporte_marketing_leads_completos.csv` (~73 MB)
- `outputs/Data_Base/reporte_marketing_leads_completos.xlsx` (~63 MB)
- `outputs/Data_Base/Grado_Pregrado/reporte_marketing_leads_completos.csv` (~70 MB)

### Acciones recomendadas

#### A) Agregar `.gitignore` para excluir outputs de datos regenerables

Los archivos de salida (`outputs/`) se pueden regenerar corriendo el pipeline, por lo que no necesitan estar en el repositorio. Agregar al `.gitignore`:

```gitignore
# Outputs de datos (regenerables con el pipeline)
marketing_report/outputs/Data_Base/
marketing_report/outputs/*/reporte_marketing_*.csv
marketing_report/outputs/*/reporte_marketing_*.xlsx

# Datos crudos sensibles
marketing_report/data/
```

#### B) Usar Git LFS para archivos grandes que sí deben versionarse

Si se decide mantener algún archivo grande en el repo (ej. un Excel final de entrega):

```bash
git lfs install
git lfs track "*.xlsx"
git lfs track "*.csv"
git add .gitattributes
```

---

## 2. Pipeline — Optimización del match Fuzzy Email (02_cruce_datos.py)

La fase de fuzzy email usa un loop O(n²) anidado que tarda varias horas con 200K+ leads.

### Acción recomendada

Reemplazar el loop por un índice de longitud + Levenshtein vectorizado, o agrupar emails por longitud ± 2 caracteres antes de comparar (similar a como ya funciona `08_fuzzy_correos.py`). Estimación de mejora: de horas a minutos.

---

## 3. Cohortes — Presupuesto por Cohorte

Cada cohorte tiene un presupuesto asignado específico. Cuando se incorporen los datos de **Aid Paid** (inversión publicitaria), se deberá:

- Vincular el gasto por período (sept–dic para 1ra cohorte, may–ago para 2da)
- Calcular CPL (Costo por Lead) y CPA (Costo por Adquisición/Inscripto) por cohorte
- Actualizar `09_utm_conversion.py` y `13_facebook_deep_dive.py` para incluir métricas de ROI

---

## 4. Dominios de Email — Auditoría Periódica

El script `15_dominios_invalidos.py` detecta errores típicos (`gmail.con`, `gmail.com.ar`, etc.). Se recomienda:

- Ejecutarlo mensualmente al ingresar nuevos datos del CRM
- Exportar los casos al equipo de admisiones para corrección en Salesforce

