from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import zipfile
import re
import webbrowser
from threading import Timer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.secret_key = 'capex-reporting-tool-2024'

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Exchange rates (can be updated as needed)
EXCHANGE_RATES = {
    'PHP_TO_USD': 1/57,
    'SGD_TO_USD': 1/1.34
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_currency_cji5(row):
    """Convert currency to USD for CJI5 file"""
    currency = row['Transaction Currency']
    amount = row['Value Trancurr']
    
    if pd.isna(currency) or pd.isna(amount):
        return amount
    
    if currency == 'Php' or currency == 'PHP':
        return amount * EXCHANGE_RATES['PHP_TO_USD']
    elif currency == 'SGD':
        return amount * EXCHANGE_RATES['SGD_TO_USD']
    else:
        return amount

def convert_currency_cji3(row):
    """Convert currency to USD for CJI3 file"""
    currency = row['Transaction Currency']
    amount = row['Value TranCurr']
    
    if pd.isna(currency) or pd.isna(amount):
        return amount
    
    if currency == 'Php' or currency == 'PHP':
        return amount * EXCHANGE_RATES['PHP_TO_USD']
    elif currency == 'SGD':
        return amount * EXCHANGE_RATES['SGD_TO_USD']
    else:
        return amount

def convert_currency_rfp_reclass(row):
    """Convert currency to USD for RFP and Reclass files"""
    currency = row['Transaction Currency']
    amount = row['Value TranCurr']
    
    if pd.isna(currency) or pd.isna(amount):
        return amount
    
    if currency == 'Php' or currency == 'PHP':
        return amount * EXCHANGE_RATES['PHP_TO_USD']
    elif currency == 'SGD':
        return amount * EXCHANGE_RATES['SGD_TO_USD']
    else:
        return amount

def process_cji5(filepath):
    """Process CJI5 file"""
    df = pd.read_excel(filepath)
    
    # Convert ERP Reference in column A to number
    if 'ERP Reference' in df.columns:
        df['ERP Reference'] = pd.to_numeric(df['ERP Reference'], errors='coerce')
    elif df.columns[0]:  # If column A exists but has different name
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    
    # Find the currency conversion columns
    if 'Transaction Currency' in df.columns and 'Value Trancurr' in df.columns:
        # Apply conversion formula
        df['Amount_USD'] = df.apply(convert_currency_cji5, axis=1)
        df['Amount_USD'] = df['Amount_USD'].round(2)
    
    return df

def process_cji3(filepath):
    """Process CJI3 file"""
    df = pd.read_excel(filepath)
    
    # Convert Purchasing Document in column A to number
    if 'Purchasing Document' in df.columns:
        df['Purchasing Document'] = pd.to_numeric(df['Purchasing Document'], errors='coerce')
    elif df.columns[0]:  # If column A exists but has different name
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    
    # Find the currency conversion columns
    if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
        # Apply conversion formula
        df['Amount_USD'] = df.apply(convert_currency_cji3, axis=1)
        df['Amount_USD'] = df['Amount_USD'].round(2)
    
    return df

def process_rfp(filepath):
    """Process RFP file"""
    df = pd.read_excel(filepath)
    
    # Filter rows where Transaction Currency has no cell color (assuming all rows without filtering)
    # In Excel, we can't detect cell colors in pandas, so we process all rows
    # If specific filtering is needed, it should be done in Excel before upload
    
    if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
        # Apply conversion formula
        df['Amount_USD'] = df.apply(convert_currency_rfp_reclass, axis=1)
        df['Amount_USD'] = df['Amount_USD'].round(2)
    
    return df

def process_reclass(filepath):
    """Process Reclass file"""
    df = pd.read_excel(filepath)
    
    # Filter rows where Transaction Currency has no cell color
    if 'Transaction Currency' in df.columns and 'Value TranCurr' in df.columns:
        # Apply conversion formula
        df['Amount_USD'] = df.apply(convert_currency_rfp_reclass, axis=1)
        df['Amount_USD'] = df['Amount_USD'].round(2)
        
        # Calculate total amount
        total_reclass = df['Amount_USD'].sum()
        
        # Add total row at the end
        total_row = pd.DataFrame([[''] * (len(df.columns) - 1) + [total_reclass]], columns=df.columns)
        total_row.iloc[0, 0] = 'TOTAL RECLASS AMOUNT'
        df = pd.concat([df, total_row], ignore_index=True)
    
    return df

def delimit_pr_number(pr_value):
    """Remove v1, v2, v3, etc. from PR numbers"""
    if pd.isna(pr_value):
        return pr_value
    
    pr_str = str(pr_value)
    # Remove patterns like v1, v2, v3, etc.
    pr_str = re.sub(r'v\d+', '', pr_str, flags=re.IGNORECASE)
    # Remove extra spaces
    pr_str = pr_str.strip()
    
    return pr_str

def process_zmm(filepath):
    """Process ZMM file"""
    df = pd.read_excel(filepath)
    
    # Find the Ariba PR Reference column (assumed to be in column C initially)
    pr_col_index = None
    for idx, col in enumerate(df.columns):
        if 'Ariba' in str(col) or 'PR' in str(col) or idx == 2:  # Column C is index 2
            pr_col_index = idx
            break
    
    if pr_col_index is not None:
        pr_col_name = df.columns[pr_col_index]
        
        # Insert the PR Reference before Project ID (copy to columns C and E)
        # First, let's identify Project ID column
        project_id_col = None
        for idx, col in enumerate(df.columns):
            if 'Project ID' in str(col) or 'Project' in str(col):
                project_id_col = idx
                break
        
        # Copy Ariba PR Reference
        pr_data = df[pr_col_name].copy()
        
        # Delimit PR numbers (remove v1, v2, v3)
        pr_data_delimited = pr_data.apply(delimit_pr_number)
        
        # Convert PR number format to Number
        pr_data_numeric = pd.to_numeric(pr_data_delimited, errors='coerce')
        
        # Find PO Number and Vendor Name columns
        po_col = None
        vendor_col = None
        
        for idx, col in enumerate(df.columns):
            if 'PO' in str(col).upper() or 'Purchase Order' in str(col):
                po_col = df.columns[idx]
            if 'Vendor' in str(col):
                vendor_col = df.columns[idx]
        
        # Reorganize columns
        # Insert PR Reference twice before Project ID
        if project_id_col:
            # Create new dataframe with reorganized columns
            cols = df.columns.tolist()
            
            # Insert PR Reference (delimited and numeric) at column C
            df.insert(2, 'Ariba PR Reference (Delimited)', pr_data_delimited)
            df.insert(3, 'Ariba PR Reference (Numeric)', pr_data_numeric)
            
            # Copy PO Number and Vendor Name if they exist
            if po_col:
                df.insert(4, 'PO Number (Copy)', df[po_col].copy())
            if vendor_col:
                df.insert(5, 'Vendor Name (Copy)', df[vendor_col].copy())
    
    return df

@app.route('/')
def index():
    return render_template('capex_index.html')

@app.route('/process', methods=['POST'])
def process_files():
    file_type = request.form.get('file_type')
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process based on file type
            if file_type == 'cji5':
                df = process_cji5(filepath)
                output_name = 'CJI5_Processed'
            elif file_type == 'cji3':
                df = process_cji3(filepath)
                output_name = 'CJI3_Processed'
            elif file_type == 'rfp':
                df = process_rfp(filepath)
                output_name = 'RFP_Processed'
            elif file_type == 'reclass':
                df = process_reclass(filepath)
                output_name = 'Reclass_Processed'
            elif file_type == 'zmm':
                df = process_zmm(filepath)
                output_name = 'ZMM_Processed'
            else:
                return jsonify({'error': 'Invalid file type'}), 400
            
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'{output_name}_{timestamp}.xlsx'
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            # Save processed file
            df.to_excel(output_path, index=False)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload .xlsx or .xls files only'}), 400

@app.route('/batch-process', methods=['POST'])
def batch_process():
    """Process multiple ZMM files at once"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    processed_files = []
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'ZMM_Batch_Processed_{timestamp}.zip'
    zip_path = os.path.join(app.config['PROCESSED_FOLDER'], zip_filename)
    
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Process the file
                    df = process_zmm(filepath)
                    
                    # Save to processed folder
                    output_filename = f'Processed_{filename}'
                    output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
                    df.to_excel(output_path, index=False)
                    
                    # Add to zip
                    zipf.write(output_path, output_filename)
                    
                    # Clean up
                    os.remove(filepath)
                    processed_files.append(output_filename)
        
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    
    except Exception as e:
        return jsonify({'error': f'Error processing files: {str(e)}'}), 500

if __name__ == '__main__':
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000')
    
    Timer(1.5, open_browser).start()
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)