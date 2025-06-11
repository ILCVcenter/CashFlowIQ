"""
tests/test_data_loader.py - בדיקות יחידה למודול data_loader
"""
import unittest
import pandas as pd
import sys
import os
from datetime import datetime

# הוספת הנתיב של הפרויקט
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_loader import (
    filter_data_by_date_range,
    filter_data_by_categories,
    filter_data_by_types
)

class TestDataLoader(unittest.TestCase):
    """בדיקות למודול data_loader"""
    
    def setUp(self):
        """הכנת נתוני בדיקה"""
        self.test_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
            'amount': [100, -50, 200, -75, 150, -100, 300, -125, 250, -80],
            'category': ['Income', 'Expense', 'Income', 'Expense', 'Income', 
                        'Expense', 'Income', 'Expense', 'Income', 'Expense'],
            'type': ['Sale', 'Material', 'Service', 'Utility', 'Sale',
                    'Material', 'Service', 'Salary', 'Sale', 'Utility']
        })
    
    def test_filter_by_date_range(self):
        """בדיקת סינון לפי טווח תאריכים"""
        start_date = datetime(2024, 1, 3).date()
        end_date = datetime(2024, 1, 7).date()
        
        filtered = filter_data_by_date_range(self.test_data, [start_date, end_date])
        
        self.assertEqual(len(filtered), 5)
        self.assertTrue(all(filtered['date'] >= pd.Timestamp(start_date)))
        self.assertTrue(all(filtered['date'] <= pd.Timestamp(end_date)))
    
    def test_filter_by_categories(self):
        """בדיקת סינון לפי קטגוריות"""
        filtered = filter_data_by_categories(self.test_data, ['Income'])
        
        self.assertEqual(len(filtered), 5)
        self.assertTrue(all(filtered['category'] == 'Income'))
    
    def test_filter_by_types(self):
        """בדיקת סינון לפי סוגים"""
        filtered = filter_data_by_types(self.test_data, ['Sale', 'Service'])
        
        self.assertEqual(len(filtered), 5)
        self.assertTrue(all(filtered['type'].isin(['Sale', 'Service'])))
    
    def test_empty_filters(self):
        """בדיקה שסינון ריק מחזיר את כל הנתונים"""
        filtered_categories = filter_data_by_categories(self.test_data, [])
        filtered_types = filter_data_by_types(self.test_data, [])
        
        self.assertEqual(len(filtered_categories), len(self.test_data))
        self.assertEqual(len(filtered_types), len(self.test_data))
    
    def test_combined_filters(self):
        """בדיקת שילוב של מספר סינונים"""
        # סינון לפי תאריך
        filtered = filter_data_by_date_range(self.test_data, 
                                           [datetime(2024, 1, 1).date(), 
                                            datetime(2024, 1, 5).date()])
        # סינון לפי קטגוריה
        filtered = filter_data_by_categories(filtered, ['Income'])
        # סינון לפי סוג
        filtered = filter_data_by_types(filtered, ['Sale'])
        
        # בתאריכים 1-5 יש 3 רשומות Income, מתוכן 2 הן Sale (בתאריכים 1 ו-5)
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(filtered['type'] == 'Sale'))
        self.assertTrue(all(filtered['category'] == 'Income'))

if __name__ == '__main__':
    unittest.main() 