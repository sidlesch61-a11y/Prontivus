#!/usr/bin/env python3
"""
Test script for ICD-10 API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_icd10_api():
    """Test ICD-10 API endpoints"""
    print("🔍 Testing ICD-10 API endpoints...")
    
    # Test 1: Search for diabetes
    print("\n1. Testing search for 'diabetes':")
    try:
        response = requests.get(f"{BASE_URL}/api/icd10/search?query=diabetes")
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"   {i+1}. {result['code']} - {result['description']} ({result['level']})")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running. Start with: python main.py")
        return
    
    # Test 2: Search for cancer
    print("\n2. Testing search for 'cancer':")
    try:
        response = requests.get(f"{BASE_URL}/api/icd10/search?query=cancer")
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results[:3]):
                print(f"   {i+1}. {result['code']} - {result['description']} ({result['level']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get specific code
    print("\n3. Testing specific code lookup (E10 - Type 1 diabetes):")
    try:
        response = requests.get(f"{BASE_URL}/api/icd10/code/E10")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Found: {result['code']} - {result['description']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Search for mental health
    print("\n4. Testing search for 'mental health':")
    try:
        response = requests.get(f"{BASE_URL}/api/icd10/search?query=mental")
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results[:3]):
                print(f"   {i+1}. {result['code']} - {result['description']} ({result['level']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_icd10_api()
