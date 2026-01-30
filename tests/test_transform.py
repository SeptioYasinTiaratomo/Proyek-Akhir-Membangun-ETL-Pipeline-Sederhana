import unittest
import pandas as pd
import os
import sys
import logging
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.load import DataLoader, load_data

logging.basicConfig(level=logging.INFO)

class TestLoadModule(unittest.TestCase):
    
    def setUp(self):
        self.data = pd.DataFrame({
            'Title': ['Test Shirt'],
            'Price': [399000.0],
            'Rating': [4.5],
            'Colors': [2],
            'Size': ['S'],
            'Gender': ['Men'],
            'timestamp': ['2026-01-29 10:00:00']
        })
        self.output_file = "tests/test_products_output.csv"
        self.loader = DataLoader()
        
        if not os.path.exists("tests"): os.makedirs("tests")
            
    def tearDown(self):
        if os.path.exists(self.output_file):
            try: os.remove(self.output_file)
            except: pass

    # --- TEST CSV ---
    def test_save_csv_success(self):
        success = self.loader.save_to_csv(self.data, self.output_file)
        self.assertTrue(success)

    def test_save_empty_dataframe(self):
        empty_df = pd.DataFrame()
        success = self.loader.save_to_csv(empty_df, self.output_file)
        self.assertFalse(success)

    def test_save_csv_error(self):
        """Simulasi error saat save CSV (misal permission denied)"""
        with patch('pandas.DataFrame.to_csv', side_effect=Exception("Disk Full")):
            success = self.loader.save_to_csv(self.data, self.output_file)
            self.assertFalse(success)

    # --- TEST GOOGLE SHEETS ---
    
    @patch('utils.load.os.path.exists')
    @patch('utils.load.service_account.Credentials')
    @patch('utils.load.build')
    def test_save_google_sheets_success(self, mock_build, mock_creds, mock_path):
        """Test Happy Path Google Sheets (Pura-pura sukses konek)"""
        print("\n🧪 Testing Google Sheets Success (Mock)...")
        
        # 1. Pura-pura file json ada
        mock_path.return_value = True 
        
        # 2. Setup Mock Service Google
        mock_service = MagicMock()
        mock_sheets = MagicMock()
        
        mock_build.return_value = mock_service
        mock_service.spreadsheets.return_value = mock_sheets
        
        # PENTING: Return dictionary asli untuk execute() agar tidak error format string
        mock_sheets.values.return_value.update.return_value.execute.return_value = {
            'updatedCells': 100
        }
        
        # 3. Jalankan fungsi
        success = self.loader.save_to_google_sheets(self.data, spreadsheet_id="dummy_id")
        
        # 4. Assert
        self.assertTrue(success)
        mock_sheets.values.return_value.clear.assert_called()
        mock_sheets.values.return_value.update.assert_called()
        print("✅ Google Sheets success path covered")

    @patch('utils.load.os.path.exists')
    def test_save_google_sheets_no_creds(self, mock_path):
        """Test jika file credentials tidak ada"""
        mock_path.return_value = False
        success = self.loader.save_to_google_sheets(self.data)
        self.assertFalse(success)

    @patch('utils.load.os.path.exists')
    @patch('utils.load.service_account.Credentials')
    def test_save_google_sheets_auth_error(self, mock_creds, mock_path):
        """Test jika login google gagal"""
        mock_path.return_value = True
        mock_creds.from_service_account_file.side_effect = Exception("Auth Failed")
        
        success = self.loader.save_to_google_sheets(self.data)
        self.assertFalse(success)

    @patch('utils.load.os.path.exists')
    @patch('utils.load.service_account.Credentials')
    @patch('utils.load.build')
    def test_save_google_sheets_api_error(self, mock_build, mock_creds, mock_path):
        """Test jika API Google error saat upload"""
        mock_path.return_value = True
        
        # Setup service mock tapi bikin error pas execute()
        mock_service = MagicMock()
        mock_service.spreadsheets.return_value.values.return_value.clear.side_effect = Exception("API Error")
        mock_build.return_value = mock_service
        
        success = self.loader.save_to_google_sheets(self.data)
        self.assertFalse(success)

    # --- TEST WRAPPER & ENTRY POINT (Coverage Booster) ---

    @patch('utils.load.DataLoader.save_to_google_sheets')
    @patch('utils.load.DataLoader.save_to_csv')
    def test_save_to_all_repositories(self, mock_save_csv, mock_save_sheets):
        """Test fungsi wrapper save_to_all_repositories"""
        print("\n🧪 Testing save_to_all_repositories wrapper...")
        
        # Setup return values
        mock_save_csv.return_value = True
        mock_save_sheets.return_value = True
        
        # Panggil fungsi wrapper
        results = self.loader.save_to_all_repositories(self.data, google_sheets_id="test_id")
        
        # Assertions
        self.assertTrue(results['csv'])
        self.assertTrue(results['google_sheets'])
        
        mock_save_csv.assert_called_once()
        mock_save_sheets.assert_called_once()
        print("✅ Wrapper function covered")

    def test_load_data_entry_point(self):
        """Test fungsi entry point load_data"""
        print("\n🧪 Testing entry point load_data...")
        
        # Mock class DataLoader di dalam utils.load
        with patch('utils.load.DataLoader') as MockLoader:
            instance = MockLoader.return_value
            instance.save_to_csv.return_value = True
            
            # Case 1: CSV Only
            res = load_data(self.data, repositories=['csv'])
            self.assertTrue(res['csv'])
            
            # Case 2: All Repositories
            instance.save_to_all_repositories.return_value = {'csv': True, 'google_sheets': True}
            res_all = load_data(self.data, repositories=['all'])
            self.assertTrue(res_all['google_sheets'])
        print("✅ Entry point covered")

if __name__ == '__main__':
    unittest.main()