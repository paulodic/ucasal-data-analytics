# Análisis de Leads Originados por Bot/Chatbot

**Datos actualizados al 17 de febrero de 2026**

### Nota Metodologica
- **Modelo de atribucion:** Deduplicado por persona (DNI). Cada canal se evalua por separado.
- **Match Exacto:** DNI (4,526), Email (2,018), Teléfono (200), Celular (196). Total: 6,940.
- **Modelo Any-Touch ESTANDAR (este informe):** Un inscripto se cuenta en CADA canal por el que consulto (Bot, Google, Meta, Otros). La suma supera 100%. Incluye todas las consultas sin filtro de fecha vs pago.
- **Modelo CAUSAL (informe separado):** Solo cuenta consultas cuya fecha <= fecha de pago. Excluye consultas post-pago (soporte, seguimiento). Ver Presupuesto_ROI_Causal.
- **Tabla 1 (Volumen):** Modelo directo por canal - cada lead se clasifica en UN canal segun su FuenteLead/UTM.
- **Tabla 3 (Match):** Desglose algoritmico del tipo de cruce Lead-Inscripto.

*(Nota Cohortes: Las tasas de conversion se calculan asumiendo como denominador los leads ingresados a partir de Septiembre 2025, coincidiendo con la inscripcion a la primera cohorte.)*

## 1. Volumen y Proporción

*Datos filtrados: leads desde Sep 2025 (Cohorte Ingreso 2026)*

| Métrica | Bot/Chatbot | Meta Ads | Google Ads | Otros Canales | Total |
|---------|------------|----------|------------|---------------|-------|
| Leads (Cohorte) | 10,244 | 159,423 | 27,981 | 30,694 | 228,342 |
| Inscriptos Confirmados | 550 | 1,087 | 1,403 | 4,929 | 6,940 |
| Tasa de Conversión | 5.37% | 0.68% | 5.01% | 16.06% | 3.04% |

## 2. Tasa de Conversión Comparativa (Bot vs Plataformas Pagas)

| Canal | Leads (Muestra) | Inscriptos | Tasa Conversión | vs Promedio |
|-------|----------------:|-----------:|----------------:|------------:|
| Bot/Chatbot | 10,244 | 550 | 5.37% | +2.33 pp |
| Meta Ads | 159,423 | 1,087 | 0.68% | -2.36 pp |
| Google Ads | 27,981 | 1,403 | 5.01% | +1.97 pp |
| Otros Canales | 30,694 | 4,929 | 16.06% | +13.02 pp |
| **Promedio General** | **228,342** | **6,940** | **3.04%** | — |

## 3. Metodología de Atribución (Tipo de Match)

Desglose algorítmico de cómo se vincularon los leads del bot con inscripciones concretadas:

| Metodología de Cruce (Lead -> Inscripto)   |   Inscriptos Confirmados |    % |
|:-------------------------------------------|-------------------------:|-----:|
| Exacto (DNI)                               |                      390 | 54.6 |
| Exacto (Email)                             |                      238 | 33.3 |
| Exacto (Teléfono)                          |                       46 |  6.4 |
| Exacto (Celular)                           |                       40 |  5.6 |

## 4. Top 10 Carreras Inscriptas vía Bot

| Carrera                                           |   Inscriptos (Muestra) |   Consultas (Muestra) |   Tasa_% |
|:--------------------------------------------------|-----------------------:|----------------------:|---------:|
| ABOGACÍA                                          |                    108 |                  1840 |     5.87 |
| ARQUITECTURA                                      |                     37 |                   127 |    29.13 |
| CONTADOR PÚBLICO                                  |                     36 |                   364 |     9.89 |
| CIENCIAS VETERINARIAS                             |                     35 |                   175 |    20    |
| LICENCIATURA EN KINESIOLOGÍA Y FISIOTERAPIA       |                     34 |                   205 |    16.59 |
| LICENCIATURA EN PSICOLOGÍA                        |                     29 |                   363 |     7.99 |
| ESCRIBANÍA                                        |                     24 |                   305 |     7.87 |
| LICENCIATURA EN HIGIENE Y SEGURIDAD EN EL TRABAJO |                     23 |                   392 |     5.87 |
| INGENIERÍA EN INFORMÁTICA                         |                     22 |                   113 |    19.47 |
| LICENCIATURA EN CRIMINALÍSTICA                    |                     19 |                   186 |    10.22 |

## 4. Distribución por Sede

| Sede                                        |   Leads |
|:--------------------------------------------|--------:|
| SALTA - CASTAÑARES PRESENCIAL               |    4641 |
| HOME                                        |    3340 |
| SALTA - DISTANCIA Modo 7                    |    1815 |
| DELEGACION S S DE JUJUY - JUJUY             |     144 |
| DELEGACIÓN SAN MIGUEL - BUENOS AIRES Modo 7 |     117 |
| SALTA - ANEXO CENTRO                        |      56 |
| BUENOS AIRES - CABA                         |      48 |
| SANTIAGO DEL ESTERO - SANTIAGO DEL ESTERO   |       7 |
| CAFAYATE - SALTA                            |       5 |
| TARTAGAL - SALTA                            |       4 |

## 5. Canales de Origen (ColaNombre)

| Cola           |   Leads |
|:---------------|--------:|
| Contact_Center |    5256 |
| Sede_33        |       2 |

## 6. Estado de los Leads de Bot

| Estado           |   Cantidad |    % |
|:-----------------|-----------:|-----:|
| Abierto          |       4916 | 48   |
| No interesado    |       2849 | 27.8 |
| Interesado       |       2051 | 20   |
| Solicitud creada |        427 |  4.2 |
| Pre Inscripción  |          1 |  0   |

