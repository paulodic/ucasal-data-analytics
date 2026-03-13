# UCASAL Marketing Analytics Pipeline

Pipeline de analytics que cruza leads de Salesforce con inscriptos del sistema academico para medir conversiones de marketing.

## Quick Start

```bash
# 1. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Instalar dependencias
pip install -r marketing_report/requirements.txt

# 3. Generar bases de datos intermedias (OBLIGATORIO antes de cualquier reporte)
python marketing_report/scripts/02_cruce_datos.py

# 4. Generar todos los reportes
python marketing_report/scripts/00_run_all.py
```

**IMPORTANTE:** `00_run_all.py` NO ejecuta `02_cruce_datos.py`. Siempre correr el paso 3 primero.

## Estructura

```
marketing_report/
  data/1_raw/          <- Datos fuente (Salesforce, inscriptos, boletas)
  scripts/             <- Pipeline de procesamiento (02, 03-23)
  outputs/             <- Reportes generados (PDF, Excel, MD, graficos)
    Data_Base/         <- CSVs intermedios por segmento
```

## Documentacion

- [README_DEV.md](marketing_report/README_DEV.md) — Guia completa para desarrolladores
- [DATA_CONTRACT_LEADS.md](marketing_report/DATA_CONTRACT_LEADS.md) — Contrato de datos, mapeo de columnas, algoritmo de matching

## Segmentos

Los reportes se generan por nivel academico:
- **Grado_Pregrado** — Incluye cursos de ingreso (codcar 1169, 1200-1204)
- **Cursos**
- **Posgrados**
