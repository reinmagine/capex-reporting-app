"""
File Detection Utility
Detects document files based on keyword patterns rather than exact filenames
Handles variations in file naming conventions (dates, case sensitivity, etc.)
"""

import os
from pathlib import Path
from typing import Optional, Dict, List


class FileDetector:
    """Flexible file detection based on keywords patterns"""
    
    # File pattern keywords (case-insensitive)
    FILE_PATTERNS = {
        'capex_availment': ['capex', 'availment', '2026'],
        'loa_approver': ['loa', 'approver', 'email'],
        'wp_loa_report': ['wp', 'loa', 'report'],
        'budget': ['budget'],
    }
    
    @staticmethod
    def find_file_by_keywords(directory: str, keywords: List[str], 
                             file_extensions: List[str] = None) -> Optional[str]:
        """
        Find a file in directory matching ALL keywords (case-insensitive)
        
        Args:
            directory: Directory to search in
            keywords: List of keywords that must appear in filename
            file_extensions: File extensions to search for (default: .xlsx, .xls)
            
        Returns:
            Full path to matching file, or None if not found
        """
        if not os.path.isdir(directory):
            return None
        
        if file_extensions is None:
            file_extensions = ['.xlsx', '.xls', '.csv']
        
        try:
            files = os.listdir(directory)
            filename_lower_list = [(f, f.lower()) for f in files]
            
            for filename, filename_lower in filename_lower_list:
                # Check file extension
                if not any(filename_lower.endswith(ext.lower()) for ext in file_extensions):
                    continue
                
                # Check if ALL keywords are in filename (case-insensitive)
                if all(keyword.lower() in filename_lower for keyword in keywords):
                    return str(Path(directory) / filename)
            
            return None
        except Exception as e:
            print(f"Error searching for files: {e}")
            return None
    
    @staticmethod
    def find_capex_availment(directory: str) -> Optional[str]:
        """
        Find CAPEX AVAILMENT file (handles date variations)
        
        Examples:
        - "2026 CAPEX AVAILMENT_as of FEB 23"
        - "2026 CAPEX AVAILMENT_as of Feb 16"
        - "CAPEX_AVAILMENT_2026"
        
        Args:
            directory: Directory to search in
            
        Returns:
            Full path to CAPEX AVAILMENT file, or None
        """
        keywords = FileDetector.FILE_PATTERNS['capex_availment']
        return FileDetector.find_file_by_keywords(directory, keywords)
    
    @staticmethod
    def find_loa_approver(directory: str) -> Optional[str]:
        """
        Find LOA Current Approver file (handles naming variations)
        
        Examples:
        - "LOA_CURRENT_APPROVER (Auto Email).xlsx"
        - "LOA Current Approver - Auto Email.xlsx"
        - "LOA_CURRENT_APPROVER.xlsx"
        
        Args:
            directory: Directory to search in
            
        Returns:
            Full path to LOA approver file, or None
        """
        keywords = FileDetector.FILE_PATTERNS['loa_approver']
        return FileDetector.find_file_by_keywords(directory, keywords)
    
    @staticmethod
    def find_wp_loa_report(directory: str) -> Optional[str]:
        """
        Find WP LOA Report file (handles naming variations)
        
        Examples:
        - "WP LOA Report.xlsx"
        - "WP_LOA_Report_2026.xlsx"
        - "WP LOA Report - 2026.xlsx"
        
        Args:
            directory: Directory to search in
            
        Returns:
            Full path to WP LOA Report file, or None
        """
        keywords = FileDetector.FILE_PATTERNS['wp_loa_report']
        return FileDetector.find_file_by_keywords(directory, keywords)
    
    @staticmethod
    def find_budget_file(directory: str) -> Optional[str]:
        """
        Find BUDGET reference file
        
        Args:
            directory: Directory to search in
            
        Returns:
            Full path to BUDGET file, or None
        """
        keywords = FileDetector.FILE_PATTERNS['budget']
        return FileDetector.find_file_by_keywords(directory, keywords)
    
    @staticmethod
    def auto_detect_all_files(directory: str) -> Dict[str, Optional[str]]:
        """
        Auto-detect all required files in a directory
        
        Args:
            directory: Directory to search in
            
        Returns:
            Dictionary with file paths:
            {
                'wp_loa_report': path or None,
                'capex_availment': path or None,
                'loa_approver': path or None,
                'budget': path or None
            }
        """
        return {
            'wp_loa_report': FileDetector.find_wp_loa_report(directory),
            'capex_availment': FileDetector.find_capex_availment(directory),
            'loa_approver': FileDetector.find_loa_approver(directory),
            'budget': FileDetector.find_budget_file(directory),
        }
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, any]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info (name, size, exists)
        """
        if not os.path.exists(file_path):
            return {'exists': False, 'name': Path(file_path).name}
        
        return {
            'exists': True,
            'name': Path(file_path).name,
            'size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'path': file_path,
        }
