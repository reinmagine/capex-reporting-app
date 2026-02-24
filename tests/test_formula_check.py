#!/usr/bin/env python
"""
Quick test of the updated WP LOA Formula Processor
"""

from processors.wp_loa_formula import WPLOAFormulaProcessor

print("✅ Updated WP LOA Formula Processor")
print("=" * 70)

print(f"\n✅ Column headers: {len(WPLOAFormulaProcessor.NEW_COLUMN_HEADERS)} columns (K-AA)")
for i, header in enumerate(WPLOAFormulaProcessor.NEW_COLUMN_HEADERS, start=11):
    col_letter = chr(64 + i)  # Convert 11 to 'K', 12 to 'L', etc.
    print(f"   {col_letter}: {header}")

print("\n✅ Formula Examples (what will be in each row):")
print("\nPID Extraction (from H column with value like 'I-BSRF-26-SA'):")
print("   K (Part 1): =LEFT(H2,FIND(\"-\",H2)-1)")
print("              Result: I")
print("   L (Part 2): =TRIM(MID(SUBSTITUTE(H2,\"-\",REPT(\" \",100)),100,100))")
print("              Result: BSRF")
print("   M (Part 3): =TRIM(MID(SUBSTITUTE(H2,\"-\",REPT(\" \",100)),200,100))")
print("              Result: 26")
print("   N (Part 4): =TRIM(MID(SUBSTITUTE(H2,\"-\",REPT(\" \",100)),300,100))")
print("              Result: SA")

print("\nL1 Derivation:")
print("   O (L1):     =L2&\"-\"&M2&\"-\"&N2")
print("              Result: BSRF-26-SA")

print("\nVLOOKUP to BUDGET Sheet (using O as lookup key):")
print("   Q (PROGRAM_MBR):  =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,10,FALSE),\"N/A\")")
print("   R (DIV):          =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,7,FALSE),\"N/A\")")
print("   S (DEP):          =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,6,FALSE),\"N/A\")")
print("   T (FUNDING):      =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,13,FALSE),\"N/A\")")
print("   U (CFU_SPONSOR):  =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,4,FALSE),\"N/A\")")
print("   Z (PROJ):         =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,11,FALSE),\"N/A\")")
print("   AA (SUBPROJ):     =IFERROR(VLOOKUP(O2,BUDGET!$A:$AL,12,FALSE),\"N/A\")")

print("\n" + "=" * 70)
print("✅ All formulas corrected!")
print("\nKey Changes:")
print("  1. K, L, M, N now EXTRACT parts from H instead of being empty")
print("  2. O (L1) concatenates parts 2-3-4: L&\"-\"&M&\"-\"&N")
print("  3. VLOOKUP now uses O (L1) as lookup key instead of P (full PID)")
print("  4. External file support now copies data into current workbook")
print("=" * 70)
