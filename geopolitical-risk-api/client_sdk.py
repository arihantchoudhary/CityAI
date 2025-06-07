"""
Geopolitical Risk Assessment API - Python Client SDK

A comprehensive Python SDK for integrating with the Geopolitical Risk Assessment API.
Provides high-level interfaces, error handling, caching, and utilities.
"""

import asyncio
import aiohttp
import requests
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json
import time
from functools import wraps
import hashlib


@dataclass
class RiskAssessment:
    """Risk assessment result data structure"""
    risk_score: int
    risk_description: str
    geopolitical_summary: str
    departure_country_risk: Dict[str, Any]
    destination_country_risk: Dict[str, Any]
    route_analysis: Dict[str, Any]
    recent_events: List[Dict[str, Any]]
    travel_days: int
    assessment_timestamp: datetime
    
    @property
    def risk_level(self) -> str:
        """Get human-readable risk level"""
        if self.risk_score <= 2:
            return "Very Low"
        elif self.risk_score <= 4:
            return "Low"
        elif self.risk_score <= 6:
            return "Medium"
        elif self.risk_score <= 8:
            return "High"
        else:
            return "Very High"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if this is a high-risk assessment"""
        return self.risk_score >= 7
    
    @property
    def chokepoints(self) -> List[str]:
        """Get list of chokepoints on the route"""
        return self.route_analysis.get('chokepoints', [])
    
    @property
    def security_zones(self) -> List[str]:
        """Get list of security zones on the route"""
        return self.route_analysis.get('security_zones', [])
    
    @property
    def high_impact_events(self) -> List[Dict[str, Any]]:
        """Get high-impact recent events (relevance score >= 7)"""
        return [event for event in self.recent_events if event.get('relevance_score', 0) >= 7]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'risk_description': self.risk_description,
            'geopolitical_summary': self.geopolitical_summary,
            'departure_country_risk': self.departure_country_risk,
            'destination_country_risk': self.destination_country_risk,
            'route_analysis': self.route_analysis,
            'recent_events': self.recent_events,
            'travel_days': self.travel_days,
            'assessment_timestamp': self.assessment_timestamp.isoformat(),
            'is_high_risk': self.is_high_risk,
            'chokepoints': self.chokepoints,
            'security_zones': self.security_zones,
            'high_impact_events': self.high_impact_events
        }


class GeopoliticalRiskAPIError(Exception):
    """Base exception for API errors"""
    pass


class ValidationError(GeopoliticalRiskAPIError):
    """Validation error exception"""
    pass


class APIConnectionError(GeopoliticalRiskAPIError):
    """API connection error exception"""
    pass


class RateLimitError(GeopoliticalRiskAPIError):
    """Rate limit exceeded exception"""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    continue
            raise APIConnectionError(f"API call failed after {max_retries} attempts: {str(last_exception)}")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    continue
            raise APIConnectionError(f"API call failed after {max_retries} attempts: {str(last_exception)}")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class GeopoliticalRiskClient:
    """Synchronous client for Geopolitical Risk Assessment API"""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8001",
        api_key: Optional[str] = None,
        timeout: int = 120,
        enable_caching: bool = True,
        cache_ttl: int = 3600
    ):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            enable_caching: Enable response caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        
        # Setup session
        self.session = requests.Session()
        if api_key:
            self.session.headers['X-API-Key'] = api_key
        self.session.headers['User-Agent'] = 'GeopoliticalRiskClient/1.0'
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        cache_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get item from cache if valid"""
        if not self.enable_caching or cache_key not in self.cache:
            return None
        
        item, timestamp = self.cache[cache_key]
        if time.time() - timestamp > self.cache_ttl:
            del self.cache[cache_key]
            return None
        
        return item
    
    def _set_cache(self, cache_key: str, value: Any):
        """Set item in cache"""
        if self.enable_caching:
            self.cache[cache_key] = (value, time.time())
    
    @retry_on_failure(max_retries=3)
    def assess_risk(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: Union[date, str],
        carrier_name: str,
        goods_type: str
    ) -> RiskAssessment:
        """
        Assess geopolitical risk for a shipping route
        
        Args:
            departure_port: Name of departure port
            destination_port: Name of destination port
            departure_date: Departure date (date object or YYYY-MM-DD string)
            carrier_name: Shipping carrier name
            goods_type: Type of goods being shipped
            
        Returns:
            RiskAssessment object with comprehensive risk analysis
            
        Raises:
            ValidationError: Invalid input parameters
            APIConnectionError: API connection issues
            RateLimitError: Rate limit exceeded
        """
        # Validate and format inputs
        if isinstance(departure_date, date):
            departure_date = departure_date.strftime("%Y-%m-%d")
        
        request_data = {
            "departure_port": departure_port,
            "destination_port": destination_port,
            "departure_date": departure_date,
            "carrier_name": carrier_name,
            "goods_type": goods_type
        }
        
        # Check cache
        cache_key = self._get_cache_key("assess_risk", request_data)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            self.logger.debug("Returning cached risk assessment")
            return cached_result
        
        # Make API request
        try:
            response = self.session.post(
                f"{self.base_url}/assess-geopolitical-risk",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 400:
                raise ValidationError(f"Invalid input: {response.text}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code != 200:
                raise APIConnectionError(f"API error {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Convert to RiskAssessment object
            result = RiskAssessment(
                risk_score=data['risk_score'],
                risk_description=data['risk_description'],
                geopolitical_summary=data['geopolitical_summary'],
                departure_country_risk=data['departure_country_risk'],
                destination_country_risk=data['destination_country_risk'],
                route_analysis=data['route_analysis'],
                recent_events=data['recent_events'],
                travel_days=data['travel_days'],
                assessment_timestamp=datetime.fromisoformat(data['assessment_timestamp'].replace('Z', '+00:00'))
            )
            
            # Cache the result
            self._set_cache(cache_key, result)
            
            return result
            
        except requests.RequestException as e:
            raise APIConnectionError(f"Request failed: {str(e)}")
    
    @retry_on_failure(max_retries=2)
    def get_country_risk(self, country: str, goods_type: Optional[str] = None) -> Dict[str, Any]:
        """Get risk profile for a specific country"""
        cache_key = self._get_cache_key("country_risk", country, goods_type)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        params = {"country": country}
        if goods_type:
            params["goods_type"] = goods_type
        
        try:
            response = self.session.get(
                f"{self.base_url}/countries/risk-profile",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            self._set_cache(cache_key, result)
            return result
            
        except requests.RequestException as e:
            raise APIConnectionError(f"Request failed: {str(e)}")
    
    @retry_on_failure(max_retries=2)
    def analyze_route(
        self, 
        departure_port: str, 
        destination_port: str, 
        goods_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze route chokepoints and security zones"""
        cache_key = self._get_cache_key("route_analysis", departure_port, destination_port, goods_type)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "departure_port": departure_port,
            "destination_port": destination_port
        }
        if goods_type:
            params["goods_type"] = goods_type
        
        try:
            response = self.session.get(
                f"{self.base_url}/routes/chokepoints",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            self._set_cache(cache_key, result)
            return result
            
        except requests.RequestException as e:
            raise APIConnectionError(f"Request failed: {str(e)}")
    
    @retry_on_failure(max_retries=2)
    def search_ports(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for ports by name"""
        try:
            response = self.session.get(
                f"{self.base_url}/ports/search",
                params={"query": query, "limit": limit},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["ports"]
            
        except requests.RequestException as e:
            raise APIConnectionError(f"Request failed: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIConnectionError(f"Health check failed: {str(e)}")
    
    def bulk_assess_risks(self, route_requests: List[Dict[str, Any]]) -> List[RiskAssessment]:
        """Assess multiple routes in batch"""
        results = []
        for i, request_data in enumerate(route_requests):
            try:
                self.logger.info(f"Processing route {i+1}/{len(route_requests)}")
                result = self.assess_risk(**request_data)
                results.append(result)
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Failed to assess route {i+1}: {str(e)}")
                # Continue with other routes
                continue
        
        return results
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def close(self):
        """Close the session"""
        self.session.close()


class AsyncGeopoliticalRiskClient:
    """Asynchronous client for Geopolitical Risk Assessment API"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_key: Optional[str] = None,
        timeout: int = 120,
        enable_caching: bool = True,
        cache_ttl: int = 3600
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        self._session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        headers = {'User-Agent': 'AsyncGeopoliticalRiskClient/1.0'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        self._session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        cache_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get item from cache if valid"""
        if not self.enable_caching or cache_key not in self.cache:
            return None
        
        item, timestamp = self.cache[cache_key]
        if time.time() - timestamp > self.cache_ttl:
            del self.cache[cache_key]
            return None
        
        return item
    
    def _set_cache(self, cache_key: str, value: Any):
        """Set item in cache"""
        if self.enable_caching:
            self.cache[cache_key] = (value, time.time())
    
    @retry_on_failure(max_retries=3)
    async def assess_risk(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: Union[date, str],
        carrier_name: str,
        goods_type: str
    ) -> RiskAssessment:
        """Async version of assess_risk"""
        if isinstance(departure_date, date):
            departure_date = departure_date.strftime("%Y-%m-%d")
        
        request_data = {
            "departure_port": departure_port,
            "destination_port": destination_port,
            "departure_date": departure_date,
            "carrier_name": carrier_name,
            "goods_type": goods_type
        }
        
        # Check cache
        cache_key = self._get_cache_key("assess_risk", request_data)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        async with self._session.post(
            f"{self.base_url}/assess-geopolitical-risk",
            json=request_data
        ) as response:
            if response.status == 400:
                text = await response.text()
                raise ValidationError(f"Invalid input: {text}")
            elif response.status == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status != 200:
                text = await response.text()
                raise APIConnectionError(f"API error {response.status}: {text}")
            
            data = await response.json()
            
            result = RiskAssessment(
                risk_score=data['risk_score'],
                risk_description=data['risk_description'],
                geopolitical_summary=data['geopolitical_summary'],
                departure_country_risk=data['departure_country_risk'],
                destination_country_risk=data['destination_country_risk'],
                route_analysis=data['route_analysis'],
                recent_events=data['recent_events'],
                travel_days=data['travel_days'],
                assessment_timestamp=datetime.fromisoformat(data['assessment_timestamp'].replace('Z', '+00:00'))
            )
            
            self._set_cache(cache_key, result)
            return result
    
    async def bulk_assess_risks_concurrent(
        self, 
        route_requests: List[Dict[str, Any]], 
        max_concurrent: int = 5
    ) -> List[RiskAssessment]:
        """Assess multiple routes concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def assess_single_route(request_data: Dict[str, Any]) -> Optional[RiskAssessment]:
            async with semaphore:
                try:
                    return await self.assess_risk(**request_data)
                except Exception as e:
                    self.logger.error(f"Failed to assess route: {str(e)}")
                    return None
        
        tasks = [assess_single_route(request) for request in route_requests]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        return [result for result in results if result is not None]


class RiskAnalyzer:
    """Higher-level risk analysis utilities"""
    
    def __init__(self, client: Union[GeopoliticalRiskClient, AsyncGeopoliticalRiskClient]):
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def compare_routes(
        self, 
        routes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare multiple routes and rank by risk"""
        if isinstance(self.client, AsyncGeopoliticalRiskClient):
            raise ValueError("Use async version for AsyncGeopoliticalRiskClient")
        
        assessments = self.client.bulk_assess_risks(routes)
        
        if not assessments:
            return {"error": "No successful assessments"}
        
        # Sort by risk score
        sorted_assessments = sorted(assessments, key=lambda x: x.risk_score)
        
        return {
            "total_routes": len(routes),
            "successful_assessments": len(assessments),
            "lowest_risk_route": {
                "risk_score": sorted_assessments[0].risk_score,
                "risk_level": sorted_assessments[0].risk_level,
                "route": f"{routes[0]['departure_port']} -> {routes[0]['destination_port']}"
            },
            "highest_risk_route": {
                "risk_score": sorted_assessments[-1].risk_score,
                "risk_level": sorted_assessments[-1].risk_level,
                "route": f"{routes[-1]['departure_port']} -> {routes[-1]['destination_port']}"
            },
            "average_risk_score": sum(a.risk_score for a in assessments) / len(assessments),
            "high_risk_routes": len([a for a in assessments if a.is_high_risk]),
            "assessments": [a.to_dict() for a in sorted_assessments]
        }
    
    def get_route_alternatives(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: Union[date, str],
        carrier_name: str,
        goods_type: str,
        alternative_ports: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze route alternatives"""
        if isinstance(self.client, AsyncGeopoliticalRiskClient):
            raise ValueError("Use async version for AsyncGeopoliticalRiskClient")
        
        # Base route assessment
        base_assessment = self.client.assess_risk(
            departure_port, destination_port, departure_date, carrier_name, goods_type
        )
        
        alternatives = []
        
        if alternative_ports:
            for alt_port in alternative_ports:
                try:
                    # Try alternative destination
                    alt_assessment = self.client.assess_risk(
                        departure_port, alt_port, departure_date, carrier_name, goods_type
                    )
                    alternatives.append({
                        "route": f"{departure_port} -> {alt_port}",
                        "risk_score": alt_assessment.risk_score,
                        "risk_level": alt_assessment.risk_level,
                        "travel_days": alt_assessment.travel_days,
                        "assessment": alt_assessment.to_dict()
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to assess alternative route to {alt_port}: {str(e)}")
        
        return {
            "base_route": {
                "route": f"{departure_port} -> {destination_port}",
                "risk_score": base_assessment.risk_score,
                "risk_level": base_assessment.risk_level,
                "travel_days": base_assessment.travel_days,
                "assessment": base_assessment.to_dict()
            },
            "alternatives": sorted(alternatives, key=lambda x: x["risk_score"]),
            "recommendation": self._generate_route_recommendation(base_assessment, alternatives)
        }
    
    def _generate_route_recommendation(
        self, 
        base_assessment: RiskAssessment, 
        alternatives: List[Dict[str, Any]]
    ) -> str:
        """Generate route recommendation based on analysis"""
        if not alternatives:
            if base_assessment.is_high_risk:
                return "High risk route with no alternatives analyzed. Consider delaying shipment or finding alternative routing."
            else:
                return "Route shows acceptable risk levels. Proceed with standard security protocols."
        
        best_alternative = min(alternatives, key=lambda x: x["risk_score"])
        
        if base_assessment.risk_score > best_alternative["risk_score"] + 1:  # Significant improvement
            return f"Recommend alternative route: {best_alternative['route']} (Risk: {best_alternative['risk_level']}) instead of base route (Risk: {base_assessment.risk_level})"
        elif base_assessment.is_high_risk:
            return "All analyzed routes show elevated risk. Consider postponing shipment or implementing enhanced security measures."
        else:
            return "Base route shows acceptable risk levels compared to alternatives. Proceed as planned."


# Convenience functions for quick usage
def assess_shipping_risk(
    departure_port: str,
    destination_port: str,
    departure_date: Union[date, str],
    carrier_name: str,
    goods_type: str,
    api_url: str = "http://localhost:8001",
    api_key: Optional[str] = None
) -> RiskAssessment:
    """
    Quick function to assess shipping risk
    
    Args:
        departure_port: Departure port name
        destination_port: Destination port name  
        departure_date: Departure date
        carrier_name: Carrier name
        goods_type: Type of goods
        api_url: API base URL
        api_key: Optional API key
        
    Returns:
        RiskAssessment object
    """
    client = GeopoliticalRiskClient(api_url, api_key)
    try:
        return client.assess_risk(departure_port, destination_port, departure_date, carrier_name, goods_type)
    finally:
        client.close()


async def assess_shipping_risk_async(
    departure_port: str,
    destination_port: str,
    departure_date: Union[date, str],
    carrier_name: str,
    goods_type: str,
    api_url: str = "http://localhost:8001",
    api_key: Optional[str] = None
) -> RiskAssessment:
    """
    Async version of assess_shipping_risk
    """
    async with AsyncGeopoliticalRiskClient(api_url, api_key) as client:
        return await client.assess_risk(departure_port, destination_port, departure_date, carrier_name, goods_type)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    print("🚀 Geopolitical Risk Assessment SDK Example")
    
    try:
        # Create client
        client = GeopoliticalRiskClient()
        
        # Test health check
        health = client.health_check()
        print(f"✅ API Health: {health['status']}")
        
        # Assess a route
        risk = assess_shipping_risk(
            departure_port="Los Angeles",
            destination_port="Shanghai",
            departure_date=date.today() + timedelta(days=7),
            carrier_name="COSCO",
            goods_type="electronics"
        )
        
        print(f"\n📊 Risk Assessment Results:")
        print(f"Risk Score: {risk.risk_score}/10 ({risk.risk_level})")
        print(f"Route: Los Angeles -> Shanghai")
        print(f"Travel Days: {risk.travel_days}")
        print(f"High Impact Events: {len(risk.high_impact_events)}")
        print(f"Chokepoints: {', '.join(risk.chokepoints) if risk.chokepoints else 'None'}")
        
        if risk.is_high_risk:
            print("⚠️  HIGH RISK ROUTE - Enhanced security measures recommended")
        else:
            print("✅ Acceptable risk level for this route")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")