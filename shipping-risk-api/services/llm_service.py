"""
LLM service for AI-powered shipping risk assessment using OpenAI
"""

from openai import AsyncOpenAI
import asyncio
import logging
import json
from datetime import date
from typing import Dict, Any

from config import get_settings
from models import WeatherData


logger = logging.getLogger(__name__)


class LLMService:
    """Service for AI-powered risk assessment using OpenAI"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model
        self.temperature = self.settings.openai_temperature
        self.max_tokens = self.settings.openai_max_tokens
        
    async def health_check(self) -> str:
        """Check if OpenAI API is accessible"""
        try:
            # Test with a simple completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10
            )
            
            if response and response.choices:
                return "healthy"
            else:
                return "unhealthy (no response)"
                
        except Exception as e:
            logger.error(f"OpenAI API health check failed: {str(e)}")
            return f"unhealthy (error: {str(e)})"
    
    async def assess_shipping_risk(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: date,
        carrier_name: str,
        goods_type: str,
        departure_weather: WeatherData,
        destination_weather: WeatherData,
        travel_days: int
    ) -> Dict[str, Any]:
        """
        Use AI to assess shipping risk based on weather and route data
        
        Args:
            departure_port: Name of departure port
            destination_port: Name of destination port
            departure_date: Date of departure
            carrier_name: Shipping carrier name
            goods_type: Type of goods being shipped
            departure_weather: Weather data for departure location
            destination_weather: Weather data for destination location
            travel_days: Estimated travel time in days
            
        Returns:
            Dict containing risk_score, risk_description, and weather_summary
        """
        try:
            # Construct detailed prompt for risk assessment
            prompt = self._build_risk_assessment_prompt(
                departure_port=departure_port,
                destination_port=destination_port,
                departure_date=departure_date,
                carrier_name=carrier_name,
                goods_type=goods_type,
                departure_weather=departure_weather,
                destination_weather=destination_weather,
                travel_days=travel_days
            )
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.settings.openai_request_timeout
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error(f"LLM risk assessment failed: {str(e)}")
            # Return fallback assessment
            return self._fallback_risk_assessment(departure_weather, destination_weather)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role and behavior"""
        return """You are an expert maritime risk analyst with deep knowledge of:
- Weather patterns and their impact on shipping operations
- Maritime safety protocols and risk factors
- Cargo handling and protection requirements
- International shipping routes and common hazards
- Seasonal weather patterns across global shipping lanes

Your task is to analyze shipping routes and provide accurate risk assessments based on weather conditions, cargo type, route characteristics, and operational factors.

You must respond in a specific JSON format with:
1. A risk score from 1-10 (1 = minimal risk, 10 = extreme risk)
2. A detailed risk description explaining your reasoning
3. A weather summary highlighting key conditions

Consider these factors in your assessment:
- Wind speed and direction (affecting vessel stability and fuel consumption)
- Wave height and sea state (cargo security, vessel stress)
- Visibility conditions (navigation safety)
- Precipitation (deck operations, cargo protection)
- Temperature extremes (cargo condition, crew safety)
- Seasonal weather patterns for the route
- Cargo sensitivity to weather conditions
- Port conditions and handling capabilities

Be conservative in your risk assessment - err on the side of caution for cargo and crew safety."""

    def _build_risk_assessment_prompt(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: date,
        carrier_name: str,
        goods_type: str,
        departure_weather: WeatherData,
        destination_weather: WeatherData,
        travel_days: int
    ) -> str:
        """Build a comprehensive prompt for risk assessment"""
        
        # Format weather data for the prompt
        departure_weather_text = self._format_weather_for_prompt(departure_weather, "departure")
        destination_weather_text = self._format_weather_for_prompt(destination_weather, "destination")
        
        prompt = f"""Please assess the weather-related shipping risk for this cargo shipment:

ROUTE INFORMATION:
- Departure Port: {departure_port}
- Destination Port: {destination_port}
- Departure Date: {departure_date.strftime('%Y-%m-%d')}
- Estimated Travel Time: {travel_days} days
- Carrier: {carrier_name}
- Cargo Type: {goods_type}

WEATHER CONDITIONS:

Departure Port Weather:
{departure_weather_text}

Destination Port Weather:
{destination_weather_text}

ASSESSMENT REQUIREMENTS:
Please analyze this shipping scenario and provide a risk assessment considering:

1. Weather impact on vessel operations and cargo safety
2. Seasonal weather patterns for this route and time of year
3. Specific risks for the cargo type ({goods_type})
4. Port conditions for loading/unloading operations
5. Overall route safety and potential delays

Respond in JSON format:
{{
  "risk_score": <integer 1-10>,
  "risk_description": "<detailed explanation of risks and reasoning>",
  "weather_summary": "<summary of key weather conditions affecting the route>"
}}

Focus on practical shipping risks and be specific about weather-related concerns."""

        return prompt
    
    def _format_weather_for_prompt(self, weather: WeatherData, location: str) -> str:
        """Format weather data for inclusion in the AI prompt"""
        forecast_type = "Forecast" if weather.is_forecast else "Current/Historical"
        
        return f"""- Condition: {weather.condition}
- Temperature: {weather.temperature_c}°C (feels like {weather.feels_like_c}°C)
- Wind: {weather.wind_speed_kph} km/h from {weather.wind_direction} ({weather.wind_degree}°)
- Humidity: {weather.humidity}%
- Pressure: {weather.pressure_mb} mb
- Visibility: {weather.visibility_km} km
- Precipitation: {weather.precipitation_mm} mm
- UV Index: {weather.uv_index}
- Data Type: {forecast_type}"""

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data"""
        try:
            # Try to find JSON in the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Validate the response structure
                if self._validate_ai_response(parsed_response):
                    return parsed_response
                else:
                    raise ValueError("Invalid response structure")
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            logger.error(f"AI response was: {ai_response}")
            
            # Attempt to extract information manually
            return self._extract_fallback_response(ai_response)
    
    def _validate_ai_response(self, response: Dict[str, Any]) -> bool:
        """Validate that the AI response has the required structure"""
        required_fields = ["risk_score", "risk_description", "weather_summary"]
        
        if not all(field in response for field in required_fields):
            return False
            
        # Validate risk score is an integer between 1-10
        risk_score = response.get("risk_score")
        if not isinstance(risk_score, int) or not 1 <= risk_score <= 10:
            return False
            
        # Validate text fields are non-empty strings
        for field in ["risk_description", "weather_summary"]:
            if not isinstance(response.get(field), str) or len(response[field].strip()) < 10:
                return False
                
        return True
    
    def _extract_fallback_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract risk assessment info when JSON parsing fails"""
        # Simple keyword-based extraction as fallback
        risk_score = 5  # Default medium risk
        
        # Look for risk indicators in the response
        response_lower = ai_response.lower()
        
        if any(word in response_lower for word in ["severe", "extreme", "dangerous", "critical"]):
            risk_score = 9
        elif any(word in response_lower for word in ["high", "significant", "major"]):
            risk_score = 7
        elif any(word in response_lower for word in ["moderate", "medium"]):
            risk_score = 5
        elif any(word in response_lower for word in ["low", "minor", "slight"]):
            risk_score = 3
        elif any(word in response_lower for word in ["minimal", "negligible"]):
            risk_score = 1
        
        return {
            "risk_score": risk_score,
            "risk_description": f"AI assessment parsing failed. Raw response: {ai_response[:500]}...",
            "weather_summary": "Weather data analysis incomplete due to parsing error."
        }
    
    def _fallback_risk_assessment(
        self, 
        departure_weather: WeatherData, 
        destination_weather: WeatherData
    ) -> Dict[str, Any]:
        """Provide a basic risk assessment when AI service fails"""
        
        # Simple rule-based assessment as fallback
        risk_factors = []
        risk_score = 1
        
        # Check departure weather
        if departure_weather.wind_speed_kph > 50:
            risk_factors.append("High winds at departure")
            risk_score += 3
        elif departure_weather.wind_speed_kph > 30:
            risk_factors.append("Moderate winds at departure")
            risk_score += 2
            
        if departure_weather.visibility_km < 5:
            risk_factors.append("Poor visibility at departure")
            risk_score += 2
            
        if departure_weather.precipitation_mm > 10:
            risk_factors.append("Heavy precipitation at departure")
            risk_score += 1
        
        # Check destination weather
        if destination_weather.wind_speed_kph > 50:
            risk_factors.append("High winds at destination")
            risk_score += 3
        elif destination_weather.wind_speed_kph > 30:
            risk_factors.append("Moderate winds at destination")
            risk_score += 2
            
        if destination_weather.visibility_km < 5:
            risk_factors.append("Poor visibility at destination")
            risk_score += 2
            
        if destination_weather.precipitation_mm > 10:
            risk_factors.append("Heavy precipitation at destination")
            risk_score += 1
        
        # Cap the risk score at 10
        risk_score = min(risk_score, 10)
        
        # Generate description
        if not risk_factors:
            description = "Weather conditions appear favorable for shipping operations. Standard operational precautions recommended."
        else:
            description = f"Weather-related concerns identified: {', '.join(risk_factors)}. Enhanced monitoring and precautions recommended."
        
        weather_summary = f"Departure: {departure_weather.condition}, {departure_weather.wind_speed_kph} km/h winds. Destination: {destination_weather.condition}, {destination_weather.wind_speed_kph} km/h winds."
        
        return {
            "risk_score": risk_score,
            "risk_description": f"[Fallback Assessment] {description}",
            "weather_summary": weather_summary
        }