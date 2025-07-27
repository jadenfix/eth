#!/usr/bin/env python3

import asyncio
import sys
import os
import requests
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_predictive_api():
    """Test the predictive analytics API endpoint"""
    try:
        print("Testing predictive analytics API...")
        
        # Test the endpoint
        url = "http://localhost:5000/analytics/predictive"
        headers = {"Content-Type": "application/json"}
        data = {"horizon": "24h"}
        
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Predictive analytics API test passed")
            return True
        else:
            print(f"❌ Predictive analytics API test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing predictive analytics API: {e}")
        return False

if __name__ == "__main__":
    test_predictive_api() 