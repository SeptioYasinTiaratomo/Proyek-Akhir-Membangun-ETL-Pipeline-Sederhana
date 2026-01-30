import sys
import io
import logging
import os
from datetime import datetime

# Setup encoding untuk Windows agar tidak error emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'etl_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import modul ETL
try:
    from utils.extract import extract_data
    from utils.transform import transform_data
    from utils.load import load_data
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)

def run_etl_pipeline():
  
    print("\n" + "✨" * 60)
    print("              FASHION STUDIO ETL PIPELINE")
    print("✨" * 60)
    
    try:
        # ===== 1. EKSTRAKSI =====
        print("\n" + "=" * 60)
        print("📥 STEP 1: DATA EXTRACTION")
        print("=" * 60)
        
        # Panggil fungsi extract
        raw_data = extract_data(max_pages=50, max_products=1000)
        
        if raw_data.empty:
            logger.error("Extraction failed or returned empty data")
            return False
            
        # ===== 2. TRANSFORMASI =====
        print("\n" + "=" * 60)
        print("🔄 STEP 2: DATA TRANSFORMATION")
        print("=" * 60)
        
        # Panggil fungsi transform
        clean_data = transform_data(raw_data)
        
        if clean_data.empty:
            logger.error("Transformation failed or returned empty data")
            return False
            
        # ===== 3. LOADING =====
        print("\n" + "=" * 60)
        print("💾 STEP 3: DATA LOADING")
        print("=" * 60)
        
        # Setup Google Sheets ID
        google_sheets_id = os.getenv('SPREADSHEET_ID')
        # Fallback ID jika environment variable tidak ada
        if not google_sheets_id:
            google_sheets_id = "1TTBCPo8qikB2vx14S3xitJOm6UycqcMnc4ZsyaNr2GQ"
            
        # Panggil fungsi load
        # Fungsi ini yang BERTANGGUNG JAWAB menyimpan ke CSV dan Google Sheets
        load_results = load_data(
            clean_data,
            repositories=['csv', 'google_sheets'],
            google_sheets_id=google_sheets_id
        )
        
        # Cek hasil loading
        print("\n" + "=" * 60)
        print("📊 LOADING RESULTS")
        print("=" * 60)
        
        success_count = sum(load_results.values())
        if load_results.get('csv'):
            print("✅ CSV Storage: SUCCESS")
        else:
            print("❌ CSV Storage: FAILED")
            
        if load_results.get('google_sheets'):
            print("✅ Google Sheets: SUCCESS")
        else:
            print("⚠️  Google Sheets: FAILED/SKIPPED")
            
        # Final Summary
        print("\n" + "=" * 60)
        if success_count > 0:
            print("🎉 ETL PIPELINE COMPLETED SUCCESSFULLY")
            return True
        else:
            print("❌ ETL PIPELINE FAILED TO SAVE DATA")
            return False
            
    except Exception as e:
        logger.error(f"ETL Pipeline Error: {e}", exc_info=True)
        print(f"\n❌ Pipeline crashed: {e}")
        return False

if __name__ == "__main__":
    run_etl_pipeline()