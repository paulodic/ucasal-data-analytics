# Informe Analitico de Marketing - Completo

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.**

*(Datos actualizados al 14 de febrero de 2026)*

## Nota Metodologica
- **Modelo de atribucion principal:** Deduplicado por persona (DNI). Cada inscripto se cuenta una vez.
- **Tipos de match:** Exacto por DNI, Email, Telefono y Celular (en ese orden de prioridad).
- **Modelo Any-Touch ESTANDAR (este informe):** Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%). Incluye todas las consultas sin filtro de fecha vs pago.
- **Modelo CAUSAL (informe separado):** Solo cuenta consultas cuya fecha <= fecha de pago. Excluye consultas post-pago. Ver Presupuesto_ROI_Causal.
- **Ventana de conversion:** Grado_Pregrado: leads desde Sep 2025. Cursos/Posgrados: leads del año calendario.
- **Datos fuente:** Salesforce (leads) + Sistema academico (inscriptos).

## Resumen Ejecutivo
- Total Consultas en Ventana de Conversion: 34
- Personas Unicas en Ventana de Conversion: 15
- Total Registros de Leads (Historico): 36
- Tasa de Conversion sobre Consultas: 44.12% (inscriptos / consultas)
- Tasa de Conversion sobre Personas: 100.00% (inscriptos / personas) **KPI principal**
- Inscriptos Atribuidos (exacto): 18
  - Match por DNI: 10
  - Match por Email: 4
  - Match por Telefono: 2
  - Match por Celular: 2
- Inscriptos sin trazabilidad (sin lead previo): 71
- Bot - Leads captados (historico): 1
- Bot - Inscriptos confirmados (muestra): 0
- Bot - Tasa de conversion: 0.00%
- Leads con UTM: 5 (13.9%)
- Leads sin UTM: 31 (86.1%)
- Registros Fuzzy Complementarios: 5

## Atribucion por Campana
- Inscriptos campana actual (2026): 5
- Inscriptos campana anterior (match historico): 31
- % inscriptos con lead de campana anterior: 206.7%

## Conclusiones y Recomendaciones
### 1. Atribucion de Marketing
Se logro trazar el origen exacto de 18 inscriptos. Metodos de match: DNI (10), Email (4), Telefono (2), Celular (2). La tasa de conversion real (deduplicada por persona) es de 100.00%.

### 2. Rendimiento del Chatbot (907)
El Bot presenta una tasa de conversion de 0.00%, inferior al promedio general de 100.00%. Capto 1 leads de los cuales 0 se inscribieron.

### 3. Campanas Digitales (UTM)
5 leads (13.9%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El 86.1% restante no tiene UTM asociado.

### 4. Calidad de Datos
5 registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.

### 5. Recomendaciones
- Implementar UTMs en todas las campanas para mejorar la trazabilidad.
- Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.
