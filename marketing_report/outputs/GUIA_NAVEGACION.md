# 📁 Guía de Navegación de Reportes de Marketing

¡Bienvenido! Este directorio (`outputs/`) contiene todos los informes, gráficas y bases de datos generados automáticamente por el pipeline de análisis de leads e inscriptos. 

Para mantener el orden y facilitar la lectura, los archivos se agrupan en subcarpetas según su propósito. A continuación, se detalla qué encontrarás en cada una y cómo utilizar las planillas de control manual.

---

## 📂 Estructura de Carpetas

### 1. `Data_Base` (Bases de Datos Maestras)
**¿Qué es?** Es la **fuente de verdad**. Contiene los cruces de datos crudos ya procesados, limpiados y unificados.
**Archivos Clave:**
- `reporte_marketing_leads_completos.[csv/xlsx]`: La base de datos maestra con absolutamente todos los leads, indicando cuáles se inscribieron y cuáles no.
- `reporte_marketing_inscriptos_origenes.[csv/xlsx]`: Una base similar a la anterior, pero filtrada exclusivamente para ver los datos de los inscriptos.
- `reporte_journey_tiempos.xlsx`: Contiene los cálculos de tiempo y los pasos que le tomó a cada inscripto concretar su inscripción desde su primera consulta.
**👉 Uso Ideal:** Usar estos archivos para conectar a herramientas de Business Intelligence (PowerBI, Tableau) o para realizar análisis de datos ad-hoc más profundos.

### 2. `Informe_Analitico` (Reporte General Completo)
**¿Qué es?** El informe principal de marketing con la visión panorámica del rendimiento (conversión general, comportamiento del bot, Sankeys).
**Archivos Clave:**
- `Informe_Analitico_Marketing_Completo.[pdf/md]`: El reporte final listo para leer, presentar o enviar. Contiene resúmenes ejecutivos, gráficas y conclusiones.
- `Tablas_Informe_Analitico.xlsx`: Un libro de Excel que consolida todas las tablas de datos que se ven resumidas en el PDF (Top orígenes, performance de modalidades, etc.).
- **Imágenes Sueltas (`.png` / `.pdf`)**: Las gráficas Sankey individuales (flujos A, B, C, D, E) exportadas en alta calidad por si necesitas pegarlas en una presentación de PowerPoint.
- `reporte_complementario_fuzzy.xlsx`: *(Ver sección de Control Manual abajo).*

### 3. `Analisis_UTM` (Rendimiento por Campañas)
**¿Qué es?** Archivos enfocados estrictamente en el rendimiento del tráfico trackeado mediante parámetros UTM.
**Archivos Clave:**
- `Analisis_UTM_Conversion.[pdf/md]`: Reporte detallado de conversiones según `UtmSource`, `UtmMedium`, `UtmCampaign`, `UtmTerm`, y `UtmContent`.
- `analisis_utm_completo.xlsx`: Las tablas de datos puros que respaldan el informe anterior.

### 4. `Google_Ads_Deep_Dive` (Enfoque en Google Ads)
**¿Qué es?** Un análisis vertical y exclusivo para todo el tráfico atribuido a Google.
**Archivos Clave:**
- `Informe_Google_Ads_Deep_Dive.[pdf/md]`: Reporte de volumen y tasas de conversión segmentado por campañas e intenciones de búsqueda dentro de Google Ads.
- `reporte_especifico_googleads.xlsx`: Las tablas de datos respaldatorias de este informe.

### 5. `Facebook_Deep_Dive` (Enfoque en Facebook/Meta)
**¿Qué es?** Análisis exclusivo del tráfico proveniente de propiedades Meta (Facebook, Instagram). Incluye leads capturados por UTM de Meta **y** por `FuenteLead = 18` (Facebook Lead Ads).
**Archivos Clave:**
- `Informe_Facebook_Deep_Dive.[pdf/md]`: Reporte con distribución por red (FB vs IG), top campañas, y tasa de conversión.
- `reporte_especifico_facebook.xlsx`: Datos tabulares detallados.

### 6. `Bot_Deep_Dive` (Leads del Bot/Chatbot)
**¿Qué es?** Análisis exclusivo de leads generados por el Bot (identificados por `FuenteLead = 907`).
**Archivos Clave:**
- `Bot_Deep_Dive_Reporte.pdf`: Informe PDF horizontal con gráficos circulares, tasa de conversión Bot vs Otros, y top carreras.
- `Bot_Deep_Dive.md`: Versión Markdown del informe.
- `datos_bot_deep_dive.xlsx`: Datos detallados (carreras, sedes, estados de leads).

### 7. `Analisis_No_Matcheados` (Análisis de Leads que No Se Inscribieron)
**¿Qué es?** Estudio comparativo entre leads que matchearon (se inscribieron) y los que no.
**Archivos Clave:**
- `Analisis_No_Matcheados.[pdf/md]`: Informe PDF **horizontal** con pie chart de proporción, distribución de consultas (barras + circulares con %), tiempos de resolución con deciles, y tasa de inscripción por dominio de correo.
- `datos_analisis_no_matcheados.xlsx`: Datos respaldatorios de cada sección.

### 8. `Calidad_Datos` (Auditoría y Limpieza de Datos)
**¿Qué es?** Herramientas de control de calidad para identificar errores de datos y oportunidades de mejora.
**Archivos Clave:**
- `control_manual_correos.xlsx`: Planilla de control manual para correos fuzzy (ver sección abajo).
- `dominios_invalidos.[md/xlsx]`: Análisis de dominios de correo con errores de tipeo (ej: `gmail.con`, `gmail.com.ar`). Estima cuántos matches se recuperarían si se corrigiesen los typos.

### 9. `Otros_Reportes`
**¿Qué es?** Una carpeta de archivo para reportes históricos o secundarios.

---

## 🕵️‍♂️ Control Manual: Reportes de Coincidencias Fuzzy (Posibles Duplicados/Errores)

Dado que las bases de datos a veces tienen errores de tipeo de los usuarios (ej. un DNI mal escrito, un correo alternativo), el sistema hace búsquedas inteligentes ("Fuzzy Matches") para atrapar esos escapes. 

Los resultados de estas búsquedas requieren **aprobación humana** y se dividen en dos archivos:

### A. Reporte Fuzzy por Nombre y Apellido
📄 `Informe_Analitico/reporte_complementario_fuzzy.xlsx`

**¿Cómo usarlo?**
1. **Revisa las columnas comparativas**: Verás los datos del "Lead" original frente a los datos del "Inscripto" detectado.
2. Observa la columna **Score**: Este es un puntaje del 1 al 100 de qué tan parecidos son los nombres.
3. **Validación visual**: Comprueba humana y lógicamente si se trata de la misma persona.
4. **Acción**: Si **SÍ** son la misma persona, debes ir a tu sistema CRM y corregir el DNI o el Email del lead original para que coincidan. En la próxima corrida, hará match directo.

### B. Reporte Fuzzy de Correos Electrónicos (Errores de Tipeo)
📄 `Calidad_Datos/control_manual_correos.xlsx`

**¿Cómo usarlo?**
1. **Abre el archivo** y revisa las columnas. Verás los Leads e Inscriptos que **no cruzaron datos** pero cuyos correos varían en **exactamente 1 letra/símbolo** (ej. *juan@gmail.com* vs *juaan@gmail.com*).
2. **Usa la columna "Validado"**: Escribe **SI** o **NO** en esa celda para dejar constancia de que un ser humano ya revisó ese par.
3. **Acción**: Al igual que el proceso anterior, entra a tu CRM y arregla el teclado/error de tipeo del correo original.
4. **Nota Tecnológica**: El script guarda memoria. Si validas una fila, no te la volverá a sugerir en correas futuras, protegiendo tu trabajo manual.
