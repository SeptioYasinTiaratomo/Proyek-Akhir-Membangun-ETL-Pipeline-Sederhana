import sys
import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.extract import extract_data

def test_extract_success():
    """Test happy path (berhasil)"""
    print("\n🧪 Testing extraction success...")
    # Mock data sukses agar tidak request asli
    with patch('requests.get') as mock_get:
        # Siapkan response palsu berisi HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        # HTML dummy sederhana
        mock_response.content = b"""
        <html>
            <div id="product-1" class="product-card">
                <div class="product-title">Test Product</div>
                <div class="product-price">$10.00</div>
                <div class="product-rating">4.5</div>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        data = extract_data(max_pages=1, max_products=5)
        assert not data.empty, "❌ No data extracted"
        assert 'price_usd' in data.columns
    print("✅ Extraction success path covered")

def test_extract_network_error():
    """Test saat terjadi error koneksi (Sad Path)"""
    print("\n🧪 Testing network error handling...")
    
    # PATCH REQUESTS GLOBAL
    with patch('requests.get') as mock_get, \
         patch('requests.Session') as mock_session:
        
        error = Exception("Simulated Network Error")
        mock_get.side_effect = error
        mock_session.return_value.get.side_effect = error
        
        data = extract_data(max_pages=1)
        assert data.empty, "Should return empty DataFrame on error"
    print("✅ Network error path covered")

def test_extract_empty_elements():
    """Test saat website kosong"""
    print("\n🧪 Testing empty page handling...")
    
    with patch('requests.get') as mock_get, \
         patch('requests.Session') as mock_session:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><div>No products</div></body></html>"
        
        mock_get.return_value = mock_response
        mock_session.return_value.get.return_value = mock_response
        
        data = extract_data(max_pages=1)
        assert data.empty
    print("✅ Empty page path covered")