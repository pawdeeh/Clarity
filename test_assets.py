"""
Asset Management Testing Guide and Examples

This file demonstrates how to use the new file upload and asset management features.

Usage:
- Run the Clarity API: python -m uvicorn app.main:app --reload
- Access Swagger docs at: http://localhost:8000/docs
- Or use the examples below with curl, Python requests, or Postman
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

# ============================================================================
# TEST SETUP - Create a test user and get auth token
# ============================================================================

def get_auth_token():
    """Create a test user and return auth token"""
    # Register a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"User creation response: {response.status_code}")
    
    # Login to get token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Successfully got auth token")
        return token
    else:
        print(f"Login failed: {response.text}")
        return None


# ============================================================================
# TEST 1: Single File Upload
# ============================================================================

def test_single_file_upload(token):
    """Test uploading a single file"""
    print("\n" + "="*70)
    print("TEST 1: Single File Upload")
    print("="*70)
    
    # Create a test file
    test_file_path = Path("test_image.txt")
    test_file_path.write_text("This is a test file content")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_image.txt", f, "text/plain")}
        response = requests.post(
            f"{BASE_URL}/assets/upload/",
            files=files,
            headers=headers
        )
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        asset = response.json()
        print(f"✓ File uploaded successfully!")
        print(f"  Asset ID: {asset['id']}")
        print(f"  Original filename: {asset['original_filename']}")
        print(f"  File type: {asset['file_type']}")
        print(f"  File size: {asset['file_size']} bytes")
        print(f"  MIME type: {asset['mime_type']}")
        return asset['id']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None
    finally:
        test_file_path.unlink()


# ============================================================================
# TEST 2: Multiple File Upload
# ============================================================================

def test_multiple_file_upload(token):
    """Test uploading multiple files at once"""
    print("\n" + "="*70)
    print("TEST 2: Multiple File Upload")
    print("="*70)
    
    # Create test files
    test_files = [
        ("test_doc1.txt", "First test document"),
        ("test_doc2.txt", "Second test document"),
        ("test_doc3.txt", "Third test document"),
    ]
    
    file_paths = []
    for filename, content in test_files:
        path = Path(filename)
        path.write_text(content)
        file_paths.append(path)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        files = [("files", open(path, "rb")) for path in file_paths]
        response = requests.post(
            f"{BASE_URL}/assets/upload-multiple/",
            files=files,
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            assets = response.json()
            print(f"✓ Uploaded {len(assets)} files successfully!")
            for asset in assets:
                print(f"  - {asset['original_filename']} (ID: {asset['id']}, Size: {asset['file_size']} bytes)")
            return [a['id'] for a in assets]
        else:
            print(f"✗ Upload failed: {response.text}")
            return []
    finally:
        for f in files:
            f[1].close()
        for path in file_paths:
            path.unlink()


# ============================================================================
# TEST 3: List Assets with Filtering
# ============================================================================

def test_list_assets(token):
    """Test listing and filtering assets"""
    print("\n" + "="*70)
    print("TEST 3: List Assets with Filtering")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # List all assets
    response = requests.get(
        f"{BASE_URL}/assets/",
        headers=headers
    )
    
    if response.status_code == 200:
        assets = response.json()
        print(f"✓ Got {len(assets)} assets")
        for asset in assets:
            print(f"  - {asset['original_filename']} ({asset['file_type']}, {asset['file_size']} bytes)")
    else:
        print(f"✗ Failed to list assets: {response.text}")


# ============================================================================
# TEST 4: Get Asset Details
# ============================================================================

def test_get_asset(token, asset_id):
    """Test getting details of a specific asset"""
    print("\n" + "="*70)
    print("TEST 4: Get Asset Details")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/assets/{asset_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        asset = response.json()
        print(f"✓ Asset details retrieved:")
        print(f"  ID: {asset['id']}")
        print(f"  Original filename: {asset['original_filename']}")
        print(f"  File type: {asset['file_type']}")
        print(f"  File size: {asset['file_size']} bytes")
        print(f"  MIME type: {asset['mime_type']}")
        print(f"  Uploaded by: {asset['uploaded_by']}")
        print(f"  Created at: {asset['created_at']}")
    else:
        print(f"✗ Failed to get asset: {response.text}")


# ============================================================================
# TEST 5: Link Asset to Document
# ============================================================================

def test_link_asset_to_document(token, asset_id):
    """Test linking an asset to a document"""
    print("\n" + "="*70)
    print("TEST 5: Link Asset to Document")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, create a document
    doc_data = {
        "title": "Test Document with Assets",
        "content": "This document has assets",
        "slug": "test-doc-with-assets"
    }
    
    doc_response = requests.post(
        f"{BASE_URL}/documents/",
        json=doc_data,
        headers=headers
    )
    
    if doc_response.status_code != 200:
        print(f"✗ Failed to create document: {doc_response.text}")
        return
    
    document_id = doc_response.json()["id"]
    print(f"✓ Created test document (ID: {document_id})")
    
    # Link asset to document
    response = requests.post(
        f"{BASE_URL}/assets/{asset_id}/link-to-document/{document_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ Asset {asset_id} linked to document {document_id}")
        print(f"  Response: {response.json()}")
    else:
        print(f"✗ Failed to link asset: {response.text}")


# ============================================================================
# TEST 6: Asset Statistics
# ============================================================================

def test_asset_stats(token):
    """Test getting asset statistics"""
    print("\n" + "="*70)
    print("TEST 6: Asset Statistics")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/assets/stats/",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Asset statistics:")
        print(f"  Total assets: {stats['total_assets']}")
        print(f"  Total storage: {stats['total_storage_mb']} MB ({stats['total_storage_bytes']} bytes)")
        print(f"  Assets by type:")
        for file_type, count in stats['assets_by_type'].items():
            print(f"    - {file_type}: {count}")
    else:
        print(f"✗ Failed to get stats: {response.text}")


# ============================================================================
# TEST 7: Download Asset
# ============================================================================

def test_download_asset(token, asset_id):
    """Test downloading an asset"""
    print("\n" + "="*70)
    print("TEST 7: Download Asset")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/assets/{asset_id}/download",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ Asset downloaded successfully!")
        print(f"  Size: {len(response.content)} bytes")
        print(f"  Content-Type: {response.headers.get('content-type')}")
    else:
        print(f"✗ Failed to download asset: {response.text}")


# ============================================================================
# TEST 8: Delete Asset
# ============================================================================

def test_delete_asset(token, asset_id):
    """Test deleting an asset"""
    print("\n" + "="*70)
    print("TEST 8: Delete Asset")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{BASE_URL}/assets/{asset_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ Asset deleted successfully!")
        print(f"  Response: {response.json()}")
    else:
        print(f"✗ Failed to delete asset: {response.text}")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*70)
    print("CLARITY FILE UPLOAD & ASSET MANAGEMENT TEST SUITE")
    print("="*70)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token. Exiting.")
        return
    
    # Run tests
    asset_id = test_single_file_upload(token)
    if asset_id:
        test_get_asset(token, asset_id)
        test_link_asset_to_document(token, asset_id)
        test_download_asset(token, asset_id)
        test_delete_asset(token, asset_id)
    
    multiple_ids = test_multiple_file_upload(token)
    
    test_list_assets(token)
    test_asset_stats(token)
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
