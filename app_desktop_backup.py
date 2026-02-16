import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
from datetime import datetime
import re

# Exchange rates
EXCHANGE_RATES = {
    'PHP_TO_USD': 1/57,
    'SGD_TO_USD': 1/1.34
}

class CAPEXReportingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAPEX Reporting Tool - Enhanced")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="CAPEX Reporting Tool", 
                        font=("Segoe UI", 24, "bold"), bg='#f0f0f0', fg='#1e3c72')
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(main_frame, text="Enhanced Edition with Pivot & Advanced Processing", 
                           font=("Segoe UI", 11), bg='#f0f0f0', fg='#666')
        subtitle.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Basic Processing
        self.create_basic_tab()
        
        # Tab 2: Advanced Processing  
        self.create_advanced_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(root, textvariable=self.status_var, 
                            font=("Segoe UI", 9), bg='#e3f2fd', 
                            fg='#1976d2', anchor=tk.W, padx=10, pady=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Exchange rates info
        rates_text = "Exchange Rates: 1 PHP = 0.01754 USD (1/57) | 1 SGD = 0.74627 USD (1/1.34)"
        rates_label = tk.Label(root, text=rates_text, font=("Segoe UI", 9), 
                              bg='#fff3cd', fg='#856404', padx=10, pady=5)
        rates_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.selected_file = None
    
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
                                     command=self.process_file, 
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
                                       command=lambda: self.process_with_pivot('cji5'),
                                       font=("Segoe UI", 10), bg='#17a2b8', fg='white',
                                       padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.pivot_cji5_btn.pack(fill=tk.X, pady=2)
        
        self.pivot_cji3_btn = tk.Button(adv_frame, text="Process CJI3 with Pivot", 
                                       command=lambda: self.process_with_pivot('cji3'),
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
        
        # ZMM Advanced
        zmm_label = tk.Label(adv_frame, text="\nZMM Advanced Processing:", 
                            font=("Segoe UI", 10, "bold"), bg='#f0f0f0')
        zmm_label.pack(anchor=tk.W, pady=(10,5))
        
        self.zmm_full_btn = tk.Button(adv_frame, text="ZMM Full Processing (with Lookup)", 
                                     command=self.zmm_full_process,
                                     font=("Segoe UI", 10), bg='#fd7e14', fg='white',
                                     padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        self.zmm_full_btn.pack(fill=tk.X, pady=2)
        
        # Help text
        help_text = scrolledtext.ScrolledText(adv_frame, height=8, width=50, 
                                             font=("Segoe UI", 9), bg='#f8f9fa', 
                                             fg='#333', wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, pady=(15,0))
        help_text.insert(tk.END, "Advanced Features Help:\n\n")
        help_text.insert(tk.END, "Pivot Tables: Automatically creates pivot summaries for CJI5/CJI3\n\n")
        help_text.insert(tk.END, "Filter GNT: Extracts Car Plan data (GNT-OTACP-25) for separate tracking\n\n")
        help_text.insert(tk.END, "Remove CBIP: Filters out M-CBIP-25 entries from RFP/Reclass files\n\n")
        help_text.insert(tk.END, "ZMM Full: Complete ZMM processing including PR lookups and pivot generation")
        help_text.config(state=tk.DISABLED)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if filename:
            self.selected_file = filename
            self.file_path.set(os.path.basename(filename))
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set(f"File selected: {os.path.basename(filename)}")
    
    def convert_currency_cji5(self, row):
        currency = row['Transaction Currency']
        amount = row['Value Trancurr']
        if pd.isna(currency) or pd.isna(amount):
            return amount
        if currency in ['Php', 'PHP']:
            return amount * EXCHANGE_RATES['PHP_TO_USD']
        elif currency == 'SGD':
            return amount * EXCHANGE_RATES['SGD_TO_USD']
        return amount
    
    def convert_currency_cji3(self, row):
        currency = row['Transaction Currency']
        amount = row['Value TranCurr']
        if pd.isna(currency) or pd.isna(amount):
            return amount
        if currency in ['Php', 'PHP']:
            return amount * EXCHANGE_RATES['PHP_TO_USD']
        elif currency == 'SGD':
            return amount * EXCHANGE_RATES['SGD_TO_USD']
        return amount
    
    def convert_currency_rfp_reclass(self, row):
        currency = row['Transaction Currency']
        amount = row['Value TranCurr']
        if pd.isna(currency) or pd.isna(amount):
            return amount
        if currency in ['Php', 'PHP']:
            return amount * EXCHANGE_RATES['PHP_TO_USD']
        elif currency == 'SGD':
            return amount * EXCHANGE_RATES['SGD_TO_USD']
        return amount
    
    def process_cji5(self, filepath, create_pivot=False):
        df = pd.read_excel(filepath)
        
        # Convert ERP Reference to number
        if 'Reference Document number' in df.columns:
            col_name = 'Reference Document number'
        elif 'Ref. document number' in df.columns:
            col_name = 'Ref. document number'
        elif len(df.columns) > 4:
            col_name = df.columns[4]  # Column E (index 4)
        else:
            col_name = df.columns[0]
        
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        
        # Currency conversion
        if 'Transaction Currency' in df.columns and 'Value Trancurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_cji5, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
        
        if create_pivot:
            # Create pivot table
            pivot = pd.pivot_table(
                df,
                values='Amount_USD',
                index=col_name,
                columns='Reference Document Category' if 'Reference Document Category' in df.columns else None,
                aggfunc='sum',
                fill_value=0
            )
            return df, pivot
        
        return df
    
    def process_cji3(self, filepath, create_pivot=False):
        df = pd.read_excel(filepath)
        
        # Convert Purchasing Document to number
        if 'Purchasing Document' in df.columns:
            col_name = 'Purchasing Document'
        elif len(df.columns) > 2:
            col_name = df.columns[2]  # Column C (index 2)
        else:
            col_name = df.columns[0]
        
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        
        # Currency conversion
        if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_cji3, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
        
        if create_pivot:
            # Create pivot table
            pivot = pd.pivot_table(
                df,
                values='Amount_USD',
                index=col_name,
                aggfunc='sum',
                fill_value=0
            )
            return df, pivot
        
        return df
    
    def process_rfp(self, filepath, remove_cbip=False):
        df = pd.read_excel(filepath)
        
        # Filter non-colored cells (process all for now)
        if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_rfp_reclass, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
        
        # Remove M-CBIP-25 if requested
        if remove_cbip and 'Object' in df.columns:
            df = df[~df['Object'].str.contains('M-CBIP-25', na=False)]
        
        return df
    
    def process_reclass(self, filepath, remove_cbip=False):
        df = pd.read_excel(filepath)
        
        # Filter and convert
        if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_rfp_reclass, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
            
            # Remove M-CBIP-25 if requested
            if remove_cbip and 'Object' in df.columns:
                df = df[~df['Object'].str.contains('M-CBIP-25', na=False)]
            
            # Calculate total
            total_reclass = df['Amount_USD'].sum()
            
            # Add total row
            total_row = pd.DataFrame([[''] * (len(df.columns) - 1) + [total_reclass]], columns=df.columns)
            total_row.iloc[0, 0] = 'TOTAL RECLASS AMOUNT'
            df = pd.concat([df, total_row], ignore_index=True)
        
        return df
    
    def delimit_pr_number(self, pr_value):
        if pd.isna(pr_value):
            return pr_value
        pr_str = str(pr_value)
        # Remove v1, v2, v3, etc.
        pr_str = re.sub(r'v\d+', '', pr_str, flags=re.IGNORECASE)
        return pr_str.strip()
    
    def process_zmm(self, filepath):
        df = pd.read_excel(filepath)
        
        # Find Ariba PR Reference column
        pr_col_index = None
        for idx, col in enumerate(df.columns):
            if 'Ariba' in str(col) or 'PR Reference' in str(col):
                pr_col_index = idx
                break
        
        if pr_col_index is not None:
            pr_col_name = df.columns[pr_col_index]
            pr_data = df[pr_col_name].copy()
            
            # Delimit PR numbers
            pr_data_delimited = pr_data.apply(self.delimit_pr_number)
            pr_data_numeric = pd.to_numeric(pr_data_delimited, errors='coerce')
            
            # Find Project ID, PO, Vendor columns
            project_col = None
            po_col = None
            vendor_col = None
            
            for idx, col in enumerate(df.columns):
                if 'Project ID' in str(col) or 'Project' in str(col):
                    project_col = idx
                if 'PO' in str(col).upper() and 'Number' in str(col):
                    po_col = df.columns[idx]
                if 'Vendor' in str(col) and 'name' in str(col).lower():
                    vendor_col = df.columns[idx]
            
            # Insert new columns before Project ID
            if project_col and project_col >= 2:
                df.insert(2, 'Ariba PR Reference (Delimited)', pr_data_delimited)
                df.insert(3, 'Ariba PR Reference (Numeric)', pr_data_numeric)
                df.insert(4, 'Ariba PR Reference (Copy)', pr_data_delimited.copy())
                
                if po_col:
                    df.insert(5, 'PO Number (Copy)', df[po_col].copy())
                if vendor_col:
                    df.insert(6, 'Vendor Name (Copy)', df[vendor_col].copy())
        
        return df
    
    def process_with_pivot(self, file_type):
        filename = filedialog.askopenfilename(
            title=f"Select {file_type.upper()} File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.status_var.set(f"Processing {file_type.upper()} with pivot...")
            self.root.update()
            
            if file_type == 'cji5':
                df, pivot = self.process_cji5(filename, create_pivot=True)
                output_name = 'CJI5_with_Pivot'
            else:
                df, pivot = self.process_cji3(filename, create_pivot=True)
                output_name = 'CJI3_with_Pivot'
            
            # Save file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f'{output_name}_{timestamp}.xlsx',
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Processed Data', index=False)
                    pivot.to_excel(writer, sheet_name='Pivot Table')
                
                self.status_var.set(f"Success! Saved with pivot table")
                messagebox.showinfo("Success", f"File processed with pivot table!\n\n{os.path.basename(save_path)}")
        
        except Exception as e:
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
            df = pd.read_excel(filename)
            
            # Look for WBS or Project columns
            wbs_col = None
            for col in df.columns:
                if 'WBS' in str(col) or 'Project' in str(col):
                    wbs_col = col
                    break
            
            if wbs_col:
                filtered_df = df[df[wbs_col].str.contains('GNT-OTACP-25', na=False)]
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    initialfile=f'CarPlan_Filtered_{timestamp}.xlsx',
                    filetypes=[("Excel Files", "*.xlsx")]
                )
                
                if save_path:
                    filtered_df.to_excel(save_path, index=False)
                    messagebox.showinfo("Success", f"Car Plan data extracted!\n\nRows: {len(filtered_df)}")
            else:
                messagebox.showwarning("Warning", "Could not find WBS or Project column")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def remove_cbip(self):
        filename = filedialog.askopenfilename(
            title="Select RFP/Reclass File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not filename:
            return
        
        try:
            df = pd.read_excel(filename)
            
            if 'Object' in df.columns:
                original_count = len(df)
                df = df[~df['Object'].str.contains('M-CBIP-25', na=False)]
                removed_count = original_count - len(df)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    initialfile=f'No_CBIP_{timestamp}.xlsx',
                    filetypes=[("Excel Files", "*.xlsx")]
                )
                
                if save_path:
                    df.to_excel(save_path, index=False)
                    messagebox.showinfo("Success", f"M-CBIP-25 removed!\n\nRemoved: {removed_count} rows\nRemaining: {len(df)} rows")
            else:
                messagebox.showwarning("Warning", "Could not find Object column")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def zmm_full_process(self):
        messagebox.showinfo("ZMM Full Processing", 
                          "This feature requires CJI5 and ZMM files.\n\n" +
                          "1. First, select your ZMM file\n" +
                          "2. Then, select your CJI5 file for lookup\n" +
                          "3. The tool will create pivot with PR lookups")
        
        # Implementation of full ZMM processing would go here
        # This is a placeholder for the complete workflow
    
    def process_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        try:
            self.status_var.set("Processing file...")
            self.process_btn.config(state=tk.DISABLED)
            self.root.update()
            
            file_type = self.file_type.get()
            
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
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f'{output_name}_{timestamp}.xlsx'
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if save_path:
                df.to_excel(save_path, index=False)
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"File processed successfully!\n\n{os.path.basename(save_path)}")
            else:
                self.status_var.set("Save cancelled")
            
            self.process_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error processing file:\n\n{str(e)}")

def main():
    root = tk.Tk()
    app = CAPEXReportingApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()