# Memoria Técnica: Cálculos de Bot/Chatbot

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión:** A nivel de base de datos (`reporte_marketing_leads_completos`), el origen Bot es aislado estrictamente rastreando la identificación codificada universal `FuenteLead_Num` que sea matemáticamente igual a `907`.
- **Match Exacto (Conversión):** Durante el cruce de Leads versus Inscriptos (ventas concretadas formales), solo se contabiliza un retorno sobre la inversión efectivo si el identificador secundario de `Match_Tipo` dictamina `"Exacto"`.
- **Proporción y Tasa de Conversión:** La proporción global se calcula versus todo el tráfico histórico registrado, mientras que la Tasa de Conversión aísla la masa de originados por IA (`907`) y la divide por aquellos Leads que lograron inscribir exitosamente.
