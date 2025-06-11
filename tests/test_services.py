"""
tests/test_services.py - בדיקות יחידה למודול services
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# הוספת הנתיב של הפרויקט
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services

class TestServices(unittest.TestCase):
    """בדיקות למודול services"""
    
    def test_get_exchange_rate_same_currency(self):
        """בדיקה שהמרה של מטבע לעצמו מחזירה 1"""
        rate = services.get_exchange_rate("USD", "USD")
        self.assertEqual(rate, 1.0)
    
    def test_get_exchange_rate_different_currencies(self):
        """בדיקה שהמרה בין מטבעות מחזירה ערך חיובי"""
        rate = services.get_exchange_rate("USD", "EUR")
        self.assertIsNotNone(rate)
        self.assertGreater(rate, 0)
    
    def test_forecast_cashflow_basic(self):
        """בדיקה בסיסית של תחזית תזרים מזומנים"""
        # יצירת נתוני בדיקה
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
        amounts = [1000, 1200, 800, 1500, 1100, 900, 1300, 1400, 1000, 1600, 1200, 1100]
        df = pd.DataFrame({
            'date': dates,
            'amount': amounts
        })
        
        # הרצת תחזית
        forecast = services.forecast_cashflow(df, periods=6)
        
        # בדיקות
        self.assertIsNotNone(forecast)
        self.assertEqual(len(forecast), 6)
        self.assertIn('date', forecast.columns)
        self.assertIn('forecast', forecast.columns)
        
        # בדיקה שהתאריכים עתידיים
        last_historical_date = df['date'].max()
        self.assertTrue(all(forecast['date'] > last_historical_date))
    
    def test_forecast_cashflow_empty_data(self):
        """בדיקה שתחזית עם נתונים ריקים לא קורסת"""
        df = pd.DataFrame({
            'date': [],
            'amount': []
        })
        
        # הרצת תחזית - צריכה להחזיר DataFrame ריק
        forecast = services.forecast_cashflow(df, periods=6)
        self.assertEqual(len(forecast), 6)  # עדיין צריך להחזיר תחזית

class TestExchangeRateFallback(unittest.TestCase):
    """בדיקות למנגנון ה-fallback של שערי חליפין"""
    
    def test_fallback_rates_exist(self):
        """בדיקה שיש ערכי fallback לזוגות מטבע נפוצים"""
        common_pairs = [
            ("USD", "EUR"),
            ("USD", "ILS"),
            ("EUR", "ILS"),
            ("GBP", "USD")
        ]
        
        for base, target in common_pairs:
            rate = services.get_exchange_rate(base, target)
            self.assertIsNotNone(rate, f"Missing rate for {base}/{target}")
            self.assertGreater(rate, 0, f"Invalid rate for {base}/{target}")

if __name__ == '__main__':
    unittest.main() 