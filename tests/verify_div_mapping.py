#!/usr/bin/env python
"""
Verify DIV IN REPORT formula with nested IF mapping
"""

print('✅ DIV IN REPORT FORMULA - NESTED IF MAPPING')
print('=' * 100)
print()

mappings = {
    'B&D': 'B&D',
    'CIPE': 'CIPE/Ting',
    'NAI': 'NAI/Raymond',
    'ND': 'ND/Dennis',
    'NOA': 'NOA/Cris',
    'Non-NTG': 'NTG Pool',
    'NTG': 'NTG / Manpower',
    'SPE': 'SPE/Joel',
    'SPP': 'SPP/Helen',
    'SS': 'SS/Marge'
}

print('Mapping Table:')
print('-' * 100)
print(f'{"DIV CODE":<15} {"→":<3} {"DIV IN REPORT (Return Value)":<50}')
print('-' * 100)

for code, name in mappings.items():
    print(f'{code:<15} {"→":<3} {name:<50}')

print()
print('=' * 100)
print()

print('Formula Structure:')
print('-' * 100)
print('Column Y (DIV IN REPORT):')
print()
print('=IF(R{row}="B&D","B&D",')
print('    IF(R{row}="CIPE","CIPE/Ting",')
print('       IF(R{row}="NAI","NAI/Raymond",')
print('          IF(R{row}="ND","ND/Dennis",')
print('             IF(R{row}="NOA","NOA/Cris",')
print('                IF(R{row}="Non-NTG","NTG Pool",')
print('                   IF(R{row}="NTG","NTG / Manpower",')
print('                      IF(R{row}="SPE","SPE/Joel",')
print('                         IF(R{row}="SPP","SPP/Helen",')
print('                            IF(R{row}="SS","SS/Marge","")')
print()
print()
print('=' * 100)
print()
print('How it works:')
print('-' * 100)
print('1. Checks the DIV code in Column R (from BUDGET VLOOKUP)')
print('2. Matches it against the mapping values')
print('3. Returns the corresponding formatted division name with responsible person')
print('4. Returns empty string ("") if no match found')
print()
print('Example:')
print('  If Column R = "SPE", then Column Y returns "SPE/Joel"')
print('  If Column R = "NTG", then Column Y returns "NTG / Manpower"')
print('  If Column R = "CIPE", then Column Y returns "CIPE/Ting"')
print()
print('=' * 100)
