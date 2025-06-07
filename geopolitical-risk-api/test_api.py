"""
Comprehensive test suite for Geopolitical Risk Assessment API
"""

import asyncio
import aiohttp
import json
import time
from datetime import date, timedelta
from typing import Dict, Any, List
import sys


class GeopoliticalAPITester:
    """Test suite for the Geopolitical Risk Assessment API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Geopolitical Risk Assessment API Test Suite")
        print(f"📍 Testing API at: {self.base_url}")
        print("=" * 60)
        
        # Test categories
        test_categories = [
            ("Health Check", self.test_health_endpoints),
            ("Port Services", self.test_port_endpoints),
            ("Country Risk Profiles", self.test_country_risk_endpoints),
            ("Route Analysis", self.test_route_analysis_endpoints),
            ("Main Risk Assessment", self.test_main_risk_assessment),
            ("Edge Cases", self.test_edge_cases),
            ("Performance", self.test_performance),
            ("Error Handling", self.test_error_handling)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n📂 {category_name}")
            print("-" * 40)
            try:
                await test_function()
            except Exception as e:
                self.add_result(f"{category_name} - FAILED", False, str(e))
                print(f"❌ {category_name} tests failed: {str(e)}")
        
        # Print summary
        self.print_test_summary()
    
    async def test_health_endpoints(self):
        """Test health check endpoints"""
        
        # Test root endpoint
        await self.test_request(
            "GET", "/", 
            "Root endpoint", 
            expected_fields=["service", "status", "timestamp"]
        )
        
        # Test health endpoint
        await self.test_request(
            "GET", "/health",
            "Health check endpoint",
            expected_fields=["status", "services", "timestamp"]
        )
    
    async def test_port_endpoints(self):
        """Test port-related endpoints"""
        
        # Test port search
        test_cases = [
            ("Los Angeles", "Major US port search"),
            ("Shanghai", "Major Chinese port search"),
            ("Singapore", "Major Asian hub search"),
            ("Rotterdam", "Major European port search"),
            ("xyz123", "Non-existent port search")  # Should return empty or no results
        ]
        
        for query, description in test_cases:
            await self.test_request(
                "GET", f"/ports/search?query={query}&limit=5",
                f"Port search: {description}",
                expected_fields=["ports"]
            )
    
    async def test_country_risk_endpoints(self):
        """Test country risk profile endpoints"""
        
        test_cases = [
            ("United States", None, "US risk profile"),
            ("China", "electronics", "China risk profile with electronics"),
            ("Singapore", "general", "Singapore risk profile"),
            ("Iran", "energy", "Iran risk profile with energy goods"),
            ("NonExistentCountry", None, "Non-existent country")  # Should handle gracefully
        ]
        
        for country, goods_type, description in test_cases:
            params = f"?country={country}"
            if goods_type:
                params += f"&goods_type={goods_type}"
            
            await self.test_request(
                "GET", f"/countries/risk-profile{params}",
                f"Country risk: {description}",
                expected_fields=["country", "risk_profile"]
            )
    
    async def test_route_analysis_endpoints(self):
        """Test route analysis endpoints"""
        
        test_cases = [
            ("Los Angeles", "Shanghai", "electronics", "US-China electronics route"),
            ("Rotterdam", "Singapore", "machinery", "Europe-Asia machinery route"),
            ("Dubai", "New York", "oil", "Middle East-US energy route"),
            ("Hamburg", "Tokyo", None, "Europe-Asia general route")
        ]
        
        for departure, destination, goods_type, description in test_cases:
            params = f"?departure_port={departure}&destination_port={destination}"
            if goods_type:
                params += f"&goods_type={goods_type}"
            
            await self.test_request(
                "GET", f"/routes/chokepoints{params}",
                f"Route analysis: {description}",
                expected_fields=["route_analysis"]
            )
    
    async def test_main_risk_assessment(self):
        """Test main geopolitical risk assessment endpoint"""
        
        # Test various route scenarios
        test_scenarios = [
            {
                "departure_port": "Los Angeles",
                "destination_port": "Shanghai", 
                "departure_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "carrier_name": "COSCO Shipping",
                "goods_type": "electronics",
                "description": "US-China electronics (high-risk scenario)"
            },
            {
                "departure_port": "Rotterdam",
                "destination_port": "Singapore",
                "departure_date": (date.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "carrier_name": "Maersk",
                "goods_type": "machinery",
                "description": "Europe-Asia machinery (medium-risk scenario)"
            },
            {
                "departure_port": "Singapore",
                "destination_port": "Rotterdam",
                "departure_date": (date.today() + timedelta(days=21)).strftime("%Y-%m-%d"),
                "carrier_name": "MSC",
                "goods_type": "textiles",
                "description": "Asia-Europe textiles (low-risk scenario)"
            },
            {
                "departure_port": "Dubai",
                "destination_port": "Houston",
                "departure_date": (date.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
                "carrier_name": "Hapag-Lloyd",
                "goods_type": "chemicals",
                "description": "Middle East-US chemicals (chokepoint risk)"
            }
        ]
        
        for scenario in test_scenarios:
            description = scenario.pop("description")
            await self.test_request(
                "POST", "/assess-geopolitical-risk",
                f"Risk assessment: {description}",
                request_data=scenario,
                expected_fields=[
                    "risk_score", "risk_description", "geopolitical_summary",
                    "departure_country_risk", "destination_country_risk",
                    "route_analysis", "recent_events", "travel_days", "assessment_timestamp"
                ],
                validate_risk_score=True
            )
    
    async def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        
        # Test with minimal valid data
        minimal_request = {
            "departure_port": "LA",  # Short name
            "destination_port": "NY",  # Short name
            "departure_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "carrier_name": "XX",  # Minimal carrier name
            "goods_type": "AB"  # Minimal goods type
        }
        
        await self.test_request(
            "POST", "/assess-geopolitical-risk",
            "Edge case: Minimal valid data",
            request_data=minimal_request,
            expected_status=200  # Should work or gracefully handle
        )
        
        # Test with maximum future date
        max_date_request = {
            "departure_port": "Los Angeles",
            "destination_port": "Shanghai",
            "departure_date": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "carrier_name": "Test Carrier",
            "goods_type": "test goods"
        }
        
        await self.test_request(
            "POST", "/assess-geopolitical-risk",
            "Edge case: Maximum future date",
            request_data=max_date_request,
            expected_status=200
        )
    
    async def test_performance(self):
        """Test API performance and response times"""
        
        print("⏱️  Testing performance...")
        
        # Standard request for timing
        standard_request = {
            "departure_port": "Singapore",
            "destination_port": "Rotterdam",
            "departure_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "carrier_name": "Maersk",
            "goods_type": "containers"
        }
        
        # Measure response time
        start_time = time.time()
        response = await self.make_request("POST", "/assess-geopolitical-risk", standard_request)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status == 200:
            if response_time < 30:
                self.add_result("Performance: Fast response", True, f"{response_time:.2f}s")
            elif response_time < 60:
                self.add_result("Performance: Acceptable response", True, f"{response_time:.2f}s")
            else:
                self.add_result("Performance: Slow response", False, f"{response_time:.2f}s")
        else:
            self.add_result("Performance: Request failed", False, f"Status: {response.status}")
        
        print(f"   Response time: {response_time:.2f} seconds")
    
    async def test_error_handling(self):
        """Test error handling and validation"""
        
        error_test_cases = [
            # Missing required fields
            ({
                "destination_port": "Shanghai",
                "departure_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "carrier_name": "COSCO",
                "goods_type": "electronics"
            }, "Missing departure_port"),
            
            # Invalid date format
            ({
                "departure_port": "Los Angeles",
                "destination_port": "Shanghai",
                "departure_date": "invalid-date",
                "carrier_name": "COSCO",
                "goods_type": "electronics"
            }, "Invalid date format"),
            
            # Past date
            ({
                "departure_port": "Los Angeles",
                "destination_port": "Shanghai",
                "departure_date": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "carrier_name": "COSCO",
                "goods_type": "electronics"
            }, "Past date"),
            
            # Empty strings
            ({
                "departure_port": "",
                "destination_port": "Shanghai",
                "departure_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "carrier_name": "COSCO",
                "goods_type": "electronics"
            }, "Empty departure_port"),
            
            # Very long strings
            ({
                "departure_port": "A" * 150,  # Too long
                "destination_port": "Shanghai",
                "departure_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "carrier_name": "COSCO",
                "goods_type": "electronics"
            }, "Oversized departure_port")
        ]
        
        for invalid_data, description in error_test_cases:
            await self.test_request(
                "POST", "/assess-geopolitical-risk",
                f"Error handling: {description}",
                request_data=invalid_data,
                expected_status=400  # Should return validation error
            )
    
    async def test_request(
        self, 
        method: str, 
        endpoint: str, 
        description: str,
        request_data: Dict[str, Any] = None,
        expected_status: int = 200,
        expected_fields: List[str] = None,
        validate_risk_score: bool = False
    ):
        """Test a single API request"""
        
        try:
            response = await self.make_request(method, endpoint, request_data)
            
            # Check status code
            if response.status != expected_status:
                self.add_result(description, False, f"Expected {expected_status}, got {response.status}")
                return
            
            # Parse response
            if response.status == 200:
                response_data = await response.json()
                
                # Check expected fields
                if expected_fields:
                    missing_fields = [field for field in expected_fields if field not in response_data]
                    if missing_fields:
                        self.add_result(description, False, f"Missing fields: {missing_fields}")
                        return
                
                # Validate risk score if applicable
                if validate_risk_score and "risk_score" in response_data:
                    risk_score = response_data["risk_score"]
                    if not isinstance(risk_score, int) or not 1 <= risk_score <= 10:
                        self.add_result(description, False, f"Invalid risk score: {risk_score}")
                        return
                
                self.add_result(description, True, "Success")
                
                # Print key information for main assessments
                if endpoint == "/assess-geopolitical-risk" and method == "POST":
                    risk_score = response_data.get("risk_score", "N/A")
                    event_count = len(response_data.get("recent_events", []))
                    chokepoints = response_data.get("route_analysis", {}).get("chokepoints", [])
                    print(f"   📊 Risk Score: {risk_score}/10, Events: {event_count}, Chokepoints: {len(chokepoints)}")
            
            else:
                # For non-200 responses, just check that we got the expected status
                self.add_result(description, True, f"Correctly returned {response.status}")
        
        except Exception as e:
            self.add_result(description, False, f"Exception: {str(e)}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None):
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == "GET":
            return await self.session.get(url)
        elif method.upper() == "POST":
            return await self.session.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        """Add test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        
        # Print result
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
        if details and not passed:
            print(f"   💬 {details}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n📋 Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🎯 Test Recommendations:")
        if passed_tests == total_tests:
            print("   • All tests passed! API is ready for use.")
        elif passed_tests / total_tests >= 0.8:
            print("   • Most tests passed. Review failed tests and address if critical.")
        else:
            print("   • Multiple test failures. Review API configuration and dependencies.")
        
        # API-specific recommendations
        if any("Health check" in result["test"] and not result["passed"] for result in self.test_results):
            print("   • Health check failed - verify API is running on correct port")
        
        if any("Risk assessment" in result["test"] and not result["passed"] for result in self.test_results):
            print("   • Risk assessment failed - check OpenAI API key and configuration")
        
        print("\n🔧 Next Steps:")
        print("   • Review API logs for detailed error information")
        print("   • Check environment variables and configuration")
        print("   • Verify external service dependencies (OpenAI, News APIs)")
        print("   • Test with different route combinations")


async def main():
    """Main test execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Geopolitical Risk Assessment API")
    parser.add_argument("--url", default="http://localhost:8001", help="API base URL")
    parser.add_argument("--quick", action="store_true", help="Run only essential tests")
    args = parser.parse_args()
    
    async with GeopoliticalAPITester(args.url) as tester:
        if args.quick:
            print("🏃‍♂️ Running Quick Test Suite")
            await tester.test_health_endpoints()
            await tester.test_request(
                "POST", "/assess-geopolitical-risk",
                "Quick risk assessment test",
                request_data={
                    "departure_port": "Singapore",
                    "destination_port": "Rotterdam",
                    "departure_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "carrier_name": "Maersk",
                    "goods_type": "containers"
                },
                expected_fields=["risk_score", "risk_description"],
                validate_risk_score=True
            )
            tester.print_test_summary()
        else:
            await tester.run_all_tests()


if __name__ == "__main__":
    # Check if event loop is already running (in Jupyter/async environment)
    try:
        loop = asyncio.get_running_loop()
        print("⚠️  Async event loop already running. Use 'await main()' in async environment.")
    except RuntimeError:
        # No event loop running, safe to run
        asyncio.run(main())