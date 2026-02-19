"""
Unified currency conversion utility
Handles conversion from various currencies to USD
"""
import pandas as pd
from config import EXCHANGE_RATES


class CurrencyConverter:
    """Single unified currency converter for all file types"""
    
    @staticmethod
    def convert_value(amount, currency, exchange_rates=None):
        """
        Convert amount from given currency to USD
        
        Args:
            amount: numeric amount to convert
            currency: currency code (e.g., 'PHP', 'SGD', 'USD')
            exchange_rates: dict of exchange rates (uses config default if None)
            
        Returns:
            Amount in USD (float)
        """
        rates = exchange_rates or EXCHANGE_RATES
        
        if pd.isna(amount) or pd.isna(currency):
            return amount
        
        currency = str(currency).upper().strip()
        
        if currency in ['USD', 'US', 'USA']:
            return float(amount)
        elif currency in ['PHP', 'PESO', 'PHILIPPINE PESO']:
            return float(amount) / rates.get('PHP', 57)
        elif currency in ['SGD', 'SINGAPORE DOLLAR']:
            return float(amount) / rates.get('SGD', 1.34)
        else:
            # Return as-is if currency not recognized
            return float(amount)
    
    @staticmethod
    def apply_currency_conversion(df, currency_col, amount_col, output_col='Amount_USD', 
                                 exchange_rates=None, round_to=2):
        """
        Apply currency conversion to entire DataFrame column
        
        Args:
            df: pandas DataFrame
            currency_col: column name with currency codes
            amount_col: column name with amounts to convert
            output_col: name of output column with USD amounts
            exchange_rates: dict of exchange rates
            round_to: decimal places to round to
            
        Returns:
            DataFrame with new USD amount column added
        """
        df = df.copy()
        
        if currency_col not in df.columns or amount_col not in df.columns:
            raise ValueError(f"Required columns not found: {currency_col}, {amount_col}")
        
        # Apply row-wise conversion
        df[output_col] = df.apply(
            lambda row: CurrencyConverter.convert_value(
                row[amount_col], 
                row[currency_col],
                exchange_rates
            ),
            axis=1
        )
        
        # Round to specified decimal places
        df[output_col] = df[output_col].round(round_to)
        
        return df
    
    @staticmethod
    def update_exchange_rates(new_rates):
        """
        Update global exchange rates
        
        Args:
            new_rates: dict with 'PHP' and 'SGD' keys containing conversion rates
        """
        global EXCHANGE_RATES
        if 'PHP' in new_rates:
            EXCHANGE_RATES['PHP'] = new_rates['PHP']
            EXCHANGE_RATES['PHP_TO_USD'] = 1 / new_rates['PHP']
        if 'SGD' in new_rates:
            EXCHANGE_RATES['SGD'] = new_rates['SGD']
            EXCHANGE_RATES['SGD_TO_USD'] = 1 / new_rates['SGD']
