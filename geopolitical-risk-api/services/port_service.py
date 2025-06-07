"""
Port service for managing port information and route calculations
"""

import logging
from typing import Dict, Any, List, Optional
import math
import asyncio

logger = logging.getLogger(__name__)


class PortService:
    """Service for port information, coordinates, and route calculations"""
    
    def __init__(self):
        self.port_cache = {}
        self._init_port_database()
    
    def _init_port_database(self):
        """Initialize comprehensive port database with geopolitical context"""
        self.ports = {
            # North America
            "Los Angeles": {
                "name": "Port of Los Angeles", "country": "United States", "code": "USLAX",
                "latitude": 33.7361, "longitude": -118.2922, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Long Beach": {
                "name": "Port of Long Beach", "country": "United States", "code": "USLGB", 
                "latitude": 33.7700, "longitude": -118.2100, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "New York": {
                "name": "Port of New York and New Jersey", "country": "United States", "code": "USNYC",
                "latitude": 40.6700, "longitude": -74.0400, "region": "North America",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Seattle": {
                "name": "Port of Seattle", "country": "United States", "code": "USSEA",
                "latitude": 47.6062, "longitude": -122.3321, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Oakland": {
                "name": "Port of Oakland", "country": "United States", "code": "USOAK",
                "latitude": 37.8044, "longitude": -122.2711, "region": "North America",
                "security_level": "High", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Savannah": {
                "name": "Port of Savannah", "country": "United States", "code": "USSAV",
                "latitude": 32.0800, "longitude": -81.0900, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Charleston": {
                "name": "Port of Charleston", "country": "United States", "code": "USCHS",
                "latitude": 32.7767, "longitude": -79.9311, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Houston": {
                "name": "Port of Houston", "country": "United States", "code": "USHOU",
                "latitude": 29.7633, "longitude": -95.3633, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Miami": {
                "name": "Port of Miami", "country": "United States", "code": "USMIA",
                "latitude": 25.7742, "longitude": -80.1936, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Vancouver": {
                "name": "Port of Vancouver", "country": "Canada", "code": "CAVAN",
                "latitude": 49.2827, "longitude": -123.1207, "region": "North America",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            
            # Asia
            "Shanghai": {
                "name": "Port of Shanghai", "country": "China", "code": "CNSHA",
                "latitude": 31.2304, "longitude": 121.4737, "region": "East Asia",
                "security_level": "High", "labor_stability": "Controlled", "infrastructure": "Excellent"
            },
            "Shenzhen": {
                "name": "Port of Shenzhen", "country": "China", "code": "CNSZN",
                "latitude": 22.5431, "longitude": 114.0579, "region": "East Asia",
                "security_level": "High", "labor_stability": "Controlled", "infrastructure": "Excellent"
            },
            "Ningbo": {
                "name": "Port of Ningbo-Zhoushan", "country": "China", "code": "CNNGB",
                "latitude": 29.8683, "longitude": 121.5440, "region": "East Asia",
                "security_level": "High", "labor_stability": "Controlled", "infrastructure": "Very Good"
            },
            "Hong Kong": {
                "name": "Port of Hong Kong", "country": "Hong Kong SAR", "code": "HKHKG",
                "latitude": 22.3193, "longitude": 114.1694, "region": "East Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Singapore": {
                "name": "Port of Singapore", "country": "Singapore", "code": "SGSIN",
                "latitude": 1.2966, "longitude": 103.7764, "region": "Southeast Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Tokyo": {
                "name": "Port of Tokyo", "country": "Japan", "code": "JPTYO",
                "latitude": 35.6528, "longitude": 139.7594, "region": "East Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Yokohama": {
                "name": "Port of Yokohama", "country": "Japan", "code": "JPYOK",
                "latitude": 35.4647, "longitude": 139.6221, "region": "East Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Kobe": {
                "name": "Port of Kobe", "country": "Japan", "code": "JPUKB",
                "latitude": 34.6901, "longitude": 135.1956, "region": "East Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Very Good"
            },
            "Busan": {
                "name": "Port of Busan", "country": "South Korea", "code": "KRPUS",
                "latitude": 35.1796, "longitude": 129.0756, "region": "East Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Kaohsiung": {
                "name": "Port of Kaohsiung", "country": "Taiwan", "code": "TWKHH",
                "latitude": 22.6163, "longitude": 120.3133, "region": "East Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            
            # Europe
            "Rotterdam": {
                "name": "Port of Rotterdam", "country": "Netherlands", "code": "NLRTM",
                "latitude": 51.9225, "longitude": 4.4792, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Antwerp": {
                "name": "Port of Antwerp", "country": "Belgium", "code": "BEANR",
                "latitude": 51.2213, "longitude": 4.4051, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Very Good", "infrastructure": "Excellent"
            },
            "Hamburg": {
                "name": "Port of Hamburg", "country": "Germany", "code": "DEHAM",
                "latitude": 53.5511, "longitude": 9.9937, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Very Good", "infrastructure": "Excellent"
            },
            "Felixstowe": {
                "name": "Port of Felixstowe", "country": "United Kingdom", "code": "GBFXT",
                "latitude": 51.9542, "longitude": 1.3511, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Le Havre": {
                "name": "Port of Le Havre", "country": "France", "code": "FRLEH",
                "latitude": 49.4944, "longitude": 0.1079, "region": "Europe",
                "security_level": "High", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Genoa": {
                "name": "Port of Genoa", "country": "Italy", "code": "ITGOA",
                "latitude": 44.4056, "longitude": 8.9463, "region": "Europe",
                "security_level": "High", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Barcelona": {
                "name": "Port of Barcelona", "country": "Spain", "code": "ESBCN",
                "latitude": 41.3851, "longitude": 2.1734, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Valencia": {
                "name": "Port of Valencia", "country": "Spain", "code": "ESVLC",
                "latitude": 39.4699, "longitude": -0.3763, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # Middle East
            "Dubai": {
                "name": "Port of Dubai", "country": "United Arab Emirates", "code": "AEDXB",
                "latitude": 25.2769, "longitude": 55.2962, "region": "Middle East",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Jebel Ali": {
                "name": "Jebel Ali Port", "country": "United Arab Emirates", "code": "AEJEA",
                "latitude": 25.0118, "longitude": 55.1370, "region": "Middle East",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            
            # Other regions
            "Santos": {
                "name": "Port of Santos", "country": "Brazil", "code": "BRSSZ",
                "latitude": -23.9618, "longitude": -46.3322, "region": "South America",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Buenos Aires": {
                "name": "Port of Buenos Aires", "country": "Argentina", "code": "ARBUE",
                "latitude": -34.6118, "longitude": -58.3960, "region": "South America",
                "security_level": "Medium", "labor_stability": "Poor", "infrastructure": "Fair"
            },
            "Melbourne": {
                "name": "Port of Melbourne", "country": "Australia", "code": "AUMEL",
                "latitude": -37.8136, "longitude": 144.9631, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Sydney": {
                "name": "Port of Sydney", "country": "Australia", "code": "AUSYD",
                "latitude": -33.8688, "longitude": 151.2093, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Durban": {
                "name": "Port of Durban", "country": "South Africa", "code": "ZADUR",
                "latitude": -29.8587, "longitude": 31.0218, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Poor", "infrastructure": "Fair"
            },
            "Cape Town": {
                "name": "Port of Cape Town", "country": "South Africa", "code": "ZACPT",
                "latitude": -33.9249, "longitude": 18.4241, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            }
        }
        
        # Create search index for port names
        self.port_search_index = {}
        for key, port in self.ports.items():
            # Index by various name variations
            search_terms = [
                key.lower(),
                port["name"].lower(),
                port["code"].lower(),
                port["country"].lower() + " " + key.lower()
            ]
            
            for term in search_terms:
                if term not in self.port_search_index:
                    self.port_search_index[term] = []
                self.port_search_index[term].append(port)
    
    async def get_port_info(self, port_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive port information including geopolitical context"""
        try:
            # Check exact match first
            if port_name in self.ports:
                return self.ports[port_name]
            
            # Search for partial matches
            port_name_lower = port_name.lower()
            
            # Try direct search in index
            if port_name_lower in self.port_search_index:
                return self.port_search_index[port_name_lower][0]
            
            # Try fuzzy matching
            best_match = self._fuzzy_search_port(port_name_lower)
            if best_match:
                return best_match
            
            logger.warning(f"Port not found: {port_name}")
            return None
            
        except Exception as e:
            logger.error(f"Port info lookup failed for {port_name}: {str(e)}")
            return None
    
    async def get_port_coordinates(self, port_name: str) -> Optional[Dict[str, float]]:
        """Get port coordinates (latitude, longitude)"""
        port_info = await self.get_port_info(port_name)
        if port_info:
            return {
                "lat": port_info["latitude"],
                "lon": port_info["longitude"]
            }
        return None
    
    async def search_ports(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for ports by name with ranking"""
        try:
            query_lower = query.lower()
            matches = []
            
            for port_key, port_info in self.ports.items():
                score = self._calculate_search_score(query_lower, port_info)
                if score > 0:
                    match = port_info.copy()
                    match["match_score"] = score
                    matches.append(match)
            
            # Sort by match score and limit results
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Port search failed for query '{query}': {str(e)}")
            return []
    
    def estimate_travel_time(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any], 
        goods_type: str
    ) -> int:
        """Estimate travel time in days considering route and cargo factors"""
        try:
            # Calculate distance
            distance_km = self._calculate_distance(
                departure_info["latitude"], departure_info["longitude"],
                destination_info["latitude"], destination_info["longitude"]
            )
            
            # Base speed calculation (container ship average: 20-25 knots)
            avg_speed_knots = 22
            avg_speed_kmh = avg_speed_knots * 1.852  # Convert to km/h
            
            # Route factor (actual routes are longer than great circle distance)
            route_factor = self._get_route_factor(departure_info, destination_info)
            actual_distance = distance_km * route_factor
            
            # Speed adjustments based on cargo type
            speed_factor = self._get_speed_factor(goods_type)
            
            # Efficiency factor (weather, port delays, etc.)
            efficiency_factor = 0.65  # 65% efficiency accounting for all delays
            
            # Calculate travel time
            effective_speed = avg_speed_kmh * speed_factor * efficiency_factor
            travel_hours = actual_distance / effective_speed
            travel_days = max(1, int(travel_hours / 24))
            
            # Add port time (loading/unloading)
            port_days = self._estimate_port_time(departure_info, destination_info, goods_type)
            
            return travel_days + port_days
            
        except Exception as e:
            logger.error(f"Travel time estimation failed: {str(e)}")
            return 14  # Default 2 weeks
    
    def _fuzzy_search_port(self, query: str) -> Optional[Dict[str, Any]]:
        """Perform fuzzy search for port names"""
        best_match = None
        best_score = 0
        
        for port_info in self.ports.values():
            score = self._calculate_search_score(query, port_info)
            if score > best_score:
                best_score = score
                best_match = port_info
        
        # Return match only if score is reasonable
        return best_match if best_score >= 0.3 else None
    
    def _calculate_search_score(self, query: str, port_info: Dict[str, Any]) -> float:
        """Calculate search relevance score"""
        score = 0.0
        
        port_name = port_info["name"].lower()
        port_code = port_info["code"].lower()
        country = port_info["country"].lower()
        
        # Exact matches
        if query == port_name:
            score += 1.0
        elif query == port_code:
            score += 0.9
        elif query in port_name:
            score += 0.8
        elif query in country:
            score += 0.3
        
        # Partial matches
        query_words = query.split()
        port_words = port_name.split()
        
        for q_word in query_words:
            for p_word in port_words:
                if q_word in p_word:
                    score += 0.2
                elif p_word.startswith(q_word):
                    score += 0.4
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points in kilometers"""
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def _get_route_factor(self, departure_info: Dict[str, Any], destination_info: Dict[str, Any]) -> float:
        """Get route factor to account for actual shipping routes vs great circle"""
        dept_region = departure_info.get("region", "")
        dest_region = destination_info.get("region", "")
        
        # Trans-oceanic routes have higher route factors
        if dept_region != dest_region:
            if ("Asia" in dept_region and "Europe" in dest_region) or ("Europe" in dept_region and "Asia" in dest_region):
                return 1.4  # Via Suez Canal or around Africa
            elif ("Asia" in dept_region and "America" in dest_region) or ("America" in dept_region and "Asia" in dest_region):
                return 1.3  # Trans-Pacific routes
            elif ("Europe" in dept_region and "America" in dest_region) or ("America" in dept_region and "Europe" in dest_region):
                return 1.2  # Trans-Atlantic routes
            else:
                return 1.3  # Other international routes
        else:
            return 1.1  # Regional routes
    
    def _get_speed_factor(self, goods_type: str) -> float:
        """Get speed factor based on cargo type"""
        goods_lower = goods_type.lower()
        
        if goods_lower in ["perishables", "food", "pharmaceuticals"]:
            return 1.1  # Faster for time-sensitive cargo
        elif goods_lower in ["hazardous", "chemicals", "oil", "gas"]:
            return 0.9  # Slower for safety
        elif goods_lower in ["automobiles", "machinery", "heavy"]:
            return 0.95  # Slightly slower for heavy cargo
        else:
            return 1.0  # Standard speed
    
    def _estimate_port_time(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any], 
        goods_type: str
    ) -> int:
        """Estimate port time (loading/unloading) in days"""
        base_port_time = 2  # Base 2 days for port operations
        
        # Adjust based on port infrastructure
        dept_infra = departure_info.get("infrastructure", "Good")
        dest_infra = destination_info.get("infrastructure", "Good")
        
        infra_factor = 1.0
        if dept_infra == "Poor" or dest_infra == "Poor":
            infra_factor = 1.5
        elif dept_infra == "Fair" or dest_infra == "Fair":
            infra_factor = 1.2
        elif dept_infra == "Excellent" and dest_infra == "Excellent":
            infra_factor = 0.8
        
        # Adjust based on labor conditions
        dept_labor = departure_info.get("labor_stability", "Good")
        dest_labor = destination_info.get("labor_stability", "Good")
        
        labor_factor = 1.0
        if dept_labor == "Poor" or dest_labor == "Poor":
            labor_factor = 1.3
        elif dept_labor == "Fair" or dest_labor == "Fair":
            labor_factor = 1.1
        
        # Adjust based on cargo type
        cargo_factor = 1.0
        goods_lower = goods_type.lower()
        
        if goods_lower in ["hazardous", "chemicals"]:
            cargo_factor = 1.4  # Extra handling time for dangerous goods
        elif goods_lower in ["automobiles", "machinery"]:
            cargo_factor = 1.2  # Special handling equipment needed
        elif goods_lower in ["bulk", "containers"]:
            cargo_factor = 0.9  # Standardized handling
        
        total_port_time = base_port_time * infra_factor * labor_factor * cargo_factor
        return max(1, int(total_port_time))
    
    def get_regional_ports(self, region: str) -> List[Dict[str, Any]]:
        """Get all ports in a specific region"""
        return [port for port in self.ports.values() if port.get("region") == region]
    
    def get_country_ports(self, country: str) -> List[Dict[str, Any]]:
        """Get all ports in a specific country"""
        return [port for port in self.ports.values() if port.get("country") == country]
    
    def assess_port_security_risk(self, port_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess security risk factors for a specific port"""
        try:
            security_assessment = {
                "overall_security_level": port_info.get("security_level", "Unknown"),
                "labor_stability": port_info.get("labor_stability", "Unknown"),
                "infrastructure_quality": port_info.get("infrastructure", "Unknown"),
                "country": port_info.get("country", "Unknown"),
                "region": port_info.get("region", "Unknown")
            }
            
            # Calculate risk score based on factors
            risk_score = 5  # Base medium risk
            
            security_level = port_info.get("security_level", "Medium")
            if security_level == "Very High":
                risk_score -= 2
            elif security_level == "High":
                risk_score -= 1
            elif security_level == "Low":
                risk_score += 2
            elif security_level == "Very Low":
                risk_score += 3
            
            labor_stability = port_info.get("labor_stability", "Fair")
            if labor_stability == "Excellent":
                risk_score -= 1
            elif labor_stability == "Poor":
                risk_score += 2
            
            infrastructure = port_info.get("infrastructure", "Fair")
            if infrastructure == "Excellent":
                risk_score -= 1
            elif infrastructure == "Poor":
                risk_score += 1
            
            security_assessment["risk_score"] = max(1, min(risk_score, 10))
            
            return security_assessment
            
        except Exception as e:
            logger.error(f"Port security assessment failed: {str(e)}")
            return {
                "overall_security_level": "Unknown",
                "risk_score": 5,
                "error": str(e)
            }