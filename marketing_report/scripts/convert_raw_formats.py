import pandas as pd
import glob
import os

base_dir = r"h:\Test-Antigravity\marketing_report\data\1_raw"
carpetas = ['inscriptos', 'leads_salesforce']

for carpeta in carpetas:
    dir_path = os.path.join(base_dir, carpeta)
    archivos_xls = glob.glob(os.path.join(dir_path, '*.xls'))
    archivos_xlsx_already = glob.glob(os.path.join(dir_path, '*.xlsx'))
    
    # Process all to ensure we have .xlsx and .csv in the correct schema
    all_files = archivos_xls + archivos_xlsx_already
    all_files = list(set(all_files)) # deduplicate
    
    for arc in all_files:
        print(f"Abriendo {arc}...")
        try:
            df = pd.read_excel(arc)
            base_name = os.path.splitext(arc)[0]
            if base_name.endswith('.xls'):
               base_name = base_name[:-4]
            
            # Export to XLSX
            path_xlsx = base_name + '.xlsx'
            if arc != path_xlsx:
                df.to_excel(path_xlsx, index=False)
                print(f"-> Guardado {path_xlsx}")
            
            # Export to CSV
            path_csv = base_name + '.csv'
            df.to_csv(path_csv, index=False)
            print(f"-> Guardado {path_csv}")
            
            # Delete old .xls
            if arc.endswith('.xls'):
                os.remove(arc)
                print(f"-> ELIMINADO antiguo: {arc}")
        except Exception as e:
            print(f"ERROR al procesar {arc}: {e}")

print("--- TODAS LAS CONVERSIONES TERMINADAS ---")
