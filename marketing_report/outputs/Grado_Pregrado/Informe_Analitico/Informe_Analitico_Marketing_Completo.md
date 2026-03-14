# Informe Analitico de Marketing - Completo

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.**

*(Datos actualizados al 17 de febrero de 2026)*

## Nota Metodologica
- **Modelo de atribucion principal:** Deduplicado por persona (DNI). Cada inscripto se cuenta una vez.
- **Tipos de match:** Exacto por DNI, Email, Telefono y Celular (en ese orden de prioridad).
- **Modelo Any-Touch ESTANDAR (este informe):** Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Incluye todas las consultas sin filtro de fecha vs pago.
- **Modelo CAUSAL (informe separado):** Solo cuenta consultas cuya fecha <= fecha de pago. Excluye consultas post-pago. Ver Presupuesto_ROI_Causal.
- **Ventana de conversion:** Grado_Pregrado: leads desde Sep 2025. Cursos/Posgrados: leads del año calendario.
- **Datos fuente:** Salesforce (leads) + Sistema academico (inscriptos).

## Resumen Ejecutivo
*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2025, coincidiendo con la inscripcion a la primera cohorte. En mayo se abren a la segunda.)*

- Total Consultas en Ventana de Conversion: 212,693
- Personas Unicas en Ventana de Conversion: 170,007
- Total Registros de Leads (Historico): 398,289
- Tasa de Conversion sobre Consultas: 3.24% (inscriptos / consultas)
- Tasa de Conversion sobre Personas: 4.06% (inscriptos / personas) **KPI principal**
- Inscriptos Atribuidos (exacto): 7,984
  - Match por DNI: 5,423
  - Match por Email: 2,151
  - Match por Telefono: 215
  - Match por Celular: 195
- Inscriptos sin trazabilidad (sin lead previo): 1,388
- Bot - Leads captados (historico): 10,240
- Bot - Inscriptos confirmados (muestra): 503
- Bot - Tasa de conversion: 6.47%
- Leads con UTM: 69,028 (17.3%)
- Leads sin UTM: 329,261 (82.7%)
- Registros Fuzzy Complementarios: 153

## Atribucion por Campana
- Inscriptos campana actual (Ingreso 2026): 10,295
- Inscriptos campana anterior (match historico): 2,714
- % inscriptos con lead de campana anterior: 39.4%

## Conclusiones y Recomendaciones
### 1. Atribucion de Marketing
Se logro trazar el origen exacto de 7,984 inscriptos. Metodos de match: DNI (5,423), Email (2,151), Telefono (215), Celular (195). La tasa de conversion real (deduplicada por persona) es de 4.06%.

### 2. Rendimiento del Chatbot (907)
El Bot presenta una tasa de conversion de 6.47%, superior al promedio general de 4.06%. Capto 10,240 leads de los cuales 503 se inscribieron.

### 3. Campanas Digitales (UTM)
69,028 leads (17.3%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El 82.7% restante no tiene UTM asociado.

### 4. Calidad de Datos
153 registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.

### 5. Recomendaciones
- Implementar UTMs en todas las campanas para mejorar la trazabilidad.
- Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.
