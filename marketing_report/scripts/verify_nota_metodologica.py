"""
verify_nota_metodologica.py
Verifica que todos los scripts de reporting incluyan:
1. Nota Metodológica (en MD y PDF)
2. Desglose de tipos de match (DNI, Email, Teléfono, Celular)
3. Referencia al modelo Any-Touch (04_reporte_final)

Ejecutar: python verify_nota_metodologica.py
"""
import os
import sys

base_dir = r"h:\Test-Antigravity\marketing_report\scripts"

# Scripts que DEBEN tener nota metodológica
SCRIPTS_REQUIRED = {
    '04_reporte_final.py':      {'nota': True, 'match': True, 'anytouch': True},
    '07_pdf_completo.py':       {'nota': True, 'match': True, 'anytouch': True},
    '08_tabla_utm.py':          {'nota': True, 'match': False, 'anytouch': True},
    '09_utm_conversion.py':     {'nota': True, 'match': False, 'anytouch': True},
    '10_google_ads_deep_dive.py': {'nota': True, 'match': False, 'anytouch': True},
    '12_analisis_no_matcheados.py': {'nota': True, 'match': True, 'anytouch': True},
    '13_facebook_deep_dive.py': {'nota': True, 'match': True, 'anytouch': True},
    '14_bot_deep_dive.py':      {'nota': True, 'match': True, 'anytouch': True},
    '16_analisis_matriculadas.py': {'nota': True, 'match': True, 'anytouch': True},
    '19_bot_consolidado.py':    {'nota': True, 'match': True, 'anytouch': True},
    '20_presupuesto_roi.py':    {'nota': True, 'match': False, 'anytouch': True},
    '21_atribucion_causal.py':  {'nota': True, 'match': False, 'anytouch': True},
    '23_embudo_conversion.py':  {'nota': True, 'match': False, 'anytouch': True},
}

# Patterns to search for
NOTA_PATTERNS = [
    'nota metodol',
    'Nota Metodol',
    'NOTA METODOL',
    'nota_met',
]

MATCH_PATTERNS = [
    'Exacto (DNI)',
    'por DNI',
    'Match_DNI',
    'insc_por_dni',
    'insc_dni',
    'inscriptos_por_dni',
    'p_dni',
]

ANYTOUCH_PATTERNS = [
    'any-touch',
    'Any-Touch',
    'any_touch',
    'anytouch',
    'AnyTouch',
    'Informe Anal',
    '04_reporte_final',
    'multi-canal',
]

def check_script(filepath, requirements):
    """Check a single script for required elements."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_lower = content.lower()
    results = {}

    # Check nota metodológica
    if requirements['nota']:
        found = any(p.lower() in content_lower for p in NOTA_PATTERNS)
        results['nota'] = found

    # Check match type desglose
    if requirements['match']:
        found = any(p.lower() in content_lower for p in MATCH_PATTERNS)
        results['match'] = found

    # Check any-touch reference
    if requirements['anytouch']:
        found = any(p.lower() in content_lower for p in ANYTOUCH_PATTERNS)
        results['anytouch'] = found

    return results


def main():
    print("=" * 70)
    print("VERIFICACIÓN: Nota Metodológica en Scripts de Reporting")
    print("=" * 70)

    all_ok = True

    for script, reqs in sorted(SCRIPTS_REQUIRED.items()):
        filepath = os.path.join(base_dir, script)
        if not os.path.exists(filepath):
            print(f"\n  [!!] {script}: ARCHIVO NO ENCONTRADO")
            all_ok = False
            continue

        results = check_script(filepath, reqs)

        issues = []
        for key, found in results.items():
            if not found:
                label = {'nota': 'Nota Metodológica', 'match': 'Desglose Match', 'anytouch': 'Ref. Any-Touch'}[key]
                issues.append(label)

        if issues:
            status = "FALTA"
            icon = "[!!]"
            detail = " | ".join(issues)
            all_ok = False
        else:
            status = "OK"
            icon = "[OK]"
            checks = []
            if reqs.get('nota'): checks.append("Nota")
            if reqs.get('match'): checks.append("Match")
            if reqs.get('anytouch'): checks.append("AnyTouch")
            detail = " + ".join(checks)

        print(f"  {icon} {script:<38} {status:<6} {detail}")

    print("\n" + "=" * 70)
    if all_ok:
        print("  RESULTADO: Todos los scripts pasan la verificación.")
        return 0
    else:
        print("  RESULTADO: Hay scripts con elementos faltantes.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
