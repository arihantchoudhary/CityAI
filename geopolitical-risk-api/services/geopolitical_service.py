"""
Geopolitical service for analyzing country risks, route security, and political factors
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, date
import asyncio

logger = logging.getLogger(__name__)


class GeopoliticalService:
    """Service for geopolitical risk assessment and route analysis"""
    
    def __init__(self):
        self.country_risk_cache = {}
        self.route_cache = {}
        
        # Initialize geopolitical data
        self._init_country_data()
        self._init_chokepoint_data()
        self._init_security_zones()
    
    def _init_country_data(self):
        """Initialize country risk data"""
        # This would typically come from external APIs or databases
        # For demo purposes, using static data with major shipping countries
        self.country_data = {
            "United States": {
                "political_stability": 8,
                "trade_freedom": 85,
                "corruption_level": "Low",
                "security_threat": "Low",
                "sanctions_status": "Sanctions issuer",
                "port_security": "High",
                "labor_conditions": "Stable",
                "regulatory_stability": "High",
                "region": "North America"
            },
            "China": {
                "political_stability": 7,
                "trade_freedom": 65,
                "corruption_level": "Medium",
                "security_threat": "Low-Medium",
                "sanctions_status": "Subject to some US sanctions",
                "port_security": "High",
                "labor_conditions": "Controlled",
                "regulatory_stability": "Medium",
                "region": "East Asia"
            },
            "Singapore": {
                "political_stability": 9,
                "trade_freedom": 95,
                "corruption_level": "Very Low",
                "security_threat": "Very Low",
                "sanctions_status": "None",
                "port_security": "Very High",
                "labor_conditions": "Excellent",
                "regulatory_stability": "Very High",
                "region": "Southeast Asia"
            },
            "United Kingdom": {
                "political_stability": 8,
                "trade_freedom": 82,
                "corruption_level": "Low",
                "security_threat": "Low",
                "sanctions_status": "Sanctions issuer",
                "port_security": "High",
                "labor_conditions": "Stable",
                "regulatory_stability": "High",
                "region": "Europe"
            },
            "Germany": {
                "political_stability": 8,
                "trade_freedom": 78,
                "corruption_level": "Low",
                "security_threat": "Low",
                "sanctions_status": "EU sanctions participant",
                "port_security": "High",
                "labor_conditions": "Good",
                "regulatory_stability": "High",
                "region": "Europe"
            },
            "South Korea": {
                "political_stability": 7,
                "trade_freedom": 75,
                "corruption_level": "Medium",
                "security_threat": "Medium (North Korea tensions)",
                "sanctions_status": "None",
                "port_security": "High",
                "labor_conditions": "Good",
                "regulatory_stability": "High",
                "region": "East Asia"
            },
            "Japan": {
                "political_stability": 8,
                "trade_freedom": 78,
                "corruption_level": "Low",
                "security_threat": "Low",
                "sanctions_status": "G7 sanctions participant",
                "port_security": "Very High",
                "labor_conditions": "Excellent",
                "regulatory_stability": "Very High",
                "region": "East Asia"
            },
            "Netherlands": {
                "political_stability": 8,
                "trade_freedom": 86,
                "corruption_level": "Very Low",
                "security_threat": "Low",
                "sanctions_status": "EU sanctions participant",
                "port_security": "Very High",
                "labor_conditions": "Excellent",
                "regulatory_stability": "Very High",
                "region": "Europe"
            },
            "United Arab Emirates": {
                "political_stability": 7,
                "trade_freedom": 82,
                "corruption_level": "Low",
                "security_threat": "Low-Medium",
                "sanctions_status": "None",
                "port_security": "High",
                "labor_conditions": "Good",
                "regulatory_stability": "High",
                "region": "Middle East"
            },
            "Iran": {
                "political_stability": 3,
                "trade_freedom": 45,
                "corruption_level": "High",
                "security_threat": "High",
                "sanctions_status": "Major international sanctions",
                "port_security": "Medium",
                "labor_conditions": "Poor",
                "regulatory_stability": "Low",
                "region": "Middle East"
            },
            "Russia": {
                "political_stability": 4,
                "trade_freedom": 50,
                "corruption_level": "High",
                "security_threat": "High",
                "sanctions_status": "Extensive international sanctions",
                "port_security": "Medium",
                "labor_conditions": "Poor",
                "regulatory_stability": "Low",
                "region": "Eastern Europe/Asia"
            },
            "Brazil": {
                "political_stability": 6,
                "trade_freedom": 68,
                "corruption_level": "Medium-High",
                "security_threat": "Medium",
                "sanctions_status": "None",
                "port_security": "Medium",
                "labor_conditions": "Fair",
                "regulatory_stability": "Medium",
                "region": "South America"
            },
            "India": {
                "political_stability": 6,
                "trade_freedom": 55,
                "corruption_level": "Medium-High",
                "security_threat": "Medium",
                "sanctions_status": "None",
                "port_security": "Medium",
                "labor_conditions": "Fair",
                "regulatory_stability": "Medium",
                "region": "South Asia"
            },
            "Australia": {
                "political_stability": 9,
                "trade_freedom": 82,
                "corruption_level": "Very Low",
                "security_threat": "Very Low",
                "sanctions_status": "Western sanctions participant",
                "port_security": "Very High",
                "labor_conditions": "Excellent",
                "regulatory_stability": "Very High",
                "region": "Oceania"
            }
        }
    
    def _init_chokepoint_data(self):
        """Initialize critical maritime chokepoints"""
        self.chokepoints = {
            "Suez Canal": {
                "description": "Critical passage between Mediterranean and Red Sea",
                "current_status": "Operational with potential for blockages",
                "risk_level": "Medium",
                "alternatives": "Cape of Good Hope (adds ~3,500 miles)",
                "security_concerns": ["Canal blockage", "Egyptian political stability", "Regional conflicts"]
            },
            "Strait of Hormuz": {
                "description": "Critical oil and gas transit point",
                "current_status": "High tension due to Iran-West relations",
                "risk_level": "High",
                "alternatives": "Limited alternatives for Persian Gulf cargo",
                "security_concerns": ["Iran military threats", "Naval incidents", "Oil price impacts"]
            },
            "Strait of Malacca": {
                "description": "Major Asia-Europe trade route",
                "current_status": "Generally stable with piracy concerns",
                "risk_level": "Medium",
                "alternatives": "Lombok Strait, Sunda Strait",
                "security_concerns": ["Piracy", "Singapore-Malaysia-Indonesia coordination", "Heavy traffic"]
            },
            "Panama Canal": {
                "description": "Critical Atlantic-Pacific connection",
                "current_status": "Operational with drought-related restrictions",
                "risk_level": "Low-Medium",
                "alternatives": "Cape Horn, US transcontinental rail",
                "security_concerns": ["Water level management", "Labor disputes", "Infrastructure maintenance"]
            },
            "Danish Straits": {
                "description": "Baltic Sea access points",
                "current_status": "Stable but monitored due to regional tensions",
                "risk_level": "Low-Medium",
                "alternatives": "Limited for Baltic traffic",
                "security_concerns": ["Russia-NATO tensions", "Environmental regulations", "Ice conditions"]
            },
            "Bab el-Mandeb": {
                "description": "Red Sea entrance, connects to Suez Canal",
                "current_status": "High risk due to Yemen conflict",
                "risk_level": "High",
                "alternatives": "Cape of Good Hope",
                "security_concerns": ["Yemen conflict", "Houthi attacks", "Saudi-Iran proxy war"]
            },
            "South China Sea": {
                "description": "Major Asian shipping lanes",
                "current_status": "Tense due to territorial disputes",
                "risk_level": "Medium-High",
                "alternatives": "Limited for intra-Asia trade",
                "security_concerns": ["China-US tensions", "Territorial disputes", "Military buildups"]
            }
        }
    
    def _init_security_zones(self):
        """Initialize high-risk maritime security zones"""
        self.security_zones = {
            "Gulf of Guinea": {
                "threat_type": "Piracy, kidnapping",
                "risk_level": "High",
                "affected_routes": ["West Africa - Europe/Americas"],
                "mitigation": "Armed guards, convoy systems"
            },
            "Somalia Coast": {
                "threat_type": "Piracy (historically)",
                "risk_level": "Medium (much improved)",
                "affected_routes": ["Red Sea - Indian Ocean"],
                "mitigation": "International naval patrols"
            },
            "Persian Gulf": {
                "threat_type": "Military incidents, sanctions enforcement",
                "risk_level": "High",
                "affected_routes": ["Gulf states - Global"],
                "mitigation": "Flag state coordination, escort services"
            },
            "Black Sea": {
                "threat_type": "Armed conflict, naval blockades",
                "risk_level": "Very High",
                "affected_routes": ["Ukraine, Russia - Global"],
                "mitigation": "Conflict zone avoidance"
            },
            "Taiwan Strait": {
                "threat_type": "Military tensions, potential blockade",
                "risk_level": "Medium-High",
                "affected_routes": ["Northeast Asia"],
                "mitigation": "Alternative routing, diplomatic monitoring"
            }
        }
    
    async def assess_country_risk(self, country: str, goods_type: str = None) -> Dict[str, Any]:
        """Assess geopolitical risk for a specific country"""
        try:
            # Check cache first
            cache_key = f"{country}_{goods_type or 'general'}"
            if cache_key in self.country_risk_cache:
                cached_time = self.country_risk_cache[cache_key].get('cached_at')
                if cached_time and (datetime.utcnow() - cached_time).seconds < 3600:  # 1 hour cache
                    return self.country_risk_cache[cache_key]['data']
            
            # Get base country data
            base_data = self.country_data.get(country, self._get_default_country_data(country))
            
            # Enhance with goods-specific analysis
            enhanced_data = await self._enhance_country_risk_for_goods(base_data, country, goods_type)
            
            # Cache the result
            self.country_risk_cache[cache_key] = {
                'data': enhanced_data,
                'cached_at': datetime.utcnow()
            }
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Country risk assessment failed for {country}: {str(e)}")
            return self._get_default_country_data(country)
    
    async def analyze_route(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any], 
        goods_type: str
    ) -> Dict[str, Any]:
        """Analyze route-specific risks including chokepoints and security zones"""
        try:
            departure_country = departure_info.get('country', 'Unknown')
            destination_country = destination_info.get('country', 'Unknown')
            
            # Determine likely shipping route and chokepoints
            route_chokepoints = self._identify_route_chokepoints(departure_info, destination_info)
            
            # Identify security zones along the route
            security_zones = self._identify_security_zones(departure_info, destination_info)
            
            # Calculate route characteristics
            distance_km = self._estimate_route_distance(departure_info, destination_info)
            travel_days = self._estimate_travel_time(distance_km, goods_type)
            
            # Assess seasonal factors
            seasonal_factors = self._assess_seasonal_factors(departure_info, destination_info)
            
            # Check for alternative routes
            alternative_routes = self._identify_alternative_routes(departure_info, destination_info)
            
            route_analysis = {
                "departure_country": departure_country,
                "destination_country": destination_country,
                "distance_km": distance_km,
                "travel_days": travel_days,
                "chokepoints": route_chokepoints,
                "security_zones": security_zones,
                "seasonal_factors": seasonal_factors,
                "alternative_routes": alternative_routes,
                "shipping_lanes": self._identify_shipping_lanes(departure_info, destination_info),
                "goods_specific_risks": self._assess_goods_route_risks(goods_type, route_chokepoints)
            }
            
            return route_analysis
            
        except Exception as e:
            logger.error(f"Route analysis failed: {str(e)}")
            return self._get_fallback_route_analysis(departure_info, destination_info)
    
    def _get_default_country_data(self, country: str) -> Dict[str, Any]:
        """Provide default risk assessment for unknown countries"""
        return {
            "country": country,
            "political_stability": 5,  # Neutral
            "trade_freedom": 60,
            "corruption_level": "Unknown",
            "security_threat": "Unknown",
            "sanctions_status": "Unknown",
            "port_security": "Unknown",
            "labor_conditions": "Unknown",
            "regulatory_stability": "Unknown",
            "cargo_restrictions": "Standard international regulations apply"
        }
    
    async def _enhance_country_risk_for_goods(
        self, 
        base_data: Dict[str, Any], 
        country: str, 
        goods_type: str
    ) -> Dict[str, Any]:
        """Enhance country risk assessment based on specific goods type"""
        enhanced = base_data.copy()
        enhanced["country"] = country
        
        if goods_type:
            # Add goods-specific risk factors
            cargo_restrictions = self._assess_cargo_restrictions(country, goods_type)
            enhanced["cargo_restrictions"] = cargo_restrictions
            
            # Adjust risk scores based on goods sensitivity
            if goods_type.lower() in ['electronics', 'technology', 'semiconductors']:
                if country in ['China', 'Russia', 'Iran', 'North Korea']:
                    enhanced["cargo_restrictions"] += " HIGH RISK: Technology transfer restrictions apply."
                    enhanced["regulatory_stability"] = "Low (tech restrictions)"
            
            elif goods_type.lower() in ['military', 'defense', 'weapons']:
                enhanced["cargo_restrictions"] += " CRITICAL: Military/dual-use export controls apply."
                enhanced["regulatory_stability"] = "High scrutiny required"
            
            elif goods_type.lower() in ['energy', 'oil', 'gas']:
                if country in ['Russia', 'Iran']:
                    enhanced["cargo_restrictions"] += " SANCTIONS: Energy sector sanctions in effect."
                    enhanced["sanctions_status"] = "Energy sanctions active"
        
        return enhanced
    
    def _assess_cargo_restrictions(self, country: str, goods_type: str) -> str:
        """Assess cargo-specific restrictions for a country"""
        restrictions = []
        
        # Technology restrictions
        if goods_type.lower() in ['electronics', 'technology', 'semiconductors', 'software']:
            if country in ['China', 'Russia', 'Iran', 'North Korea']:
                restrictions.append("Technology export controls")
            if country in ['China']:
                restrictions.append("CFIUS review may be required")
        
        # Dual-use goods
        if goods_type.lower() in ['chemicals', 'materials', 'machinery']:
            restrictions.append("Dual-use export license may be required")
        
        # Sanctioned countries
        if country in ['Iran', 'Russia', 'North Korea']:
            restrictions.append("Comprehensive sanctions apply")
        
        return "; ".join(restrictions) if restrictions else "Standard regulations"
    
    def _identify_route_chokepoints(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> List[str]:
        """Identify likely chokepoints for a shipping route"""
        chokepoints = []
        
        dept_region = self._get_region_from_country(departure_info.get('country', ''))
        dest_region = self._get_region_from_country(destination_info.get('country', ''))
        
        # Europe to/from Asia routes
        if ('Europe' in dept_region and 'Asia' in dest_region) or ('Asia' in dept_region and 'Europe' in dest_region):
            chokepoints.extend(["Suez Canal", "Strait of Malacca"])
        
        # Middle East routes
        if 'Middle East' in dept_region or 'Middle East' in dest_region:
            chokepoints.extend(["Strait of Hormuz", "Bab el-Mandeb"])
        
        # Pacific routes
        if 'Americas' in dept_region and 'Asia' in dest_region:
            chokepoints.append("Panama Canal")
        
        # South China Sea routes
        if dept_region == 'East Asia' or dest_region == 'East Asia':
            chokepoints.append("South China Sea")
        
        return list(set(chokepoints))  # Remove duplicates
    
    def _identify_security_zones(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> List[str]:
        """Identify security risk zones along the route"""
        zones = []
        
        dept_region = self._get_region_from_country(departure_info.get('country', ''))
        dest_region = self._get_region_from_country(destination_info.get('country', ''))
        
        # West Africa routes
        if 'Africa' in dept_region or 'Africa' in dest_region:
            zones.append("Gulf of Guinea")
        
        # Middle East routes
        if 'Middle East' in dept_region or 'Middle East' in dest_region:
            zones.extend(["Persian Gulf", "Somalia Coast"])
        
        # Black Sea routes
        if departure_info.get('country') in ['Ukraine', 'Russia'] or destination_info.get('country') in ['Ukraine', 'Russia']:
            zones.append("Black Sea")
        
        # Taiwan Strait
        if departure_info.get('country') in ['Taiwan', 'China'] or destination_info.get('country') in ['Taiwan', 'China']:
            zones.append("Taiwan Strait")
        
        return list(set(zones))
    
    def _get_region_from_country(self, country: str) -> str:
        """Get region classification for a country"""
        region_map = {
            'United States': 'North America',
            'Canada': 'North America',
            'Mexico': 'North America',
            'China': 'East Asia',
            'Japan': 'East Asia',
            'South Korea': 'East Asia',
            'Singapore': 'Southeast Asia',
            'Malaysia': 'Southeast Asia',
            'Thailand': 'Southeast Asia',
            'India': 'South Asia',
            'United Arab Emirates': 'Middle East',
            'Saudi Arabia': 'Middle East',
            'Iran': 'Middle East',
            'United Kingdom': 'Europe',
            'Germany': 'Europe',
            'Netherlands': 'Europe',
            'France': 'Europe',
            'Russia': 'Eastern Europe/Asia',
            'Brazil': 'South America',
            'Australia': 'Oceania'
        }
        return region_map.get(country, 'Unknown')
    
    def _estimate_route_distance(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> int:
        """Estimate shipping distance in kilometers"""
        # This is a simplified estimation - in production, use proper route calculation
        dept_lat = departure_info.get('latitude', 0)
        dept_lon = departure_info.get('longitude', 0)
        dest_lat = destination_info.get('latitude', 0)
        dest_lon = destination_info.get('longitude', 0)
        
        # Haversine formula for great circle distance
        import math
        
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(dept_lat)
        lat2_rad = math.radians(dest_lat)
        delta_lat = math.radians(dest_lat - dept_lat)
        delta_lon = math.radians(dest_lon - dept_lon)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        # Add routing factor (actual shipping routes are longer than great circle)
        routing_factor = 1.3  # 30% longer for realistic routing
        return int(distance * routing_factor)
    
    def _estimate_travel_time(self, distance_km: int, goods_type: str) -> int:
        """Estimate travel time in days"""
        # Average container ship speed: 20-25 knots, use 22 knots average
        # 1 knot = 1.852 km/h
        avg_speed_kmh = 22 * 1.852  # ~40.7 km/h
        
        # Factor in port time, weather delays, etc.
        efficiency_factor = 0.7  # 70% efficiency accounting for delays
        
        travel_hours = distance_km / (avg_speed_kmh * efficiency_factor)
        travel_days = max(1, int(travel_hours / 24))
        
        return travel_days
    
    def _assess_seasonal_factors(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> str:
        """Assess seasonal factors affecting the route"""
        current_month = datetime.utcnow().month
        
        factors = []
        
        # Monsoon season (June-September)
        if 6 <= current_month <= 9:
            if 'Asia' in self._get_region_from_country(departure_info.get('country', '')):
                factors.append("Monsoon season in Asia")
        
        # Hurricane season (June-November)
        if 6 <= current_month <= 11:
            if 'Americas' in self._get_region_from_country(departure_info.get('country', '')):
                factors.append("Hurricane season in Atlantic/Pacific")
        
        # Winter ice conditions (December-March)
        if current_month in [12, 1, 2, 3]:
            if departure_info.get('country') in ['Russia', 'Canada'] or destination_info.get('country') in ['Russia', 'Canada']:
                factors.append("Winter ice conditions in northern routes")
        
        return "; ".join(factors) if factors else "No significant seasonal factors"
    
    def _identify_shipping_lanes(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> str:
        """Identify primary shipping lanes for the route"""
        dept_region = self._get_region_from_country(departure_info.get('country', ''))
        dest_region = self._get_region_from_country(destination_info.get('country', ''))
        
        if 'Europe' in dept_region and 'Asia' in dest_region:
            return "Europe-Asia main line (via Suez Canal)"
        elif 'Americas' in dept_region and 'Asia' in dest_region:
            return "Trans-Pacific main line"
        elif 'Americas' in dept_region and 'Europe' in dest_region:
            return "Trans-Atlantic main line"
        else:
            return "Regional feeder routes"
    
    def _identify_alternative_routes(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> str:
        """Identify alternative routing options"""
        chokepoints = self._identify_route_chokepoints(departure_info, destination_info)
        
        alternatives = []
        if "Suez Canal" in chokepoints:
            alternatives.append("Cape of Good Hope (adds ~2 weeks)")
        if "Panama Canal" in chokepoints:
            alternatives.append("Cape Horn or US land bridge")
        if "Strait of Malacca" in chokepoints:
            alternatives.append("Lombok Strait or Sunda Strait")
        
        return "; ".join(alternatives) if alternatives else "Limited alternative routes"
    
    def _assess_goods_route_risks(self, goods_type: str, chokepoints: List[str]) -> str:
        """Assess goods-specific risks for the route"""
        risks = []
        
        if goods_type.lower() in ['electronics', 'technology']:
            if "South China Sea" in chokepoints:
                risks.append("Technology transfer scrutiny in disputed waters")
        
        if goods_type.lower() in ['energy', 'oil', 'gas']:
            if "Strait of Hormuz" in chokepoints:
                risks.append("Energy chokepoint vulnerability")
        
        if goods_type.lower() in ['food', 'agriculture']:
            risks.append("Temperature-sensitive cargo considerations")
        
        return "; ".join(risks) if risks else "Standard cargo handling protocols"
    
    def _get_fallback_route_analysis(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide fallback route analysis if main analysis fails"""
        return {
            "departure_country": departure_info.get('country', 'Unknown'),
            "destination_country": destination_info.get('country', 'Unknown'),
            "distance_km": 10000,  # Default estimate
            "travel_days": 14,  # Default estimate
            "chokepoints": ["Analysis unavailable"],
            "security_zones": ["Analysis unavailable"],
            "seasonal_factors": "Unable to assess",
            "alternative_routes": "Analysis unavailable",
            "shipping_lanes": "Standard commercial routes",
            "goods_specific_risks": "Standard protocols apply"
        }
    
    async def fallback_risk_assessment(
        self,
        departure_country_risk: Dict[str, Any],
        destination_country_risk: Dict[str, Any],
        route_analysis: Dict[str, Any],
        news_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide fallback risk assessment when LLM fails"""
        try:
            risk_factors = []
            risk_score = 1
            
            # Assess country stability
            dept_stability = departure_country_risk.get('political_stability', 5)
            dest_stability = destination_country_risk.get('political_stability', 5)
            
            if dept_stability <= 3 or dest_stability <= 3:
                risk_factors.append("Political instability concerns")
                risk_score += 4
            elif dept_stability <= 5 or dest_stability <= 5:
                risk_factors.append("Moderate political concerns")
                risk_score += 2
            
            # Check sanctions
            dept_sanctions = departure_country_risk.get('sanctions_status', '')
            dest_sanctions = destination_country_risk.get('sanctions_status', '')
            
            if 'sanctions' in dept_sanctions.lower() or 'sanctions' in dest_sanctions.lower():
                risk_factors.append("Sanctions complications")
                risk_score += 3
            
            # Assess chokepoints
            chokepoints = route_analysis.get('chokepoints', [])
            high_risk_points = ['Strait of Hormuz', 'Bab el-Mandeb', 'South China Sea']
            
            for point in chokepoints:
                if any(hrp in point for hrp in high_risk_points):
                    risk_factors.append(f"High-risk chokepoint: {point}")
                    risk_score += 2
                    break
            
            # Check security zones
            security_zones = route_analysis.get('security_zones', [])
            if security_zones:
                risk_factors.append("Security risk zones on route")
                risk_score += 1
            
            # Recent events impact
            events = news_analysis.get('events', [])
            high_impact_events = [e for e in events if e.get('relevance_score', 0) >= 7]
            if high_impact_events:
                risk_factors.append("High-impact recent events")
                risk_score += 2
            
            risk_score = min(risk_score, 10)
            
            if not risk_factors:
                description = "No major geopolitical risks identified. Standard security protocols recommended."
                summary = "Low geopolitical risk environment for this route."
            else:
                description = f"Geopolitical risks identified: {', '.join(risk_factors)}. Enhanced security measures and monitoring recommended."
                summary = f"Elevated risk due to: {', '.join(risk_factors[:3])}."
            
            return {
                "risk_score": risk_score,
                "risk_description": description,
                "geopolitical_summary": summary
            }
            
        except Exception as e:
            logger.error(f"Fallback assessment failed: {str(e)}")
            return {
                "risk_score": 5,
                "risk_description": "Unable to assess geopolitical risk due to system error. Manual review recommended.",
                "geopolitical_summary": "Risk assessment unavailable - proceed with enhanced caution."
            }