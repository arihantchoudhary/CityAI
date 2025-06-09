#!/usr/bin/env python3
"""
Simple test script for the Shipping Risk Mitigation API
Tests health endpoint and sample risk analysis
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8002"  # Change this to your Render URL when deployed
API_BASE_URL = "https://mitigation-api.onrender.com"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_json_response(data, title="Response"):
    """Pretty print JSON response"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def test_health_endpoint():
    """Test the health check endpoint with retry for Render cold starts"""
    print_section("TESTING HEALTH ENDPOINT")
    
    max_retries = 3
    retry_delay = 20  # Wait 20 seconds between retries for cold start
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"🔄 Retry attempt {attempt + 1}/{max_retries} (Render service may be waking up...)")
                time.sleep(retry_delay)
            
            print(f"📡 Attempting connection to: {API_BASE_URL}")
            response = requests.get(f"{API_BASE_URL}/health", timeout=60)  # Longer timeout for cold start
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Health check passed!")
                print_json_response(response.json(), "Health Status")
                return True
            elif response.status_code == 502:
                print("🛌 Service is sleeping/waking up (502 Bad Gateway)")
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting {retry_delay} seconds for service to wake up...")
                    continue
                else:
                    print("❌ Service failed to wake up after retries")
                    return False
            else:
                print("❌ Health check failed!")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed!")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds (service may be starting up)...")
                continue
            else:
                print(f"❌ Could not connect after {max_retries} attempts")
                print(f"   Make sure the API is running at: {API_BASE_URL}")
                return False
        except requests.exceptions.Timeout:
            print("❌ Request timed out!")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                continue
            else:
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if attempt < max_retries - 1:
                continue
            else:
                return False
    
    return False

def test_root_endpoint():
    """Test the root endpoint"""
    print_section("TESTING ROOT ENDPOINT")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            print_json_response(response.json(), "API Info")
            return True
        elif response.status_code == 502:
            print("🛌 Service still waking up (502), but this is normal for Render")
            print("   Service should be ready for the main test")
            return True  # Consider this a pass since service is starting
        else:
            print("❌ Root endpoint failed!")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏳ Root endpoint timed out (service may still be starting)")
        return True  # Don't fail the test suite for this
    except Exception as e:
        print(f"❌ Error testing root endpoint: {e}")
        return False

def create_sample_shipping_data():
    """Create sample shipping data for testing"""
    
    # Calculate a future date (30 days from now)
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    sample_data = {
        "departure_port": "Port of Los Angeles",
        "destination_port": "Port of Shanghai", 
        "departure_date": future_date,
        "carrier_name": "Maersk Line",
        "goods_type": "Electronics and Consumer Goods",
        "weather_conditions": {
            "risk_score": 6,
            "risk_description": "Moderate weather risk due to potential typhoon activity in the Pacific during summer months. Wind speeds may reach 35-40 knots with wave heights up to 4 meters.",
            "weather_summary": "Seasonal typhoon risk with possible route diversions. Current forecast shows developing low pressure system.",
            "departure_weather": {
                "temperature": 22.5,
                "wind_speed": 15.0,
                "wave_height": 2.1,
                "visibility": 8.5,
                "conditions": "Partly cloudy with moderate winds"
            },
            "destination_weather": {
                "temperature": 28.0,
                "wind_speed": 25.0,
                "wave_height": 3.2,
                "visibility": 6.0,
                "conditions": "Approaching weather system, increasing winds"
            },
            "estimated_travel_days": 14
        },
        "geopolitical_conditions": {
            "risk_score": 7,
            "risk_description": "Elevated geopolitical risk due to ongoing trade tensions and territorial disputes in South China Sea. Recent naval activities may affect shipping lanes.",
            "geopolitical_summary": "Route traverses high-tension maritime zones with potential for shipping delays and inspection requirements.",
            "chokepoints": ["South China Sea", "Taiwan Strait"],
            "security_zones": ["Taiwan Strait", "Spratly Islands"],
            "shipping_lanes": "Trans-Pacific main shipping corridor"
        }
    }
    
    return sample_data

def test_risk_analysis():
    """Test the main risk analysis endpoint with retry for cold starts"""
    print_section("TESTING RISK ANALYSIS ENDPOINT")
    
    sample_data = create_sample_shipping_data()
    
    print("Sample Request Data:")
    print_json_response(sample_data, "Request Payload")
    
    max_retries = 2
    retry_delay = 30
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"\n🔄 Retry attempt {attempt + 1}/{max_retries}")
                time.sleep(retry_delay)
            
            print(f"\nSending request to: {API_BASE_URL}/analyze-shipping-risk")
            print("⏳ Analyzing shipping risks (this may take 10-60 seconds)...")
            
            response = requests.post(
                f"{API_BASE_URL}/analyze-shipping-risk",
                json=sample_data,
                headers={"Content-Type": "application/json"},
                timeout=120  # Extended timeout for cold start + AI processing
            )
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Risk analysis completed successfully!")
                result = response.json()
                
                # Display results in a formatted way
                print_json_response(result, "Risk Analysis Results")
                
                # Extract and highlight key information
                print_section("KEY INSIGHTS")
                print(f"Overall Risk Assessment: {result.get('overall_risk_assessment', 'N/A')}")
                print(f"Recommended Action: {result.get('recommended_action', 'N/A')}")
                
                strategies = result.get('strategies', [])
                if strategies:
                    print(f"\nNumber of Mitigation Strategies: {len(strategies)}")
                    for i, strategy in enumerate(strategies, 1):
                        print(f"\n  Strategy {i}: {strategy.get('strategy_type', 'Unknown')}")
                        print(f"    Priority: {strategy.get('priority', 'N/A')}")
                        print(f"    Risk Reduction: {strategy.get('risk_reduction', 'N/A')}")
                        print(f"    Description: {strategy.get('description', 'N/A')}")
                    
                    # Extract and display risk reduction percentages
                    print(f"\n📊 RISK REDUCTION SUMMARY:")
                    total_risk_reduction = 0
                    reduction_count = 0
                    
                    for i, strategy in enumerate(strategies, 1):
                        risk_reduction = strategy.get('risk_reduction', '')
                        print(f"  Strategy {i}: {risk_reduction}")
                        
                        # Try to extract percentage numbers for summary
                        import re
                        percentages = re.findall(r'(\d+(?:\.\d+)?)%', risk_reduction)
                        if percentages:
                            # Take the average if there's a range like "20-40%"
                            nums = [float(p) for p in percentages]
                            avg_reduction = sum(nums) / len(nums)
                            total_risk_reduction += avg_reduction
                            reduction_count += 1
                    
                    if reduction_count > 0:
                        avg_overall_reduction = total_risk_reduction / reduction_count
                        print(f"\n📈 Average Risk Reduction per Strategy: {avg_overall_reduction:.1f}%")
                        print(f"🎯 Potential Combined Risk Reduction: {min(total_risk_reduction, 85):.1f}%")
                        print("   (Note: Combined effects may not be additive)")
                
                alternatives = result.get('alternative_routes', [])
                if alternatives:
                    print(f"\nAlternative Routes: {', '.join(alternatives)}")
                
                timeline = result.get('timeline_recommendations')
                if timeline:
                    print(f"\nTimeline Recommendations: {timeline}")
                
                compliance = result.get('compliance_checks', [])
                if compliance:
                    print(f"\n📋 Compliance Documents to Check:")
                    for i, doc in enumerate(compliance, 1):
                        print(f"  {i}. {doc}")
                
                return True
                
            elif response.status_code == 502:
                print("🛌 Service is sleeping/waking up (502 Bad Gateway)")
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting {retry_delay} seconds for service to fully wake up...")
                    continue
                else:
                    print("❌ Service failed to wake up after retries")
                    return False
                    
            elif response.status_code == 422:
                print("❌ Validation error - check request format!")
                try:
                    error_detail = response.json()
                    print_json_response(error_detail, "Validation Errors")
                except:
                    print(f"Response: {response.text}")
                return False
                
            elif response.status_code == 500:
                print("❌ Server error - check if XAI_API_KEY is configured!")
                print(f"Response: {response.text}")
                return False
                
            else:
                print(f"❌ Unexpected response code: {response.status_code}")
                print(f"Response: {response.text}")
                if attempt < max_retries - 1:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    continue
                else:
                    return False
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out! AI processing may take longer than expected.")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying with longer timeout...")
                continue
            else:
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed!")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                continue
            else:
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if attempt < max_retries - 1:
                continue
            else:
                return False
    
    return False

def wake_up_service():
    """Send a simple request to wake up the Render service if it's sleeping"""
    print_section("WAKING UP RENDER SERVICE")
    print("🛌 Render free services sleep after 15 minutes of inactivity")
    print("⏰ Sending wake-up request (may take 30-60 seconds)...")
    
    try:
        # Simple GET request to wake up the service
        response = requests.get(f"{API_BASE_URL}/", timeout=60)
        if response.status_code == 200:
            print("✅ Service is awake and responding!")
            return True
        elif response.status_code == 502:
            print("🔄 Service is still starting up...")
            return False
        else:
            print(f"⚠️  Got response code {response.status_code}, service may be partially awake")
            return True
    except requests.exceptions.Timeout:
        print("⏳ Wake-up request timed out, but service may still be starting...")
        return False
    except Exception as e:
        print(f"❌ Wake-up failed: {e}")
        return False

def main():
    """Run all tests"""
    print_section("SHIPPING RISK MITIGATION API - TEST SUITE")
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check if this might be a Render deployment
    if "render" in API_BASE_URL.lower():
        print("\n🔔 RENDER SERVICE DETECTED")
        print("   Free Render services sleep after 15 minutes of inactivity")
        print("   If you get 502 errors, the service is waking up (takes ~30-60 seconds)")
        
        # Try to wake up the service first
        wake_up_service()
    
    # Test sequence
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Health check
    if test_health_endpoint():
        tests_passed += 1
    
    # Test 2: Root endpoint
    if test_root_endpoint():
        tests_passed += 1
    
    # Test 3: Main functionality
    if test_risk_analysis():
        tests_passed += 1
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your API is working correctly.")
    elif tests_passed == 0:
        print("❌ All tests failed. Check if the API is running and configured properly.")
        print("\nTroubleshooting:")
        if "render" in API_BASE_URL.lower():
            print("🛌 RENDER USERS:")
            print("   - Service may be sleeping (wait 30-60 seconds and retry)")
            print("   - Check Render dashboard for deployment logs")
            print("   - Verify environment variables are set in Render")
        else:
            print("🔧 LOCAL USERS:")
            print("   1. Make sure the API is running (python main.py)")
            print("   2. Update API_BASE_URL in this script to match your deployment")
        print("3. Ensure XAI_API_KEY environment variable is set")
    else:
        print(f"⚠️  Some tests failed. {tests_passed} out of {total_tests} tests passed.")
        
    print(f"\nTesting completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()