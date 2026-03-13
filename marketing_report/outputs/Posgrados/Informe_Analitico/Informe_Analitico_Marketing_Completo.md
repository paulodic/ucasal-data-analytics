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
- Total Registros de Leads (Historico): 133
- Personas Unicas (Muestra para conversion): 84
- Tasa de Conversion Global (deduplicada): 100.00%
- Inscriptos Atribuidos (exacto): 58
  - Match por DNI: 24
  - Match por Email: 18
  - Match por Telefono: 9
  - Match por Celular: 7
- Inscriptos sin trazabilidad (sin lead previo): 222
- Bot - Leads captados (historico): 6
- Bot - Inscriptos confirmados (muestra): 4
- Bot - Tasa de conversion: 100.00%
- Leads con UTM: 15 (11.3%)
- Leads sin UTM: 118 (88.7%)
- Registros Fuzzy Complementarios: 45

## Atribucion por Campana
- Inscriptos campana actual (2026): 34
- Inscriptos campana anterior (match historico): 99
- % inscriptos con lead de campana anterior: 117.9%

## Conclusiones y Recomendaciones
### 1. Atribucion de Marketing
Se logro trazar el origen exacto de 58 inscriptos. Metodos de match: DNI (24), Email (18), Telefono (9), Celular (7). La tasa de conversion real (deduplicada por persona) es de 100.00%.

### 2. Rendimiento del Chatbot (907)
El Bot presenta una tasa de conversion de 100.00%, inferior al promedio general de 100.00%. Capto 6 leads de los cuales 4 se inscribieron.

### 3. Campanas Digitales (UTM)
15 leads (11.3%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El 88.7% restante no tiene UTM asociado.

### 4. Calidad de Datos
45 registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.

### 5. Recomendaciones
- Implementar UTMs en todas las campanas para mejorar la trazabilidad.
- Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.
