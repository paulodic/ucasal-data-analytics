# Memoria Técnica: Análisis de Conversión UTM

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión Global:** Cualquier Lead que registre un valor no nulo ni vacío en al menos una de las dimensiones de rastreo estandar (Source, Medium, Campaign, Term, Content). Se unifican todas en minúsculas para eliminar duplicidades lógicas (ej. 'Instagram' vs 'instagram').
- **Deduplicación:** Se aglutina a la persona por su Documento Nacional de Identidad (`DNI`) para medir "Personas Únicas", utilizando el Correo Electrónico como comodín secundario de clave primaria para aquellos leads capturados tempranamente sin DNI.
- **Tasa de Conversión Pura:** La fórmula ejecutada se remite a aislar de un clúster UTM las Personas Únicas, dividir dentro de ellas las conversiones de Match "Exacto" en Inscriptos Base General, y eliminar los Fuzzys para atribuir métricas fiables ajenas al ruido humano de facturación.
- **Any-Touch:** Un inscripto se cuenta en CADA canal por el que consultó. Para atribución multi-canal, referirse al Informe Analítico (04_reporte_final).
