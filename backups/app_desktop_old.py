import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        self.root.title("CAPEX Reporting Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="CAPEX Reporting Tool", 
                        font=("Segoe UI", 24, "bold"), bg='#f0f0f0', fg='#1e3c72')
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(main_frame, text="Automate your Excel reporting tasks", 
                           font=("Segoe UI", 12), bg='#f0f0f0', fg='#666')
        subtitle.pack(pady=(0, 30))
        
        # File type selection
        type_frame = tk.LabelFrame(main_frame, text="Select Report Type", 
                                  font=("Segoe UI", 12, "bold"), bg='#f0f0f0', 
                                  fg='#1e3c72', padx=20, pady=20)
        type_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.file_type = tk.StringVar(value="cji5")
        
        # Radio buttons for file types
        types = [
            ("CJI5 File - Convert ERP Reference & Currency", "cji5"),
            ("CJI3 File - Convert Purchasing Document & Currency", "cji3"),
            ("RFP File - Filter & Convert Currency", "rfp"),
            ("Reclass File - Convert Currency & Calculate Total", "reclass"),
            ("ZMM File - Process PR Numbers & Copy Columns", "zmm")
        ]
        
        for text, value in types:
            rb = tk.Radiobutton(type_frame, text=text, variable=self.file_type, 
                               value=value, font=("Segoe UI", 11), bg='#f0f0f0',
                               activebackground='#f0f0f0', pady=5)
            rb.pack(anchor=tk.W)
        
        # File selection
        file_frame = tk.Frame(main_frame, bg='#f0f0f0')
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.file_path = tk.StringVar(value="No file selected")
        file_label = tk.Label(file_frame, textvariable=self.file_path, 
                             font=("Segoe UI", 10), bg='#f0f0f0', fg='#333')
        file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Browse File", 
                              command=self.browse_file, font=("Segoe UI", 11, "bold"),
                              bg='#2a5298', fg='white', padx=20, pady=10,
                              relief=tk.FLAT, cursor="hand2")
        browse_btn.pack(side=tk.RIGHT)
        
        # Process button
        self.process_btn = tk.Button(main_frame, text="Process File", 
                                     command=self.process_file, 
                                     font=("Segoe UI", 14, "bold"),
                                     bg='#28a745', fg='white', padx=40, pady=15,
                                     relief=tk.FLAT, cursor="hand2", state=tk.DISABLED)
        self.process_btn.pack(pady=10)
        
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
    
    def process_cji5(self, filepath):
        df = pd.read_excel(filepath)
        if 'ERP Reference' in df.columns:
            df['ERP Reference'] = pd.to_numeric(df['ERP Reference'], errors='coerce')
        elif len(df.columns) > 0:
            df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
        if 'Transaction Currency' in df.columns and 'Value Trancurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_cji5, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
        return df
    
    def process_cji3(self, filepath):
        df = pd.read_excel(filepath)
        if 'Purchasing Document' in df.columns:
            df['Purchasing Document'] = pd.to_numeric(df['Purchasing Document'], errors='coerce')
        elif len(df.columns) > 0:
            df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
        if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_cji3, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
        return df
    
    def process_rfp(self, filepath):
        df = pd.read_excel(filepath)
        if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_rfp_reclass, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
        return df
    
    def process_reclass(self, filepath):
        df = pd.read_excel(filepath)
        if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
            df['Amount_USD'] = df.apply(self.convert_currency_rfp_reclass, axis=1)
            df['Amount_USD'] = df['Amount_USD'].round(2)
            total_reclass = df['Amount_USD'].sum()
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
        df = pd.read_excel(filepath)
        pr_col_index = None
        for idx, col in enumerate(df.columns):
            if 'Ariba' in str(col) or 'PR' in str(col) or idx == 2:
                pr_col_index = idx
                break
        
        if pr_col_index is not None:
            pr_col_name = df.columns[pr_col_index]
            pr_data = df[pr_col_name].copy()
            pr_data_delimited = pr_data.apply(self.delimit_pr_number)
            pr_data_numeric = pd.to_numeric(pr_data_delimited, errors='coerce')
            
            po_col = None
            vendor_col = None
            for idx, col in enumerate(df.columns):
                if 'PO' in str(col).upper() or 'Purchase Order' in str(col):
                    po_col = df.columns[idx]
                if 'Vendor' in str(col):
                    vendor_col = df.columns[idx]
            
            df.insert(2, 'Ariba PR Reference (Delimited)', pr_data_delimited)
            df.insert(3, 'Ariba PR Reference (Numeric)', pr_data_numeric)
            
            if po_col:
                df.insert(4, 'PO Number (Copy)', df[po_col].copy())
            if vendor_col:
                df.insert(5, 'Vendor Name (Copy)', df[vendor_col].copy())
        return df
    
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
            
            # Ask where to save
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f'{output_name}_{timestamp}.xlsx'
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            
            if save_path:
                df.to_excel(save_path, index=False)
                self.status_var.set(f"Success! File saved: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"File processed and saved successfully!\n\n{os.path.basename(save_path)}")
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