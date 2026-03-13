# Informe Analitico de Marketing - Completo

**Aviso: Este documento es un BORRADOR. Todos los datos contenidos aqui estan pendientes de verificacion.**

*(Datos actualizados al 17 de febrero de 2026)*

## Nota Metodologica
- **Modelo de atribucion principal:** Deduplicado por persona (DNI). Cada inscripto se cuenta una vez.
- **Tipos de match:** Exacto por DNI, Email, Telefono y Celular (en ese orden de prioridad).
- **Modelo Any-Touch:** Disponible en el Informe Analitico (04). Un inscripto se cuenta en CADA canal por el que consulto (la suma supera 100%).
- **Ventana de conversion:** Grado_Pregrado: leads desde Sep 2025. Cursos/Posgrados: leads del año calendario.
- **Datos fuente:** Salesforce (leads) + Sistema academico (inscriptos).

## Resumen Ejecutivo
*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2025, coincidiendo con la inscripcion a la primera cohorte. En mayo se abren a la segunda.)*

- Total Registros de Leads (Historico): 398,401
- Personas Unicas (Muestra para conversion): 169,894
- Tasa de Conversion Global (deduplicada): 4.07%
- Inscriptos Atribuidos (exacto): 7,993
  - Match por DNI: 5,423
  - Match por Email: 2,151
  - Match por Telefono: 227
  - Match por Celular: 192
- Inscriptos sin trazabilidad (sin lead previo): 1,377
- Bot - Leads captados (historico): 10,240
- Bot - Inscriptos confirmados (muestra): 502
- Bot - Tasa de conversion: 6.55%
- Leads con UTM: 69,035 (17.3%)
- Leads sin UTM: 329,366 (82.7%)
- Registros Fuzzy Complementarios: 155

## Atribucion por Campana
- Inscriptos campana actual (Ingreso 2026): 10,448
- Inscriptos campana anterior (match historico): 2,722
- % inscriptos con lead de campana anterior: 39.4%

## Conclusiones y Recomendaciones
### 1. Atribucion de Marketing
Se logro trazar el origen exacto de 7,993 inscriptos. Metodos de match: DNI (5,423), Email (2,151), Telefono (227), Celular (192). La tasa de conversion real (deduplicada por persona) es de 4.07%.

### 2. Rendimiento del Chatbot (907)
El Bot presenta una tasa de conversion de 6.55%, superior al promedio general de 4.07%. Capto 10,240 leads de los cuales 502 se inscribieron.

### 3. Campanas Digitales (UTM)
69,035 leads (17.3%) tienen informacion de UTM, lo que permite rastrear las campanas digitales. El 82.7% restante no tiene UTM asociado.

### 4. Calidad de Datos
155 registros requirieron cruce fuzzy (similitud de nombres) y se presentan en un informe complementario aparte para verificacion humana.

### 5. Recomendaciones
- Implementar UTMs en todas las campanas para mejorar la trazabilidad.
- Evaluar estrategias de remarketing dado el tiempo de maduracion de los leads.
