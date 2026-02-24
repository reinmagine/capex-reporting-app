"""
Test Script for WP LOA Formula Processor

Run this after placing your WP LOA Report file in uploads folder
"""

import sys
from pathlib import Path
from processors.wp_loa_formula import WPLOAFormulaProcessor
from processors.budget_analyzer import analyze_budget_sheet

def main():
    uploads_dir = Path('uploads')
    
    # Find Excel file in uploads
    excel_files = list(uploads_dir.glob('*.xlsx')) + list(uploads_dir.glob('*.xls'))
    
    if not excel_files:
        print("⚠️  No Excel files found in 'uploads' folder")
        print("\nSteps to test:")
        print("1. Place your WP LOA Report Excel file in the 'uploads' folder")
        print("2. Run this script again")
        print("\nTo diagnose VLOOKUP issues:")
        print("   python test_wp_loa.py analyze")
        return
    
    input_file = excel_files[0]
    print(f"\n📁 Found file: {input_file.name}")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        print("\n🔍 Analyzing BUDGET sheet structure...")
        analyze_budget_sheet(str(input_file))
        return
    
    try:
        print("\n⚙️  Running formula processor...")
        processor = WPLOAFormulaProcessor(str(input_file))
        processor.load_file()
        processor.create_formulas()
        
        output_file = uploads_dir / f"output_{input_file.name}"
        processor.save_workbook(str(output_file))
        
        print(f"\n✅ Processing complete!")
        print(f"📝 Output file: {output_file.name}")
        
        summary = processor.get_summary()
        print("\n📊 Summary:")
        for key, value in summary.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")
        
        print("\n✓ Headers should appear in row 1 (columns K-AA)")
        print("✓ Formulas should appear in cells (not calculated values)")
        print("✓ If VLOOKUP shows 'N/A': Run 'python test_wp_loa.py analyze' to check BUDGET sheet")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
