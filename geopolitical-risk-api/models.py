"""
Pydantic models for geopolitical risk assessment API request/response validation
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import re


class ShippingRiskRequest(BaseModel):
    """Request model for geopolitical shipping risk assessment"""
    
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


class CountryRiskProfile(BaseModel):
    """Country-specific geopolitical risk profile"""
    
    country: str = Field(description="Country name")
    political_stability: int = Field(description="Political stability score (1-10)")
    trade_freedom: int = Field(description="Trade freedom index (0-100)")
    corruption_level: str = Field(description="Corruption level assessment")
    security_threat: str = Field(description="Security threat level")
    sanctions_status: str = Field(description="Current sanctions status")
    port_security: str = Field(description="Port security rating")
    labor_conditions: str = Field(description="Labor relations and conditions")
    regulatory_stability: str = Field(description="Regulatory environment stability")
    cargo_restrictions: str = Field(description="Cargo-specific restrictions and controls")


class RouteAnalysis(BaseModel):
    """Route-specific analysis including chokepoints and security zones"""
    
    departure_country: str = Field(description="Departure country")
    destination_country: str = Field(description="Destination country")
    distance_km: int = Field(description="Estimated route distance in kilometers")
    travel_days: int = Field(description="Estimated travel time in days")
    chokepoints: List[str] = Field(description="Critical chokepoints along the route")
    security_zones: List[str] = Field(description="Security risk zones on the route")
    seasonal_factors: str = Field(description="Seasonal considerations affecting the route")
    alternative_routes: str = Field(description="Available alternative routing options")
    shipping_lanes: str = Field(description="Primary shipping lanes utilized")
    goods_specific_risks: str = Field(description="Goods-specific risks for this route")


class GeopoliticalEvent(BaseModel):
    """Individual geopolitical event or news item"""
    
    title: str = Field(description="Event title or headline")
    summary: str = Field(description="Brief summary of the event")
    source: str = Field(description="News source")
    published_date: str = Field(description="Publication date (ISO format)")
    url: Optional[str] = Field(None, description="Source URL")
    relevance_score: int = Field(description="Relevance score (1-10)")
    severity: str = Field(description="Event severity level")
    
    # Additional metadata
    security_related: Optional[bool] = Field(None, description="Whether event is security-related")
    sanctions_related: Optional[bool] = Field(None, description="Whether event is sanctions-related")
    chokepoint_related: Optional[str] = Field(None, description="Related chokepoint if applicable")
    bilateral_relevance: Optional[str] = Field(None, description="Bilateral relationship relevance")
    goods_specific: Optional[str] = Field(None, description="Goods type relevance")


class GeopoliticalRiskResponse(BaseModel):
    """Response model for geopolitical shipping risk assessment"""
    
    risk_score: int = Field(
        ..., 
        ge=1, 
        le=10,
        description="Geopolitical risk score from 1 (lowest risk) to 10 (highest risk)"
    )
    risk_description: str = Field(
        ...,
        description="Detailed explanation of the geopolitical risk assessment and reasoning"
    )
    geopolitical_summary: str = Field(
        ...,
        description="Summary of key geopolitical factors affecting the route"
    )
    departure_country_risk: CountryRiskProfile = Field(
        ...,
        description="Geopolitical risk profile for departure country"
    )
    destination_country_risk: CountryRiskProfile = Field(
        ...,
        description="Geopolitical risk profile for destination country"
    )
    route_analysis: RouteAnalysis = Field(
        ...,
        description="Analysis of route-specific risks and characteristics"
    )
    recent_events: List[GeopoliticalEvent] = Field(
        ...,
        description="Recent geopolitical events affecting the route"
    )
    travel_days: int = Field(
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
                "risk_description": "Elevated geopolitical risk due to ongoing trade tensions between departure and destination countries, critical chokepoint security concerns, and recent sanctions developments. The electronics cargo type faces additional technology transfer restrictions.",
                "geopolitical_summary": "Route traverses high-tension maritime zones with active trade disputes and technology transfer restrictions affecting electronics shipments.",
                "departure_country_risk": {
                    "country": "United States",
                    "political_stability": 8,
                    "trade_freedom": 85,
                    "corruption_level": "Low",
                    "security_threat": "Low",
                    "sanctions_status": "Sanctions issuer",
                    "port_security": "High",
                    "labor_conditions": "Stable",
                    "regulatory_stability": "High",
                    "cargo_restrictions": "Technology export controls apply to electronics"
                },
                "destination_country_risk": {
                    "country": "China",
                    "political_stability": 7,
                    "trade_freedom": 65,
                    "corruption_level": "Medium",
                    "security_threat": "Low-Medium",
                    "sanctions_status": "Subject to some US sanctions",
                    "port_security": "High",
                    "labor_conditions": "Controlled",
                    "regulatory_stability": "Medium",
                    "cargo_restrictions": "HIGH RISK: Technology transfer restrictions apply"
                },
                "route_analysis": {
                    "departure_country": "United States",
                    "destination_country": "China",
                    "distance_km": 18500,
                    "travel_days": 14,
                    "chokepoints": ["South China Sea", "Panama Canal"],
                    "security_zones": ["Taiwan Strait"],
                    "seasonal_factors": "Hurricane season in Pacific",
                    "alternative_routes": "Panama Canal or US land bridge",
                    "shipping_lanes": "Trans-Pacific main line",
                    "goods_specific_risks": "Technology transfer scrutiny in disputed waters"
                },
                "recent_events": [
                    {
                        "title": "New technology export controls announced affecting China trade",
                        "summary": "Additional trade controls implemented on semiconductor and electronics exports to China",
                        "source": "reuters.com",
                        "published_date": "2025-06-01T10:00:00Z",
                        "relevance_score": 9,
                        "severity": "high",
                        "sanctions_related": True,
                        "goods_specific": "electronics"
                    }
                ],
                "travel_days": 14,
                "assessment_timestamp": "2025-06-07T10:30:00Z"
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
                "timestamp": "2025-06-07T10:30:00Z"
            }
        }


class PortInfo(BaseModel):
    """Port information model with geopolitical context"""
    
    name: str = Field(description="Official port name")
    country: str = Field(description="Country where port is located")
    code: str = Field(description="International port code")
    latitude: float = Field(description="Port latitude")
    longitude: float = Field(description="Port longitude")
    region: str = Field(description="Geographic region")
    security_level: str = Field(description="Port security rating")
    labor_stability: str = Field(description="Labor relations stability")
    infrastructure: str = Field(description="Infrastructure quality rating")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Port of Los Angeles",
                "country": "United States",
                "code": "USLAX",
                "latitude": 33.7361,
                "longitude": -118.2922,
                "region": "North America",
                "security_level": "High",
                "labor_stability": "Good",
                "infrastructure": "Excellent"
            }
        }


class CountryRiskProfileResponse(BaseModel):
    """Response model for country risk profile endpoint"""
    
    country: str = Field(description="Country name")
    risk_profile: CountryRiskProfile = Field(description="Detailed risk profile")
    
    class Config:
        schema_extra = {
            "example": {
                "country": "China",
                "risk_profile": {
                    "country": "China",
                    "political_stability": 7,
                    "trade_freedom": 65,
                    "corruption_level": "Medium",
                    "security_threat": "Low-Medium",
                    "sanctions_status": "Subject to some US sanctions",
                    "port_security": "High",
                    "labor_conditions": "Controlled",
                    "regulatory_stability": "Medium",
                    "cargo_restrictions": "Technology transfer restrictions for electronics"
                }
            }
        }


class RouteAnalysisResponse(BaseModel):
    """Response model for route analysis endpoint"""
    
    route_analysis: RouteAnalysis = Field(description="Comprehensive route analysis")
    
    class Config:
        schema_extra = {
            "example": {
                "route_analysis": {
                    "departure_country": "United States",
                    "destination_country": "China",
                    "distance_km": 18500,
                    "travel_days": 14,
                    "chokepoints": ["South China Sea", "Panama Canal"],
                    "security_zones": ["Taiwan Strait"],
                    "seasonal_factors": "Hurricane season in Pacific",
                    "alternative_routes": "Panama Canal or US land bridge",
                    "shipping_lanes": "Trans-Pacific main line",
                    "goods_specific_risks": "Technology transfer scrutiny in disputed waters"
                }
            }
        }


class PortSearchResponse(BaseModel):
    """Response model for port search endpoint"""
    
    ports: List[PortInfo] = Field(description="List of matching ports")
    
    class Config:
        schema_extra = {
            "example": {
                "ports": [
                    {
                        "name": "Port of Los Angeles",
                        "country": "United States",
                        "code": "USLAX",
                        "latitude": 33.7361,
                        "longitude": -118.2922,
                        "region": "North America",
                        "security_level": "High",
                        "labor_stability": "Good",
                        "infrastructure": "Excellent"
                    }
                ]
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    
    status: str = Field(description="Overall service status")
    services: Dict[str, str] = Field(description="Individual service statuses")
    timestamp: str = Field(description="Health check timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "llm_service": "healthy",
                    "news_service": "healthy", 
                    "geopolitical_service": "healthy",
                    "port_service": "healthy"
                },
                "timestamp": "2025-06-07T10:30:00Z"
            }
        }


class NewsIntelligence(BaseModel):
    """News intelligence analysis model"""
    
    events: List[GeopoliticalEvent] = Field(description="Relevant geopolitical events")
    sentiment: str = Field(description="Overall sentiment analysis")
    confidence: str = Field(description="Confidence level of intelligence")
    summary: str = Field(description="Intelligence summary")
    last_updated: str = Field(description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "events": [
                    {
                        "title": "Maritime security alert in South China Sea",
                        "summary": "Increased naval activity reported in disputed waters",
                        "source": "reuters.com",
                        "published_date": "2025-06-05T14:30:00Z",
                        "relevance_score": 8,
                        "severity": "medium",
                        "security_related": True,
                        "chokepoint_related": "South China Sea"
                    }
                ],
                "sentiment": "negative",
                "confidence": "medium",
                "summary": "Intelligence identifies 3 high-impact events affecting route security",
                "last_updated": "2025-06-07T10:30:00Z"
            }
        }