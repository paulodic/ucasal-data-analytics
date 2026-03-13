# Informe Analitico de Marketing - Completo

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.**

*(Datos actualizados al 14 de febrero de 2026)*

## Nota Metodologica
- **Modelo de atribucion principal:** Deduplicado por persona (DNI). Cada inscripto se cuenta una vez.
- **Tipos de match:** Exacto por DNI, Email, Telefono y Celular (en ese orden de prioridad).
- **Modelo Any-Touch:** Disponible en el Informe Analitico (04). Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%).
- **Ventana de conversion:** Grado_Pregrado: leads desde Sep 2025. Cursos/Posgrados: leads del año calendario.
- **Datos fuente:** Salesforce (leads) + Sistema academico (inscriptos).

## Resumen Ejecutivo
- Total Registros de Leads (Historico): 40
- Personas Unicas (Muestra para conversion): 18
- Tasa de Conversion Global (deduplicada): 100.00%
- Inscriptos Atribuidos (exacto): 19
  - Match por DNI: 10
  - Match por Email: 4
  - Match por Telefono: 3
  - Match por Celular: 2
- Inscriptos sin trazabilidad (sin lead previo): 71
- Bot - Leads captados (historico): 1
- Bot - Inscriptos confirmados (muestra): 0
- Bot - Tasa de conversion: 0.00%
- Leads con UTM: 5 (12.5%)
- Leads sin UTM: 35 (87.5%)
- Registros Fuzzy Complementarios: 4

## Atribucion por Campana
- Inscriptos campana actual (2026): 7
- Inscriptos campana anterior (match historico): 33
- % inscriptos con lead de campana anterior: 183.3%

## Conclusiones y Recomendaciones
### 1. Atribucion de Marketing
Se logro trazar el origen exacto de 19 inscriptos. Metodos de match: DNI (10), Email (4), Telefono (3), Celular (2). La tasa de conversion real (deduplicada por persona) es de 100.00%.

### 2. Rendimiento del Chatbot (907)
El Bot presenta una tasa de conversion de 0.00%, inferior al promedio general de 100.00%. Capto 1 leads de los cuales 0 se inscribieron.

### 3. Campanas Digitales (UTM)
5 leads (12.5%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El 87.5% restante no tiene UTM asociado.

### 4. Calidad de Datos
4 registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.

### 5. Recomendaciones
- Implementar UTMs en todas las campanas para mejorar la trazabilidad.
- Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.
