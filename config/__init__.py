"""
CAPEX Reporting Tool Configuration Module
Exports all configuration settings from config.py
"""

from config.config import (
    EXCHANGE_RATES,
    COLUMN_MAPPINGS,
    FILE_TYPES,
    SPECIAL_MARKERS,
    OUTPUT_COLUMNS,
    WP_LOA_CONFIG
)

__all__ = [
    'EXCHANGE_RATES',
    'COLUMN_MAPPINGS',
    'FILE_TYPES',
    'SPECIAL_MARKERS',
    'OUTPUT_COLUMNS',
    'WP_LOA_CONFIG'
]
