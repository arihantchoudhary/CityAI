#!/usr/bin/env python3
"""
Compare direct LLM call vs API endpoint call to find the difference
"""

import asyncio
import requests
from datetime import date, timedelta

# Direct imports for testing LLM service
from services.llm_service import LLMService
from services.weather_service import WeatherService
from services.port_service import PortService

async def test_direct_vs_api():
    """Test the same assessment both directly and via API"""
    
    print("🔍 Comparing Direct LLM Call vs API Endpoint")
    print("=" * 60)
    
    # Test data
    tomorrow = date.today() + timedelta(days=1)
    test_data = {
        "departure_port": "Los Angeles",
        "destination_port": "Shanghai",
        "departure_date": tomorrow.strftime("%Y-%m-%d"),
        "carrier_name": "COSCO Shipping",
        "goods_type": "electronics"
    }
    
    # =================================
    # DIRECT CALL TEST
    # =================================
    print("🤖 Testing DIRECT LLM service call...")
    try:
        # Initialize services
        llm_service = LLMService()
        weather_service = WeatherService()
        port_service = PortService()
        
        # Get data (same as API would do)
        la_coords = await port_service.get_port_coordinates("Los Angeles")
        shanghai_coords = await port_service.get_port_coordinates("Shanghai")
        
        la_weather = await weather_service.get_weather_data(
            la_coords["lat"], la_coords["lon"], tomorrow
        )
        shanghai_weather = await weather_service.get_weather_data(
            shanghai_coords["lat"], shanghai_coords["lon"], tomorrow
        )
        
        travel_days = port_service.estimate_travel_time(la_coords, shanghai_coords, "electronics")
        
        # Direct LLM call
        direct_result = await llm_service.assess_shipping_risk(
            departure_port="Los Angeles",
            destination_port="Shanghai",
            departure_date=tomorrow,
            carrier_name="COSCO Shipping",
            goods_type="electronics",
            departure_weather=la_weather,
            destination_weather=shanghai_weather,
            travel_days=travel_days
        )
        
        print(f"✅ DIRECT CALL successful!")
        print(f"   Risk Score: {direct_result['risk_score']}/10")
        print(f"   Is Fallback: {'[Fallback Assessment]' in direct_result['risk_description']}")
        print(f"   Is OpenAI Error: {'[OpenAI API Error:' in direct_result['risk_description']}")
        print(f"   Description preview: {direct_result['risk_description'][:100]}...")
        
    except Exception as e:
        print(f"❌ DIRECT CALL failed: {e}")
        direct_result = None
    
    # =================================
    # API ENDPOINT TEST
    # =================================
    print(f"\n🌐 Testing API ENDPOINT call...")
    try:
        response = requests.post(
            "http://localhost:8000/assess-shipping-risk",
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            api_result = response.json()
            
            print(f"✅ API CALL successful!")
            print(f"   Risk Score: {api_result['risk_score']}/10")
            print(f"   Is Fallback: {'[Fallback Assessment]' in api_result['risk_description']}")
            print(f"   Is OpenAI Error: {'[OpenAI API Error:' in api_result['risk_description']}")
            print(f"   Is API Error: {'[API Endpoint Error]' in api_result['risk_description']}")
            print(f"   Description preview: {api_result['risk_description'][:100]}...")
            
        else:
            print(f"❌ API CALL failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            api_result = None
            
    except Exception as e:
        print(f"❌ API CALL failed: {e}")
        api_result = None
    
    # =================================
    # COMPARISON
    # =================================
    print(f"\n" + "=" * 60)
    print("📊 COMPARISON RESULTS:")
    
    if direct_result and api_result:
        direct_is_real = not ('[Fallback Assessment]' in direct_result['risk_description'] or 
                             '[OpenAI API Error:' in direct_result['risk_description'])
        api_is_real = not ('[Fallback Assessment]' in api_result['risk_description'] or 
                          '[OpenAI API Error:' in api_result['risk_description'] or
                          '[API Endpoint Error]' in api_result['risk_description'])
        
        print(f"   Direct call uses real OpenAI: {'✅ YES' if direct_is_real else '❌ NO'}")
        print(f"   API call uses real OpenAI: {'✅ YES' if api_is_real else '❌ NO'}")
        print(f"   Risk scores match: {'✅ YES' if abs(direct_result['risk_score'] - api_result['risk_score']) <= 1 else '❌ NO'}")
        
        if direct_is_real and not api_is_real:
            print(f"\n💡 DIAGNOSIS: Direct call works, but API endpoint fails!")
            print(f"   This means there's an issue in the FastAPI endpoint code.")
            print(f"   Check the server logs for detailed error messages.")
            print(f"   The API endpoint might be catching an exception that the direct call doesn't encounter.")
            
        elif not direct_is_real and not api_is_real:
            print(f"\n💡 DIAGNOSIS: Both calls are failing!")
            print(f"   The issue is in the LLM service itself.")
            
        elif direct_is_real and api_is_real:
            print(f"\n💡 DIAGNOSIS: Both calls work perfectly!")
            print(f"   The issue might have been resolved, or there's intermittent failure.")
    
    else:
        print("❌ Cannot compare - one or both calls failed completely")

if __name__ == "__main__":
    print("🚀 Make sure your API server is running: python main.py")
    print("   Then this script will compare direct vs API calls\n")
    asyncio.run(test_direct_vs_api())