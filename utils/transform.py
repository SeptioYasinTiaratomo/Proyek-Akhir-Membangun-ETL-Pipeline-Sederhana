import pandas as pd
import numpy as np
import logging
from typing import Optional
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    """Kelas untuk transformasi data sesuai kriteria submission"""
    
    def __init__(self, exchange_rate: float = 16000):
        self.exchange_rate = exchange_rate
        logger.info(f"DataTransformer initialized with exchange rate: Rp {exchange_rate:,}")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Lakukan semua proses transformasi sesuai kriteria:
        1. Hapus duplikat
        2. Handle missing values
        3. Convert USD ke IDR
        4. Clean semua kolom
        5. Convert data types
        """
        try:
            logger.info("="*60)
            logger.info("STARTING DATA TRANSFORMATION")
            logger.info("="*60)
            
            initial_count = len(df)
            logger.info(f"Initial data: {initial_count} rows")
            
            # Buat copy untuk transformasi
            df_clean = df.copy()
            
            # 1. HAPUS DUPLIKAT
            df_clean = self._remove_duplicates(df_clean)
            
            # 2. HANDLE MISSING VALUES
            df_clean = self._handle_missing_values(df_clean)
            
            # 3. HAPUS DATA INVALID
            df_clean = self._remove_invalid_data(df_clean)
            
            # 4. KONVERSI MATA UANG (USD -> IDR)
            df_clean = self._convert_currency(df_clean)
            
            # 5. CLEAN RATING COLUMN
            df_clean = self._clean_rating(df_clean)
            
            # 6. CLEAN COLORS COLUMN
            df_clean = self._clean_colors(df_clean)
            
            # 7. CLEAN SIZE COLUMN
            df_clean = self._clean_size(df_clean)
            
            # 8. CLEAN GENDER COLUMN
            df_clean = self._clean_gender(df_clean)

            # 9. REORDER COLUMNS untuk output yang rapi
            df_clean = self._reorder_columns(df_clean)
            
            # 10. KONVERSI TIPE DATA
            df_clean = self._convert_dtypes(df_clean)
                
            
            final_count = len(df_clean)
            removed_count = initial_count - final_count
            
            logger.info("="*60)
            logger.info("TRANSFORMATION COMPLETE")
            logger.info("="*60)
            logger.info(f"Initial rows: {initial_count}")
            logger.info(f"Final rows: {final_count}")
            logger.info(f"Rows removed: {removed_count}")
            logger.info(f"Success rate: {(final_count/initial_count*100):.1f}%")
            
            # Print summary ke console
            print(f"\n✅ Transformation Results:")
            print(f"   Initial: {initial_count} rows")
            print(f"   Final: {final_count} rows")
            print(f"   Removed: {removed_count} rows")
            
            if final_count > 0:
                print(f"\n📋 Sample transformed data:")
                print("-" * 80)
                
                # --- PERBAIKAN: Definisi variabel dilakukan DI SINI ---
                cols_to_show = ['Title', 'Price', 'Rating', 'Size', 'Gender']
                
                # Filter kolom yang ada
                cols_exist = [c for c in cols_to_show if c in df_clean.columns]
                
                sample = df_clean[cols_exist].head(3)
                
                # Format price dengan Rp
                sample_display = sample.copy()
                if 'Price' in sample_display.columns:
                    sample_display['Price'] = sample_display['Price'].apply(lambda x: f"Rp {x:,.2f}")
                
                print(sample_display.to_string(index=False))
                print("-" * 80)
            
            return df_clean
        
        except Exception as e:
            logger.error(f"Error in clean_data: {e}")
            raise
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hapus data duplikat berdasarkan title"""
        try:
            before = len(df)
            df_clean = df.drop_duplicates(subset=['title'], keep='first')
            after = len(df_clean)
            removed = before - after
            
            if removed > 0:
                logger.info(f"Removed {removed} duplicate rows")
                print(f"   Removed {removed} duplicate rows")
            
            return df_clean
        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values di semua kolom"""
        try:
            # Check missing values sebelum cleaning
            missing_before = df.isnull().sum()
            if missing_before.sum() > 0:
                logger.info(f"Missing values before: {missing_before[missing_before > 0].to_dict()}")
            
            # Fill missing values dengan nilai default
            fill_values = {
                'title': 'Unknown Product',
                'price_usd': 0.0,
                'rating': 0.0,
                'colors': 0,
                'size': 'Unknown',
                'gender': 'Unisex',
                'page': 0,
                'scrape_timestamp': datetime.now().isoformat()
            }
            
            for col, default_val in fill_values.items():
                if col in df.columns:
                    df[col] = df[col].fillna(default_val)
            
            # Remove rows dengan title kosong atau "Unknown Product"
            df = df[~df['title'].isna()]
            df = df[df['title'] != 'Unknown Product']
            
            # Remove rows dengan price_usd = 0 atau kosong
            df = df[df['price_usd'] > 0]
            
            missing_after = df.isnull().sum()
            if missing_after.sum() > 0:
                logger.warning(f"Missing values after: {missing_after[missing_after > 0].to_dict()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error handling missing values: {e}")
            return df
    
    def _remove_invalid_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove data invalid sesuai kriteria"""
        try:
            initial = len(df)
            
            # 1. Remove "Unknown Product" (sudah dilakukan di handle_missing_values)
            # 2. Remove rating invalid
            df = df[~df['rating'].astype(str).str.contains('Invalid', case=False, na=False)]
            
            # 3. Remove price invalid atau 0
            df = df[df['price_usd'] > 0]
            
            # 4. Remove jika rating di luar range 0-5
            df['rating_numeric'] = pd.to_numeric(df['rating'], errors='coerce')
            df = df[(df['rating_numeric'] >= 0) & (df['rating_numeric'] <= 5)]
            df = df.drop(columns=['rating_numeric'], errors='ignore')
            
            removed = initial - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} invalid rows")
                print(f"   Removed {removed} invalid rows (Invalid Rating, etc.)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error removing invalid data: {e}")
            return df
    
    def _convert_currency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert USD to IDR dengan rate Rp 16.000"""
        try:
            if 'price_usd' not in df.columns:
                logger.error("price_usd column not found")
                return df
            
            df['price_idr'] = df['price_usd'] * self.exchange_rate
            df['price_idr'] = df['price_idr'].round(2)
            
            logger.info(f"Converted currency: USD -> IDR (rate: Rp {self.exchange_rate:,})")
            print(f"   Converted prices: USD -> IDR (Rp {self.exchange_rate:,})")
            
            # Show sample conversion
            if len(df) > 0:
                sample = df[['title', 'price_usd', 'price_idr']].head(2)
                logger.debug(f"Sample conversion: {sample.to_dict('records')}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return df
    
    def _clean_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean rating column - pastikan float dan antara 0-5"""
        try:
            # Jika rating berupa string seperti "4.5 / 5" atau "Invalid Rating"
            if df['rating'].dtype == 'object':
                # Handle "Invalid Rating"
                df['rating'] = df['rating'].replace(['Invalid Rating', 'Not Rated', 'N/A'], '0.0')
                
                # Extract numeric part dari string seperti "4.5 / 5"
                df['rating'] = df['rating'].astype(str).str.extract(r'(\d+\.?\d*)')[0]
            
            # Convert to numeric
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            
            # Fill NA dan clip ke range 0-5
            df['rating'] = df['rating'].fillna(0.0)
            df['rating'] = df['rating'].clip(0.0, 5.0)
            
            logger.info("Cleaned rating column")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning rating: {e}")
            return df
    
    def _clean_colors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean colors column - extract hanya angka"""
        try:
            if df['colors'].dtype == 'object':
                # Extract numbers from string seperti "3 Colors"
                df['colors'] = df['colors'].astype(str).str.extract(r'(\d+)')[0]
            
            # Convert to numeric
            df['colors'] = pd.to_numeric(df['colors'], errors='coerce')
            
            # Fill NA dengan 0
            df['colors'] = df['colors'].fillna(0).astype(int)
            
            logger.info("Cleaned colors column (numbers only)")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning colors: {e}")
            return df
    
    def _clean_size(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean size column - hapus 'Size: ' prefix"""
        try:
            # Remove 'Size: ' prefix
            df['size'] = df['size'].astype(str).str.replace('Size: ', '', regex=False)
            df['size'] = df['size'].str.replace('SIZE: ', '', case=False, regex=False)
            
            # Strip whitespace
            df['size'] = df['size'].str.strip()
            
            # Standardize size values
            size_mapping = {
                'XS': 'XS', 'S': 'S', 'M': 'M', 'L': 'L', 
                'XL': 'XL', 'XXL': 'XXL', 'XXXL': 'XXXL',
                'Unknown': 'M', '': 'M', 'nan': 'M'
            }
            
            df['size'] = df['size'].map(size_mapping).fillna('M')
            
            logger.info("Cleaned size column (removed 'Size: ' prefix)")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning size: {e}")
            return df
    
    def _clean_gender(self, df: pd.DataFrame) -> pd.DataFrame:
       
        try:
            # Pastikan jadi string dulu
            df['gender'] = df['gender'].astype(str)
            
            # Hapus kata "Gender:" (huruf besar/kecil) dan spasi di sekitarnya
            # Contoh: "Gender: Men " -> "Men"
            df['gender'] = df['gender'].apply(lambda x: re.sub(r'gender:\s*', '', x, flags=re.IGNORECASE).strip())
            
            # Mapping agar sesuai output Reviewer ("Men" tetap "Men", bukan "Male")
            gender_mapping = {
                'Men': 'Men', 'Male': 'Men', 'Man': 'Men', 'M': 'Men',
                'Women': 'Women', 'Female': 'Women', 'Woman': 'Women', 'F': 'Women',
                'Unisex': 'Unisex', 'Both': 'Unisex'
            }
            
            # Map values. Jika tidak dikenali (NaN), ubah jadi 'Unisex'
            df['gender'] = df['gender'].map(gender_mapping).fillna('Unisex')
            
            logger.info("Cleaned gender column (Logic fixed for Men/Women)")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning gender: {e}")
            df['gender'] = 'Unisex' # Fallback
            return df
    
    def _reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
       
        try:

            if 'scrape_timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['scrape_timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            rename_map = {
                'title': 'Title',
                'price_idr': 'Price',
                'rating': 'Rating',
                'colors': 'Colors',
                'size': 'Size',
                'gender': 'Gender',
                'timestamp': 'timestamp' 
            }
            df = df.rename(columns=rename_map)
            
            # --- PENTING: Masukkan 'timestamp' ke dalam target_cols ---
            target_cols = ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'timestamp']
            
            # Ambil kolom yang tersedia
            available_cols = [c for c in target_cols if c in df.columns]
            df = df[available_cols]
            
            logger.info("Reordered columns including timestamp")
            return df
            
        except Exception as e:
            logger.error(f"Error reordering columns: {e}")
            return df
        
    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert data types agar persis dengan gambar (object, float64, int64)
        """
        try:
          
            if 'Title' in df.columns:
                df['Title'] = df['Title'].astype('object')
                
            if 'Price' in df.columns:
                df['Price'] = pd.to_numeric(df['Price'], errors='coerce').astype('float64')
                
            if 'Rating' in df.columns:
                df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').astype('float64')
                
            if 'Colors' in df.columns:
                df['Colors'] = pd.to_numeric(df['Colors'], errors='coerce').fillna(0).astype('int64')
                
            if 'Size' in df.columns:
                df['Size'] = df['Size'].astype('object')
                
            if 'Gender' in df.columns:
                df['gender'] = df['gender'].str.replace(r'Gender:\s*', '', regex=True, case=False)
                df['gender'] = df['gender'].str.strip()

                gender_mapping = {
                'Men': 'Men', 'Male': 'Men', 'Man': 'Men', 'M': 'Men',
                'Women': 'Women', 'Female': 'Women', 'Woman': 'Women', 'F': 'Women',
                'Unisex': 'Unisex', 'Both': 'Unisex', 'All': 'Unisex'
                }
                df['gender'] = df['gender'].map(gender_mapping).fillna('Unisex')

            logger.info("Cleaned gender column (Fixed Men/Women logic)")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning gender: {e}")
            return df
    
    def validate_transformation(self, df: pd.DataFrame) -> bool:
        # Update validasi untuk mengecek nama kolom Capital Case
        required_cols = ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            logger.warning(f"Validation failed. Missing columns: {missing}")
            return False
        
        # Cek dtypes (Text harus object)
        if df['Title'].dtype != 'O': # 'O' stands for Object
             logger.warning("Title column is not Object type")
             
        logger.info("✅ Validation passed")
        return True

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Fungsi utama untuk transformasi data"""
    logger.info("Starting data transformation process")
    
    try:
        transformer = DataTransformer()
        transformed_df = transformer.clean_data(df)
        
        # Validasi hasil transformasi
        if not transformed_df.empty:
            transformer.validate_transformation(transformed_df)
        
        return transformed_df
        
    except Exception as e:
        logger.error(f"Error in transform_data: {e}")
        raise

if __name__ == "__main__":
    # Test the transformer
    print("🧪 Testing DataTransformer...")
    
    # Buat test data sesuai dengan data real dari website
    test_data = pd.DataFrame({
        'title': ['Jacket 42', 'Crewneck 43', 'Unknown Product', 'T-shirt 44'],
        'price_usd': [421.51, 181.85, 100.00, 207.02],
        'rating': ['3.7 / 5', '4.5 / 5', 'Invalid Rating', '3.0 / 5'],
        'colors': ['3 Colors', '3 Colors', '5 Colors', '3 Colors'],
        'size': ['Size: M', 'Size: L', 'Size: M', 'Size: XL'],
        'gender': ['Gender: Men', 'Gender: Men', 'Gender: Men', 'Gender: Women'],
        'page': [1, 1, 1, 1],
        'scrape_timestamp': ['2024-01-28T12:00:00'] * 4
    })
    
    print("\nOriginal test data:")
    print(test_data)
    
    transformed = transform_data(test_data)
    
    print("\nTransformed data:")
    print(transformed)
    
    print("\nData types after transformation:")
    print(transformed.dtypes)