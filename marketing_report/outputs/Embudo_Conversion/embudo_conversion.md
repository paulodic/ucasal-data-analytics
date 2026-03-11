# Embudo de Conversion: Consulta -> Boleta -> Inscripción

Fecha: 2026-03-06

## Resumen por Segmento

### Grado_Pregrado

| Etapa | Personas | Tasa desde anterior |
|---|---:|---:|
| Consulta (leads con DNI) | 61,452 | - |
| Generó Boleta | 2,252 | 3.7% |
| Pagó (inscripto) | 4,789 | 7.8% |

**Boleta -> Pago (todas las boletas):** 297 / 7,704 = 3.9%

**Boletas sin lead asociado:** 5,452  |  **Inscriptos sin lead:** 4,029

![Embudo Grado_Pregrado](chart_embudo_Grado_Pregrado.png)

### Cursos

| Etapa | Personas | Tasa desde anterior |
|---|---:|---:|
| Consulta (leads con DNI) | 334 | - |
| Generó Boleta | 6 | 1.8% |
| Pagó (inscripto) | 324 | 97.0% |

**Boleta -> Pago (todas las boletas):** 5 / 374 = 1.3%

**Boletas sin lead asociado:** 368  |  **Inscriptos sin lead:** 557

![Embudo Cursos](chart_embudo_Cursos.png)

### Posgrados

| Etapa | Personas | Tasa desde anterior |
|---|---:|---:|
| Consulta (leads con DNI) | 45 | - |
| Generó Boleta | 0 | 0.0% |
| Pagó (inscripto) | 36 | 80.0% |

**Boleta -> Pago (todas las boletas):** 0 / 136 = 0.0%

**Boletas sin lead asociado:** 136  |  **Inscriptos sin lead:** 303

![Embudo Posgrados](chart_embudo_Posgrados.png)

## Desglose por Canal

| Segmento | Canal | Leads | Con Boleta | Tasa L->B | Inscriptos | Tasa L->I | Tasa B->I |
|---|---|---:|---:|---:|---:|---:|---:|
| Grado_Pregrado | Google | 21,418 | 473 | 2.2% | 538 | 2.5% | 113.7% |
| Grado_Pregrado | Meta | 12,220 | 362 | 3.0% | 284 | 2.3% | 78.5% |
| Grado_Pregrado | Bot | 821 | 111 | 13.5% | 222 | 27.0% | 200.0% |
| Grado_Pregrado | Otros | 26,993 | 1,306 | 4.8% | 3,745 | 13.9% | 286.8% |
| Cursos | Google | 20 | 0 | 0.0% | 16 | 80.0% | 0.0% |
| Cursos | Meta | 34 | 2 | 5.9% | 34 | 100.0% | 1700.0% |
| Cursos | Bot | 10 | 0 | 0.0% | 9 | 90.0% | 0.0% |
| Cursos | Otros | 270 | 4 | 1.5% | 265 | 98.1% | 6625.0% |
| Posgrados | Google | 6 | 0 | 0.0% | 4 | 66.7% | 0.0% |
| Posgrados | Meta | 7 | 0 | 0.0% | 3 | 42.9% | 0.0% |
| Posgrados | Bot | 2 | 0 | 0.0% | 2 | 100.0% | 0.0% |
| Posgrados | Otros | 30 | 0 | 0.0% | 27 | 90.0% | 0.0% |

![Canal](chart_embudo_canal.png)

## Desglose por Campana

| Segmento | Campana | Leads | Con Boleta | Tasa L->B | Inscriptos | Tasa L->I |
|---|---|---:|---:|---:|---:|---:|
| Grado_Pregrado | Ingreso 2026 | 20,372 | 1,826 | 9.0% | 3,934 | 19.3% |
| Grado_Pregrado | Campaña Anterior | 41,080 | 426 | 1.0% | 855 | 2.1% |
| Cursos | 2026 | 63 | 0 | 0.0% | 58 | 92.1% |
| Cursos | Campaña Anterior | 271 | 6 | 2.2% | 266 | 98.2% |
| Posgrados | 2026 | 20 | 0 | 0.0% | 17 | 85.0% |
| Posgrados | Campaña Anterior | 25 | 0 | 0.0% | 19 | 76.0% |

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

- **Persona** = DNI limpio único. Leads sin DNI no se incluyen en el embudo.
- **Consulta**: persona que generó al menos 1 lead/consulta en Salesforce.
- **Boleta**: persona cuyo DNI aparece en el archivo de boletas generadas.
- **Inscripto**: persona cuyo lead matcheó exactamente con un inscripto (pagó matrícula).
- La tasa Lead->Boleta puede subestimarse si la persona usó datos diferentes en Salesforce vs sistema de boletas.
- La tasa Boleta->Pago se calcula sobre TODAS las boletas del segmento (no solo las conectadas a leads).