"""
Module untuk ekstraksi data REAL dari website Fashion Studio Dicoding
Author: ETL Pipeline Project
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging
from typing import List, Dict, Optional
import re
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractor:
    """Kelas untuk REAL scraping dari website Fashion Studio"""
    
    def __init__(self, base_url: str = "https://fashion-studio.dicoding.dev"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        logger.info(f"Initialized DataExtractor for: {base_url}")
    
    def scrape_page(self, page_num: int) -> List[Dict]:
        """
        Scrape data dari satu halaman website
        """
        try:
            # URL untuk halaman tertentu
            if page_num == 1:
                url = self.base_url
            else:
                url = f"{self.base_url}/page{page_num}"
            
            logger.info(f"Scraping halaman {page_num}: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if page exists (404 means no more pages)
            if response.status_code == 404:
                logger.warning(f"Halaman {page_num} tidak ditemukan (404)")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # CARI ELEMEN PRODUK BERDASARKAN STRUKTUR HTML
            # Dari HTML yang dilihat: <div class="collection-card">
            product_elements = soup.find_all('div', class_='collection-card')
            
            if not product_elements:
                # Coba alternatif selector
                product_elements = soup.find_all('div', class_=lambda x: x and 'card' in x)
            
            logger.info(f"Found {len(product_elements)} product elements on page {page_num}")
            
            page_data = []
            for idx, product in enumerate(product_elements):
                try:
                    product_data = self._extract_product_data(product, idx)
                    if product_data:
                        product_data['page'] = page_num
                        product_data['scrape_timestamp'] = datetime.now().isoformat()
                        page_data.append(product_data)
                        
                        if (idx + 1) % 5 == 0:
                            logger.debug(f"  Extracted {idx + 1} products...")
                            
                except Exception as e:
                    logger.debug(f"  Failed to extract product {idx}: {str(e)[:50]}")
                    continue
            
            logger.info(f"Successfully extracted {len(page_data)} products from page {page_num}")
            return page_data
            
        except requests.RequestException as e:
            logger.error(f"HTTP Error scraping page {page_num}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scraping page {page_num}: {e}")
            return []
    
    def _extract_product_data(self, element, idx: int) -> Optional[Dict]:
        """Extract product data dari HTML element"""
        try:
            # 1. Extract TITLE
            title_elem = element.find('h3', class_='product-title')
            title = title_elem.text.strip() if title_elem else "Unknown Product"
            
            # Skip jika Unknown Product
            if title == "Unknown Product":
                return None
            
            # 2. Extract PRICE (USD)
            price_usd = self._extract_price(element)
            
            # 3. Extract RATING
            rating = self._extract_rating(element)
            
            # 4. Extract COLORS
            colors = self._extract_colors(element)
            
            # 5. Extract SIZE
            size = self._extract_size(element)
            
            # 6. Extract GENDER
            gender = self._extract_gender(element)
            
            return {
                'title': title,
                'price_usd': price_usd,
                'rating': rating,
                'colors': colors,
                'size': size,
                'gender': gender,
                'product_index': idx
            }
            
        except Exception as e:
            logger.debug(f"Error extracting product {idx}: {e}")
            return None
    
    def _extract_price(self, element) -> float:
        """Extract price in USD"""
        try:
            # Cari elemen harga
            price_elem = element.find('span', class_='price')
            if not price_elem:
                # Coba cari <p class="price">
                price_elem = element.find('p', class_='price')
            
            if price_elem:
                price_text = price_elem.text.strip()
                # Pattern: $421.51
                match = re.search(r'\$(\d+\.?\d*)', price_text)
                if match:
                    return float(match.group(1))
            
            # Jika tidak ditemukan atau "Price Unavailable"
            return 0.0
            
        except:
            return 0.0
    
    def _extract_rating(self, element) -> float:
        """Extract rating"""
        try:
            # Cari teks yang mengandung "Rating:"
            all_text = element.get_text()
            
            # Pattern: Rating: ⭐ 3.7 / 5
            match = re.search(r'Rating:.*?(\d+\.?\d*)\s*/\s*5', all_text)
            if match:
                return float(match.group(1))
            
            # Pattern alternatif
            match = re.search(r'⭐\s*(\d+\.?\d*)\s*/', all_text)
            if match:
                return float(match.group(1))
            
            # Jika "Invalid Rating" atau "Not Rated"
            if 'Invalid Rating' in all_text or 'Not Rated' in all_text:
                return 0.0
            
            return 0.0  # Default jika tidak ditemukan
            
        except:
            return 0.0
    
    def _extract_colors(self, element) -> int:
        """Extract number of colors"""
        try:
            all_text = element.get_text()
            
            # Pattern: 3 Colors
            match = re.search(r'(\d+)\s*Colors?', all_text)
            if match:
                return int(match.group(1))
            
            return 0
            
        except:
            return 0
    
    def _extract_size(self, element) -> str:
        """Extract size"""
        try:
            all_text = element.get_text()
            
            # Pattern: Size: M
            match = re.search(r'Size:\s*([A-Za-z]+)', all_text)
            if match:
                return match.group(1).strip()
            
            return 'Unknown'
            
        except:
            return 'Unknown'
    
    def _extract_gender(self, element) -> str:
        """Extract gender"""
        try:
            all_text = element.get_text()
            
            # Pattern: Gender: Men
            match = re.search(r'Gender:\s*([A-Za-z]+)', all_text)
            if match:
                gender = match.group(1).strip()
                # Standardize gender values
                if gender.lower() in ['men', 'man', 'male']:
                    return 'Male'
                elif gender.lower() in ['women', 'woman', 'female']:
                    return 'Female'
                elif gender.lower() == 'unisex':
                    return 'Unisex'
                else:
                    return gender
            
            return 'Unisex'
            
        except:
            return 'Unisex'
    
    def scrape_all_pages(self, max_pages: int = 50, max_products: int = 1000) -> pd.DataFrame:
        """Scrape semua halaman"""
        all_data = []
        
        logger.info(f"Starting to scrape {max_pages} pages (max {max_products} products)")
        
        for page_num in range(1, max_pages + 1):
            try:
                page_data = self.scrape_page(page_num)
                all_data.extend(page_data)
                
                logger.info(f"Page {page_num}: {len(page_data)} products (Total: {len(all_data)})")
                
                # Delay untuk menghindari rate limiting
                time.sleep(1)
                
                # Stop jika sudah mencapai batas produk
                if len(all_data) >= max_products:
                    logger.info(f"Reached target of {max_products} products, stopping...")
                    all_data = all_data[:max_products]
                    break
                    
                # Stop jika halaman kosong (tidak ada produk)
                if len(page_data) == 0:
                    logger.warning(f"Page {page_num} returned 0 products, might be last page")
                    break
                    
            except KeyboardInterrupt:
                logger.warning("Scraping interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                continue
        
        # Buat DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            logger.info(f"Total products extracted: {len(df)}")
            return df
        else:
            logger.warning("No data extracted!")
            return pd.DataFrame()
    
    def save_raw_data(self, df: pd.DataFrame, filename: str = "raw_products.csv") -> bool:
        """Save raw data to CSV"""
        try:
            if df.empty:
                logger.warning("DataFrame is empty")
                return False
            
            df.to_csv(filename, index=False)
            logger.info(f"Saved raw data to {filename} ({len(df)} rows)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False

def extract_data(max_pages: int = 50, max_products: int = 1000) -> pd.DataFrame:
    """Main extraction function"""
    logger.info("Starting REAL data extraction from website")
    
    extractor = DataExtractor()
    df = extractor.scrape_all_pages(max_pages=max_pages, max_products=max_products)
    
    if not df.empty:
        extractor.save_raw_data(df, "raw_products.csv")
        logger.info("Extraction completed successfully")
        
        # Tampilkan sample
        print(f"\n✅ Successfully scraped {len(df)} REAL products!")
        print(f"📁 Saved to: raw_products.csv")
        
        if len(df) > 0:
            print("\n📋 Sample of scraped data:")
            print("-" * 80)
            sample = df[['title', 'price_usd', 'rating', 'colors', 'size', 'gender']].head(5)
            print(sample.to_string())
            print("-" * 80)
    else:
        logger.warning("Extraction completed but no data")
        print("\n⚠️ Warning: No data was scraped.")
    
    return df

def test_scraping():
    """Test scraping dengan 1 halaman"""
    print("🧪 Testing REAL scraping...")
    extractor = DataExtractor()
    
    # Test halaman 1
    test_data = extractor.scrape_page(1)
    
    print(f"✅ Got {len(test_data)} products from page 1")
    
    if test_data:
        print("\nSample product data:")
        for key, value in test_data[0].items():
            print(f"  {key}: {value}")
    
    return test_data

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='REAL Data Extraction from Fashion Website')
    parser.add_argument('--test', action='store_true', help='Test scraping (1 page)')
    parser.add_argument('--pages', type=int, default=5, help='Number of pages to scrape')
    parser.add_argument('--max-products', type=int, default=100, help='Max products to collect')
    
    args = parser.parse_args()
    
    if args.test:
        test_scraping()
    else:
        print(f"\n🚀 Starting REAL extraction: {args.pages} pages, max {args.max_products} products")
        print("="*60)
        
        df = extract_data(max_pages=args.pages, max_products=args.max_products)