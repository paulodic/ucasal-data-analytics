import pandas as pd
import glob
import sys
import datetime

try:
    paths = [
        'h:/Test-Antigravity/marketing_report/outputs/Data_Base/Grado_Pregrado/reporte_marketing_leads_completos.csv',
        'h:/Test-Antigravity/marketing_report/outputs/Data_Base/Cursos/reporte_marketing_leads_completos.csv',
        'h:/Test-Antigravity/marketing_report/outputs/Data_Base/Posgrados/reporte_marketing_leads_completos.csv'
    ]
    
    dfs = []
    for p in paths:
        try:
            dfs.append(pd.read_csv(p, usecols=["Consulta: Fecha de creación"], low_memory=False))
        except Exception as e:
            pass
            
    df = pd.concat(dfs, ignore_index=True)
    
    df['fecha'] = pd.to_datetime(df["Consulta: Fecha de creación"], dayfirst=True, format='mixed', errors='coerce').dt.date
    dates = df['fecha'].dropna().unique()
    
    # Sort dates
    dates = sorted(list(dates))
    
    start_date = datetime.date(2025, 9, 1) # Inicio ciclo comercial central
    
    valid_dates = [d for d in dates if d >= start_date]
    
    real_start = valid_dates[0]
    real_end = valid_dates[-1]
    
    d_range = pd.date_range(start=real_start, end=real_end).date
    missing = set(d_range) - set(valid_dates)
    
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        pass
        
    print(f"Rango de Fechas Analizado: {real_start} a {real_end}")
    print(f"Total de días dentro del calendario natural: {len(d_range)}")
    print(f"Días CON registros en el CSV: {len(valid_dates)}")
    print(f"Huecos totales (Días SIN NINGUN lead): {len(missing)}\n")
    
    if len(missing) > 0:
        print("LISTADO EXHAUSTIVO DE HUECOS DE FECHA:")
        for m in sorted(list(missing)):
            print(f"- {m.strftime('%Y-%m-%d')} ({m.strftime('%A')})")
    else:
        print("No se encontraron baches en las fechas. Se tienen leads todos los días ininterrumpidamente.")
        
except Exception as e:
    import traceback
    traceback.print_exc()
