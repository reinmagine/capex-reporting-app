"""
CAPEX Reporting Tool - Desktop Application
Refactored version using modular processors and utilities
Implements PRIORITY 1 fixes: Unified code, modular structure, file validation
"""
import sys
from pathlib import Path

# Add parent directory to Python path to allow importing processors and utils modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
from datetime import datetime
import threading
import requests
import openpyxl

from processors.cji import CJIProcessor
from processors.rfp_reclass import RFPReclassProcessor
from processors.zmm import ZMMProcessor, ZMMConsolidator
from processors.wp_loa_formula import WPLOAFormulaProcessor
from utils.validators import FileValidator
from utils.auto_updater import check_updates_on_startup
from config import EXCHANGE_RATES
from config.version import VERSION, VERSION_CHECK_URL





class CAPEXReportingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"CAPEX Reporting Tool v{VERSION}")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Default exchange rates (no live fetching)
        self.exchange_rates = {
            'PHP_TO_USD': 1/57,
            'SGD_TO_USD': 1/1.34,
            'PHP': 57,
            'SGD': 1.34
        }
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="CAPEX Reporting Tool", 
                        font=("Segoe UI", 20, "bold"), bg='#f0f0f0', fg='#29348F')
        title.pack(pady=(0, 2))
        
        subtitle = tk.Label(main_frame, 
                           text=f"v{VERSION}", 
                           font=("Segoe UI", 9), bg='#f0f0f0', fg='#666')
        subtitle.pack(pady=(0, 15))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_basic_tab()
        self.create_advanced_tab()
        self.create_consolidation_tab()
        self.create_wp_loa_tab()
        
        # Loading frame (initially hidden)
        self.loading_frame = tk.Frame(root, bg='#ffffff')
        self.loading_label = tk.Label(self.loading_frame, 
                                     text="Processing file, please wait...", 
                                     font=("Segoe UI", 11, "bold"), 
                                     bg='#ffffff', fg='#29348F', pady=20, padx=40)
        self.loading_label.pack()
        
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 20), padx=40)
        
        # Status bar (simple and clean)
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(root, textvariable=self.status_var, 
                            font=("Segoe UI", 8), bg='#e8e8e8', 
                            fg='#555', anchor=tk.W, padx=10, pady=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.selected_file = None
    

    
    def show_loading(self, message="Processing file, please wait..."):
        """Show loading indicator"""
        self.loading_label.config(text=message)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.progress.start(10)
        self.root.update()
    
    def hide_loading(self):
        """Hide loading indicator"""
        self.progress.stop()
        self.loading_frame.place_forget()
        self.root.update()
    
    def create_basic_tab(self):
        """Create basic processing tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Basic Processing (STEP 4-5)")
        
        # File type selection
        type_frame = tk.LabelFrame(tab, text="Select Report Type", 
                                  font=("Segoe UI", 10, "bold"), bg='#f0f0f0', 
                                  fg='#29348F', padx=15, pady=15)
        type_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.file_type = tk.StringVar(value="cji5")
        
        types = [
            ("CJI5 - Convert ERP Reference & Currency", "cji5"),
            ("CJI3 - Convert Purchasing Document & Currency", "cji3"),
            ("RFP - Filter & Convert Currency", "rfp"),
            ("Reclass - Convert Currency & Calculate Total", "reclass"),
            ("ZMM - Process PR Numbers & Copy Columns", "zmm")
        ]
        
        for text, value in types:
            rb = tk.Radiobutton(type_frame, text=text, variable=self.file_type, 
                               value=value, font=("Segoe UI", 9), bg='#f0f0f0',
                               activebackground='#f0f0f0', fg='#333', pady=4)
            rb.pack(anchor=tk.W)
        
        # File selection
        file_frame = tk.Frame(tab, bg='#f0f0f0')
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.file_path = tk.StringVar(value="No file selected")
        file_label = tk.Label(file_frame, textvariable=self.file_path, 
                             font=("Segoe UI", 9), bg='#f0f0f0', fg='#555')
        file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Browse File", 
                              command=self.browse_file, font=("Segoe UI", 9, "bold"),
                              bg='#29348F', fg='white', padx=15, pady=8,
                              relief=tk.FLAT, cursor="hand2")
        browse_btn.pack(side=tk.RIGHT)
        
        # Process button
        self.process_btn = tk.Button(tab, text="Process File", 
                                     command=self.process_file_threaded, 
                                     font=("Segoe UI", 11, "bold"),
                                     bg='#29348F', fg='white', padx=30, pady=10,
                                     relief=tk.FLAT, cursor="hand2", state=tk.DISABLED)
        self.process_btn.pack(pady=15)
    
    def create_advanced_tab(self):
        """Create advanced features tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Advanced (STEP 6-7, 12-14, 1)")
        
        adv_frame = tk.LabelFrame(tab, text="Advanced Processing Options", 
                                 font=("Segoe UI", 10, "bold"), bg='#f0f0f0', 
                                 fg='#29348F', padx=15, pady=15)
        adv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pivot table generation (STEP 6-7)
        pivot_label = tk.Label(adv_frame, text="Pivot Table Generation (STEP 6-7):", 
                              font=("Segoe UI", 9, "bold"), bg='#f0f0f0', fg='#29348F')
        pivot_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.pivot_cji5_btn = tk.Button(adv_frame, text="Process CJI5 with Pivot Table", 
                                       command=lambda: self.process_with_pivot_threaded('cji5'),
                                       font=("Segoe UI", 9), bg='#29348F', fg='white',
                                       padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji5_btn.pack(fill=tk.X, pady=2)
        
        self.pivot_cji3_btn = tk.Button(adv_frame, text="Process CJI3 with Pivot Table", 
                                       command=lambda: self.process_with_pivot_threaded('cji3'),
                                       font=("Segoe UI", 9), bg='#29348F', fg='white',
                                       padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji3_btn.pack(fill=tk.X, pady=2)
        
        # Filtering options
        filter_label = tk.Label(adv_frame, text="\nFiltering & Special Processing:", 
                               font=("Segoe UI", 9, "bold"), bg='#f0f0f0', fg='#29348F')
        filter_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.filter_gnt_btn = tk.Button(adv_frame, text="Filter GNT-OTACP-25 Car Plan (STEP 1, 9-10)", 
                                       command=self.filter_carplan,
                                       font=("Segoe UI", 9), bg='#757575', fg='white',
                                       padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.filter_gnt_btn.pack(fill=tk.X, pady=2)
        
        self.no_carplan_btn = tk.Button(adv_frame, text="Process CJI5 Without Car Plan (STEP 14)", 
                                        command=self.process_cji5_no_carplan,
                                        font=("Segoe UI", 9), bg='#757575', fg='white',
                                        padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.no_carplan_btn.pack(fill=tk.X, pady=2)
        
        self.remove_cbip_btn = tk.Button(adv_frame, text="Remove M-CBIP-25 from RFP/Reclass (STEP 12-13)", 
                                        command=self.remove_cbip,
                                        font=("Segoe UI", 9), bg='#757575', fg='white',
                                        padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.remove_cbip_btn.pack(fill=tk.X, pady=2)
    
    def create_consolidation_tab(self):
        """Create consolidation & merge tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Consolidation (STEP 1, 8)")
        
        cons_frame = tk.LabelFrame(tab, text="File Consolidation & Merge Options", 
                                  font=("Segoe UI", 10, "bold"), bg='#f0f0f0', 
                                  fg='#29348F', padx=15, pady=15)
        cons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ZMM Consolidation (STEP 1)
        zmm_label = tk.Label(cons_frame, text="ZMM Consolidation (STEP 1):", 
                            font=("Segoe UI", 9, "bold"), bg='#f0f0f0', fg='#29348F')
        zmm_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.consolidate_zmm_btn = tk.Button(cons_frame, 
                                            text="Consolidate Multiple ZMM Files with Header Validation", 
                                            command=self.consolidate_zmm_files,
                                            font=("Segoe UI", 9), bg='#e65100', fg='white',
                                            padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.consolidate_zmm_btn.pack(fill=tk.X, pady=2)
        
        # CJI Merge (STEP 8)
        merge_label = tk.Label(cons_frame, text="\nData Merge & Lookup (STEP 8):", 
                              font=("Segoe UI", 9, "bold"), bg='#f0f0f0', fg='#29348F')
        merge_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.merge_cji_btn = tk.Button(cons_frame, 
                                      text="Merge CJI5 & CJI3 Data", 
                                      command=self.merge_cji_data,
                                      font=("Segoe UI", 9), bg='#6a1b9a', fg='white',
                                      padx=15, pady=7, relief=tk.FLAT, cursor="hand2")
        self.merge_cji_btn.pack(fill=tk.X, pady=2)
    
    def browse_file(self):
        """Browse and select file"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if filename:
            self.selected_file = filename
            file_size = os.path.getsize(filename) / (1024 * 1024)
            self.file_path.set(f"{os.path.basename(filename)} ({file_size:.1f} MB)")
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set(f"File selected: {os.path.basename(filename)}")
    
    def process_file_threaded(self):
        """Run file processing in a separate thread"""
        thread = threading.Thread(target=self.process_file)
        thread.daemon = True
        thread.start()
    
    def process_file(self):
        """Process selected file using formula-based approach (instant processing)"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        try:
            file_type = self.file_type.get()
            
            # Show loading (will be very quick now)
            self.show_loading(f"Processing {file_type.upper()} file with formulas...")
            self.process_btn.config(state=tk.DISABLED)
            
            # Validate file first
            temp_df = pd.read_excel(self.selected_file)
            validation = FileValidator.get_validation_report(temp_df, file_type)
            
            if not validation['is_valid']:
                self.hide_loading()
                self.process_btn.config(state=tk.NORMAL)
                missing = '\n'.join(validation['missing_columns']) if validation['missing_columns'] else "Unknown"
                messagebox.showerror("File Validation Error", 
                                   f"Invalid {file_type.upper()} file structure.\n\n" +
                                   f"Missing columns:\n{missing}")
                return
            
            # Use formula-based processing (instant - just creates formulas)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name_base = ''
            
            if file_type == 'cji5':
                processor = CJIProcessor('cji5')
                processor.process_basic_formula(self.selected_file, self.exchange_rates)
                output_name_base = 'CJI5_Processed'
                row_count = processor.ws.max_row - 1  # Subtract header
                
            elif file_type == 'cji3':
                processor = CJIProcessor('cji3')
                processor.process_basic_formula(self.selected_file, self.exchange_rates)
                output_name_base = 'CJI3_Processed'
                row_count = processor.ws.max_row - 1
                
            elif file_type == 'rfp':
                processor = RFPReclassProcessor('rfp')
                processor.process_with_total_formula(self.selected_file, self.exchange_rates, remove_cbip=False)
                output_name_base = 'RFP_Processed'
                row_count = processor.ws.max_row - 1
                
            elif file_type == 'reclass':
                processor = RFPReclassProcessor('reclass')
                processor.process_with_total_formula(self.selected_file, self.exchange_rates, remove_cbip=False)
                output_name_base = 'Reclass_Processed'
                row_count = processor.ws.max_row - 1
                
            elif file_type == 'zmm':
                processor = ZMMProcessor()
                processor.process_basic_formula(self.selected_file)
                output_name_base = 'ZMM_Processed'
                row_count = processor.ws.max_row - 1
            else:
                raise ValueError("Invalid file type")
            
            # Hide loading before save dialog
            self.hide_loading()
            
            default_filename = f'{output_name_base}_{timestamp}.xlsx'
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                # Show loading during save
                self.show_loading(f"Saving {output_name_base}...")
                
                # Save the workbook with formulas
                processor.wb.save(save_path)
                
                self.hide_loading()
                
                file_size = os.path.getsize(save_path) / (1024 * 1024)
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", 
                                  f"File processed successfully with FORMULAS!\n\n" +
                                  f"File: {os.path.basename(save_path)}\n" +
                                  f"Size: {file_size:.1f} MB\n" +
                                  f"Rows: {row_count:,}\n\n")
            else:
                self.status_var.set("Save cancelled")
                self.hide_loading()
            
            self.process_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.hide_loading()
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error processing file:\n\n{str(e)}")
    
    def process_with_pivot_threaded(self, file_type):
        """Run pivot processing in a separate thread"""
        thread = threading.Thread(target=lambda: self.process_with_pivot(file_type))
        thread.daemon = True
        thread.start()
    
    def process_with_pivot(self, file_type):
        """Process file with pivot table (STEP 6-7) - WITH FORMULA PRESERVATION"""
        filename = filedialog.askopenfilename(
            title=f"Select {file_type.upper()} File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading(f"Processing {file_type.upper()} with pivot table...")

            # Step 1: Load file ONCE for both formula processing and pivot calculation
            original_df = pd.read_excel(filename)
            
            # Step 2: Setup processor for formula creation
            processor = CJIProcessor(file_type)
            processor.df = original_df.copy()
            processor.wb = openpyxl.load_workbook(filename)
            processor.ws = processor.wb.active
            processor.validate_and_prepare()
            
            # Step 3: Get column mappings
            ref_col_key = 'reference_doc' if file_type == 'cji5' else 'purch_doc'
            ref_col = processor.columns.get(ref_col_key)
            cat_col = processor.columns.get('reference_category') if file_type == 'cji5' else None
            currency_col = processor.columns.get('trans_currency')
            amount_col = processor.columns.get('value_amount')
            project_col = processor.columns.get('project')
            
            if not ref_col:
                raise ValueError(f"Reference column not found for {file_type.upper()}")
            
            # Step 4: Add formulas to openpyxl workbook for Processed Data sheet
            from openpyxl.utils import get_column_letter
            php_rate = self.exchange_rates.get('PHP', 57)
            sgd_rate = self.exchange_rates.get('SGD', 1.34)
            
            # Get column indices from openpyxl sheet
            ref_idx = self._get_column_idx_from_sheet(processor.ws, processor.columns.get(ref_col_key))
            currency_idx = self._get_column_idx_from_sheet(processor.ws, currency_col)
            amount_idx = self._get_column_idx_from_sheet(processor.ws, amount_col)
            project_idx = self._get_column_idx_from_sheet(processor.ws, project_col) if project_col else None
            
            # Add Amount_USD column header
            usd_col_idx = processor.ws.max_column + 1
            processor.ws.cell(row=1, column=usd_col_idx).value = 'Amount_USD'
            
            # Add formulas for each row
            ref_letter = get_column_letter(ref_idx)
            currency_letter = get_column_letter(currency_idx)
            amount_letter = get_column_letter(amount_idx)
            
            for row in range(2, processor.ws.max_row + 1):
                is_subtotal = False
                if project_idx:
                    project_cell = processor.ws.cell(row=row, column=project_idx)
                    if not project_cell.value or str(project_cell.value).strip() == '':
                        is_subtotal = True
                
                cell_obj = processor.ws.cell(row=row, column=usd_col_idx)
                if not is_subtotal:
                    formula = (
                        f"=IF(UPPER({currency_letter}{row})=\"PHP\",{amount_letter}{row}/{php_rate},"
                        f"IF(UPPER({currency_letter}{row})=\"SGD\",{amount_letter}{row}/{sgd_rate},"
                        f"{amount_letter}{row}))"
                    )
                    cell_obj.value = formula
            
            # Step 5: Calculate Amount_USD for pivot (from original df)
            def calc_usd(row):
                if project_col and (pd.isna(row.get(project_col)) or str(row.get(project_col)).strip() == ''):
                    return None
                currency = str(row.get(currency_col, '')).upper()
                amount = row.get(amount_col, 0)
                if pd.isna(amount):
                    return 0
                if currency == 'PHP':
                    return amount / php_rate
                elif currency == 'SGD':
                    return amount / sgd_rate
                else:
                    return amount
            
            original_df['Amount_USD'] = original_df.apply(calc_usd, axis=1)
            df_for_pivot = original_df[original_df[ref_col].notna()].copy()
            
            # Step 6: Create pivot table
            if file_type == 'cji5' and cat_col and cat_col in df_for_pivot.columns:
                pivot = pd.pivot_table(
                    df_for_pivot,
                    values='Amount_USD',
                    index=ref_col,
                    columns=cat_col,
                    aggfunc='sum',
                    fill_value=0,
                    margins=True
                )
            else:
                pivot = pd.pivot_table(
                    df_for_pivot,
                    values='Amount_USD',
                    index=ref_col,
                    aggfunc='sum',
                    fill_value=0,
                    margins=True
                )

            self.hide_loading()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'{file_type.upper()}_with_Pivot_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )

            if save_path:
                self.show_loading("Saving file with pivot table and formulas...")

                # Step 7: Rename first sheet and add pivot
                processor.wb.active.title = 'Processed Data'
                
                # Add pivot table sheet
                pivot_ws = processor.wb.create_sheet('Pivot Table')
                pivot_df = pivot.reset_index()
                
                for c_idx, col in enumerate(pivot_df.columns, 1):
                    pivot_ws.cell(row=1, column=c_idx).value = col
                
                for r_idx, row in enumerate(pivot_df.values, 2):
                    for c_idx, value in enumerate(row, 1):
                        pivot_ws.cell(row=r_idx, column=c_idx).value = value
                
                # Save once
                processor.wb.save(save_path)
                self.hide_loading()

                file_size = os.path.getsize(save_path) / (1024 * 1024)
                self.status_var.set(f"Success! {file_type.upper()} with pivot saved")
                messagebox.showinfo("Success",
                                  f"File processed with pivot table!\n\n" +
                                  f"File: {os.path.basename(save_path)}\n" +
                                  f"Size: {file_size:.1f} MB\n\n" +
                                  f"Sheets:\n" +
                                  f"  1. Processed Data (with formulas in Amount_USD)\n" +
                                  f"  2. Pivot Table (calculated summary)")

        except Exception as e:
            self.hide_loading()
            self.status_var.set("Error occurred")
            import traceback
            messagebox.showerror("Error", f"Error: {str(e)}\n\n{traceback.format_exc()}")
    
    def _get_column_idx_from_sheet(self, ws, col_name):
        """Get column index from openpyxl sheet"""
        for idx, cell in enumerate(ws[1], start=1):
            if cell.value == col_name:
                return idx
        return None
    
    def _get_col_index(self, ws, col_name, columns):
        """Get column index from column name"""
        for idx, col in enumerate(columns, 1):
            if col == col_name:
                return idx
        return None
    
    def filter_carplan(self):
        """Filter Car Plan data (STEP 1, 9-10)"""
        filename = filedialog.askopenfilename(
            title="Select CJI5/CJI3 File to Filter Car Plan",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading("Filtering Car Plan data...")
            
            file_type = 'cji5' if 'CJI5' in filename else 'cji3'
            processor = CJIProcessor(file_type)
            processor.load_file(filename)
            processor.validate_and_prepare()
            main_df, carplan_df = processor.separate_carplan()
            
            self.hide_loading()
            
            if carplan_df is None or len(carplan_df) == 0:
                messagebox.showwarning("No Car Plan Data", 
                                     "No GNT-OTACP-25 car plan entries found in file")
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'CarPlan_GNT-OTACP-25_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving Car Plan data...")
                carplan_df.to_excel(save_path, index=False, engine='openpyxl')
                self.hide_loading()
                messagebox.showinfo("Success", 
                                  f"Car Plan data extracted!\n\n" +
                                  f"Rows: {len(carplan_df):,}")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def process_cji5_no_carplan(self):
        """Process CJI5 without car plan (STEP 14)"""
        filename = filedialog.askopenfilename(
            title="Select CJI5 File (Will exclude Car Plan GNT-OTACP-25)",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading("Processing CJI5 without Car Plan...")
            
            processor = CJIProcessor('cji5')
            processor.load_file(filename)
            processor.validate_and_prepare()
            df, removed_count = processor.process_without_carplan(self.exchange_rates)
            
            self.hide_loading()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'CJI5_NoCarPlan_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving CJI5 file without Car Plan...")
                processor.save(save_path)
                self.hide_loading()
                messagebox.showinfo("Success", 
                                  f"CJI5 processed without car plan!\n\n" +
                                  f"Car plan entries removed: {removed_count:,}\n" +
                                  f"Remaining rows: {len(df):,}")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def remove_cbip(self):
        """Remove CBIP entries from RFP/Reclass (STEP 12-13)"""
        filename = filedialog.askopenfilename(
            title="Select RFP/Reclass File to Remove M-CBIP-25",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading("Removing M-CBIP-25 entries...")
            
            file_type = 'rfp' if 'RFP' in filename else 'reclass'
            processor = RFPReclassProcessor(file_type)
            processor.load_file(filename)
            processor.validate_and_prepare()
            
            original_count = len(processor.df)
            removed = processor.remove_marker('cbip_code', 'object')
            
            self.hide_loading()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'{file_type.upper()}_No_CBIP_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving file without M-CBIP-25...")
                processor.save(save_path)
                self.hide_loading()
                messagebox.showinfo("Success", 
                                  f"M-CBIP-25 removed!\n\n" +
                                  f"Removed: {removed:,} rows\n" +
                                  f"Remaining: {len(processor.df):,} rows")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def consolidate_zmm_files(self):
        """Consolidate multiple ZMM files (STEP 1)"""
        filenames = filedialog.askopenfilenames(
            title="Select ZMM Files to Consolidate (select 2 or more)",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filenames or len(filenames) < 2:
            messagebox.showwarning("Error", "Please select at least 2 files to consolidate")
            return
        
        try:
            self.show_loading(f"Validating headers for {len(filenames)} ZMM files...")
            
            # Validate headers match
            headers_match, differences = ZMMConsolidator.validate_headers(filenames)
            
            if not headers_match:
                self.hide_loading()
                msg = "Header mismatches found:\n\n"
                for diff in differences:
                    msg += f"{os.path.basename(diff['file'])}\n"
                    if diff['missing_cols']:
                        msg += f"  Missing: {', '.join(diff['missing_cols'])}\n"
                    if diff['extra_cols']:
                        msg += f"  Extra: {', '.join(diff['extra_cols'])}\n"
                
                messagebox.showwarning("Header Validation Failed", msg)
                return
            
            self.show_loading("Consolidating ZMM files...")
            
            # Consolidate files
            consolidated_df = ZMMConsolidator.consolidate_zmm_files(filenames)
            
            self.hide_loading()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'ZMM_Consolidated_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving consolidated ZMM file...")
                consolidated_df.to_excel(save_path, index=False, engine='openpyxl')
                self.hide_loading()
                messagebox.showinfo("Success", 
                                  f"ZMM files consolidated!\n\n" +
                                  f"Files merged: {len(filenames)}\n" +
                                  f"Total rows: {len(consolidated_df):,}")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def merge_cji_data(self):
        """
        Merge CJI5 & CJI3 Data with Lookup (STEP 8)
        
        STEP 8 Implementation:
        1. Load both CJI5 and CJI3 pivot files
        2. Lookup duplicate values from CJI3 (Purchasing Doc) to CJI5 (Ref. Doc number)
        3. Remove duplicates if found
        4. Merge into single table with PO number & PO Amount
        """
        try:
            # Step 1: Select CJI5 Pivot File
            cji5_file = filedialog.askopenfilename(
                title="Select CJI5 Pivot File",
                filetypes=[("Excel Files", "*.xlsx *.xls")]
            )
            if not cji5_file:
                return
            
            # Step 2: Select CJI3 Pivot File
            cji3_file = filedialog.askopenfilename(
                title="Select CJI3 Pivot File",
                filetypes=[("Excel Files", "*.xlsx *.xls")]
            )
            if not cji3_file:
                return
            
            self.show_loading("Merging CJI5 & CJI3 data with lookup...")
            
            # Load both files
            cji5_pivot = pd.read_excel(cji5_file)
            cji3_pivot = pd.read_excel(cji3_file)
            
            # Rename columns for clarity
            cji5_pivot.columns = ['REF_DOC_NUM'] + [f'CJI5_{col}' if col != 'REF_DOC_NUM' else col for col in cji5_pivot.columns[1:]]
            cji3_pivot.columns = ['PURCH_DOC_NUM'] + [f'CJI3_{col}' if col != 'PURCH_DOC_NUM' else col for col in cji3_pivot.columns[1:]]
            
            # Step 3: Lookup for duplicates - Check if Purchasing Doc from CJI3 exists in CJI5 Ref Doc
            # This creates a new column in CJI3 pivot showing if there's a match in CJI5
            cji3_pivot['DUPLICATE_IN_CJI5'] = cji3_pivot['PURCH_DOC_NUM'].isin(cji5_pivot['REF_DOC_NUM']).apply(
                lambda x: 'YES' if x else 'N/A'
            )
            
            # Step 4: Separate duplicates from non-duplicates
            duplicates = cji3_pivot[cji3_pivot['DUPLICATE_IN_CJI5'] == 'YES'].copy()
            no_duplicates = cji3_pivot[cji3_pivot['DUPLICATE_IN_CJI5'] == 'N/A'].copy()
            
            # Step 5: For items without duplicates, merge CJI5 & CJI3
            # Merge CJI5 and non-duplicate CJI3 data
            merged_data = pd.concat([cji5_pivot, no_duplicates], axis=0, ignore_index=True)
            
            # Create output workbook
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'CJI_Merged_{timestamp}.xlsx'
            
            self.hide_loading()
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=output_filename,
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving merged CJI data...")
                
                # Reset indices to ensure clean data
                merged_data = merged_data.reset_index(drop=True)
                duplicates = duplicates.reset_index(drop=True)
                
                # Use openpyxl directly to avoid sheet visibility issues
                from openpyxl import Workbook
                
                wb = Workbook()
                wb.remove(wb.active)  # Remove default sheet
                
                # Sheet 1: Merged data
                ws1 = wb.create_sheet('Merged Data', 0)
                ws1.sheet_state = 'visible'
                
                # Write headers
                for c_idx, col in enumerate(merged_data.columns, 1):
                    ws1.cell(row=1, column=c_idx).value = col
                
                # Write data rows
                for r_idx, row_data in enumerate(merged_data.values, 2):
                    for c_idx, value in enumerate(row_data, 1):
                        ws1.cell(row=r_idx, column=c_idx).value = value
                
                # Sheet 2: Duplicates found (for review)
                ws2 = wb.create_sheet('Duplicates', 1)
                ws2.sheet_state = 'visible'
                
                # Write headers
                for c_idx, col in enumerate(duplicates.columns, 1):
                    ws2.cell(row=1, column=c_idx).value = col
                
                # Write data rows
                for r_idx, row_data in enumerate(duplicates.values, 2):
                    for c_idx, value in enumerate(row_data, 1):
                        ws2.cell(row=r_idx, column=c_idx).value = value
                
                # Sheet 3: Summary
                lookup_summary = pd.DataFrame({
                    'Item': ['Total CJI5 Records', 'Total CJI3 Records', 'Duplicates Found', 'Merged Records'],
                    'Count': [len(cji5_pivot), len(cji3_pivot), len(duplicates), len(merged_data)]
                })
                ws3 = wb.create_sheet('Summary', 2)
                ws3.sheet_state = 'visible'
                
                # Write headers
                for c_idx, col in enumerate(lookup_summary.columns, 1):
                    ws3.cell(row=1, column=c_idx).value = col
                
                # Write data rows
                for r_idx, row_data in enumerate(lookup_summary.values, 2):
                    for c_idx, value in enumerate(row_data, 1):
                        ws3.cell(row=r_idx, column=c_idx).value = value
                
                wb.save(save_path)
                
                self.hide_loading()
                self.status_var.set(f"Success! Merged file saved")
                messagebox.showinfo("Success", 
                                  f"CJI Data Merge Completed!\n\n" +
                                  f"Merge Summary:\n" +
                                  f"  • CJI5 Records: {len(cji5_pivot):,}\n" +
                                  f"  • CJI3 Records: {len(cji3_pivot):,}\n" +
                                  f"  • Duplicates Found: {len(duplicates):,}\n" +
                                  f"  • Final Merged Records: {len(merged_data):,}\n\n" +
                                  f"Sheets created:\n" +
                                  f"  1. Merged Data (CJI5 + CJI3 non-duplicates)\n" +
                                  f"  2. Duplicates (for manual review)\n" +
                                  f"  3. Summary (statistics)\n\n" +
                                  f"Note: Review duplicates sheet. Remove one if needed.")
        
        except Exception as e:
            self.hide_loading()
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error merging CJI data:\n\n{str(e)}")
    
    def create_wp_loa_tab(self):
        """Create WP LOA Report processing tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="WP LOA Report Processing")
        
        # Title
        title_frame = tk.Frame(tab, bg='#f0f0f0')
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title = tk.Label(title_frame, text="WP LOA Report Automation", 
                        font=("Segoe UI", 13, "bold"), bg='#f0f0f0', fg='#29348F')
        title.pack(anchor=tk.W)
        
        desc = tk.Label(title_frame, 
                       text="Automate VLOOKUP operations, filtering, and derived column generation for WP LOA reports",
                       font=("Segoe UI", 8), bg='#f0f0f0', fg='#666')
        desc.pack(anchor=tk.W)
        
        # Main content frame
        content = tk.Frame(tab, bg='#f0f0f0')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Step 1: Select main WP LOA file
        file_frame = tk.LabelFrame(content, text="Step 1: Select WP LOA Report File", 
                                  font=("Segoe UI", 10, "bold"), bg='#f0f0f0',
                                  fg='#29348F', padx=15, pady=15)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.wp_loa_file_path = tk.StringVar(value="No file selected")
        file_label = tk.Label(file_frame, textvariable=self.wp_loa_file_path,
                             font=("Segoe UI", 8), bg='#f0f0f0', fg='#555')
        file_label.pack(side=tk.LEFT, pady=5, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Browse...", 
                              command=self.browse_wp_loa_file,
                              font=("Segoe UI", 8), bg='#29348F', fg='white',
                              padx=15, relief=tk.FLAT, cursor="hand2")
        browse_btn.pack(side=tk.LEFT)
        
        # Step 2: External files (optional)
        extern_frame = tk.LabelFrame(content, text="Step 2: Load External Reference Files", 
                                    font=("Segoe UI", 10, "bold"), bg='#f0f0f0',
                                    fg='#29348F', padx=15, pady=15)
        extern_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # CAPEX AVAILMENT file
        avail_frame = tk.Frame(extern_frame, bg='#f0f0f0')
        avail_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(avail_frame, text="CAPEX AVAILMENT File:", 
                font=("Segoe UI", 8), bg='#f0f0f0', fg='#333').pack(side=tk.LEFT)
        
        self.availment_file_path = tk.StringVar(value="Not selected")
        tk.Label(avail_frame, textvariable=self.availment_file_path,
                font=("Segoe UI", 8), bg='#f0f0f0', fg='#999').pack(side=tk.LEFT, padx=10)
        
        tk.Button(avail_frame, text="Browse", 
                 command=self.browse_availment_file,
                 font=("Segoe UI", 7), bg='#29348F', fg='white',
                 padx=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)
        
        tk.Button(avail_frame, text="Clear", 
                 command=lambda: self.availment_file_path.set("Not selected"),
                 font=("Segoe UI", 7), bg='#999', fg='white',
                 padx=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # LOA Current Approver file
        loa_frame = tk.Frame(extern_frame, bg='#f0f0f0')
        loa_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(loa_frame, text="LOA Current Approver File:", 
                font=("Segoe UI", 8), bg='#f0f0f0', fg='#333').pack(side=tk.LEFT)
        
        self.loa_approver_file_path = tk.StringVar(value="Not selected")
        tk.Label(loa_frame, textvariable=self.loa_approver_file_path,
                font=("Segoe UI", 8), bg='#f0f0f0', fg='#999').pack(side=tk.LEFT, padx=10)
        
        tk.Button(loa_frame, text="Browse", 
                 command=self.browse_loa_approver_file,
                 font=("Segoe UI", 7), bg='#29348F', fg='white',
                 padx=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)
        
        tk.Button(loa_frame, text="Clear", 
                 command=lambda: self.loa_approver_file_path.set("Not selected"),
                 font=("Segoe UI", 7), bg='#999', fg='white',
                 padx=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Processing options
        options_frame = tk.LabelFrame(content, text="Processing Options", 
                                     font=("Segoe UI", 10, "bold"), bg='#f0f0f0',
                                     fg='#29348F', padx=15, pady=15)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_mga_mia = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Filter for MGA/MIA PR numbers only",
                      variable=self.filter_mga_mia, font=("Segoe UI", 8),
                      bg='#f0f0f0', fg='#333').pack(anchor=tk.W, pady=3)
        
        self.filter_year_26 = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Filter out year 2026",
                      variable=self.filter_year_26, font=("Segoe UI", 8),
                      bg='#f0f0f0', fg='#333').pack(anchor=tk.W, pady=3)
        
        # LOA CURRENT APPROVER section
        loa_approver_frame = tk.LabelFrame(content, text="LOA CURRENT APPROVER Processing", 
                                          font=("Segoe UI", 10, "bold"), bg='#f0f0f0',
                                          fg='#29348F', padx=15, pady=15)
        loa_approver_frame.pack(fill=tk.X, pady=(10, 10))
        
        # Row 1: LOA CURRENT APPROVER file selection
        loa_row1 = tk.Frame(loa_approver_frame, bg='#f0f0f0')
        loa_row1.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(loa_row1, text="LOA CURRENT APPROVER File:", font=("Segoe UI", 8), 
                bg='#f0f0f0', fg='#333').pack(side=tk.LEFT, padx=(0, 5))
        
        self.loa_approver_file_path_input = tk.StringVar(value="No file selected")
        loa_approver_label = tk.Label(loa_row1, textvariable=self.loa_approver_file_path_input,
                                      font=("Segoe UI", 8), bg='#f0f0f0', fg='#999')
        loa_approver_label.pack(side=tk.LEFT, pady=5, padx=(0, 10))
        
        browse_approver_btn = tk.Button(loa_row1, text="Browse", 
                                       command=self.browse_loa_approver_file_for_processing,
                                       font=("Segoe UI", 8), bg='#29348F', fg='white',
                                       padx=12, relief=tk.FLAT, cursor="hand2")
        browse_approver_btn.pack(side=tk.LEFT)
        
        # Row 2: Reference WP LOA Report file selection
        loa_row2 = tk.Frame(loa_approver_frame, bg='#f0f0f0')
        loa_row2.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(loa_row2, text="Processed WP LOA Report File:", font=("Segoe UI", 8), 
                bg='#f0f0f0', fg='#333').pack(side=tk.LEFT, padx=(0, 5))
        
        self.loa_reference_file_path_input = tk.StringVar(value="No file selected")
        loa_reference_label = tk.Label(loa_row2, textvariable=self.loa_reference_file_path_input,
                                       font=("Segoe UI", 8), bg='#f0f0f0', fg='#999')
        loa_reference_label.pack(side=tk.LEFT, pady=5, padx=(0, 10))
        
        browse_reference_btn = tk.Button(loa_row2, text="Browse", 
                                        command=self.browse_loa_reference_file,
                                        font=("Segoe UI", 8), bg='#29348F', fg='white',
                                        padx=12, relief=tk.FLAT, cursor="hand2")
        browse_reference_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_reference_btn = tk.Button(loa_row2, text="Clear", 
                                       command=lambda: self.loa_reference_file_path_input.set("No file selected"),
                                       font=("Segoe UI", 8), bg='#999', fg='white',
                                       padx=12, relief=tk.FLAT, cursor="hand2")
        clear_reference_btn.pack(side=tk.LEFT)
        
        # Row 3: Process button
        loa_row3 = tk.Frame(loa_approver_frame, bg='#f0f0f0')
        loa_row3.pack(fill=tk.X)
        
        process_approver_btn = tk.Button(loa_row3, text="Process LOA Current Approver", 
                                        command=self.process_loa_current_approver_threaded,
                                        font=("Segoe UI", 8, "bold"), 
                                        bg='#6a1b9a', fg='white', padx=15,
                                        relief=tk.FLAT, cursor="hand2")
        process_approver_btn.pack(side=tk.LEFT)
        
        # Process button
        button_frame = tk.Frame(content, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=15)
        
        process_btn = tk.Button(button_frame, text="Process WP LOA Report", 
                               command=self.process_wp_loa_threaded,
                               font=("Segoe UI", 10, "bold"), 
                               bg='#29348F', fg='white', padx=20, pady=10,
                               relief=tk.FLAT, cursor="hand2")
        process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(button_frame, text="Clear All", 
                             command=self.clear_wp_loa_form,
                             font=("Segoe UI", 9), 
                             bg='#999', fg='white', padx=15, pady=10,
                             relief=tk.FLAT, cursor="hand2")
        clear_btn.pack(side=tk.LEFT)
    
    def browse_wp_loa_file(self):
        """Browse for WP LOA report file"""
        file = filedialog.askopenfilename(
            title="Select WP LOA Report File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.wp_loa_file_path.set(file)
            self.status_var.set(f"Selected: {os.path.basename(file)}")
    
    def browse_availment_file(self):
        """Browse for CAPEX AVAILMENT file"""
        file = filedialog.askopenfilename(
            title="Select 2026 CAPEX AVAILMENT File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.availment_file_path.set(file)
    
    def browse_loa_approver_file_for_processing(self):
        """Browse for LOA CURRENT APPROVER file for processing"""
        file = filedialog.askopenfilename(
            title="Select LOA CURRENT APPROVER File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.loa_approver_file_path_input.set(file)
            self.status_var.set(f"Selected: {os.path.basename(file)}")
    
    def browse_loa_reference_file(self):
        """Browse for processed WP LOA report file"""
        file = filedialog.askopenfilename(
            title="Select Processed WP LOA Report File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.loa_reference_file_path_input.set(file)
            self.status_var.set(f"Reference file selected: {os.path.basename(file)}")
    
    def clear_wp_loa_form(self):
        """Clear all WP LOA form fields"""
        self.wp_loa_file_path.set("No file selected")
        self.availment_file_path.set("Not selected")
        self.loa_approver_file_path.set("Not selected")
        self.loa_approver_file_path_input.set("No file selected")
        self.loa_reference_file_path_input.set("No file selected")
        self.status_var.set("Form cleared")
    
    def process_loa_current_approver_threaded(self):
        """Process LOA CURRENT APPROVER file in background thread"""
        if self.loa_approver_file_path_input.get() == "No file selected":
            messagebox.showerror("Error", "Please select a LOA CURRENT APPROVER file first")
            return
        
        thread = threading.Thread(target=self.process_loa_current_approver, daemon=True)
        thread.start()
    
    def process_loa_current_approver(self):
        """Process LOA CURRENT APPROVER file with formulas and formatting"""
        try:
            self.show_loading("Processing LOA CURRENT APPROVER file... Adding formulas and columns")
            
            loa_file = self.loa_approver_file_path_input.get()
            reference_file = self.loa_reference_file_path_input.get()
            
            # If reference file is not selected, set to None
            if reference_file == "No file selected":
                reference_file = None
            
            # Create formula processor and process the file
            processor = WPLOAFormulaProcessor(loa_file)
            
            # Process LOA CURRENT APPROVER file - returns tuple (success, output_path_or_error)
            success, result = processor.process_loa_current_approver(loa_file, reference_file_path=reference_file)
            
            if success:
                self.hide_loading()
                output_path = result
                
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                self.status_var.set(f"Success! LOA CURRENT APPROVER processed")
                messagebox.showinfo("Success",
                                  f"LOA CURRENT APPROVER Processed Successfully!\n\n" +
                                  f"File: {os.path.basename(output_path)}\n" +
                                  f"Location: {os.path.dirname(output_path)}\n" +
                                  f"Size: {file_size:.1f} MB\n\n" +
                                  f"Columns Added (L-AD):\n" +
                                  f"  • PID (Mother and Sub) - L\n" +
                                  f"  • 1, YEAR, 3 - M-O\n" +
                                  f"  • L1, L2 - P-Q\n" +
                                  f"  • PROGRAM MBR, DIV, DEP, FUNDING - R-U\n" +
                                  f"  • Network Classif - X (from BUDGET)\n" +
                                  f"  • PROPONENT, DIV IN REPORT, PROGRAM IN REPORT - Y-AA\n" +
                                  f"  • PROJ, SUBPROJ - AB-AC\n" +
                                  f"  • Current Approver 1 (formatted name) - AD\n\n" +
                                  f"All columns contain formulas for auto-calculation\n\n" +
                                  f"File saved as _Processed version (original file not modified)")
            else:
                self.hide_loading()
                error_msg = result
                messagebox.showerror("Error", f"Failed to process LOA CURRENT APPROVER file:\n\n{error_msg}")
                self.status_var.set("Processing failed")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error processing LOA CURRENT APPROVER:\n\n{str(e)}")
            self.status_var.set("Error during processing")
    
    def browse_loa_approver_file(self):
        """Browse for LOA Current Approver file"""
        file = filedialog.askopenfilename(
            title="Select LOA_CURRENT_APPROVER File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.loa_approver_file_path.set(file)
    
    def process_wp_loa_threaded(self):
        """Process WP LOA report in background thread"""
        if self.wp_loa_file_path.get() == "No file selected":
            messagebox.showerror("Error", "Please select a WP LOA Report file first")
            return
        
        thread = threading.Thread(target=self.process_wp_loa, daemon=True)
        thread.start()
    
    def process_wp_loa(self):
        """Process WP LOA report with Excel formulas"""
        try:
            self.show_loading("Processing WP LOA Report... Creating formulas")
            
            # Get file paths
            main_file = self.wp_loa_file_path.get()
            availment_file = None if self.availment_file_path.get() == "Not selected" else self.availment_file_path.get()
            loa_approver_file = None if self.loa_approver_file_path.get() == "Not selected" else self.loa_approver_file_path.get()
            
            # Create formula processor
            processor = WPLOAFormulaProcessor(main_file)
            
            # Process file and save with formulas
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'WP_LOA_Processed_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if temp_save_path:
                success = processor.process_and_save(temp_save_path, availment_file, loa_approver_file)
                
                if success:
                    self.hide_loading()
                    
                    summary = processor.get_summary()
                    
                    summary_text = "WP LOA Report Processed Successfully!\n\n"
                    summary_text += f"Total rows: {summary['total_rows']}\n"
                    summary_text += f"Columns added: {summary['columns_added']}\n"
                    summary_text += f"Output type: {summary['output_type']}\n"
                    summary_text += f"Column range: {summary.get('column_range', 'K-AA')}\n\n"
                    summary_text += "Formulas created in columns K-AA:\n"
                    summary_text += "  • K: PID (copy from H)\n"
                    summary_text += "  • L, M, N: User-entered L1 components\n"
                    summary_text += "  • O: L1 formula (L&\"-\"&M&\"-\"&N)\n"
                    summary_text += "  • P: L2 (copy from H)\n"
                    summary_text += "  • Q-U: PROGRAM_MBR, DIV, DEP, FUNDING, CFU_SPONSOR\n"
                    summary_text += "  • V-X: AVAILMENT_TRACKER, PROPONENT, PROPONENT_1\n"
                    summary_text += "  • Y-AA: DIV_IN_REPORT, PROJ, SUBPROJ\n\n"
                    summary_text += "All VLOOKUP formulas use IFERROR() for safe lookups\n"
                    summary_text += "Formulas are preserved in output file\n"
                    summary_text += "Edit columns L, M, N as needed - formulas auto-update"
                    
                    messagebox.showinfo("Success", summary_text)
                    self.status_var.set(f"WP LOA processing complete - {summary['total_rows']} rows with formulas")
                else:
                    self.hide_loading()
                    messagebox.showerror("Error", "Failed to process file")
                    self.status_var.set("Processing failed")
            else:
                self.hide_loading()
                self.status_var.set("Processing cancelled by user")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error processing WP LOA report:\n\n{str(e)}")
            self.status_var.set("Error during processing")


def main():
    # Check for updates in background (silently downloads if available)
    check_updates_on_startup(VERSION, VERSION_CHECK_URL)
    
    root = tk.Tk()
    app = CAPEXReportingApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
