"""
Weather service for fetching weather data from WeatherAPI.com
"""

import aiohttp
import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
import json

from config import get_settings
from models import WeatherData


logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data from WeatherAPI.com"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.weatherapi_base_url
        self.api_key = self.settings.weatherapi_key
        self.timeout = aiohttp.ClientTimeout(total=self.settings.weather_request_timeout)
        
    async def health_check(self) -> str:
        """Check if the weather API is accessible"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Test with a simple current weather request
                url = f"{self.base_url}/current.json"
                params = {
                    'key': self.api_key,
                    'q': '40.7128,-74.0060',  # NYC coordinates
                    'aqi': 'no'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return "healthy"
                    else:
                        return f"unhealthy (status: {response.status})"
                        
        except Exception as e:
            logger.error(f"Weather API health check failed: {str(e)}")
            return f"unhealthy (error: {str(e)})"
    
    async def get_weather_data(
        self, 
        latitude: float, 
        longitude: float, 
        target_date: date
    ) -> WeatherData:
        """
        Fetch weather data for a specific location and date
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            target_date: Date for which to fetch weather data
            
        Returns:
            WeatherData: Structured weather information
            
        Raises:
            Exception: If weather data cannot be fetched
        """
        try:
            # Determine if we need current, historical, or forecast data
            today = date.today()
            is_future = target_date > today
            is_recent_past = target_date >= (today - timedelta(days=7))
            
            if is_future:
                # Use forecast API (up to 14 days in advance)
                days_ahead = (target_date - today).days
                if days_ahead > 14:
                    logger.warning(f"Date too far in future ({days_ahead} days), using 14-day forecast")
                    days_ahead = 14
                    
                weather_data = await self._get_forecast_weather(latitude, longitude, days_ahead)
            elif is_recent_past:
                # Use history API (last 7 days available in free tier)
                weather_data = await self._get_historical_weather(latitude, longitude, target_date)
            else:
                # Date too far in past, use current weather as fallback
                logger.warning(f"Date too far in past, using current weather as approximation")
                weather_data = await self._get_current_weather(latitude, longitude)
                
            return weather_data
            
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {str(e)}")
            raise Exception(f"Weather data unavailable: {str(e)}")
    
    async def _get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Fetch current weather data"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': f"{latitude},{longitude}",
                'aqi': 'no'
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Weather API error: {response.status} - {error_text}")
                
                data = await response.json()
                return self._parse_weather_data(data['current'], is_forecast=False)
    
    async def _get_forecast_weather(
        self, 
        latitude: float, 
        longitude: float, 
        days_ahead: int
    ) -> WeatherData:
        """Fetch forecast weather data"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': f"{latitude},{longitude}",
                'days': min(days_ahead + 1, 14),  # Include today + future days
                'aqi': 'no',
                'alerts': 'no'
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Weather API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Get the forecast for the target day (index based on days ahead)
                forecast_days = data['forecast']['forecastday']
                if days_ahead < len(forecast_days):
                    forecast_day = forecast_days[days_ahead]['day']
                    return self._parse_forecast_data(forecast_day, is_forecast=True)
                else:
                    # Fallback to last available day
                    forecast_day = forecast_days[-1]['day']
                    return self._parse_forecast_data(forecast_day, is_forecast=True)
    
    async def _get_historical_weather(
        self, 
        latitude: float, 
        longitude: float, 
        target_date: date
    ) -> WeatherData:
        """Fetch historical weather data"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            url = f"{self.base_url}/history.json"
            params = {
                'key': self.api_key,
                'q': f"{latitude},{longitude}",
                'dt': target_date.strftime('%Y-%m-%d')
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Weather API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Use the day's average data from historical records
                day_data = data['forecast']['forecastday'][0]['day']
                return self._parse_forecast_data(day_data, is_forecast=False)
    
    def _parse_weather_data(self, weather_data: Dict[str, Any], is_forecast: bool) -> WeatherData:
        """Parse current weather data from API response"""
        return WeatherData(
            temperature_c=weather_data.get('temp_c', 0.0),
            feels_like_c=weather_data.get('feelslike_c', weather_data.get('temp_c', 0.0)),
            humidity=weather_data.get('humidity', 0),
            wind_speed_kph=weather_data.get('wind_kph', 0.0),
            wind_direction=weather_data.get('wind_dir', 'N'),
            wind_degree=weather_data.get('wind_degree', 0),
            pressure_mb=weather_data.get('pressure_mb', 1013.25),
            visibility_km=weather_data.get('vis_km', 10.0),
            uv_index=weather_data.get('uv', 0.0),
            condition=weather_data.get('condition', {}).get('text', 'Unknown'),
            condition_code=weather_data.get('condition', {}).get('code', 1000),
            precipitation_mm=weather_data.get('precip_mm', 0.0),
            is_forecast=is_forecast,
            data_timestamp=datetime.utcnow()
        )
    
    def _parse_forecast_data(self, day_data: Dict[str, Any], is_forecast: bool) -> WeatherData:
        """Parse forecast/historical day data from API response"""
        return WeatherData(
            temperature_c=day_data.get('avgtemp_c', 0.0),
            feels_like_c=day_data.get('avgtemp_c', 0.0),  # Forecast doesn't have feels_like
            humidity=day_data.get('avghumidity', 0),
            wind_speed_kph=day_data.get('maxwind_kph', 0.0),
            wind_direction='N',  # Day forecast doesn't include direction
            wind_degree=0,
            pressure_mb=1013.25,  # Not available in day forecast
            visibility_km=day_data.get('avgvis_km', 10.0),
            uv_index=day_data.get('uv', 0.0),
            condition=day_data.get('condition', {}).get('text', 'Unknown'),
            condition_code=day_data.get('condition', {}).get('code', 1000),
            precipitation_mm=day_data.get('totalprecip_mm', 0.0),
            is_forecast=is_forecast,
            data_timestamp=datetime.utcnow()
        )
    
    async def get_marine_conditions(
        self, 
        latitude: float, 
        longitude: float, 
        target_date: date
    ) -> Dict[str, Any]:
        """
        Get marine-specific weather conditions
        
        Note: WeatherAPI.com free tier has limited marine data.
        This method attempts to gather what's available and estimates marine conditions.
        """
        try:
            # Get basic weather data first
            weather_data = await self.get_weather_data(latitude, longitude, target_date)
            
            # Estimate marine conditions based on weather data
            marine_conditions = {
                'wind_speed_kph': weather_data.wind_speed_kph,
                'wind_direction': weather_data.wind_direction,
                'visibility_km': weather_data.visibility_km,
                'precipitation_mm': weather_data.precipitation_mm,
                'wave_height_estimate_m': self._estimate_wave_height(weather_data.wind_speed_kph),
                'sea_state': self._estimate_sea_state(weather_data.wind_speed_kph),
                'weather_severity': self._assess_weather_severity(weather_data)
            }
            
            return marine_conditions
            
        except Exception as e:
            logger.error(f"Failed to get marine conditions: {str(e)}")
            return {
                'error': str(e),
                'fallback_used': True
            }
    
    def _estimate_wave_height(self, wind_speed_kph: float) -> float:
        """Estimate wave height based on wind speed (simplified calculation)"""
        # Rough approximation: wave height in meters based on wind speed
        if wind_speed_kph < 10:
            return 0.3  # Calm
        elif wind_speed_kph < 20:
            return 0.8  # Light breeze
        elif wind_speed_kph < 30:
            return 1.5  # Moderate breeze
        elif wind_speed_kph < 40:
            return 2.5  # Strong breeze
        elif wind_speed_kph < 60:
            return 4.0  # Gale
        else:
            return 6.0  # Storm conditions
    
    def _estimate_sea_state(self, wind_speed_kph: float) -> str:
        """Estimate sea state description based on wind speed"""
        if wind_speed_kph < 10:
            return "Calm (slight waves)"
        elif wind_speed_kph < 20:
            return "Smooth (light waves)"
        elif wind_speed_kph < 30:
            return "Moderate (regular waves)"
        elif wind_speed_kph < 40:
            return "Rough (larger waves)"
        elif wind_speed_kph < 60:
            return "Very rough (high waves)"
        else:
            return "Severe (very high waves)"
    
    def _assess_weather_severity(self, weather_data: WeatherData) -> str:
        """Assess overall weather severity for shipping"""
        severity_score = 0
        
        # Wind speed factor
        if weather_data.wind_speed_kph > 60:
            severity_score += 4
        elif weather_data.wind_speed_kph > 40:
            severity_score += 3
        elif weather_data.wind_speed_kph > 25:
            severity_score += 2
        elif weather_data.wind_speed_kph > 15:
            severity_score += 1
        
        # Visibility factor
        if weather_data.visibility_km < 1:
            severity_score += 3
        elif weather_data.visibility_km < 5:
            severity_score += 2
        elif weather_data.visibility_km < 10:
            severity_score += 1
        
        # Precipitation factor
        if weather_data.precipitation_mm > 20:
            severity_score += 2
        elif weather_data.precipitation_mm > 5:
            severity_score += 1
        
        # Determine severity level
        if severity_score >= 7:
            return "SEVERE"
        elif severity_score >= 5:
            return "HIGH"
        elif severity_score >= 3:
            return "MODERATE"
        elif severity_score >= 1:
            return "LOW"
        else:
            return "MINIMAL"