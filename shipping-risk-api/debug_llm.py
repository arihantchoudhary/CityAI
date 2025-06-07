#!/usr/bin/env python3
"""
Debug script to test OpenAI integration specifically
Run this to see exactly what's happening with the LLM calls
"""

import asyncio
import sys
from datetime import date, timedelta

try:
    from config import get_settings
    from services.llm_service import LLMService
    from services.weather_service import WeatherService
    from services.port_service import PortService
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_openai_simple():
    """Test a simple OpenAI call"""
    print("🔍 Testing simple OpenAI call...")
    
    try:
        llm_service = LLMService()
        
        # Simple test call
        response = await llm_service.client.chat.completions.create(
            model=llm_service.model,
            messages=[{"role": "user", "content": "Say 'Hello world' in JSON format: {\"message\": \"Hello world\"}"}],
            max_tokens=50,
            timeout=30
        )
        
        content = response.choices[0].message.content
        print(f"✅ Simple OpenAI call successful!")
        print(f"   Model: {llm_service.model}")
        print(f"   Response: {content}")
        return True
        
    except Exception as e:
        print(f"❌ Simple OpenAI call failed: {e}")
        return False

async def test_risk_assessment_step_by_step():
    """Test the full risk assessment with detailed debugging"""
    print("\n🚢 Testing risk assessment step by step...")
    
    try:
        # Initialize services
        llm_service = LLMService()
        weather_service = WeatherService()
        port_service = PortService()
        
        print("📍 Step 1: Getting port coordinates...")
        la_coords = await port_service.get_port_coordinates("Los Angeles")
        shanghai_coords = await port_service.get_port_coordinates("Shanghai")
        print(f"   LA: {la_coords}")
        print(f"   Shanghai: {shanghai_coords}")
        
        print("🌤️  Step 2: Getting weather data...")
        tomorrow = date.today() + timedelta(days=1)
        la_weather = await weather_service.get_weather_data(
            la_coords["lat"], la_coords["lon"], tomorrow
        )
        shanghai_weather = await weather_service.get_weather_data(
            shanghai_coords["lat"], shanghai_coords["lon"], tomorrow
        )
        print(f"   LA weather: {la_weather.condition}, {la_weather.temperature_c}°C")
        print(f"   Shanghai weather: {shanghai_weather.condition}, {shanghai_weather.temperature_c}°C")
        
        print("🤖 Step 3: Testing LLM risk assessment...")
        
        # Call the LLM service directly with debug info
        result = await llm_service.assess_shipping_risk(
            departure_port="Los Angeles",
            destination_port="Shanghai",
            departure_date=tomorrow,
            carrier_name="Test Carrier",
            goods_type="electronics",
            departure_weather=la_weather,
            destination_weather=shanghai_weather,
            travel_days=14
        )
        
        print(f"✅ LLM assessment completed!")
        print(f"   Risk Score: {result['risk_score']}/10")
        print(f"   Description preview: {result['risk_description'][:100]}...")
        
        # Check if it's a fallback
        if "[Fallback Assessment]" in result['risk_description'] or "[OpenAI API Error:" in result['risk_description']:
            print("⚠️  WARNING: This is a fallback assessment, not from OpenAI")
            print(f"   Full description: {result['risk_description']}")
            return False
        else:
            print("✅ This is a real OpenAI assessment!")
            return True
            
    except Exception as e:
        print(f"❌ Risk assessment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main debug function"""
    print("🔧 LLM Integration Debug Script")
    print("=" * 50)
    
    # Check configuration
    try:
        settings = get_settings()
        print(f"📋 Configuration:")
        print(f"   OpenAI Model: {settings.openai_model}")
        print(f"   OpenAI Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
        print(f"   Weather Key: {'✅ Set' if settings.weatherapi_key else '❌ Missing'}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Run tests
    simple_test = await test_openai_simple()
    full_test = await test_risk_assessment_step_by_step()
    
    print("\n" + "=" * 50)
    print("📊 Debug Results:")
    print(f"   Simple OpenAI call: {'✅ PASS' if simple_test else '❌ FAIL'}")
    print(f"   Full risk assessment: {'✅ PASS' if full_test else '❌ FAIL'}")
    
    if simple_test and not full_test:
        print("\n💡 Analysis: OpenAI works but something fails in the risk assessment")
        print("   Likely causes:")
        print("   1. AI response format issues (not valid JSON)")
        print("   2. Prompt too long or complex")
        print("   3. Timeout during processing")
        print("   4. Response validation failing")
        print("\n   Check the detailed logs above for the exact error!")
    elif not simple_test:
        print("\n💡 Analysis: Basic OpenAI connection failing")
        print("   Check your API key and billing setup")

if __name__ == "__main__":
    asyncio.run(main())