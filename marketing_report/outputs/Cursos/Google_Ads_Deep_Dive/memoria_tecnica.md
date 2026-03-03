# Memoria Técnica: Cálculos de Google Ads Deep Dive

**Métricas y Lógica Aplicada:**
- **Filtro de Inclusión:** Se aíslan todos los Leads cuyo campo `UtmSource` contenga la cadena `"google"` (case-insensitive).
- **Match Exacto (Conversión):** Se restringe la consideración de "Inscriptos" únicamente a aquellos leads donde el campo `Match_Tipo` dictamina una correlación "Exacta" validada por el CRM frente a la universidad. Las coincidencias difusas (Fuzzy) han sido expresamente retiradas del cálculo estadístico de atribución.
- **Limpieza y Deduplicación:** Como una misma persona pudo consultar en varias ocasiones mediante el mismo Ad, previo a generar la base contable se ejecuta una eliminación de duplicados absolutos empleando el documento de identidad (`DNI`) como clave primaria primaria (Primary Key), y el `Correo` como respaldo en caso de carecer de identificación estatal. Esto asegura que no se inflen artificialmente las interacciones del anuncio.
- **Tasa de Conversión (CR%):** Obtenida mediante la fórmula estricta `(Inscriptos Exactos / Volumen Físico de Personas Únicas de la campaña) * 100`.
