#!/usr/bin/env python3
"""
Simple test script for the Shipping Weather Risk Assessment API
Run this to verify your setup is working correctly.
"""

import asyncio
import sys
from datetime import date, timedelta

try:
    from config import validate_settings, print_settings
    from services.weather_service import WeatherService
    from services.llm_service import LLMService
    from services.port_service import PortService
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and have installed requirements")
    sys.exit(1)


async def test_configuration():
    """Test that configuration is properly set up"""
    print("🔧 Testing Configuration...")
    try:
        settings = validate_settings()
        print("✅ Configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_port_service():
    """Test port lookup functionality"""
    print("\n🌍 Testing Port Service...")
    try:
        port_service = PortService()
        
        # Test port lookup
        la_coords = await port_service.get_port_coordinates("Los Angeles")
        if la_coords:
            print(f"✅ Port lookup works: Los Angeles -> {la_coords['lat']}, {la_coords['lon']}")
        else:
            print("❌ Port lookup failed")
            return False
            
        # Test port search
        search_results = await port_service.search_ports("shanghai", 3)
        if search_results:
            print(f"✅ Port search works: Found {len(search_results)} results for 'shanghai'")
        else:
            print("❌ Port search failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Port service error: {e}")
        return False


async def test_weather_service():
    """Test weather API connectivity"""
    print("\n🌤️  Testing Weather Service...")
    try:
        weather_service = WeatherService()
        
        # Test health check
        health_status = await weather_service.health_check()
        if health_status == "healthy":
            print("✅ Weather API connection is healthy")
        else:
            print(f"❌ Weather API health check failed: {health_status}")
            return False
            
        # Test weather data fetch (Los Angeles coordinates)
        tomorrow = date.today() + timedelta(days=1)
        weather_data = await weather_service.get_weather_data(33.7361, -118.2922, tomorrow)
        if weather_data:
            print(f"✅ Weather data fetch works: {weather_data.condition}, {weather_data.temperature_c}°C")
        else:
            print("❌ Weather data fetch failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Weather service error: {e}")
        return False


async def test_llm_service():
    """Test OpenAI/LLM connectivity"""
    print("\n🤖 Testing LLM Service...")
    try:
        llm_service = LLMService()
        
        # Test health check
        health_status = await llm_service.health_check()
        if health_status == "healthy":
            print("✅ OpenAI API connection is healthy")
            return True
        else:
            print(f"❌ OpenAI API health check failed: {health_status}")
            return False
            
    except Exception as e:
        print(f"❌ LLM service error: {e}")
        return False


async def test_full_integration():
    """Test a complete risk assessment workflow"""
    print("\n🚢 Testing Full Integration...")
    try:
        # Initialize services
        port_service = PortService()
        weather_service = WeatherService()
        llm_service = LLMService()
        
        # Get port coordinates
        la_coords = await port_service.get_port_coordinates("Los Angeles")
        shanghai_coords = await port_service.get_port_coordinates("Shanghai")
        
        if not la_coords or not shanghai_coords:
            print("❌ Could not get port coordinates")
            return False
        
        # Get weather data
        tomorrow = date.today() + timedelta(days=1)
        la_weather = await weather_service.get_weather_data(
            la_coords["lat"], la_coords["lon"], tomorrow
        )
        shanghai_weather = await weather_service.get_weather_data(
            shanghai_coords["lat"], shanghai_coords["lon"], tomorrow
        )
        
        # Estimate travel time
        travel_days = port_service.estimate_travel_time(la_coords, shanghai_coords, "electronics")
        
        # Get AI risk assessment
        risk_assessment = await llm_service.assess_shipping_risk(
            departure_port="Los Angeles",
            destination_port="Shanghai", 
            departure_date=tomorrow,
            carrier_name="Test Carrier",
            goods_type="electronics",
            departure_weather=la_weather,
            destination_weather=shanghai_weather,
            travel_days=travel_days
        )
        
        if risk_assessment and "risk_score" in risk_assessment:
            print(f"✅ Full integration test passed!")
            print(f"   Risk Score: {risk_assessment['risk_score']}/10")
            print(f"   Travel Time: {travel_days} days")
            print(f"   Description: {risk_assessment['risk_description'][:100]}...")
            return True
        else:
            print("❌ Risk assessment failed")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 Shipping Weather Risk Assessment API - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Port Service", test_port_service),
        ("Weather Service", test_weather_service),
        ("LLM Service", test_llm_service),
        ("Full Integration", test_full_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is ready to use.")
        print("🚀 Start the server with: python main.py")
        print("📖 API docs available at: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
        print("💡 Common fixes:")
        print("   - Verify your .env file has correct API keys")
        print("   - Check your internet connection")
        print("   - Ensure you have billing set up for OpenAI")
        print("   - Verify WeatherAPI.com account is active")


if __name__ == "__main__":
    asyncio.run(main())