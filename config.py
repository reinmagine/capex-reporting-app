"""
CAPEX Reporting Tool Configuration
Central location for all column mappings, exchange rates, and processing rules
"""

# Exchange rates (can be updated or fetched from API)
EXCHANGE_RATES = {
    'PHP_TO_USD': 1/57,
    'SGD_TO_USD': 1/1.34,
    'PHP': 57,
    'SGD': 1.34,
}

# Column name mappings with flexible aliases
COLUMN_MAPPINGS = {
    'cji5': {
        'reference_doc': [
            'Ref. document number',
            'Reference Document number',
            'ERP Reference',
            'Reference Number'
        ],
        'reference_category': [
            'Reference Document Category',
            'Document Category'
        ],
        'trans_currency': [
            'Transaction Currency',
            'Currency'
        ],
        'value_amount': [
            'Value Trancurr',
            'Value TranCurr',
            'Amount',
            'Transaction Value'
        ],
        'project': [
            'Project definition',
            'WBS',
            'Project'
        ]
    },
    'cji3': {
        'purch_doc': [
            'Purchasing Document',
            'Purchase Document',
            'PO Number'
        ],
        'trans_currency': [
            'Transaction Currency',
            'Currency'
        ],
        'value_amount': [
            'Value TranCurr',
            'Value Trancurr',
            'Amount',
            'Transaction Value'
        ],
        'project': [
            'Project definition',
            'WBS',
            'Project'
        ]
    },
    'rfp': {
        'trans_currency': [
            'Transaction Currency',
            'Currency'
        ],
        'value_amount': [
            'Value TranCurr',
            'Value Trancurr',
            'Amount',
            'Transaction Value'
        ],
        'object': [
            'Object',
            'Cost Center',
            'WBS'
        ]
    },
    'reclass': {
        'trans_currency': [
            'Transaction Currency',
            'Currency'
        ],
        'value_amount': [
            'Value TranCurr',
            'Value Trancurr',
            'Amount',
            'Transaction Value'
        ],
        'object': [
            'Object',
            'Cost Center',
            'WBS'
        ]
    },
    'zmm': {
        'ariba_pr_ref': [
            'Ariba PR Reference',
            'PR Reference',
            'PR Number'
        ],
        'po_number': [
            'PO Number',
            'PO',
            'Purchase Order'
        ],
        'project_id': [
            'Project ID',
            'Project'
        ],
        'vendor': [
            'Vendor Name',
            'Vendor',
            'Supplier'
        ]
    }
}

# File processing specifications
FILE_TYPES = {
    'cji5': {
        'name': 'CJI5 File',
        'description': 'Convert ERP Reference & Currency',
        'steps': ['convert_reference', 'convert_currency', 'add_usd_amount']
    },
    'cji3': {
        'name': 'CJI3 File',
        'description': 'Convert Purchasing Document & Currency',
        'steps': ['convert_reference', 'convert_currency', 'add_usd_amount']
    },
    'rfp': {
        'name': 'RFP File',
        'description': 'Filter & Convert Currency',
        'steps': ['convert_currency', 'add_usd_amount', 'calculate_total']
    },
    'reclass': {
        'name': 'Reclass File',
        'description': 'Convert Currency & Calculate Total',
        'steps': ['convert_currency', 'add_usd_amount', 'calculate_total']
    },
    'zmm': {
        'name': 'ZMM File',
        'description': 'Process PR Numbers & Copy Columns',
        'steps': ['find_pr_column', 'delimit_pr', 'copy_columns']
    }
}

# Special markers/codes to filter
SPECIAL_MARKERS = {
    'car_plan': 'GNT-OTACP-25',
    'cbip_code': 'M-CBIP-25'
}

# Output column names
OUTPUT_COLUMNS = {
    'usd_amount': 'Amount_USD',
    'pr_ref_delimited': 'Ariba PR Reference (Delimited)',
    'pr_ref_numeric': 'Ariba PR Reference (Numeric)',
    'pr_ref_copy': 'Ariba PR Reference (Copy)',
    'po_copy': 'PO Number (Copy)',
    'vendor_copy': 'Vendor Name (Copy)'
}
