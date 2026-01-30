import pandas as pd
import logging
import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- BAGIAN INI DIPINDAHKAN KE ATAS (TOP LEVEL) ---
# Tujuannya agar unittest.mock bisa menemukan objek 'build' dan 'service_account'
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False
    # Definisi dummy agar tidak error saat di-mock jika library belum install
    service_account = None
    build = None
    HttpError = None
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Kelas untuk loading data ke CSV dan Google Sheets"""
    
    def __init__(self):
        logger.info("DataLoader initialized")
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = "products.csv") -> bool:
        """
        Simpan data ke CSV file
        """
        try:
            if df.empty:
                logger.error("Cannot save empty DataFrame to CSV")
                print("❌ Error: DataFrame is empty")
                return False
            
            print(f"\n💾 Saving to CSV...")
            
            # Kolom yang akan disimpan (Pastikan timestamp ada)
            required_columns = ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'timestamp']
            
            # Ambil kolom yang benar-benar ada di DataFrame
            available_columns = [col for col in required_columns if col in df.columns]
            
            if not available_columns:
                print(f"⚠️  Warning: No valid columns found. Available in DF: {df.columns.tolist()}")
                output_df = df.copy()
            else:
                output_df = df[available_columns].copy()
            
            # SAVE TO CSV
            output_df.to_csv(filename, index=False)
            
            # VERIFIKASI
            file_size = os.path.getsize(filename) / 1024  # Size in KB
            
            print(f"✅ CSV saved successfully!")
            print(f"   📁 File: {os.path.abspath(filename)}")
            print(f"   📊 Rows: {len(output_df):,}")
            print(f"   📈 Columns: {len(output_df.columns)}")
            print(f"   💾 Size: {file_size:.2f} KB")
            
            # PRINT SAMPLE DATA
            print(f"\n📋 Sample data (first 3 rows):")
            print("-" * 80)
            
            # Format Price untuk display saja
            display_df = output_df.head(3).copy()
            if 'Price' in display_df.columns:
                 if pd.api.types.is_numeric_dtype(display_df['Price']):
                    display_df['Price'] = display_df['Price'].apply(lambda x: f"Rp {x:,.2f}")
            
            print(display_df.to_string(index=False))
            print("-" * 80)
            
            logger.info(f"Saved {len(output_df)} rows to CSV: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            print(f"❌ Error saving to CSV: {e}")
            return False
    
    def save_to_google_sheets(self, df: pd.DataFrame, 
                            spreadsheet_id: Optional[str] = None,
                            credentials_file: str = "google-sheets-api.json") -> bool:
        """
        Simpan data ke Google Sheets
        """
        try:
            print(f"\n📊 Saving to Google Sheets...")
            
            # Cek Library Google (menggunakan flag global)
            if not GOOGLE_LIBS_AVAILABLE:
                print(f"   ❌ Library Google tidak terinstall.")
                print(f"   💡 Install: pip install google-api-python-client google-auth")
                return False

            # Gunakan spreadsheet ID Default jika tidak ada
            if not spreadsheet_id:
                spreadsheet_id = "1TTBCPo8qikB2vx14S3xitJOm6UycqcMnc4ZsyaNr2GQ"
            
            print(f"   🔗 Spreadsheet ID: {spreadsheet_id}")
            
            # 1. CHECK CREDENTIALS
            if not os.path.exists(credentials_file):
                print(f"   ❌ File credentials tidak ditemukan: {credentials_file}")
                return False
            
            print(f"   ✅ Found credentials file: {credentials_file}")
            
            # 2. PREPARE DATA
            output_df = self._prepare_output_dataframe(df)
            if output_df is None or output_df.empty:
                print(f"   ❌ DataFrame kosong")
                return False
            
            print(f"   📊 Data siap: {len(output_df)} rows, {len(output_df.columns)} columns")
            
            # 3. AUTHENTICATE
            try:
                SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_file, scopes=SCOPES
                )
                service = build('sheets', 'v4', credentials=credentials)
                print(f"   ✅ Authenticated with Google Sheets API")
                
            except Exception as e:
                print(f"   ❌ Authentication failed: {e}")
                return False
            
            # 4. WRITE DATA
            output_df = output_df.fillna('')
            # Convert timestamp/objects to string explicitly for JSON serialization
            output_df = output_df.astype(str)
            
            headers = output_df.columns.tolist()
            values = output_df.values.tolist()
            all_data = [headers] + values
            
            try:
                print(f"   ✍️  Writing data...")
                
                # Clear existing data
                service.spreadsheets().values().clear(
                    spreadsheetId=spreadsheet_id,
                    range='Sheet1!A:Z',
                    body={}
                ).execute()
                
                # Update new data
                body = {'values': all_data, 'majorDimension': 'ROWS'}
                result = service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='Sheet1!A1',
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                print(f"\n   🎉 DATA BERHASIL DISIMPAN KE GOOGLE SHEETS!")
                print(f"   📈 Cells updated: {result.get('updatedCells', 0):,}")
                print(f"   🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                return True
                
            except Exception as e:
                print(f"   ❌ Error writing to Sheets: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error in save_to_google_sheets: {e}")
            return False
    
    def _prepare_output_dataframe(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Prepare DataFrame untuk output (Cleaning final sebelum upload)"""
        try:
            if df.empty: return None
            
            # --- UPDATE: Tambahkan 'timestamp' agar masuk ke Google Sheets juga ---
            target_cols = ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'timestamp']
            
            available = [c for c in target_cols if c in df.columns]
            
            output_df = df[available].copy()
            
            # Pastikan tipe data aman
            if 'Colors' in output_df.columns:
                output_df['Colors'] = pd.to_numeric(output_df['Colors'], errors='coerce').fillna(0).astype(int)
            
            if 'Price' in output_df.columns:
                 output_df['Price'] = pd.to_numeric(output_df['Price'], errors='coerce').fillna(0)

            return output_df
            
        except Exception as e:
            logger.error(f"Error preparing output DataFrame: {e}")
            return None

    def save_to_all_repositories(self, df: pd.DataFrame, google_sheets_id: Optional[str] = None) -> Dict[str, bool]:
        """Simpan ke CSV dan Sheets"""
        print("\n" + "="*80)
        print("🚀 SAVING TO DATA REPOSITORIES")
        print("="*80)
        
        results = {'csv': False, 'google_sheets': False}
        
        # 1. CSV
        print(f"\n📌 Basic Requirement: CSV File")
        results['csv'] = self.save_to_csv(df)
        
        # 2. Google Sheets
        print(f"\n📌 Skilled Requirement: Google Sheets")
        results['google_sheets'] = self.save_to_google_sheets(df, google_sheets_id)
        
        self._print_save_summary(results)
        return results

    def _print_save_summary(self, results: Dict[str, bool]):
        print("\n" + "="*80)
        print("📊 SAVE OPERATIONS SUMMARY")
        print("="*80)
        
        count = sum(results.values())
        for repo, success in results.items():
            symbol = "✅" if success else "❌"
            print(f"{symbol} {repo.upper():15}")
            
        print(f"\n📈 Success rate: {count}/{len(results)} repositories")
        if results['csv'] and results['google_sheets']:
            print("🎉 ALL CRITERIA MET!")

# Fungsi utama yang dipanggil main.py
def load_data(df: pd.DataFrame, repositories: List[str] = ['csv', 'google_sheets'], **kwargs) -> Dict[str, bool]:
    loader = DataLoader()
    
    if 'all' in repositories or 'google_sheets' in repositories:
         return loader.save_to_all_repositories(df, kwargs.get('google_sheets_id'))
    else:
         # CSV Only
         return {'csv': loader.save_to_csv(df)}

if __name__ == "__main__":
    # Test sederhana
    print("Testing DataLoader...")
    df_test = pd.DataFrame({
        'Title': ['Baju Test', 'Celana Test'],
        'Price': [150000.0, 200000.0],
        'Rating': [4.5, 5.0],
        'Colors': [2, 1],
        'Size': ['M', 'L'],
        'Gender': ['Male', 'Female'],
        'timestamp': ['2025-01-01 10:00:00', '2025-01-01 10:00:00']
    })
    DataLoader().save_to_csv(df_test, "test_output.csv")