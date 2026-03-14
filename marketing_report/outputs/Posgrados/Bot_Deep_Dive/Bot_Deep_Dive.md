# Análisis de Leads Originados por Bot/Chatbot

**Datos actualizados al 14 de febrero de 2026**

### Nota Metodologica
- **Modelo de atribucion:** Deduplicado por persona (DNI). Cada canal se evalua por separado.
- **Match Exacto:** DNI (23), Email (18), Teléfono (15), Celular (7). Total: 63.
- **Modelo Any-Touch ESTANDAR (este informe):** Un inscripto se cuenta en CADA canal por el que consulto (Bot, Google, Meta, Otros). La suma supera 100%. Incluye todas las consultas sin filtro de fecha vs pago.
- **Modelo CAUSAL (informe separado):** Solo cuenta consultas cuya fecha <= fecha de pago. Excluye consultas post-pago (soporte, seguimiento). Ver Presupuesto_ROI_Causal.
- **Tabla 1 (Volumen):** Modelo directo por canal - cada lead se clasifica en UN canal segun su FuenteLead/UTM.
- **Tabla 3 (Match):** Desglose algoritmico del tipo de cruce Lead-Inscripto.

## 1. Volumen y Proporción

*Datos filtrados: leads año 2026*

| Métrica | Bot/Chatbot | Meta Ads | Google Ads | Otros Canales | Total |
|---------|------------|----------|------------|---------------|-------|
| Leads (Cohorte) | 7 | 75 | 21 | 36 | 139 |
| Inscriptos Confirmados | 5 | 31 | 9 | 23 | 63 |
| Tasa de Conversión | 71.43% | 41.33% | 42.86% | 63.89% | 45.32% |

## 2. Tasa de Conversión Comparativa (Bot vs Plataformas Pagas)

| Canal | Leads (Muestra) | Inscriptos | Tasa Conversión | vs Promedio |
|-------|----------------:|-----------:|----------------:|------------:|
| Bot/Chatbot | 7 | 5 | 71.43% | +26.10 pp |
| Meta Ads | 75 | 31 | 41.33% | -3.99 pp |
| Google Ads | 21 | 9 | 42.86% | -2.47 pp |
| Otros Canales | 36 | 23 | 63.89% | +18.57 pp |
| **Promedio General** | **139** | **63** | **45.32%** | — |

## 3. Metodología de Atribución (Tipo de Match)

Desglose algorítmico de cómo se vincularon los leads del bot con inscripciones concretadas:

| Metodología de Cruce (Lead -> Inscripto)   |   Inscriptos Confirmados |    % |
|:-------------------------------------------|-------------------------:|-----:|
| Exacto (DNI)                               |                        3 | 50   |
| Exacto (Email)                             |                        2 | 33.3 |
| Exacto (Teléfono)                          |                        1 | 16.7 |

## 4. Top 10 Carreras Inscriptas vía Bot

| Carrera                    |   Inscriptos (Muestra) |   Consultas (Muestra) |   Tasa_% |
|:---------------------------|-----------------------:|----------------------:|---------:|
| ABOGACÍA                   |                      6 |                     6 |      100 |
| LICENCIATURA EN PSICOLOGÍA |                      0 |                     1 |        0 |

## 4. Distribución por Sede

| Sede                          |   Leads |
|:------------------------------|--------:|
| HOME                          |       6 |
| SALTA - CASTAÑARES PRESENCIAL |       1 |

## 5. Canales de Origen (ColaNombre)

| Cola           |   Leads |
|:---------------|--------:|
| Contact_Center |       3 |

## 6. Estado de los Leads de Bot

| Estado        |   Cantidad |    % |
|:--------------|-----------:|-----:|
| No interesado |          4 | 57.1 |
| Abierto       |          2 | 28.6 |
| Interesado    |          1 | 14.3 |

