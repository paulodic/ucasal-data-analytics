import csv

f = open(r'h:\Test-Antigravity\marketing_report\outputs\reporte_marketing_leads_completos.csv', 'r', encoding='utf-8')
reader = csv.reader(f)
headers = next(reader)
row1 = next(reader)
f.close()

print("Columns:")
for i, h in enumerate(headers):
    print(f"[{i}] {h} -> {row1[i]}")
