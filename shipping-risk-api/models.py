"""
Pydantic models for request/response validation and serialization
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, Dict, Any
import re


class ShippingRiskRequest(BaseModel):
    """Request model for shipping risk assessment"""
    
    departure_port: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Name of the departure port",
        example="Port of Los Angeles"
    )
    destination_port: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Name of the destination port",
        example="Port of Shanghai"
    )
    departure_date: date = Field(
        ...,
        description="Date of departure (YYYY-MM-DD)",
        example="2025-06-15"
    )
    carrier_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Name of the shipping carrier",
        example="COSCO Shipping"
    )
    goods_type: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Type of goods being shipped",
        example="electronics"
    )
    
    @validator('departure_date')
    def validate_departure_date(cls, v):
        """Ensure departure date is not in the past"""
        if v < date.today():
            raise ValueError('Departure date cannot be in the past')
        # Limit to reasonable future (1 year)
        if (v - date.today()).days > 365:
            raise ValueError('Departure date cannot be more than 1 year in the future')
        return v
    
    @validator('departure_port', 'destination_port')
    def validate_port_names(cls, v):
        """Basic validation for port names"""
        # Remove extra whitespace
        v = v.strip()
        if not v:
            raise ValueError('Port name cannot be empty')
        # Check for reasonable characters (letters, numbers, spaces, hyphens)
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError('Port name contains invalid characters')
        return v
    
    @validator('carrier_name', 'goods_type')
    def validate_text_fields(cls, v):
        """Basic validation for text fields"""
        v = v.strip()
        if not v:
            raise ValueError('Field cannot be empty')
        return v


class WeatherData(BaseModel):
    """Weather data structure"""
    
    temperature_c: float = Field(description="Temperature in Celsius")
    feels_like_c: float = Field(description="Feels like temperature in Celsius")
    humidity: int = Field(description="Humidity percentage")
    wind_speed_kph: float = Field(description="Wind speed in km/h")
    wind_direction: str = Field(description="Wind direction")
    wind_degree: int = Field(description="Wind direction in degrees")
    pressure_mb: float = Field(description="Pressure in millibars")
    visibility_km: float = Field(description="Visibility in kilometers")
    uv_index: float = Field(description="UV index")
    condition: str = Field(description="Weather condition description")
    condition_code: int = Field(description="Weather condition code")
    precipitation_mm: float = Field(description="Precipitation in millimeters")
    
    # Marine-specific data (if available)
    wave_height_m: Optional[float] = Field(None, description="Wave height in meters")
    swell_height_m: Optional[float] = Field(None, description="Swell height in meters")
    swell_direction: Optional[str] = Field(None, description="Swell direction")
    
    # Forecast vs current/historical indicator
    is_forecast: bool = Field(description="Whether this is forecast or historical/current data")
    data_timestamp: datetime = Field(description="Timestamp of weather data")


class ShippingRiskResponse(BaseModel):
    """Response model for shipping risk assessment"""
    
    risk_score: int = Field(
        ..., 
        ge=1, 
        le=10,
        description="Risk score from 1 (lowest risk) to 10 (highest risk)"
    )
    risk_description: str = Field(
        ...,
        description="Detailed explanation of the risk assessment reasoning"
    )
    weather_summary: str = Field(
        ...,
        description="Summary of weather conditions affecting the route"
    )
    departure_weather: WeatherData = Field(
        ...,
        description="Weather data for departure port"
    )
    destination_weather: WeatherData = Field(
        ...,
        description="Weather data for destination port"
    )
    estimated_travel_days: int = Field(
        ...,
        description="Estimated travel time in days"
    )
    assessment_timestamp: datetime = Field(
        ...,
        description="When this assessment was generated"
    )
    
    class Config:
        """Pydantic model configuration"""
        schema_extra = {
            "example": {
                "risk_score": 7,
                "risk_description": "High risk due to severe weather conditions expected along the Pacific route. Strong winds and high waves could cause delays and potential cargo damage.",
                "weather_summary": "Departure: Clear skies, moderate winds. Route: Storm system expected. Destination: Heavy precipitation forecast.",
                "departure_weather": {
                    "temperature_c": 22.5,
                    "feels_like_c": 24.0,
                    "humidity": 65,
                    "wind_speed_kph": 15.2,
                    "wind_direction": "SW",
                    "wind_degree": 225,
                    "pressure_mb": 1013.2,
                    "visibility_km": 10.0,
                    "uv_index": 6.0,
                    "condition": "Partly cloudy",
                    "condition_code": 1003,
                    "precipitation_mm": 0.0,
                    "wave_height_m": 1.2,
                    "is_forecast": True,
                    "data_timestamp": "2025-06-15T12:00:00Z"
                },
                "estimated_travel_days": 14,
                "assessment_timestamp": "2025-06-05T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    detail: str = Field(description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Unknown departure port: Invalid Port Name",
                "error_type": "ValidationError",
                "timestamp": "2025-06-05T10:30:00Z"
            }
        }


class PortInfo(BaseModel):
    """Port information model"""
    
    name: str = Field(description="Port name")
    country: str = Field(description="Country where port is located")
    latitude: float = Field(description="Port latitude")
    longitude: float = Field(description="Port longitude")
    port_code: Optional[str] = Field(None, description="International port code")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Port of Los Angeles",
                "country": "United States",
                "latitude": 33.7361,
                "longitude": -118.2922,
                "port_code": "USLAX"
            }
        }