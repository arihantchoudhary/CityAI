#!/usr/bin/env python3
"""
Simple script to test the Shipping Risk API
Just run: python simple_test.py
"""

import requests
import json
from datetime import date, timedelta

# API endpoint
# BASE_URL = "http://localhost:8000"
BASE_URL = "https://shipping-risk-api.onrender.com"

def test_health():
    """Test if the API is running"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
        return False

def test_port_search():
    """Test port search functionality"""
    print("\n🌍 Testing port search...")
    try:
        response = requests.get(f"{BASE_URL}/ports/search?query=shanghai&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['ports'])} ports matching 'shanghai'")
            for port in data['ports']:
                print(f"   - {port['name']}, {port['country']}")
            return True
        else:
            print(f"❌ Port search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Port search error: {e}")
        return False

def test_risk_assessment():
    """Test the main risk assessment endpoint"""
    print("\n🚢 Testing risk assessment...")
    
    # Calculate tomorrow's date
    tomorrow = date.today() + timedelta(days=1)
    
    # Test data
    test_data = {
        "departure_port": "Los Angeles",
        "destination_port": "Shanghai", 
        "departure_date": tomorrow.strftime("%Y-%m-%d"),
        "carrier_name": "COSCO Shipping",
        "goods_type": "electronics"
    }
    
    print(f"📋 Testing with data:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/assess-shipping-risk",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=120  # Give it 2 minutes for AI processing
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Risk assessment successful!")
            print(f"   🎯 Risk Score: {data['risk_score']}/10")
            print(f"   📅 Travel Days: {data['estimated_travel_days']}")
            print(f"   🌤️  Departure Weather: {data['departure_weather']['condition']}")
            print(f"   🌧️  Destination Weather: {data['destination_weather']['condition']}")
            print(f"   📝 Risk Description: {data['risk_description'][:100]}...")
            print(f"   ☁️  Weather Summary: {data['weather_summary'][:100]}...")
            return True
        else:
            print(f"❌ Risk assessment failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (this can happen if OpenAI is slow)")
        return False
    except Exception as e:
        print(f"❌ Risk assessment error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Simple API Test Script")
    print("=" * 50)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_health():
        tests_passed += 1
    
    if test_port_search():
        tests_passed += 1
        
    if test_risk_assessment():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your API is working perfectly!")
    elif tests_passed > 0:
        print("⚠️  Some tests passed. Check any errors above.")
    else:
        print("❌ All tests failed. Check your setup:")
        print("   1. Is the API running? (python main.py)")
        print("   2. Are your API keys set in .env?")
        print("   3. Do you have internet connection?")

if __name__ == "__main__":
    main()