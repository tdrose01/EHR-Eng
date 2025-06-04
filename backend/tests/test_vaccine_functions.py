#!/usr/bin/env python3
"""
Unit tests for vaccine scheduling functions
"""
import os
import sys
import unittest
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class VaccineFunctionsTest(unittest.TestCase):
    """Test cases for vaccine scheduling PostgreSQL functions"""

    def setUp(self):
        """Set up database connection for test"""
        try:
            self.conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                port=os.environ.get('DB_PORT', '5432'),
                dbname=os.environ.get('DB_NAME', 'healthrecords'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'postgres')
            )
            self.conn.autocommit = True
            print("Database connection established")
        except Exception as e:
            print(f"Database connection error: {e}")
            self.skipTest("Database connection failed")

    def tearDown(self):
        """Close database connection after test"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_calculate_next_dose_date(self):
        """Test calculate_next_dose_date function"""
        cursor = self.conn.cursor()
        
        # Test with EXAMPLE_VACCINE for 18-65 age (7 days interval)
        cursor.execute(
            "SELECT calculate_next_dose_date(%s, %s, %s, %s, %s, %s)",
            ["EXAMPLE_VACCINE", "EXAMPLE_BRAND", "EXAMPLE_MANUFACTURER", 
             1, datetime.date.today(), datetime.date.today() - datetime.timedelta(days=365*30)]
        )
        next_date = cursor.fetchone()[0]
        
        # Check that next date is 7 days after today for dose 1->2
        self.assertEqual(next_date, datetime.date.today() + datetime.timedelta(weeks=1))
        
        # Test with EXAMPLE_VACCINE for seniors (28 days interval)
        cursor.execute(
            "SELECT calculate_next_dose_date(%s, %s, %s, %s, %s, %s)",
            ["EXAMPLE_VACCINE", "EXAMPLE_BRAND_SENIOR", "EXAMPLE_MANUFACTURER", 
             1, datetime.date.today(), datetime.date.today() - datetime.timedelta(days=365*70)]
        )
        next_date = cursor.fetchone()[0]
        
        # Check that next date is 28 days after today for dose 1->2
        self.assertEqual(next_date, datetime.date.today() + datetime.timedelta(weeks=4))
        
        cursor.close()

    def test_get_vaccine_alternative_schedules(self):
        """Test get_vaccine_alternative_schedules function"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        # Test with EXAMPLE_VACCINE for dose 2 which has alternatives
        cursor.execute(
            "SELECT * FROM get_vaccine_alternative_schedules(%s, %s, %s, %s)",
            ["EXAMPLE_VACCINE", "EXAMPLE_BRAND", "EXAMPLE_MANUFACTURER", 2]
        )
        alternatives = cursor.fetchall()
        
        # Should have two alternative schedules
        self.assertEqual(len(alternatives), 2)
        self.assertTrue(any(alt['interval_weeks'] == 1 for alt in alternatives))  # 7 days
        self.assertTrue(any(alt['interval_weeks'] == 4 for alt in alternatives))  # 28 days
        
        # Test with a different dose which has no alternatives
        cursor.execute(
            "SELECT * FROM get_vaccine_alternative_schedules(%s, %s, %s, %s)",
            ["EXAMPLE_VACCINE", "EXAMPLE_BRAND", "EXAMPLE_MANUFACTURER", 1]
        )
        alternatives = cursor.fetchall()
        
        # Should have only one schedule
        self.assertLessEqual(len(alternatives), 1)
        
        cursor.close()
        
    def test_get_vaccine_dose_by_age(self):
        """Test get_vaccine_dose_by_age function"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        # Test for adult 30 years old
        birthdate = datetime.date.today() - datetime.timedelta(days=365*30)
        cursor.execute(
            "SELECT * FROM get_vaccine_dose_by_age(%s, %s, %s, %s)",
            ["EXAMPLE_VACCINE", "EXAMPLE_BRAND", "EXAMPLE_MANUFACTURER", birthdate]
        )
        dose_info = cursor.fetchone()
        
        # Check dose amount for adult
        self.assertIsNotNone(dose_info)
        self.assertEqual(dose_info['dose_amount'], '0.5 mL')
        self.assertEqual(dose_info['preferred_route'], 'IM')
        
        # Test for senior 70 years old
        birthdate = datetime.date.today() - datetime.timedelta(days=365*70)
        cursor.execute(
            "SELECT * FROM get_vaccine_dose_by_age(%s, %s, %s, %s)",
            ["EXAMPLE_VACCINE", "EXAMPLE_BRAND_SENIOR", "EXAMPLE_MANUFACTURER", birthdate]
        )
        dose_info = cursor.fetchone()
        
        # Check dose amount for senior
        self.assertIsNotNone(dose_info)
        self.assertEqual(dose_info['dose_amount'], '0.5 mL')
        
        cursor.close()


if __name__ == '__main__':
    unittest.main() 