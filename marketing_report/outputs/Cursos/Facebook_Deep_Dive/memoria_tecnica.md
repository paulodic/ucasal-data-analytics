# Memoria Técnica: Cálculos de Facebook/Meta Ads Deep Dive

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión:** Se capturan a todos los Leads en los cuales el originador de fuente (`FuenteLead_Num`) coincida de manera estricta con el Id `18` (Facebook Lead Ads en el sistema local). Simultáneamente, se engloban aquellos prospectos con identificadores UTM pre-establecidos (`fb`, `facebook`, `ig`, `instagram`, `meta`) alojados dentro del rastreador en crudo `UtmSource`.
- **Match Exacto (Conversión):** En sincronía con el pipeline general, una conversión a 'Inscripto' solo es atribuida de existir el identificador de cruce numérico exacto proveniente del módulo madre (`02_cruce`).
- **Filtrado Dimensional Visual:** Por requerimientos funcionales y estéticos comerciales, el cruce y la presentación de volumen visual de Campañas suprime micro-campañas basura (consideradas aquellas de recolección de leads inferiores a 5). No obstante, para el cálculo base principal el acumulado toma el 100% de los datos orgánicos.
