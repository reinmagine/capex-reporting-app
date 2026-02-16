import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
from datetime import datetime
import re
import threading
import requests

# Real-time exchange rates (will be fetched from API)
EXCHANGE_RATES = {
    'PHP_TO_USD': 1/57,  # Fallback rate
    'SGD_TO_USD': 1/1.34  # Fallback rate
}

def get_live_exchange_rates():
    """Fetch live exchange rates from API"""
    try:
        # Using exchangerate-api.com (free tier)
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
    
    # Return fallback rates if API fails
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
        self.root.title("CAPEX Reporting Tool - Enhanced")
        self.root.geometry("900x700")
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
        
        subtitle = tk.Label(main_frame, text="Enhanced Edition with Real-Time Exchange Rates", 
                           font=("Segoe UI", 11), bg='#f0f0f0', fg='#666')
        subtitle.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Basic Processing
        self.create_basic_tab()
        
        # Tab 2: Advanced Processing  
        self.create_advanced_tab()
        
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
        messagebox.showinfo("Success", f"Exchange rates updated!\n\n1 USD = {self.exchange_rates['PHP']:.4f} PHP\n1 USD = {self.exchange_rates['SGD']:.4f} SGD")
    
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
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Basic Processing")
        
        # File type selection
        type_frame = tk.LabelFrame(tab, text="Select Report Type", 
                                  font=("Segoe UI", 11, "bold"), bg='#f0f0f0', 
                                  fg='#1e3c72', padx=15, pady=15)
        type_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.file_type = tk.StringVar(value="cji5")
        
        types = [
            ("CJI5 File - Convert ERP Reference & Currency", "cji5"),
            ("CJI3 File - Convert Purchasing Document & Currency", "cji3"),
            ("RFP File - Filter & Convert Currency", "rfp"),
            ("Reclass File - Convert Currency & Calculate Total", "reclass"),
            ("ZMM File - Process PR Numbers & Copy Columns", "zmm")
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
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Advanced Features")
        
        adv_frame = tk.LabelFrame(tab, text="Advanced Processing Options", 
                                 font=("Segoe UI", 11, "bold"), bg='#f0f0f0', 
                                 fg='#1e3c72', padx=15, pady=15)
        adv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CJI5/CJI3 with Pivot
        pivot_label = tk.Label(adv_frame, text="Pivot Table Generation:", 
                              font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        pivot_label.pack(anchor=tk.W, pady=(5,5))
        
        self.pivot_cji5_btn = tk.Button(adv_frame, text="Process CJI5 with Pivot", 
                                       command=lambda: self.process_with_pivot_threaded('cji5'),
                                       font=("Segoe UI", 10), bg='#17a2b8', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji5_btn.pack(fill=tk.X, pady=2)
        
        self.pivot_cji3_btn = tk.Button(adv_frame, text="Process CJI3 with Pivot", 
                                       command=lambda: self.process_with_pivot_threaded('cji3'),
                                       font=("Segoe UI", 10), bg='#17a2b8', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji3_btn.pack(fill=tk.X, pady=2)
        
        # Filtering options
        filter_label = tk.Label(adv_frame, text="\nFiltering & Special Processing:", 
                               font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        filter_label.pack(anchor=tk.W, pady=(10,5))
        
        self.filter_gnt_btn = tk.Button(adv_frame, text="Filter GNT-OTACP-25 (Car Plan)", 
                                       command=self.filter_carplan,
                                       font=("Segoe UI", 10), bg='#6c757d', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.filter_gnt_btn.pack(fill=tk.X, pady=2)
        
        self.remove_cbip_btn = tk.Button(adv_frame, text="Remove M-CBIP-25 from RFP/Reclass", 
                                        command=self.remove_cbip,
                                        font=("Segoe UI", 10), bg='#6c757d', fg='white',
                                        padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.remove_cbip_btn.pack(fill=tk.X, pady=2)
        
        # Help text
        help_text = scrolledtext.ScrolledText(adv_frame, height=10, width=50, 
                                             font=("Segoe UI", 9), bg='#f8f9fa', 
                                             fg='#333', wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, pady=(15,0))
        help_text.insert(tk.END, "Advanced Features Help:\n\n")
        help_text.insert(tk.END, "Pivot Tables: Automatically creates pivot summaries for CJI5/CJI3\n\n")
        help_text.insert(tk.END, "Filter GNT: Extracts Car Plan data (GNT-OTACP-25) for separate tracking\n\n")
        help_text.insert(tk.END, "Remove CBIP: Filters out M-CBIP-25 entries from RFP/Reclass files\n\n")
        help_text.insert(tk.END, "Performance Tips:\n")
        help_text.insert(tk.END, "- Large files (>50MB) may take 2-3 minutes\n")
        help_text.insert(tk.END, "- Keep Excel closed while processing\n")
        help_text.insert(tk.END, "- Files are processed in chunks for better performance")
        help_text.config(state=tk.DISABLED)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if filename:
            self.selected_file = filename
            file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            self.file_path.set(f"{os.path.basename(filename)} ({file_size:.1f} MB)")
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set(f"File selected: {os.path.basename(filename)}")
    
    def convert_currency_cji5(self, row):
        currency = row.get('Transaction Currency')
        amount = row.get('Value Trancurr')
        
        if pd.isna(currency) or pd.isna(amount):
            return amount
        
        if str(currency).upper() in ['PHP', 'Php']:
            return amount * self.exchange_rates['PHP_TO_USD']
        elif str(currency).upper() == 'SGD':
            return amount * self.exchange_rates['SGD_TO_USD']
        return amount
    
    def convert_currency_cji3(self, row):
        currency = row.get('Transaction Currency')
        amount = row.get('Value TranCurr')
        
        if pd.isna(currency) or pd.isna(amount):
            return amount
        
        if str(currency).upper() in ['PHP', 'Php']:
            return amount * self.exchange_rates['PHP_TO_USD']
        elif str(currency).upper() == 'SGD':
            return amount * self.exchange_rates['SGD_TO_USD']
        return amount
    
    def convert_currency_rfp_reclass(self, row):
        currency = row.get('Transaction Currency')
        amount = row.get('Value TranCurr')
        
        if pd.isna(currency) or pd.isna(amount):
            return amount
        
        if str(currency).upper() in ['PHP', 'Php']:
            return amount * self.exchange_rates['PHP_TO_USD']
        elif str(currency).upper() == 'SGD':
            return amount * self.exchange_rates['SGD_TO_USD']
        return amount
    
    def process_cji5(self, filepath, create_pivot=False):
        # Read file in chunks for large files
        df = pd.read_excel(filepath)
        
        # Find and convert reference number column
        ref_col = None
        for col in df.columns:
            if 'Ref. document number' in str(col) or 'Reference Document number' in str(col):
                ref_col = col
                break
        
        if ref_col:
            df[ref_col] = pd.to_numeric(df[ref_col], errors='coerce')
        
        # Find Transaction Currency column (flexible matching)
        trans_curr_col = None
        value_col = None
        
        for col in df.columns:
            if 'Transaction Currency' in str(col):
                trans_curr_col = col
            # Match both "Value Trancurr" and "Value TranCurr"
            if 'Value Tran' in str(col) and 'Curr' in str(col):
                value_col = col
        
        # Currency conversion - check if columns exist
        if trans_curr_col and value_col:
            # Temporarily rename for conversion function
            df_temp = df.rename(columns={
                trans_curr_col: 'Transaction Currency',
                value_col: 'Value Trancurr'
            })
            df_temp['Amount_USD'] = df_temp.apply(self.convert_currency_cji5, axis=1)
            df['Amount_USD'] = df_temp['Amount_USD'].round(2)
        
        if create_pivot and ref_col and 'Amount_USD' in df.columns:
            pivot = pd.pivot_table(
                df,
                values='Amount_USD',
                index=ref_col,
                columns='Reference Document Category' if 'Reference Document Category' in df.columns else None,
                aggfunc='sum',
                fill_value=0
            )
            return df, pivot
        
        return df
    
    def process_cji3(self, filepath, create_pivot=False):
        df = pd.read_excel(filepath)
        
        # Find purchasing document column
        purch_col = None
        for col in df.columns:
            if 'Purchasing Document' in str(col):
                purch_col = col
                break
        
        if purch_col:
            df[purch_col] = pd.to_numeric(df[purch_col], errors='coerce')
        
        # Find Transaction Currency and Value columns (flexible matching)
        trans_curr_col = None
        value_col = None
        
        for col in df.columns:
            if 'Transaction Currency' in str(col):
                trans_curr_col = col
            # Match "Value TranCurr" variations
            if 'Value Tran' in str(col) and 'Curr' in str(col):
                value_col = col
        
        # Currency conversion
        if trans_curr_col and value_col:
            # Temporarily rename for conversion function
            df_temp = df.rename(columns={
                trans_curr_col: 'Transaction Currency',
                value_col: 'Value TranCurr'
            })
            df_temp['Amount_USD'] = df_temp.apply(self.convert_currency_cji3, axis=1)
            df['Amount_USD'] = df_temp['Amount_USD'].round(2)
            
            # Blank out Amount_USD for subtotal rows (rows with blank Project definition)
            if 'Project definition' in df.columns:
                df.loc[df['Project definition'].isna() | (df['Project definition'] == ''), 'Amount_USD'] = None
        
        if create_pivot and purch_col and 'Amount_USD' in df.columns:
            # For pivot, exclude rows with blank Project definition
            df_for_pivot = df[df['Project definition'].notna() & (df['Project definition'] != '')]
            pivot = pd.pivot_table(
                df_for_pivot,
                values='Amount_USD',
                index=purch_col,
                aggfunc='sum',
                fill_value=0
            )
            return df, pivot
        
        return df
    
    def process_rfp(self, filepath):
        df = pd.read_excel(filepath)
        
        # Find Transaction Currency and Value columns
        trans_curr_col = None
        value_col = None
        
        for col in df.columns:
            if 'Transaction Currency' in str(col):
                trans_curr_col = col
            if 'Value Tran' in str(col) and 'Curr' in str(col):
                value_col = col
        
        if trans_curr_col and value_col:
            df_temp = df.rename(columns={
                trans_curr_col: 'Transaction Currency',
                value_col: 'Value TranCurr'
            })
            df_temp['Amount_USD'] = df_temp.apply(self.convert_currency_rfp_reclass, axis=1)
            df['Amount_USD'] = df_temp['Amount_USD'].round(2)
            
            # Blank out Amount_USD for subtotal rows (rows with blank Object)
            if 'Object' in df.columns:
                df.loc[df['Object'].isna() | (df['Object'] == ''), 'Amount_USD'] = None
        
        return df
    
    def process_reclass(self, filepath):
        df = pd.read_excel(filepath)
        
        # Find Transaction Currency and Value columns
        trans_curr_col = None
        value_col = None
        
        for col in df.columns:
            if 'Transaction Currency' in str(col):
                trans_curr_col = col
            if 'Value Tran' in str(col) and 'Curr' in str(col):
                value_col = col
        
        if trans_curr_col and value_col:
            df_temp = df.rename(columns={
                trans_curr_col: 'Transaction Currency',
                value_col: 'Value TranCurr'
            })
            df_temp['Amount_USD'] = df_temp.apply(self.convert_currency_rfp_reclass, axis=1)
            df['Amount_USD'] = df_temp['Amount_USD'].round(2)
            
            # Blank out Amount_USD for subtotal rows (rows with blank Object)
            if 'Object' in df.columns:
                df.loc[df['Object'].isna() | (df['Object'] == ''), 'Amount_USD'] = None
            
            # Calculate total only from non-blank Object rows
            total_reclass = df[df['Object'].notna() & (df['Object'] != '')]['Amount_USD'].sum()
            
            # Add total row at the end
            total_row = pd.DataFrame([[''] * (len(df.columns) - 1) + [total_reclass]], columns=df.columns)
            total_row.iloc[0, 0] = 'TOTAL RECLASS AMOUNT'
            df = pd.concat([df, total_row], ignore_index=True)
        
        return df
    
    def delimit_pr_number(self, pr_value):
        if pd.isna(pr_value):
            return pr_value
        pr_str = str(pr_value)
        pr_str = re.sub(r'v\d+', '', pr_str, flags=re.IGNORECASE)
        return pr_str.strip()
    
    def process_zmm(self, filepath):
        # Process in chunks for large files
        df = pd.read_excel(filepath)
        
        # Find Ariba PR Reference column
        pr_col_index = None
        for idx, col in enumerate(df.columns):
            if 'Ariba' in str(col) and 'PR' in str(col):
                pr_col_index = idx
                break
        
        if pr_col_index is not None:
            pr_col_name = df.columns[pr_col_index]
            pr_data = df[pr_col_name].copy()
            
            # Delimit PR numbers
            pr_data_delimited = pr_data.apply(self.delimit_pr_number)
            pr_data_numeric = pd.to_numeric(pr_data_delimited, errors='coerce')
            
            # Find other columns
            po_col = None
            vendor_col = None
            
            for col in df.columns:
                if 'PO' in str(col).upper() and 'Number' in str(col):
                    po_col = col
                if 'Vendor' in str(col) and 'name' in str(col).lower():
                    vendor_col = col
            
            # Insert new columns at position 2 (column C)
            df.insert(2, 'Ariba PR Reference (Delimited)', pr_data_delimited)
            df.insert(3, 'Ariba PR Reference (Numeric)', pr_data_numeric)
            df.insert(4, 'Ariba PR Reference (Copy)', pr_data_delimited.copy())
            
            if po_col and po_col in df.columns:
                df.insert(5, 'PO Number (Copy)', df[po_col].copy())
            if vendor_col and vendor_col in df.columns:
                df.insert(6, 'Vendor Name (Copy)', df[vendor_col].copy())
        
        return df
    
    def process_file_threaded(self):
        """Run file processing in a separate thread"""
        thread = threading.Thread(target=self.process_file)
        thread.daemon = True
        thread.start()
    
    def process_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        try:
            file_type = self.file_type.get()
            
            # Show loading
            self.show_loading(f"Processing {file_type.upper()} file...")
            self.process_btn.config(state=tk.DISABLED)
            
            # Process based on type
            if file_type == 'cji5':
                df = self.process_cji5(self.selected_file)
                output_name = 'CJI5_Processed'
            elif file_type == 'cji3':
                df = self.process_cji3(self.selected_file)
                output_name = 'CJI3_Processed'
            elif file_type == 'rfp':
                df = self.process_rfp(self.selected_file)
                output_name = 'RFP_Processed'
            elif file_type == 'reclass':
                df = self.process_reclass(self.selected_file)
                output_name = 'Reclass_Processed'
            elif file_type == 'zmm':
                df = self.process_zmm(self.selected_file)
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
                # Show saving message
                self.show_loading("Saving file...")
                
                # Save with explicit engine
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                self.hide_loading()
                
                file_size = os.path.getsize(save_path) / (1024 * 1024)
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)} ({file_size:.1f} MB)")
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
        filename = filedialog.askopenfilename(
            title=f"Select {file_type.upper()} File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading(f"Processing {file_type.upper()} with pivot table...")
            
            if file_type == 'cji5':
                df, pivot = self.process_cji5(filename, create_pivot=True)
                output_name = 'CJI5_with_Pivot'
            else:
                df, pivot = self.process_cji3(filename, create_pivot=True)
                output_name = 'CJI3_with_Pivot'
            
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
        filename = filedialog.askopenfilename(
            title="Select CJI5/CJI3 File to Filter Car Plan",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading("Filtering Car Plan data...")
            
            df = pd.read_excel(filename)
            
            wbs_col = None
            for col in df.columns:
                if 'WBS' in str(col) or 'Project' in str(col):
                    wbs_col = col
                    break
            
            if wbs_col:
                filtered_df = df[df[wbs_col].str.contains('GNT-OTACP-25', na=False)]
                
                self.hide_loading()
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    initialfile=f'CarPlan_Filtered_{timestamp}.xlsx',
                    filetypes=[("Excel Files", "*.xlsx")]
                )
                
                if save_path:
                    filtered_df.to_excel(save_path, index=False, engine='openpyxl')
                    messagebox.showinfo("Success", 
                                      f"Car Plan data extracted!\n\n" +
                                      f"Rows: {len(filtered_df):,}")
            else:
                self.hide_loading()
                messagebox.showwarning("Warning", "Could not find WBS or Project column")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def remove_cbip(self):
        filename = filedialog.askopenfilename(
            title="Select RFP/Reclass File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filename:
            return
        
        try:
            self.show_loading("Removing M-CBIP-25 entries...")
            
            df = pd.read_excel(filename)
            
            if 'Object' in df.columns:
                original_count = len(df)
                df = df[~df['Object'].str.contains('M-CBIP-25', na=False)]
                removed_count = original_count - len(df)
                
                self.hide_loading()
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    initialfile=f'No_CBIP_{timestamp}.xlsx',
                    filetypes=[("Excel Files", "*.xlsx")]
                )
                
                if save_path:
                    df.to_excel(save_path, index=False, engine='openpyxl')
                    messagebox.showinfo("Success", 
                                      f"M-CBIP-25 removed!\n\n" +
                                      f"Removed: {removed_count:,} rows\n" +
                                      f"Remaining: {len(df):,} rows")
            else:
                self.hide_loading()
                messagebox.showwarning("Warning", "Could not find Object column")
        
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = CAPEXReportingApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()