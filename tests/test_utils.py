"""
tests/test_utils.py - בדיקות יחידה למודול utils
"""
import unittest
import pandas as pd
import sys
import os

# הוספת הנתיב של הפרויקט
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils

class TestUtils(unittest.TestCase):
    """בדיקות למודול utils"""
    
    def setUp(self):
        """הכנת נתוני בדיקה"""
        self.test_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'amount': [100, 200, 150],
            'category': ['Income', 'Income', 'Expense'],
            'type': ['Sale', 'Service', 'Material']
        })
    
    def test_execute_sql_basic_select(self):
        """בדיקת ביצוע שאילתת SELECT בסיסית"""
        sql = "SELECT * FROM data WHERE amount > 100"
        result = utils.execute_sql(self.test_data, sql)
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['amount'] > 100))
    
    def test_execute_sql_aggregation(self):
        """בדיקת ביצוע שאילתת צבירה"""
        sql = "SELECT category, SUM(amount) as total FROM data GROUP BY category"
        result = utils.execute_sql(self.test_data, sql)
        
        self.assertEqual(len(result), 2)
        income_total = result[result['category'] == 'Income']['total'].iloc[0]
        self.assertEqual(income_total, 300)
    
    def test_execute_sql_date_filtering(self):
        """בדיקת סינון לפי תאריך"""
        sql = "SELECT * FROM data WHERE CAST(date AS DATE) >= '2024-01-02'"
        result = utils.execute_sql(self.test_data, sql)
        
        self.assertEqual(len(result), 2)
    
    def test_execute_sql_invalid_query(self):
        """בדיקה ששאילתה לא תקינה זורקת שגיאה"""
        sql = "SELECT * FROM non_existent_table"
        
        with self.assertRaises(Exception):
            utils.execute_sql(self.test_data, sql)
    
    def test_execute_sql_empty_result(self):
        """בדיקה ששאילתה שלא מחזירה תוצאות מחזירה DataFrame ריק"""
        sql = "SELECT * FROM data WHERE amount > 1000"
        result = utils.execute_sql(self.test_data, sql)
        
        self.assertTrue(result.empty)
        self.assertIsInstance(result, pd.DataFrame)

if __name__ == '__main__':
    unittest.main() 