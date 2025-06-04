#!/usr/bin/env python3
"""
Regression tests for vaccine API endpoints
"""
import os
import sys
import unittest
import json
import datetime
import requests
from unittest import mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the API app for testing
from api.vaccine_api import app

class VaccineApiTest(unittest.TestCase):
    """Test cases for vaccine API endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    @mock.patch('api.vaccine_api.get_db_connection')
    def test_get_vaccine_schedules(self, mock_db_conn):
        """Test the schedules endpoint"""
        # Mock database cursor and connection
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn
        
        # Set up mock return values
        mock_cursor.fetchall.return_value = [
            {
                'vaccine_name': 'EXAMPLE_VACCINE',
                'brand_name': 'EXAMPLE_BRAND',
                'manufacturer': 'EXAMPLE_MANUFACTURER',
                'dose_number': 1,
                'min_age_weeks': 936,
                'max_age_weeks': 3380,
                'interval_from_previous_weeks': None,
                'preferred_interval_weeks': 0,
                'notes': 'First dose for adults 18-65 years of age. Intramuscular administration only. Dose amount: 0.5 mL'
            }
        ]
        
        # Test the endpoint
        response = self.app.get('/api/vaccines/schedules?vaccine=EXAMPLE_VACCINE')
        data = json.loads(response.data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['schedules']), 1)
        self.assertEqual(data['schedules'][0]['vaccine_name'], 'EXAMPLE_VACCINE')

    @mock.patch('api.vaccine_api.get_db_connection')
    def test_get_alternative_schedules(self, mock_db_conn):
        """Test the alternative schedules endpoint"""
        # Mock database cursor and connection
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn
        
        # Set up mock return values
        mock_cursor.fetchall.return_value = [
            {'interval_weeks': 1, 'description': 'Standard schedule: 7 days after first dose'},
            {'interval_weeks': 4, 'description': 'Alternative schedule: 28 days after first dose'}
        ]
        
        # Test the endpoint
        url = '/api/vaccines/alternative-schedules?vaccine=EXAMPLE_VACCINE&brand=EXAMPLE_BRAND&manufacturer=EXAMPLE_MANUFACTURER&doseNumber=2'
        response = self.app.get(url)
        data = json.loads(response.data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['hasAlternatives'])
        self.assertEqual(len(data['alternatives']), 2)

    @mock.patch('api.vaccine_api.get_db_connection')
    def test_calculate_next_dose(self, mock_db_conn):
        """Test the next dose calculation endpoint"""
        # Mock database cursor and connection
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn
        
        # Set up mock return values
        test_date = (datetime.date.today() + datetime.timedelta(weeks=1))
        mock_cursor.fetchone.side_effect = [
            # First fetchone is for patient birthdate
            (datetime.date.today() - datetime.timedelta(days=365*30),),
            # Second fetchone is for next dose date
            (test_date,)
        ]
        
        # Test the endpoint
        url = (f'/api/vaccines/next-dose?vaccine=EXAMPLE_VACCINE&brand=EXAMPLE_BRAND&manufacturer=EXAMPLE_MANUFACTURER'
               f'&doseNumber=1&date={datetime.date.today().isoformat()}&patientId=1')
        response = self.app.get(url)
        data = json.loads(response.data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['nextDoseDate'], test_date.isoformat())
        self.assertFalse(data['customIntervalUsed'])

    @mock.patch('api.vaccine_api.get_db_connection')
    def test_dose_by_age(self, mock_db_conn):
        """Test the dose by age endpoint"""
        # Mock database cursor and connection
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn
        
        # Set up mock return values
        mock_cursor.fetchone.side_effect = [
            # First fetchone is for patient birthdate
            {'birth_date': datetime.date.today() - datetime.timedelta(days=365*30)},
            # Second fetchone is for dose info
            {
                'dose_amount': '0.5 mL',
                'preferred_route': 'IM',
                'preferred_site': 'RA',
                'route_name': 'Intramuscular',
                'site_name': 'Right Arm',
                'notes': 'Standard adult dose, administered intramuscularly'
            }
        ]
        
        # Test the endpoint
        url = '/api/vaccines/dose-by-age?vaccine=EXAMPLE_VACCINE&brand=EXAMPLE_BRAND&manufacturer=EXAMPLE_MANUFACTURER&patientId=1'
        response = self.app.get(url)
        data = json.loads(response.data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['doseInfo']['dose_amount'], '0.5 mL')
        self.assertEqual(data['doseInfo']['preferred_route'], 'IM')


class RegressionTest(unittest.TestCase):
    """Regression tests for vaccine API against a live server"""
    
    def setUp(self):
        """Set up base URL and session"""
        self.base_url = os.environ.get('API_BASE_URL', 'http://localhost:8004')
        self.session = requests.Session()
        
    def tearDown(self):
        """Close session"""
        self.session.close()
        
    def test_endpoints_availability(self):
        """Test that all required endpoints are available"""
        endpoints = [
            '/api/vaccines/schedules',
            '/api/vaccines/alternative-schedules',
            '/api/vaccines/next-dose',
            '/api/vaccines/available',
            '/api/vaccines/dose-by-age'
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", params={'dummy': 'param'})
                # We don't expect 200 since we're not providing valid params,
                # but we should get 400 Bad Request instead of 404 Not Found
                self.assertNotEqual(response.status_code, 404, f"Endpoint {endpoint} not found")
            except requests.RequestException as e:
                # Only fail if API is unreachable
                if "Connection refused" in str(e):
                    self.fail(f"API server unreachable at {self.base_url}")
                else:
                    print(f"Warning: {e}")
    
    def test_valid_api_responses(self):
        """Test with valid parameters to ensure API returns proper structure"""
        # We're only testing API response structure here, not actual data values
        try:
            # Test get available vaccines
            response = self.session.get(f"{self.base_url}/api/vaccines/available")
            if response.status_code == 200:
                data = response.json()
                self.assertTrue('success' in data)
                self.assertTrue('vaccines' in data)
                
                # If we have some vaccines, test more endpoints
                if data['success'] and len(data['vaccines']) > 0:
                    vaccine = data['vaccines'][0]
                    
                    # Test schedules
                    params = {
                        'vaccine': vaccine['vaccineName'],
                        'brand': vaccine['brandName'],
                        'manufacturer': vaccine['manufacturer']
                    }
                    response = self.session.get(f"{self.base_url}/api/vaccines/schedules", params=params)
                    if response.status_code == 200:
                        data = response.json()
                        self.assertTrue('success' in data)
                        self.assertTrue('schedules' in data)
        except requests.RequestException as e:
            # Only fail if API is unreachable
            if "Connection refused" in str(e):
                self.fail(f"API server unreachable at {self.base_url}")
            else:
                print(f"Warning: {e}")


if __name__ == '__main__':
    unittest.main() 