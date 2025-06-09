# Shipping Risk Mitigation API

## Deployment on Render

### 1. Setup Repository
1. Create a new GitHub repository
2. Upload these files:
   - `main.py` (the FastAPI application)
   - `requirements.txt` (Python dependencies)
   - `render.yaml` (optional - for infrastructure as code)

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and connect your GitHub account
2. Create a new "Web Service"
3. Connect your repository
4. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: 
     - `XAI_API_KEY`: Your xAI API key (get it from [x.ai](https://x.ai))

### 3. Get Your xAI API Key
1. Visit [x.ai](https://x.ai) and sign up/login
2. Go to the API section and generate an API key
3. Add this key to your Render environment variables

## API Usage Examples

### Example Request

```python
import requests
import json

# Your deployed API URL (replace with your Render URL)
API_URL = "https://your-app.onrender.com"

# Sample shipping risk analysis request
request_data = {
    "departure_port": "Port of Los Angeles",
    "destination_port": "Port of Shanghai",
    "departure_date": "2025-07-15",
    "carrier_name": "Maersk Line",
    "goods_type": "Electronics and Consumer Goods",
    "weather_conditions": {
        "risk_score": 6,
        "risk_description": "Moderate weather risk due to potential typhoon activity in the Pacific during summer months",
        "weather_summary": "Seasonal typhoon risk with possible route diversions",
        "departure_weather": {
            "temperature": 22.5,
            "wind_speed": 15.0,
            "wave_height": 2.1,
            "visibility": 8.5,
            "conditions": "Partly cloudy with moderate winds"
        },
        "destination_weather": {
            "temperature": 28.0,
            "wind_speed": 25.0,
            "wave_height": 3.2,
            "visibility": 6.0,
            "conditions": "Approaching weather system, increasing winds"
        },
        "estimated_travel_days": 14
    },
    "geopolitical_conditions": {
        "risk_score": 7,
        "risk_description": "Elevated geopolitical risk due to ongoing trade tensions and territorial disputes in South China Sea",
        "geopolitical_summary": "Route traverses high-tension maritime zones with potential for shipping delays",
        "chokepoints": ["South China Sea", "Taiwan Strait"],
        "security_zones": ["Taiwan Strait", "Spratly Islands"],
        "shipping_lanes": "Trans-Pacific main shipping corridor"
    }
}

# Make the API call
response = requests.post(
    f"{API_URL}/analyze-shipping-risk",
    json=request_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print("Risk Analysis Results:")
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Example Response

```json
{
  "overall_risk_assessment": "High risk level detected due to combined weather (6/10) and geopolitical factors (7/10). Trans-Pacific route faces typhoon season challenges and geopolitical tensions in South China Sea.",
  "recommended_action": "Proceed with enhanced monitoring and implement multiple mitigation strategies",
  "strategies": [
    {
      "strategy_type": "Route Optimization",
      "priority": "High",
      "description": "Consider northern Pacific route to avoid South China Sea tensions and reduce typhoon exposure",
      "implementation_time": "2-3 days for route planning",
      "cost_impact": "moderate (5-8% increase in fuel costs)",
      "risk_reduction": "30-40% geopolitical risk reduction"
    },
    {
      "strategy_type": "Weather Mitigation",
      "priority": "High",
      "description": "Implement enhanced weather monitoring with 6-hour updates and flexible departure timing",
      "implementation_time": "immediate",
      "cost_impact": "minimal",
      "risk_reduction": "25-35% weather risk reduction"
    },
    {
      "strategy_type": "Documentation & Compliance",
      "priority": "Medium",
      "description": "Verify all customs documentation and ensure compliance with recent trade regulations",
      "implementation_time": "1-2 days",
      "cost_impact": "minimal",
      "risk_reduction": "regulatory compliance assured"
    },
    {
      "strategy_type": "Insurance & Financial",
      "priority": "Medium",
      "description": "Consider additional marine insurance coverage for high-risk route segments",
      "implementation_time": "1 day",
      "cost_impact": "moderate (0.5-1% of cargo value)",
      "risk_reduction": "financial protection for delays/damages"
    }
  ],
  "alternative_routes": [
    "Northern Pacific route via Aleutian Islands",
    "Southern route via Philippines and Indonesia",
    "Split shipping via multiple smaller vessels"
  ],
  "timeline_recommendations": "Monitor conditions for 48-72 hours before departure. Consider delaying departure by 2-3 days if typhoon develops.",
  "compliance_checks": [
    "Verify carrier's insurance coverage for geopolitical risks",
    "Check cargo documentation for restricted items",
    "Confirm customs pre-clearance for both ports",
    "Validate carrier's safety certifications"
  ]
}
```

### cURL Example

```bash
curl -X POST "https://your-app.onrender.com/analyze-shipping-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "departure_port": "Port of Rotterdam",
    "destination_port": "Port of Singapore",
    "departure_date": "2025-08-20",
    "carrier_name": "MSC Mediterranean",
    "goods_type": "Automotive Parts",
    "weather_conditions": {
      "risk_score": 4,
      "risk_description": "Low to moderate weather risk with seasonal monsoons",
      "weather_summary": "Generally favorable conditions with potential monsoon delays",
      "departure_weather": {
        "temperature": 18.0,
        "wind_speed": 12.0,
        "wave_height": 1.8,
        "visibility": 9.0,
        "conditions": "Clear skies, light winds"
      },
      "destination_weather": {
        "temperature": 31.0,
        "wind_speed": 18.0,
        "wave_height": 2.5,
        "visibility": 7.5,
        "conditions": "Partly cloudy, monsoon season"
      },
      "estimated_travel_days": 18
    },
    "geopolitical_conditions": {
      "risk_score": 5,
      "risk_description": "Moderate risk due to Red Sea shipping disruptions and Suez Canal considerations",
      "geopolitical_summary": "Alternative routes may be needed due to regional instability",
      "chokepoints": ["Suez Canal", "Strait of Malacca"],
      "security_zones": ["Red Sea", "Gulf of Aden"],
      "shipping_lanes": "Europe-Asia main trade route"
    }
  }'
```

## API Endpoints

### POST `/analyze-shipping-risk`
Analyzes shipping risks and provides mitigation strategies.

**Request Body**: ShippingRequest object (see example above)
**Response**: MitigationResponse object with strategies

### GET `/health`
Health check endpoint to verify API status.

### GET `/`
API information and available endpoints.

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `500`: Internal Server Error (API issues)

Example error response:
```json
{
  "detail": "Error analyzing shipping risk: Invalid date format"
}
```

## Environment Variables

- `XAI_API_KEY`: Required - Your xAI API key for accessing Grok
- `PORT`: Optional - Port number (defaults to 8000, automatically set by Render)

## Testing Your Deployment

Once deployed, test your API:

1. Visit `https://your-app.onrender.com/` to see the welcome message
2. Check `https://your-app.onrender.com/health` to verify the API is running
3. Use the example requests above to test the main functionality

## Monitoring and Logs

- Check Render dashboard for deployment logs
- Monitor API performance and usage
- Set up alerts for API failures if needed