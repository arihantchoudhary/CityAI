"""
Shipping Geopolitical Risk Assessment API

A FastAPI application that assesses geopolitical and security risks for shipping routes
by analyzing political conditions, security threats, and using LLM for intelligent risk evaluation.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from typing import Optional

from models import ShippingRiskRequest, GeopoliticalRiskResponse, ErrorResponse
from services.geopolitical_service import GeopoliticalService
from services.llm_service import LLMService
from services.port_service import PortService
from services.news_service import NewsService
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Shipping Geopolitical Risk Assessment API",
    description="Analyze geopolitical and security risks for shipping routes using AI",
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
geopolitical_service = GeopoliticalService()
llm_service = LLMService()
port_service = PortService()
news_service = NewsService()


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Shipping Geopolitical Risk Assessment API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check with service status"""
    try:
        # Test external service connectivity
        llm_status = await llm_service.health_check()
        news_status = await news_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "llm_service": llm_status,
                "news_service": news_status,
                "geopolitical_service": "healthy",
                "port_service": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post(
    "/assess-geopolitical-risk",
    response_model=GeopoliticalRiskResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Risk Assessment"]
)
async def assess_geopolitical_risk(request: ShippingRiskRequest):
    """
    Assess geopolitical and security risk for a shipping route
    
    This endpoint:
    1. Validates the shipping route and parameters
    2. Analyzes geopolitical conditions for departure and destination countries
    3. Fetches real-time news and events affecting the route
    4. Evaluates route-specific chokepoints and security zones
    5. Uses AI to analyze all factors and assess risk
    6. Returns a risk score (1-10) with detailed reasoning
    
    Args:
        request: Shipping route details including ports, dates, carrier, and goods
        
    Returns:
        GeopoliticalRiskResponse: Risk score, description, and geopolitical details
        
    Raises:
        HTTPException: 400 for invalid input, 500 for service errors
    """
    try:
        logger.info(f"Processing geopolitical risk assessment: {request.departure_port} -> {request.destination_port}")
        
        # Step 1: Validate and get port information
        departure_info = await port_service.get_port_info(request.departure_port)
        destination_info = await port_service.get_port_info(request.destination_port)
        
        if not departure_info:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown departure port: {request.departure_port}"
            )
        if not destination_info:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown destination port: {request.destination_port}"
            )
            
        # Step 2: Analyze route characteristics and chokepoints
        logger.info("Analyzing route characteristics and chokepoints")
        route_analysis = await geopolitical_service.analyze_route(
            departure_info, destination_info, request.goods_type
        )
        
        # Step 3: Get country-specific geopolitical assessments
        logger.info("Fetching geopolitical assessments for countries")
        
        departure_country_risk = await geopolitical_service.assess_country_risk(
            departure_info["country"], request.goods_type
        )
        
        destination_country_risk = await geopolitical_service.assess_country_risk(
            destination_info["country"], request.goods_type
        )
        
        # Step 4: Fetch real-time news and events
        logger.info("Gathering real-time geopolitical intelligence")
        
        news_analysis = await news_service.get_route_intelligence(
            departure_info["country"],
            destination_info["country"],
            route_analysis["chokepoints"],
            request.goods_type
        )
        
        # Step 5: Calculate estimated travel time for temporal analysis
        travel_days = port_service.estimate_travel_time(
            departure_info, destination_info, request.goods_type
        )
        
        # Step 6: Use LLM to assess comprehensive geopolitical risk
        logger.info("Generating AI geopolitical risk assessment")
        
        try:
            risk_assessment = await llm_service.assess_geopolitical_risk(
                departure_port=request.departure_port,
                destination_port=request.destination_port,
                departure_date=request.departure_date,
                carrier_name=request.carrier_name,
                goods_type=request.goods_type,
                departure_country_risk=departure_country_risk,
                destination_country_risk=destination_country_risk,
                route_analysis=route_analysis,
                news_analysis=news_analysis,
                travel_days=travel_days
            )
            logger.info(f"LLM risk assessment completed: score={risk_assessment.get('risk_score', 'unknown')}")
            
            # Check if it's a fallback assessment
            risk_desc = risk_assessment.get('risk_description', '')
            if '[Fallback Assessment]' in risk_desc or '[OpenAI API Error:' in risk_desc:
                logger.warning("LLM service returned fallback assessment")
                logger.warning(f"Fallback reason: {risk_desc[:200]}...")
            
        except Exception as llm_error:
            logger.error(f"LLM service call failed: {str(llm_error)}")
            import traceback
            logger.error(f"LLM traceback: {traceback.format_exc()}")
            
            # Create manual fallback if LLM service completely fails
            risk_assessment = await geopolitical_service.fallback_risk_assessment(
                departure_country_risk, destination_country_risk, route_analysis, news_analysis
            )
            risk_assessment["risk_description"] = f"[API Endpoint Error] LLM service failed: {str(llm_error)}. {risk_assessment['risk_description']}"
        
        # Step 7: Build comprehensive response
        response = GeopoliticalRiskResponse(
            risk_score=risk_assessment["risk_score"],
            risk_description=risk_assessment["risk_description"],
            geopolitical_summary=risk_assessment["geopolitical_summary"],
            departure_country_risk=departure_country_risk,
            destination_country_risk=destination_country_risk,
            route_analysis=route_analysis,
            recent_events=news_analysis["events"],
            travel_days=travel_days,
            assessment_timestamp=datetime.utcnow()
        )
        
        logger.info(f"Geopolitical risk assessment completed. Score: {response.risk_score}/10")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in geopolitical risk assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/countries/risk-profile", tags=["Countries"])
async def get_country_risk_profile(country: str, goods_type: Optional[str] = None):
    """
    Get detailed risk profile for a specific country
    
    Args:
        country: Country name
        goods_type: Optional goods type for specific risk analysis
        
    Returns:
        Detailed country risk profile
    """
    try:
        risk_profile = await geopolitical_service.assess_country_risk(country, goods_type)
        return {"country": country, "risk_profile": risk_profile}
    except Exception as e:
        logger.error(f"Country risk profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Country risk analysis failed")


@app.get("/routes/chokepoints", tags=["Routes"])
async def analyze_route_chokepoints(
    departure_port: str, 
    destination_port: str,
    goods_type: Optional[str] = None
):
    """
    Analyze chokepoints and security zones for a specific route
    
    Args:
        departure_port: Departure port name
        destination_port: Destination port name
        goods_type: Optional goods type for specific analysis
        
    Returns:
        Route analysis with chokepoints and security information
    """
    try:
        departure_info = await port_service.get_port_info(departure_port)
        destination_info = await port_service.get_port_info(destination_port)
        
        if not departure_info or not destination_info:
            raise HTTPException(status_code=400, detail="Invalid port names")
            
        route_analysis = await geopolitical_service.analyze_route(
            departure_info, destination_info, goods_type or "general"
        )
        return {"route_analysis": route_analysis}
    except Exception as e:
        logger.error(f"Route analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Route analysis failed")


@app.get("/ports/search", tags=["Ports"])
async def search_ports(query: str, limit: int = 10):
    """
    Search for ports by name
    
    Args:
        query: Port name search term
        limit: Maximum number of results to return
        
    Returns:
        List of matching ports with coordinates and country info
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
    port = int(os.environ.get("PORT", 8001))  # Different port from weather API
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )