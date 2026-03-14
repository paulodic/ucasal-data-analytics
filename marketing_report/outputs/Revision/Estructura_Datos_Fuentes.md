# Diccionario de Datos: Fuentes de Información Marketing

Este documento detalla la estructura original de los datos de origen utilizados para el análisis de conversiones, tiempos de resolución y marketing. Los datos se dividen típicamente en dos grupos: **Consultas (Leads)** e **Inscriptos (Transaccional)**.

## 1. Base de Consultas (Ej. Leads de Salesforce)
Cada registro representa una consulta individual o un Lead capturado.

| Columna Original | Descripción / Propósito |
|-----------------|------------------------|
| `Id. candidato/contacto` | Identificador único del lead en el CRM (Salesforce). |
| `Consulta: ID Consulta` | Identificador específico del ticket o interacción de la consulta. |
| `Correo` | Dirección de correo electrónico proporcionada por el prospecto. Usado como clave de cruce. |
| `Nombre` | Nombre y Apellido del candidato. |
| `DNI` | Documento Nacional de Identidad del prospecto. **Clave principal de cruce**. |
| `Telefono` | Número de teléfono de contacto (sujeto a limpieza de prefijos). |
| `Tipo de Carrera` / `Modo` | Familia académica de interés y modalidad (Presencial, Online, etc.). |
| `Código Carrera` / `Carrera` | Identificadores de la carrera de interés del candidato. |
| `CódigoSede` / `Sede Nombre` | Sede física de interés (si aplica). |
| `FuenteLead` | **Clave principal de Marketing:** Código que indica el ecosistema o formulario de origen (ej. 18 = Facebook Lead Ads, 907 = Chatbot, 3 = Web Orgánico). |
| `UtmSource`, `UtmCampaign`, `UtmMedium`, `UtmTerm`, `UtmContent` | **Parámetros Tracking:** Etiquetas UTM recolectadas por la URL de pauta, dictamina la fuente exacta de la campaña publicitaria pagada. |
| `ColaNombre` / `PrimeraCola` | Equipo o segmento de atención pre-asignado. |
| `Estado` | Estado de resolución o maduración del lead en el sistema CRM. |
| `Consulta: Fecha de creación` | Fecha cronológica de captura/creación del lead. Útil para medir tiempos de cierre y *Journey*. |
| `Consulta: Nombre del propietario` | Agente o Asesor comercial responsable del caso. |

## 2. Base de Inscriptos (Ej. Sistema Académico / Pagos)
Cada registro representa una transacción de inscripción concretada.

| Columna Original | Descripción / Propósito |
|-----------------|------------------------|
| `Cod. Lugar` / `Lugar` | Sede o campus corporativo donde se registra la inscripción matriculada. |
| `Cod. Sector` / `Sector` | Unidad de negocio a la que pertenece el inscripto. |
| `Cod. Carrera` / `Carrera` / `Cod. Modo` / `Modo` | El programa académico y modalidad efectivamente cursada por el estudiante. |
| `Tipcar` | Tipología particular del registro (Sujeto a verificación interna). |
| `Tipo de DNI` / `DNI` | Documento del inscripto. **Clave principal de cruce exacto y principal elemento de deduplicación**. |
| `Apellido y Nombre` | Nombre utilizado por el inscripto en el formulario de pago. Usado por el algoritmo automático de coincidencias similares (Fuzzy Match). |
| `Email` / `Celular` / `Telefono` | Datos de contacto transaccionales al pagar. Claves secundarias de cruce si el DNI falla. |
| `Cod. Operador` / `Cod. Empresa` / `Cod. Vendedor` | Metadatos de la operación de ventas en el ERP interno. |
| `Fecha Pago` / `Fecha Aplicación` | Fecha de concreción económica. Fundamental para graficar "Picos y Valles" de mercado y medir cuántos días tomó la decisión. |
| `Haber` / `Conceptos` / `Reci. - Trans.` | Descriptores y números de remito de la operación financiera (Montos, cuotas o inscripción inicial). |
| `Tipo Origen` | Etiqueta contable transaccional del lugar de pago. |
