#!/usr/bin/env python3
"""
Simple test script for Geopolitical Risk Assessment API
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys


def test_api_endpoint(api_url="http://localhost:8001"):
    """Test the main geopolitical risk assessment endpoint"""
    
    print("🚀 Testing Geopolitical Risk Assessment API")
    print(f"📍 API URL: {api_url}")
    print("=" * 60)
    
    # Test data - same as the curl command
    test_data = {
        "departure_port": "Los Angeles",
        "destination_port": "Shanghai",
        "departure_date": "2025-06-15",
        "carrier_name": "COSCO",
        "goods_type": "electronics"
    }
    
    print(f"📤 Sending request to: {api_url}/assess-geopolitical-risk")
    print(f"📦 Request data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        # Make the API request
        response = requests.post(
            f"{api_url}/assess-geopolitical-risk",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minute timeout
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! API is working")
            
            # Parse response
            result = response.json()
            
            # Print key results
            print("\n📊 RISK ASSESSMENT RESULTS:")
            print("-" * 40)
            print(f"🎯 Risk Score: {result['risk_score']}/10")
            print(f"📈 Risk Level: {get_risk_level(result['risk_score'])}")
            print(f"🚢 Travel Days: {result['travel_days']}")
            print(f"📅 Assessment Time: {result['assessment_timestamp']}")
            
            # Print risk description
            print(f"\n📝 Risk Description:")
            print(f"{result['risk_description'][:300]}...")
            
            # Print geopolitical summary
            print(f"\n🌍 Geopolitical Summary:")
            print(f"{result['geopolitical_summary']}")
            
            # Print country risks
            print(f"\n🏛️ Country Risk Profiles:")
            dep_country = result['departure_country_risk']
            dest_country = result['destination_country_risk']
            
            print(f"   Departure ({dep_country['country']}):")
            print(f"   • Political Stability: {dep_country['political_stability']}/10")
            print(f"   • Trade Freedom: {dep_country['trade_freedom']}/100")
            print(f"   • Sanctions Status: {dep_country['sanctions_status']}")
            
            print(f"   Destination ({dest_country['country']}):")
            print(f"   • Political Stability: {dest_country['political_stability']}/10")
            print(f"   • Trade Freedom: {dest_country['trade_freedom']}/100")
            print(f"   • Sanctions Status: {dest_country['sanctions_status']}")
            
            # Print route analysis
            route = result['route_analysis']
            print(f"\n🛣️ Route Analysis:")
            print(f"   • Distance: {route['distance_km']} km")
            print(f"   • Chokepoints: {', '.join(route['chokepoints']) if route['chokepoints'] else 'None'}")
            print(f"   • Security Zones: {', '.join(route['security_zones']) if route['security_zones'] else 'None'}")
            
            # Print recent events
            events = result['recent_events']
            print(f"\n📰 Recent Events: {len(events)} events monitored")
            if events:
                print("   Top events:")
                for i, event in enumerate(events[:3], 1):
                    print(f"   {i}. {event['title'][:60]}...")
                    print(f"      Relevance: {event['relevance_score']}/10")
            
            # Risk assessment
            if result['risk_score'] >= 7:
                print(f"\n⚠️  HIGH RISK ROUTE")
                print("   Recommendation: Enhanced security measures required")
            elif result['risk_score'] >= 5:
                print(f"\n🟡 MEDIUM RISK ROUTE")
                print("   Recommendation: Standard precautions with monitoring")
            else:
                print(f"\n✅ LOW RISK ROUTE")
                print("   Recommendation: Standard shipping protocols")
            
            return True
            
        elif response.status_code == 400:
            print("❌ BAD REQUEST - Invalid input data")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw error: {response.text}")
            return False
            
        elif response.status_code == 429:
            print("❌ RATE LIMITED - Too many requests")
            print("   Wait a moment and try again")
            return False
            
        elif response.status_code == 500:
            print("❌ SERVER ERROR - API internal error")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw error: {response.text}")
            return False
            
        else:
            print(f"❌ UNEXPECTED RESPONSE: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("   Cannot connect to API. Is it running?")
        print("   Try: python main.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR")
        print("   API request took too long (>2 minutes)")
        print("   This might indicate API performance issues")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False


def get_risk_level(score):
    """Convert risk score to descriptive level"""
    if score <= 2:
        return "Very Low"
    elif score <= 4:
        return "Low"
    elif score <= 6:
        return "Medium"
    elif score <= 8:
        return "High"
    else:
        return "Very High"


def test_health_endpoint(api_url="http://localhost:8001"):
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        
        if response.status_code == 200:
            health = response.json()
            print("✅ Health check passed")
            print(f"   Status: {health['status']}")
            
            services = health.get('services', {})
            for service, status in services.items():
                icon = "✅" if status == "healthy" else "❌"
                print(f"   {icon} {service}: {status}")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False


def test_additional_routes():
    """Test with additional route examples"""
    print("\n🧪 Testing Additional Routes...")
    
    additional_tests = [
        {
            "name": "Europe to Asia (Low Risk)",
            "data": {
                "departure_port": "Rotterdam",
                "destination_port": "Singapore",
                "departure_date": (date.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "carrier_name": "Maersk",
                "goods_type": "textiles"
            }
        },
        {
            "name": "Middle East to US (Medium Risk)",
            "data": {
                "departure_port": "Dubai",
                "destination_port": "New York",
                "departure_date": (date.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
                "carrier_name": "MSC",
                "goods_type": "machinery"
            }
        }
    ]
    
    for test in additional_tests:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   Route: {test['data']['departure_port']} → {test['data']['destination_port']}")
        
        try:
            response = requests.post(
                "http://localhost:8001/assess-geopolitical-risk",
                json=test['data'],
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Risk Score: {result['risk_score']}/10 ({get_risk_level(result['risk_score'])})")
                print(f"   📅 Travel Days: {result['travel_days']}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def main():
    """Main test function"""
    # api_url = "http://localhost:8001"
    api_url = "https://geopolitical-risk-api.onrender.com"
    
    # Check if custom URL provided
    if len(sys.argv) > 1:
        api_url = sys.argv[1].rstrip('/')
    
    print("🧪 Geopolitical Risk API Test Suite")
    print(f"🌐 Testing API at: {api_url}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Health check
    health_ok = test_health_endpoint(api_url)
    
    if not health_ok:
        print("\n❌ Health check failed. Cannot proceed with other tests.")
        print("💡 Make sure the API is running: python main.py")
        sys.exit(1)
    
    # Test 2: Main risk assessment
    main_test_ok = test_api_endpoint(api_url)
    
    if not main_test_ok:
        print("\n❌ Main API test failed.")
        sys.exit(1)
    
    # Test 3: Additional routes (optional)
    try:
        test_additional_routes()
    except Exception as e:
        print(f"⚠️ Additional tests failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print(f"✅ Health Check: {'Passed' if health_ok else 'Failed'}")
    print(f"✅ Main Assessment: {'Passed' if main_test_ok else 'Failed'}")
    print(f"📊 Overall Status: {'SUCCESS' if health_ok and main_test_ok else 'PARTIAL'}")


if __name__ == "__main__":
    main()