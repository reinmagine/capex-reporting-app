"""
CAPEX Reporting Tool - Desktop Application
Refactored version using modular processors and utilities
Implements PRIORITY 1 fixes: Unified code, modular structure, file validation
"""
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
from utils.validators import FileValidator
from config import EXCHANGE_RATES


def get_live_exchange_rates():
    """Fetch live exchange rates from API"""
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        data = response.json()
        
        if 'rates' in data:
            php_rate = data['rates'].get('PHP', 57)
            sgd_rate = data['rates'].get('SGD', 1.34)
            
            return {
                'PHP_TO_USD': 1 / php_rate,
                'SGD_TO_USD': 1 / sgd_rate,
                'PHP': php_rate,
                'SGD': sgd_rate,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except:
        pass
    
    return {
        'PHP_TO_USD': 1/57,
        'SGD_TO_USD': 1/1.34,
        'PHP': 57,
        'SGD': 1.34,
        'timestamp': 'Offline (using default rates)'
    }


class CAPEXReportingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAPEX Reporting Tool")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Fetch exchange rates on startup
        self.exchange_rates = get_live_exchange_rates()
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="CAPEX Reporting Tool", 
                        font=("Segoe UI", 24, "bold"), bg='#f0f0f0', fg='#1e3c72')
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(main_frame, 
                           text="Refactored", 
                           font=("Segoe UI", 10), bg='#f0f0f0', fg='#666')
        subtitle.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_basic_tab()
        self.create_advanced_tab()
        self.create_consolidation_tab()
        
        # Loading frame (initially hidden)
        self.loading_frame = tk.Frame(root, bg='white', bd=2, relief=tk.RAISED)
        self.loading_label = tk.Label(self.loading_frame, 
                                     text="Processing file, please wait...", 
                                     font=("Segoe UI", 12, "bold"), 
                                     bg='white', fg='#1e3c72', pady=20, padx=40)
        self.loading_label.pack()
        
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 20), padx=40)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(root, textvariable=self.status_var, 
                            font=("Segoe UI", 9), bg='#e3f2fd', 
                            fg='#1976d2', anchor=tk.W, padx=10, pady=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Exchange rates info
        rates_text = self.get_rates_display_text()
        self.rates_label = tk.Label(root, text=rates_text, font=("Segoe UI", 9), 
                                   bg='#fff3cd', fg='#856404', padx=10, pady=5)
        self.rates_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Refresh rates button
        refresh_frame = tk.Frame(root, bg='#fff3cd')
        refresh_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        refresh_btn = tk.Button(refresh_frame, text="Refresh Exchange Rates", 
                               command=self.refresh_rates, font=("Segoe UI", 8),
                               bg='#ffc107', fg='#000', padx=10, pady=2,
                               relief=tk.FLAT, cursor="hand2")
        refresh_btn.pack(pady=2)
        
        self.selected_file = None
    
    def get_rates_display_text(self):
        """Get formatted exchange rates display text"""
        php_rate = self.exchange_rates.get('PHP', 57)
        sgd_rate = self.exchange_rates.get('SGD', 1.34)
        timestamp = self.exchange_rates.get('timestamp', 'Unknown')
        
        return f"Exchange Rates ({timestamp}): 1 USD = {php_rate:.4f} PHP | 1 USD = {sgd_rate:.4f} SGD"
    
    def refresh_rates(self):
        """Refresh exchange rates from API"""
        self.status_var.set("Fetching live exchange rates...")
        self.root.update()
        
        self.exchange_rates = get_live_exchange_rates()
        rates_text = self.get_rates_display_text()
        self.rates_label.config(text=rates_text)
        
        self.status_var.set("Exchange rates updated!")
        messagebox.showinfo("Success", 
                          f"Exchange rates updated!\n\n" +
                          f"1 USD = {self.exchange_rates['PHP']:.4f} PHP\n" +
                          f"1 USD = {self.exchange_rates['SGD']:.4f} SGD")
    
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
                                  font=("Segoe UI", 11, "bold"), bg='#f0f0f0', 
                                  fg='#1e3c72', padx=15, pady=15)
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
                               value=value, font=("Segoe UI", 10), bg='#f0f0f0',
                               activebackground='#f0f0f0', pady=3)
            rb.pack(anchor=tk.W)
        
        # File selection
        file_frame = tk.Frame(tab, bg='#f0f0f0')
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.file_path = tk.StringVar(value="No file selected")
        file_label = tk.Label(file_frame, textvariable=self.file_path, 
                             font=("Segoe UI", 9), bg='#f0f0f0', fg='#333')
        file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Browse File", 
                              command=self.browse_file, font=("Segoe UI", 10, "bold"),
                              bg='#2a5298', fg='white', padx=15, pady=8,
                              relief=tk.FLAT, cursor="hand2")
        browse_btn.pack(side=tk.RIGHT)
        
        # Process button
        self.process_btn = tk.Button(tab, text="Process File", 
                                     command=self.process_file_threaded, 
                                     font=("Segoe UI", 12, "bold"),
                                     bg='#28a745', fg='white', padx=30, pady=12,
                                     relief=tk.FLAT, cursor="hand2", state=tk.DISABLED)
        self.process_btn.pack(pady=10)
    
    def create_advanced_tab(self):
        """Create advanced features tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Advanced (STEP 6-7, 12-14, 1)")
        
        adv_frame = tk.LabelFrame(tab, text="Advanced Processing Options", 
                                 font=("Segoe UI", 11, "bold"), bg='#f0f0f0', 
                                 fg='#1e3c72', padx=15, pady=15)
        adv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pivot table generation (STEP 6-7)
        pivot_label = tk.Label(adv_frame, text="Pivot Table Generation (STEP 6-7):", 
                              font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        pivot_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.pivot_cji5_btn = tk.Button(adv_frame, text="Process CJI5 with Pivot Table", 
                                       command=lambda: self.process_with_pivot_threaded('cji5'),
                                       font=("Segoe UI", 10), bg='#17a2b8', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji5_btn.pack(fill=tk.X, pady=2)
        
        self.pivot_cji3_btn = tk.Button(adv_frame, text="Process CJI3 with Pivot Table", 
                                       command=lambda: self.process_with_pivot_threaded('cji3'),
                                       font=("Segoe UI", 10), bg='#17a2b8', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji3_btn.pack(fill=tk.X, pady=2)
        
        # Filtering options
        filter_label = tk.Label(adv_frame, text="\nFiltering & Special Processing:", 
                               font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        filter_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.filter_gnt_btn = tk.Button(adv_frame, text="Filter GNT-OTACP-25 Car Plan (STEP 1, 9-10)", 
                                       command=self.filter_carplan,
                                       font=("Segoe UI", 10), bg='#6c757d', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.filter_gnt_btn.pack(fill=tk.X, pady=2)
        
        self.no_carplan_btn = tk.Button(adv_frame, text="Process CJI5 Without Car Plan (STEP 14)", 
                                        command=self.process_cji5_no_carplan,
                                        font=("Segoe UI", 10), bg='#6c757d', fg='white',
                                        padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.no_carplan_btn.pack(fill=tk.X, pady=2)
        
        self.remove_cbip_btn = tk.Button(adv_frame, text="Remove M-CBIP-25 from RFP/Reclass (STEP 12-13)", 
                                        command=self.remove_cbip,
                                        font=("Segoe UI", 10), bg='#6c757d', fg='white',
                                        padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.remove_cbip_btn.pack(fill=tk.X, pady=2)
        
        # Help text
        help_text = scrolledtext.ScrolledText(adv_frame, height=6, width=50, 
                                             font=("Segoe UI", 8), bg='#f8f9fa', 
                                             fg='#333', wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        help_text.insert(tk.END, "PRIORITY 1 IMPLEMENTATIONS (COMPLETE):\n\n")
        help_text.insert(tk.END, "✓ Unified Currency Converter - All files use single conversion logic\n")
        help_text.insert(tk.END, "✓ File Validation - Validates column structure before processing\n")
        help_text.insert(tk.END, "✓ Flexible Column Mapping - Handles various column name variations\n")
        help_text.insert(tk.END, "✓ Modular Processors - Each file type has dedicated processor\n")
        help_text.insert(tk.END, "✓ Removed Redundant Code - Eliminated duplicate functions\n")
        help_text.config(state=tk.DISABLED)
    
    def create_consolidation_tab(self):
        """Create consolidation & merge tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Consolidation (STEP 1, 8)")
        
        cons_frame = tk.LabelFrame(tab, text="File Consolidation & Merge Options", 
                                  font=("Segoe UI", 11, "bold"), bg='#f0f0f0', 
                                  fg='#1e3c72', padx=15, pady=15)
        cons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ZMM Consolidation (STEP 1)
        zmm_label = tk.Label(cons_frame, text="ZMM Consolidation (STEP 1):", 
                            font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        zmm_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.consolidate_zmm_btn = tk.Button(cons_frame, 
                                            text="Consolidate Multiple ZMM Files with Header Validation", 
                                            command=self.consolidate_zmm_files,
                                            font=("Segoe UI", 10), bg='#ff6f00', fg='white',
                                            padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.consolidate_zmm_btn.pack(fill=tk.X, pady=2)
        
        # CJI Merge (STEP 8)
        merge_label = tk.Label(cons_frame, text="\nData Merge & Lookup (STEP 8):", 
                              font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        merge_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.merge_cji_btn = tk.Button(cons_frame, 
                                      text="Merge CJI5 & CJI3 Data (Priority 3)", 
                                      command=self.merge_cji_data,
                                      font=("Segoe UI", 10), bg='#9c27b0', fg='white',
                                      padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.merge_cji_btn.pack(fill=tk.X, pady=2)
        
        # Help text
        help_text = scrolledtext.ScrolledText(cons_frame, height=8, width=50, 
                                             font=("Segoe UI", 8), bg='#f8f9fa', 
                                             fg='#333', wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        help_text.insert(tk.END, "PRIORITY 1-2 IMPLEMENTATIONS:\n\n")
        help_text.insert(tk.END, "✓ STEP 1 - ZMM Consolidation:\n")
        help_text.insert(tk.END, "  - Validates headers match\n")
        help_text.insert(tk.END, "  - Consolidates files with matching headers\n\n")
        help_text.insert(tk.END, "⏳ STEP 8 - CJI Merge (Priority 3):\n")
        help_text.insert(tk.END, "  - Detects duplicates\n")
        help_text.insert(tk.END, "  - Merges CJI5 & CJI3")
        help_text.config(state=tk.DISABLED)
    
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
        """Process selected file using appropriate processor"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        try:
            file_type = self.file_type.get()
            
            # Show loading
            self.show_loading(f"Processing {file_type.upper()} file...")
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
            
            # Process based on type
            if file_type == 'cji5':
                processor = CJIProcessor('cji5')
                processor.load_file(self.selected_file)
                processor.validate_and_prepare()
                df = processor.process_basic(self.exchange_rates)
                output_name = 'CJI5_Processed'
                
            elif file_type == 'cji3':
                processor = CJIProcessor('cji3')
                processor.load_file(self.selected_file)
                processor.validate_and_prepare()
                df = processor.process_basic(self.exchange_rates)
                output_name = 'CJI3_Processed'
                
            elif file_type == 'rfp':
                processor = RFPReclassProcessor('rfp')
                processor.load_file(self.selected_file)
                processor.validate_and_prepare()
                df = processor.process_with_total(self.exchange_rates, remove_cbip=False)
                output_name = 'RFP_Processed'
                
            elif file_type == 'reclass':
                processor = RFPReclassProcessor('reclass')
                processor.load_file(self.selected_file)
                processor.validate_and_prepare()
                df = processor.process_with_total(self.exchange_rates, remove_cbip=False)
                output_name = 'Reclass_Processed'
                
            elif file_type == 'zmm':
                processor = ZMMProcessor()
                processor.load_file(self.selected_file)
                processor.validate_and_prepare()
                df = processor.process_basic()
                output_name = 'ZMM_Processed'
            else:
                raise ValueError("Invalid file type")
            
            # Hide loading before save dialog
            self.hide_loading()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f'{output_name}_{timestamp}.xlsx'
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                self.show_loading("Saving file...")
                processor.save(save_path)
                self.hide_loading()
                
                file_size = os.path.getsize(save_path) / (1024 * 1024)
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", 
                                  f"File processed successfully!\n\n" +
                                  f"File: {os.path.basename(save_path)}\n" +
                                  f"Size: {file_size:.1f} MB\n" +
                                  f"Rows: {len(df):,}")
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


def main():
    root = tk.Tk()
    app = CAPEXReportingApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
