"""
CJI5 and CJI3 file processors (STEP 4-7)
Handles conversion of reference documents and currency
"""
import pandas as pd
from processors.base import BaseProcessor
from config import OUTPUT_COLUMNS


class CJIProcessor(BaseProcessor):
    """Processor for CJI5 and CJI3 files"""
    
    def __init__(self, file_type):
        if file_type not in ['cji5', 'cji3']:
            raise ValueError(f"Invalid CJI file type: {file_type}")
        super().__init__(file_type)
    
    def process_basic(self, exchange_rates=None):
        """
        Basic CJI processing: Convert reference and currency
        
        Args:
            exchange_rates: optional custom exchange rates dict
            
        Returns:
            Processed DataFrame
        """
        # STEP 4: Convert reference document to numeric
        ref_col_key = 'reference_doc' if self.file_type == 'cji5' else 'purch_doc'
        self.convert_reference_to_numeric(ref_col_key)
        
        # STEP 5: Convert currency to USD
        self.convert_currency(exchange_rates)
        
        # Blank out amounts for subtotal rows
        self.blank_subtotal_rows('project')
        
        return self.df
    
    def process_with_pivot(self, exchange_rates=None):
        """
        CJI processing with pivot table generation (STEP 6-7)
        
        Args:
            exchange_rates: optional custom exchange rates dict
            
        Returns:
            Tuple of (processed_df, pivot_df)
        """
        # First do basic processing
        self.process_basic(exchange_rates)
        
        # Prepare data for pivot (exclude subtotal rows)
        project_col = self.columns.get('project')
        if project_col:
            df_for_pivot = self.df[
                self.df[project_col].notna() & (self.df[project_col] != '')
            ].copy()
        else:
            df_for_pivot = self.df.copy()
        
        # Create pivot table
        ref_col_key = 'reference_doc' if self.file_type == 'cji5' else 'purch_doc'
        ref_col = self.columns.get(ref_col_key)
        
        if self.file_type == 'cji5':
            # STEP 6: CJI5 Pivot
            # Columns: Reference Document Category, Rows: Reference Document number, Values: Amount_USD
            cat_col = self.columns.get('reference_category')
            if cat_col:
                pivot = pd.pivot_table(
                    df_for_pivot,
                    values=OUTPUT_COLUMNS['usd_amount'],
                    index=ref_col,
                    columns=cat_col,
                    aggfunc='sum',
                    fill_value=0,
                    margins=True
                )
            else:
                pivot = pd.pivot_table(
                    df_for_pivot,
                    values=OUTPUT_COLUMNS['usd_amount'],
                    index=ref_col,
                    aggfunc='sum',
                    fill_value=0,
                    margins=True
                )
        else:
            # STEP 7: CJI3 Pivot
            # Rows: Purchasing Document Number, Values: Amount_USD
            pivot = pd.pivot_table(
                df_for_pivot,
                values=OUTPUT_COLUMNS['usd_amount'],
                index=ref_col,
                aggfunc='sum',
                fill_value=0,
                margins=True
            )
        
        return self.df, pivot
    
    def process_without_carplan(self, exchange_rates=None):
        """
        Process CJI file excluding car plan entries (STEP 14)
        
        Args:
            exchange_rates: optional custom exchange rates dict
            
        Returns:
            Processed DataFrame without car plan
        """
        # Remove car plan entries (GNT-OTACP-25)
        carplan_marker = 'GNT-OTACP-25'
        project_col = self.columns.get('project')
        
        if project_col:
            original_count = len(self.df)
            self.df = self.df[
                ~self.df[project_col].astype(str).str.contains(carplan_marker, na=False)
            ]
            removed_count = original_count - len(self.df)
            
            # Now process remaining data
            self.process_basic(exchange_rates)
            
            return self.df, removed_count
        
        # If no project column, just do normal processing
        self.process_basic(exchange_rates)
        return self.df, 0
    
    def separate_carplan(self):
        """
        Separate car plan entries from main file (STEP 1)
        
        Returns:
            Tuple of (main_df, carplan_df)
        """
        carplan_marker = 'GNT-OTACP-25'
        project_col = self.columns.get('project')
        
        if not project_col:
            return self.df, None
        
        carplan_mask = self.df[project_col].astype(str).str.contains(carplan_marker, na=False)
        carplan_df = self.df[carplan_mask].copy()
        main_df = self.df[~carplan_mask].copy()
        
        self.df = main_df
        
        return main_df, carplan_df
