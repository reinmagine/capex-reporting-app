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
                                      text="Merge CJI5 & CJI3 Data (Priority 3)", 
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
                # Save the workbook with formulas
                processor.wb.save(save_path)
                
                file_size = os.path.getsize(save_path) / (1024 * 1024)
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", 
                                  f"File processed successfully with FORMULAS!\n\n" +
                                  f"File: {os.path.basename(save_path)}\n" +
                                  f"Size: {file_size:.1f} MB\n" +
                                  f"Rows: {row_count:,}\n\n" +
                                  f"✓ All formulas retained - Excel will calculate on open\n" +
                                  f"✓ Processing took only seconds!")
            else:
                self.status_var.set("Save cancelled")
            
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
        """Process file with pivot table (STEP 6-7)"""
        filename = filedialog.askopenfilename(
            title=f"Select {file_type.upper()} File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading(f"Processing {file_type.upper()} with pivot table...")
            
            processor = CJIProcessor(file_type)
            processor.load_file(filename)
            processor.validate_and_prepare()
            df, pivot = processor.process_with_pivot(self.exchange_rates)
            
            output_name = f'{file_type.upper()}_with_Pivot'
            
            self.hide_loading()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'{output_name}_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving file with pivot table...")
                
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Processed Data', index=False)
                    pivot.to_excel(writer, sheet_name='Pivot Table')
                
                self.hide_loading()
                
                self.status_var.set(f"Success! Saved with pivot table")
                messagebox.showinfo("Success", 
                                  f"File processed with pivot table!\n\n" +
                                  f"{os.path.basename(save_path)}\n" +
                                  f"Sheets: Processed Data, Pivot Table")
        
        except Exception as e:
            self.hide_loading()
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error: {str(e)}")
    
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
                carplan_df.to_excel(save_path, index=False, engine='openpyxl')
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
                processor.save(save_path)
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
                processor.save(save_path)
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
                consolidated_df.to_excel(save_path, index=False, engine='openpyxl')
                messagebox.showinfo("Success", 
                                  f"ZMM files consolidated!\n\n" +
                                  f"Files merged: {len(filenames)}\n" +
                                  f"Total rows: {len(consolidated_df):,}")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def merge_cji_data(self):
        """Merge CJI5 and CJI3 data (STEP 8)"""
        messagebox.showinfo("Coming Soon", 
                          "CJI Data Merge (STEP 8) is under development.\n\n" +
                          "This will implement:\n" +
                          "- Paste CJI5 pivot to CJI3\n" +
                          "- Lookup duplicate Purchasing Doc\n" +
                          "- Remove duplicates\n" +
                          "- Merge into single table\n\n" +
                          "Expected Priority 3")
    
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
    
    def browse_loa_approver_file(self):
        """Browse for LOA Current Approver file"""
        file = filedialog.askopenfilename(
            title="Select LOA_CURRENT_APPROVER File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.loa_approver_file_path.set(file)
    
    def clear_wp_loa_form(self):
        """Clear all WP LOA form fields"""
        self.wp_loa_file_path.set("No file selected")
        self.availment_file_path.set("Not selected")
        self.loa_approver_file_path.set("Not selected")
        self.status_var.set("Form cleared")
    
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
                    summary_text += "✓ All VLOOKUP formulas use IFERROR() for safe lookups\n"
                    summary_text += "✓ Formulas are preserved in output file\n"
                    summary_text += "✓ Edit columns L, M, N as needed - formulas auto-update"
                    
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
