# Embudo de Conversion: Consulta -> Boleta -> Inscripción

Fecha: 2026-03-12

## Resumen por Segmento

### Grado_Pregrado

| Etapa | Personas | Tasa desde anterior |
|---|---:|---:|
| Consulta (leads con DNI) | 63,966 | - |
| Generó Boleta | 2,479 | 3.9% |
| Pagó (inscripto) | 5,547 | 8.7% |

**Boleta -> Pago (todas las boletas):** 444 / 7,704 = 5.8%

**Boletas sin lead asociado:** 5,225  |  **Inscriptos sin lead:** 4,042

![Embudo Grado_Pregrado](chart_embudo_Grado_Pregrado.png)

### Cursos

| Etapa | Personas | Tasa desde anterior |
|---|---:|---:|
| Consulta (leads con DNI) | 11 | - |
| Generó Boleta | 0 | 0.0% |
| Pagó (inscripto) | 10 | 90.9% |

**Boleta -> Pago (todas las boletas):** 0 / 374 = 0.0%

**Boletas sin lead asociado:** 374  |  **Inscriptos sin lead:** 84

![Embudo Cursos](chart_embudo_Cursos.png)

### Posgrados

| Etapa | Personas | Tasa desde anterior |
|---|---:|---:|
| Consulta (leads con DNI) | 47 | - |
| Generó Boleta | 0 | 0.0% |
| Pagó (inscripto) | 38 | 80.9% |

**Boleta -> Pago (todas las boletas):** 0 / 136 = 0.0%

**Boletas sin lead asociado:** 136  |  **Inscriptos sin lead:** 301

![Embudo Posgrados](chart_embudo_Posgrados.png)

## Desglose por Canal

| Segmento | Canal | Leads | Con Boleta | Tasa L->B | Inscriptos | Tasa L->I | Tasa B->I |
|---|---|---:|---:|---:|---:|---:|---:|
| Grado_Pregrado | Google | 21,570 | 505 | 2.3% | 579 | 2.7% | 114.7% |
| Grado_Pregrado | Meta | 13,028 | 391 | 3.0% | 338 | 2.6% | 86.4% |
| Grado_Pregrado | Bot | 968 | 134 | 13.8% | 267 | 27.6% | 199.3% |
| Grado_Pregrado | Otros | 28,400 | 1,449 | 5.1% | 4,363 | 15.4% | 301.1% |
| Cursos | Google | 1 | 0 | 0.0% | 1 | 100.0% | 0.0% |
| Cursos | Meta | 2 | 0 | 0.0% | 2 | 100.0% | 0.0% |
| Cursos | Bot | 0 | 0 | 0.0% | 0 | 0.0% | 0.0% |
| Cursos | Otros | 8 | 0 | 0.0% | 7 | 87.5% | 0.0% |
| Posgrados | Google | 8 | 0 | 0.0% | 6 | 75.0% | 0.0% |
| Posgrados | Meta | 7 | 0 | 0.0% | 3 | 42.9% | 0.0% |
| Posgrados | Bot | 2 | 0 | 0.0% | 2 | 100.0% | 0.0% |
| Posgrados | Otros | 30 | 0 | 0.0% | 27 | 90.0% | 0.0% |

![Canal](chart_embudo_canal.png)

## Desglose por Campana

| Segmento | Campana | Leads | Con Boleta | Tasa L->B | Inscriptos | Tasa L->I |
|---|---|---:|---:|---:|---:|---:|
| Grado_Pregrado | Ingreso 2026 | 22,997 | 2,068 | 9.0% | 4,700 | 20.4% |
| Grado_Pregrado | Campaña Anterior | 40,969 | 411 | 1.0% | 847 | 2.1% |
| Cursos | 2026 | 3 | 0 | 0.0% | 3 | 100.0% |
| Cursos | Campaña Anterior | 8 | 0 | 0.0% | 7 | 87.5% |
| Posgrados | 2026 | 20 | 0 | 0.0% | 17 | 85.0% |
| Posgrados | Campaña Anterior | 27 | 0 | 0.0% | 21 | 77.8% |

## Sankey: Origen -> Boleta -> Pago

### Grado_Pregrado

![Sankey Grado_Pregrado](sankey_embudo_Grado_Pregrado.png)

> *"Boleta No Pagada" refleja el snapshot actual del archivo. Boletas ya pagadas
> desaparecen del archivo fuente, por lo que la cifra real de boletas generadas es mayor.*

### Cursos

![Sankey Cursos](sankey_embudo_Cursos.png)

> *"Boleta No Pagada" refleja el snapshot actual del archivo. Boletas ya pagadas
> desaparecen del archivo fuente, por lo que la cifra real de boletas generadas es mayor.*

### Posgrados

![Sankey Posgrados](sankey_embudo_Posgrados.png)

> *"Boleta No Pagada" refleja el snapshot actual del archivo. Boletas ya pagadas
> desaparecen del archivo fuente, por lo que la cifra real de boletas generadas es mayor.*


## Nota Metodológica

- **Modelo de atribución:** Embudo por persona (DNI). Deduplicado por DNI limpio.
- **Persona** = DNI limpio único. Leads sin DNI no se incluyen en el embudo.
- **Consulta**: persona que generó al menos 1 lead/consulta en Salesforce.
- **Boleta**: persona cuyo DNI aparece en el archivo de boletas generadas.
- **Inscripto**: persona cuyo lead matcheó exactamente con un inscripto (pagó matrícula). Match Exacto: DNI > Email > Teléfono > Celular (prioridad).
- La tasa Lead->Boleta puede subestimarse si la persona usó datos diferentes en Salesforce vs sistema de boletas.
- La tasa Boleta->Pago se calcula sobre TODAS las boletas del segmento (no solo las conectadas a leads).
- **Any-Touch:** Para atribución multi-canal (inscriptos que consultaron por más de un canal), referirse al Informe Analítico (04_reporte_final).
- **Ventana:** Grado/Pregrado desde 01/09/2025, Cursos y Posgrados desde 01/01/2026.