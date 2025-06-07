"""
Shipping Weather Risk Assessment API

A FastAPI application that assesses weather-related risks for shipping routes
by analyzing weather data and using LLM for intelligent risk evaluation.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from typing import Optional

from models import ShippingRiskRequest, ShippingRiskResponse, ErrorResponse
from services.weather_service import WeatherService
from services.llm_service import LLMService
from services.port_service import PortService
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Shipping Weather Risk Assessment API",
    description="Analyze weather-related risks for shipping routes using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
weather_service = WeatherService()
llm_service = LLMService()
port_service = PortService()


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Shipping Weather Risk Assessment API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check with service status"""
    try:
        # Test external service connectivity
        weather_status = await weather_service.health_check()
        llm_status = await llm_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "weather_api": weather_status,
                "llm_service": llm_status,
                "port_service": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post(
    "/assess-shipping-risk",
    response_model=ShippingRiskResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Risk Assessment"]
)
async def assess_shipping_risk(request: ShippingRiskRequest):
    """
    Assess weather-related risk for a shipping route
    
    This endpoint:
    1. Validates the shipping route and parameters
    2. Fetches weather data for departure and destination ports
    3. Uses AI to analyze weather conditions and assess risk
    4. Returns a risk score (1-10) with detailed reasoning
    
    Args:
        request: Shipping route details including ports, dates, carrier, and goods
        
    Returns:
        ShippingRiskResponse: Risk score, description, and weather details
        
    Raises:
        HTTPException: 400 for invalid input, 500 for service errors
    """
    try:
        logger.info(f"Processing risk assessment request: {request.departure_port} -> {request.destination_port}")
        
        # Step 1: Validate and get port coordinates
        departure_coords = await port_service.get_port_coordinates(request.departure_port)
        destination_coords = await port_service.get_port_coordinates(request.destination_port)
        
        if not departure_coords:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown departure port: {request.departure_port}"
            )
        if not destination_coords:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown destination port: {request.destination_port}"
            )
            
        # Step 2: Fetch weather data for both locations
        logger.info("Fetching weather data for departure and destination")
        
        departure_weather = await weather_service.get_weather_data(
            departure_coords["lat"],
            departure_coords["lon"],
            request.departure_date
        )
        
        destination_weather = await weather_service.get_weather_data(
            destination_coords["lat"],
            destination_coords["lon"],
            request.departure_date  # For now, using departure date for destination too
        )
        
        # Step 3: Calculate estimated travel time and route weather
        travel_days = port_service.estimate_travel_time(
            departure_coords, destination_coords, request.goods_type
        )
        
        # Step 4: Use LLM to assess risk based on all factors
        logger.info("Generating AI risk assessment")
        
        risk_assessment = await llm_service.assess_shipping_risk(
            departure_port=request.departure_port,
            destination_port=request.destination_port,
            departure_date=request.departure_date,
            carrier_name=request.carrier_name,
            goods_type=request.goods_type,
            departure_weather=departure_weather,
            destination_weather=destination_weather,
            travel_days=travel_days
        )
        
        # Step 5: Build response
        response = ShippingRiskResponse(
            risk_score=risk_assessment["risk_score"],
            risk_description=risk_assessment["risk_description"],
            weather_summary=risk_assessment["weather_summary"],
            departure_weather=departure_weather,
            destination_weather=destination_weather,
            estimated_travel_days=travel_days,
            assessment_timestamp=datetime.utcnow()
        )
        
        logger.info(f"Risk assessment completed. Score: {response.risk_score}/10")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in risk assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/ports/search", tags=["Ports"])
async def search_ports(query: str, limit: int = 10):
    """
    Search for ports by name
    
    Args:
        query: Port name search term
        limit: Maximum number of results to return
        
    Returns:
        List of matching ports with coordinates
    """
    try:
        results = await port_service.search_ports(query, limit)
        return {"ports": results}
    except Exception as e:
        logger.error(f"Port search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Port search failed")


if __name__ == "__main__":
    # For development only - use proper ASGI server for production
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )