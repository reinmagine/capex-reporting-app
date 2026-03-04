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
            'Purchasing Document Number',
            'Purchase Document',
            'PO Number',
            'Document Number'
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

# WP LOA Report configuration
WP_LOA_CONFIG = {
    'required_columns': [
        'WP LOA',
        'BOQ PR (Pending no Ariba PR Only(',
        'YEAR',
        'PID (Mother and Sub)',
        'Amount (USD)'
    ],
    'budget_tab_name': 'BUDGET',
    'page_tab_name': 'page',
    'external_lookup_columns': {
        'PROPONENT': {
            'file_key': 'loa_approver',
            'sheet': 'page',
            'lookup_column': 'LOA#',
            'return_column': 'Current Approver'
        },
        'AVAILMENT_TRACKER': {
            'file_key': 'availment',
            'sheet': 'data_2026',
            'lookup_column': 'WP LOA Reference',
            'return_column': 0
        },
        'DIV_IN_REPORT': {
            'file_key': 'availment',
            'sheet': 'data_2026',
            'lookup_column': 'PRReferenceNumber',
            'return_column': 'Division'
        }
    },
    'derived_columns': {
        'L1': {
            'type': 'concatenate',
            'columns': ['PID (Mother and Sub)', '1', 'YEAR'],
            'separator': '-',
            'description': 'Concatenation of PID, L1 value, and Year'
        },
        'L2': {
            'type': 'copy',
            'source': 'PID (Mother and Sub)',
            'description': 'Copy of PID column'
        },
        'PROGRAM_MBR': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 9,
            'description': 'VLOOKUP to BUDGET sheet column 9'
        },
        'DIV': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 7,
            'description': 'VLOOKUP to BUDGET sheet column 7'
        },
        'DEP': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 6,
            'description': 'VLOOKUP to BUDGET sheet column 6'
        },
        'FUNDING': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 13,
            'description': 'VLOOKUP to BUDGET sheet column 13'
        },
        'CFU_SPONSOR': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 4,
            'description': 'VLOOKUP to BUDGET sheet column 4'
        },
        'PROPONENT_1': {
            'type': 'format_name',
            'source': 'PROPONENT',
            'description': 'Reformat PROPONENT name from "Last, First" to "First Last"'
        },
        'PROJ': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 11,
            'description': 'VLOOKUP to BUDGET sheet column 11'
        },
        'SUBPROJ': {
            'type': 'vlookup_budget',
            'lookup_col': 'L2',
            'return_col': 12,
            'description': 'VLOOKUP to BUDGET sheet column 12'
        }
    }
}
