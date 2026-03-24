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
import platform
import subprocess

try:
    import winreg
except ImportError:
    winreg = None

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
        self.root.title(f"CAPEX Reporting Automation Tool v{VERSION}")
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
        title = tk.Label(main_frame, text="CAPEX Reporting Automation Tool", 
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
        self._apply_system_theme()

    def _pick_single_input_file(self, title, filetypes):
        """Pick one input file from a file dialog."""
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    def _pick_multiple_input_files(self, title, filetypes, min_count=2):
        """Pick multiple input files from a file dialog."""
        return filedialog.askopenfilenames(title=title, filetypes=filetypes)

    def _detect_system_dark_mode(self):
        """Detect if the OS is currently using dark mode."""
        try:
            system_name = platform.system()

            if system_name == 'Windows' and winreg is not None:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                ) as reg_key:
                    # 0 = dark mode, 1 = light mode
                    apps_use_light_theme, _ = winreg.QueryValueEx(reg_key, 'AppsUseLightTheme')
                    return apps_use_light_theme == 0

            if system_name == 'Darwin':
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return result.returncode == 0 and result.stdout.strip().lower() == 'dark'
        except Exception:
            pass

        return False

    def _map_theme_color(self, color_value, is_background=True):
        """Map hardcoded light colors to dark-mode-friendly colors."""
        if not color_value:
            return None

        color_key = str(color_value).strip().lower()

        background_map = {
            '#f0f0f0': '#1f2329',
            '#ffffff': '#2a2f36',
            '#e8e8e8': '#171b20',
            '#29348f': '#7fa7ff',
            '#6a1b9a': '#b388ff',
            '#757575': '#5e6673',
            '#999': '#6b7481',
            '#999999': '#6b7481',
            '#e65100': '#ff8a3d',
            'white': '#2a2f36',
            'systembuttonface': '#1f2329'
        }

        foreground_map = {
            '#29348f': '#9cb8ff',
            '#6a1b9a': '#ccb3ff',
            '#333': '#eceff4',
            '#333333': '#eceff4',
            '#555': '#c4cad4',
            '#555555': '#c4cad4',
            '#666': '#b5bdc8',
            '#666666': '#b5bdc8',
            '#999': '#a6b0bf',
            '#999999': '#a6b0bf',
            'systembuttontext': '#eceff4'
        }

        theme_map = background_map if is_background else foreground_map
        return theme_map.get(color_key)

    def _apply_theme_to_widget_tree(self, widget):
        """Recursively apply dark-mode mapping to existing Tk widgets."""
        config_updates = {}

        # Background-like properties
        for prop in ('bg', 'background', 'activebackground', 'highlightbackground', 'selectbackground'):
            if prop in widget.keys():
                mapped = self._map_theme_color(widget.cget(prop), is_background=True)
                if mapped:
                    config_updates[prop] = mapped

        # Foreground-like properties
        for prop in ('fg', 'foreground', 'activeforeground', 'disabledforeground', 'insertbackground', 'selectforeground'):
            if prop in widget.keys():
                mapped = self._map_theme_color(widget.cget(prop), is_background=False)
                if mapped:
                    config_updates[prop] = mapped

        if config_updates:
            try:
                widget.configure(**config_updates)
            except tk.TclError:
                pass

        for child in widget.winfo_children():
            self._apply_theme_to_widget_tree(child)

    def _apply_system_theme(self):
        """Apply theme adaptation based on OS light/dark mode setting."""
        is_dark_mode = self._detect_system_dark_mode()
        if not is_dark_mode:
            return

        # TTK styling for notebook/progressbar in dark mode.
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure('TFrame', background='#1f2329')
        style.configure('TNotebook', background='#1f2329', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2a2f36', foreground='#eceff4', padding=(10, 4))
        style.map(
            'TNotebook.Tab',
            background=[('selected', '#3a4250')],
            foreground=[('selected', '#ffffff')]
        )
        style.configure('Horizontal.TProgressbar', troughcolor='#2a2f36', background='#7fa7ff')

        self._apply_theme_to_widget_tree(self.root)

    def _show_success(self, process_name, output_path=None, metrics=None, notes=None):
        """Show clean, consistent success messages across all processing flows."""
        lines = [f"{process_name} completed."]

        if output_path:
            lines.append("")
            lines.append(f"File: {os.path.basename(output_path)}")
            lines.append(f"Location: {os.path.dirname(output_path)}")
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                lines.append(f"Size: {file_size:.1f} MB")

        if metrics:
            lines.append("")
            for label, value in metrics:
                lines.append(f"{label}: {value}")

        if notes:
            lines.append("")
            for note in notes:
                lines.append(f"- {note}")

        messagebox.showinfo('Success', '\n'.join(lines))
    

    
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
        filename = self._pick_single_input_file(
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
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)}")
                self._show_success(
                    process_name=f"{file_type.upper()} processing",
                    output_path=save_path,
                    metrics=[('Rows', f'{row_count:,}')],
                    notes=['Formulas are included in the output file.']
                )
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
        filename = self._pick_single_input_file(
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

                self.status_var.set(f"Success! {file_type.upper()} with pivot saved")
                self._show_success(
                    process_name=f"{file_type.upper()} pivot processing",
                    output_path=save_path,
                    notes=['Includes 2 sheets: Processed Data and Pivot Table.']
                )

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
        filename = self._pick_single_input_file(
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
                self._show_success(
                    process_name='Car Plan extraction',
                    output_path=save_path,
                    metrics=[('Rows', f'{len(carplan_df):,}')]
                )
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def process_cji5_no_carplan(self):
        """Process CJI5 without car plan (STEP 14)"""
        filename = self._pick_single_input_file(
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
                self._show_success(
                    process_name='CJI5 processing (without Car Plan)',
                    output_path=save_path,
                    metrics=[
                        ('Car Plan entries removed', f'{removed_count:,}'),
                        ('Remaining rows', f'{len(df):,}')
                    ]
                )
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def remove_cbip(self):
        """Remove CBIP entries from RFP/Reclass (STEP 12-13)"""
        filename = self._pick_single_input_file(
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
                self._show_success(
                    process_name=f"{file_type.upper()} cleanup",
                    output_path=save_path,
                    metrics=[
                        ('Removed rows', f'{removed:,}'),
                        ('Remaining rows', f'{len(processor.df):,}')
                    ]
                )
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def consolidate_zmm_files(self):
        """Consolidate multiple ZMM files (STEP 1)"""
        filenames = self._pick_multiple_input_files(
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
                self._show_success(
                    process_name='ZMM consolidation',
                    output_path=save_path,
                    metrics=[
                        ('Files merged', len(filenames)),
                        ('Total rows', f'{len(consolidated_df):,}')
                    ]
                )
        
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
            cji5_file = self._pick_single_input_file(
                title="Select CJI5 Pivot File",
                filetypes=[("Excel Files", "*.xlsx *.xls")]
            )
            if not cji5_file:
                return
            
            # Step 2: Select CJI3 Pivot File
            cji3_file = self._pick_single_input_file(
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
                self._show_success(
                    process_name='CJI data merge',
                    output_path=save_path,
                    metrics=[
                        ('CJI5 records', f'{len(cji5_pivot):,}'),
                        ('CJI3 records', f'{len(cji3_pivot):,}'),
                        ('Duplicates found', f'{len(duplicates):,}'),
                        ('Merged records', f'{len(merged_data):,}')
                    ],
                    notes=['Includes 3 sheets: Merged Data, Duplicates, and Summary.']
                )
        
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

        # Keep WP LOA actions near Step 1 to avoid confusion with LOA Current Approver processing.
        wp_loa_actions = tk.Frame(file_frame, bg='#f0f0f0')
        wp_loa_actions.pack(side=tk.RIGHT)

        browse_btn = tk.Button(wp_loa_actions, text="Browse...",
                      command=self.browse_wp_loa_file,
                      font=("Segoe UI", 8), bg='#29348F', fg='white',
                      padx=12, relief=tk.FLAT, cursor="hand2")
        browse_btn.pack(side=tk.LEFT, padx=(0, 6))

        clear_btn = tk.Button(wp_loa_actions, text="Clear",
                     command=self.clear_wp_loa_main_file,
                     font=("Segoe UI", 8),
                     bg='#999', fg='white', padx=12,
                     relief=tk.FLAT, cursor="hand2")
        clear_btn.pack(side=tk.LEFT)
        
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

        # Step 3: Process WP LOA report (placed after external references to reduce confusion)
        process_wp_loa_frame = tk.Frame(content, bg='#f0f0f0')
        process_wp_loa_frame.pack(fill=tk.X, pady=(0, 10))

        process_btn = tk.Button(process_wp_loa_frame, text="Process WP LOA Report",
                       command=self.process_wp_loa_threaded,
                       font=("Segoe UI", 9, "bold"),
                       bg='#29348F', fg='white', padx=15, pady=6,
                       relief=tk.FLAT, cursor="hand2")
        process_btn.pack(side=tk.LEFT, padx=(0, 6))

        clear_all_btn = tk.Button(process_wp_loa_frame, text="Clear All",
                      command=self.clear_wp_loa_form,
                      font=("Segoe UI", 9),
                      bg='#999', fg='white', padx=12, pady=6,
                      relief=tk.FLAT, cursor="hand2")
        clear_all_btn.pack(side=tk.LEFT)
        
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
        
        # Row 2: Process button (removed reference file - now uses BUDGET sheet only)
        loa_row2 = tk.Frame(loa_approver_frame, bg='#f0f0f0')
        loa_row2.pack(fill=tk.X, pady=(10, 0))
        
        process_approver_btn = tk.Button(loa_row2, text="Process LOA Current Approver", 
                                        command=self.process_loa_current_approver_threaded,
                                        font=("Segoe UI", 8, "bold"), 
                                        bg='#6a1b9a', fg='white', padx=15,
                                        relief=tk.FLAT, cursor="hand2")
        process_approver_btn.pack(side=tk.LEFT, padx=(0, 6))

        clear_approver_btn = tk.Button(loa_row2, text="Clear",
                           command=self.clear_loa_current_approver_selection,
                           font=("Segoe UI", 8),
                           bg='#999', fg='white', padx=12,
                           relief=tk.FLAT, cursor="hand2")
        clear_approver_btn.pack(side=tk.LEFT)
        
    def browse_wp_loa_file(self):
        """Browse for WP LOA report file"""
        file = self._pick_single_input_file(
            title="Select WP LOA Report File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.wp_loa_file_path.set(file)
            self.status_var.set(f"Selected: {os.path.basename(file)}")

    def clear_wp_loa_main_file(self):
        """Clear only the selected WP LOA report file."""
        self.wp_loa_file_path.set("No file selected")
        self.status_var.set("WP LOA file selection cleared")
    
    def browse_availment_file(self):
        """Browse for CAPEX AVAILMENT file"""
        file = self._pick_single_input_file(
            title="Select 2026 CAPEX AVAILMENT File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.availment_file_path.set(file)
    
    def browse_loa_approver_file_for_processing(self):
        """Browse for LOA CURRENT APPROVER file for processing"""
        file = self._pick_single_input_file(
            title="Select LOA CURRENT APPROVER File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file:
            self.loa_approver_file_path_input.set(file)
            self.status_var.set(f"Selected: {os.path.basename(file)}")

    def clear_loa_current_approver_selection(self):
        """Clear LOA CURRENT APPROVER processing file selection only."""
        self.loa_approver_file_path_input.set("No file selected")
        self.status_var.set("LOA CURRENT APPROVER file selection cleared")
    
    def clear_wp_loa_form(self):
        """Clear all WP LOA form fields"""
        self.wp_loa_file_path.set("No file selected")
        self.availment_file_path.set("Not selected")
        self.loa_approver_file_path.set("Not selected")
        self.loa_approver_file_path_input.set("No file selected")
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
            
            # Create formula processor and process the file
            processor = WPLOAFormulaProcessor(loa_file)
            
            # Process LOA CURRENT APPROVER file - returns tuple (success, output_path_or_error)
            # Always uses BUDGET sheet from the same workbook for lookups
            success, result = processor.process_loa_current_approver(loa_file)
            
            if success:
                self.hide_loading()
                output_path = result
                
                self.status_var.set(f"Success! LOA CURRENT APPROVER processed")
                self._show_success(
                    process_name='LOA CURRENT APPROVER processing',
                    output_path=output_path,
                    metrics=[('Columns added/updated', 'L-AD')],
                    notes=[
                        'Lookups reference the BUDGET sheet in the same file.',
                        'Original file is not modified.'
                    ]
                )
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
        file = self._pick_single_input_file(
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
                    self._show_success(
                        process_name='WP LOA report processing',
                        output_path=temp_save_path,
                        metrics=[
                            ('Total rows', summary['total_rows']),
                            ('Columns added', summary['columns_added']),
                            ('Column range', summary.get('column_range', 'K-AA'))
                        ],
                        notes=['Formulas are preserved and recalculate in Excel.']
                    )
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
