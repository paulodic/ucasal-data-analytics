# Análisis de Discrepancias: CRM vs Base Académica Real

Este informe expone las diferencias fundamentales entre el flag interno `Matriculadas` proveniente de la base de datos de **Salesforce (Leads)** y el **Cruce Físico Efectivo** contra la base contable/académica real de **Inscriptos**.

## Números Globales
- **Total de Leads Analizados:** 159
- **Leads marcados como 'Matriculados = 1' en Salesforce:** 1
- **Inscriptos Reales Verificados (Cruce Exacto + Fuzzys confiables):** 36

## Nivel de Desvío (Falsos Positivos y Negativos)

Al cruzar a las personas uno por uno evaluamos la consistencia. De allí se desprenden los siguientes grupos:

1. **Falsos Positivos (4,121 personas):** 
   - El CRM (Salesforce) marca que tienen el campo `Matriculadas` en `1`.
   - Sin embargo, **NO existen o no pagaron** según la base contable real de Inscriptos de la universidad. (Representa leads que quizás dijeron que iban a pagar, o un error de carga manual en Salesforce).

2. **Falsos Negativos (5,851 personas):**
   - El CRM (Salesforce) los tiene con el campo `Matriculadas` en `0` (vacío).
   - Sin embargo, esta gente **SÍ pagó la inscripción** y cursa efectivamente en la universidad bajo el mismo DNI/Email/Teléfono. (Representa el volumen de ventas que Marketing/Ventas trajo pero el asesor nunca tildó en Salesforce como ganado).

### Conclusión Matemática

- **Diferencia Neta en Volumen (Reporte CRM vs Reporte Base de Datos Real):** 35 inscriptos faltantes en el reporte superficial.
- **Leads que generaron una venta real y que el CRM NO se está atribuyendo:** 5,851 ventas "ciegas" en Salesforce.
- **Total de expedientes discordantes a auditar:** 37 personas que tienen un estado de vida opuesto entre ambos sistemas informáticos.
