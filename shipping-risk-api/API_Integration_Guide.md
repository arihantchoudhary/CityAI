# Shipping Weather Risk Assessment API - Integration Guide

## Base URL
```
http://localhost:8000
```

## Main Endpoint

### POST /assess-shipping-risk

Analyzes weather-related risks for shipping routes using AI.

---

## Request Format

### HTTP Method
```
POST /assess-shipping-risk
```

### Headers
```
Content-Type: application/json
```

### Request Body Schema
```json
{
  "departure_port": "string",
  "destination_port": "string", 
  "departure_date": "YYYY-MM-DD",
  "carrier_name": "string",
  "goods_type": "string"
}
```

### Field Specifications

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `departure_port` | string | Yes | 2-100 chars | Name of departure port |
| `destination_port` | string | Yes | 2-100 chars | Name of destination port |
| `departure_date` | string | Yes | YYYY-MM-DD format, future date, within 1 year | Date of departure |
| `carrier_name` | string | Yes | 2-100 chars | Shipping carrier name |
| `goods_type` | string | Yes | 2-100 chars | Type of goods being shipped |

### Request Example
```json
{
  "departure_port": "Port of Los Angeles",
  "destination_port": "Port of Shanghai",
  "departure_date": "2025-06-15",
  "carrier_name": "COSCO Shipping", 
  "goods_type": "electronics"
}
```

---

## Response Format

### Success Response (HTTP 200)

```json
{
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
    "wave_height_m": null,
    "swell_height_m": null,
    "swell_direction": null,
    "is_forecast": true,
    "data_timestamp": "2025-06-15T12:00:00Z"
  },
  "destination_weather": {
    "temperature_c": 18.3,
    "feels_like_c": 19.1,
    "humidity": 78,
    "wind_speed_kph": 45.7,
    "wind_direction": "NE",
    "wind_degree": 45,
    "pressure_mb": 998.5,
    "visibility_km": 8.2,
    "uv_index": 3.0,
    "condition": "Heavy rain",
    "condition_code": 1195,
    "precipitation_mm": 12.5,
    "wave_height_m": null,
    "swell_height_m": null,
    "swell_direction": null,
    "is_forecast": true,
    "data_timestamp": "2025-06-15T12:00:00Z"
  },
  "estimated_travel_days": 14,
  "assessment_timestamp": "2025-06-05T10:30:00Z"
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `risk_score` | integer | Risk score from 1 (lowest) to 10 (highest) |
| `risk_description` | string | Detailed AI-generated risk explanation |
| `weather_summary` | string | Summary of weather conditions affecting route |
| `departure_weather` | object | Weather data for departure port |
| `destination_weather` | object | Weather data for destination port |
| `estimated_travel_days` | integer | Estimated travel time in days |
| `assessment_timestamp` | string | ISO timestamp when assessment was generated |

### Weather Object Schema

| Field | Type | Description |
|-------|------|-------------|
| `temperature_c` | float | Temperature in Celsius |
| `feels_like_c` | float | Feels-like temperature in Celsius |
| `humidity` | integer | Humidity percentage (0-100) |
| `wind_speed_kph` | float | Wind speed in km/h |
| `wind_direction` | string | Wind direction (N, NE, E, SE, S, SW, W, NW) |
| `wind_degree` | integer | Wind direction in degrees (0-360) |
| `pressure_mb` | float | Atmospheric pressure in millibars |
| `visibility_km` | float | Visibility in kilometers |
| `uv_index` | float | UV index |
| `condition` | string | Weather condition description |
| `condition_code` | integer | Numeric weather condition code |
| `precipitation_mm` | float | Precipitation in millimeters |
| `wave_height_m` | float/null | Wave height in meters (if available) |
| `swell_height_m` | float/null | Swell height in meters (if available) |
| `swell_direction` | string/null | Swell direction (if available) |
| `is_forecast` | boolean | True if forecast data, false if current/historical |
| `data_timestamp` | string | ISO timestamp of weather data |

---

## Error Responses

### Validation Error (HTTP 400)
```json
{
  "detail": "Unknown departure port: Invalid Port Name",
  "error_type": "ValidationError",
  "timestamp": "2025-06-05T10:30:00Z"
}
```

### Server Error (HTTP 500)
```json
{
  "detail": "Internal server error: Weather service unavailable",
  "error_type": "ServerError", 
  "timestamp": "2025-06-05T10:30:00Z"
}
```

---

## Additional Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "weather_api": "healthy",
    "llm_service": "healthy",
    "port_service": "healthy"
  },
  "timestamp": "2025-06-05T10:30:00Z"
}
```

### GET /ports/search
Search for ports by name.

**Parameters:**
- `query` (string): Search term
- `limit` (integer, optional): Max results (default: 10)

**Response:**
```json
{
  "ports": [
    {
      "name": "Port of Shanghai",
      "country": "China",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "code": "CNSHA",
      "match_score": 0.95
    }
  ]
}
```

---

## Supported Ports (50+ Major Ports)

**Asia:** Shanghai, Shenzhen, Singapore, Busan, Hong Kong, Tokyo, Yokohama, Kobe, Kaohsiung, Ningbo, Qingdao, Tianjin, Guangzhou, Dalian

**North America:** Los Angeles, Long Beach, Oakland, Seattle, Tacoma, New York, Savannah, Charleston, Miami, Houston

**Europe:** Rotterdam, Antwerp, Hamburg, Felixstowe, Le Havre, Genoa, Barcelona, Valencia

**Middle East:** Dubai, Jebel Ali

**Others:** Santos (Brazil), Buenos Aires (Argentina), Durban (South Africa), Cape Town (South Africa), Sydney (Australia), Melbourne (Australia)

---

## Sample Integration Code

### Python with requests
```python
import requests
from datetime import date, timedelta

url = "http://localhost:8000/assess-shipping-risk"
data = {
    "departure_port": "Los Angeles",
    "destination_port": "Shanghai",
    "departure_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
    "carrier_name": "COSCO",
    "goods_type": "electronics"
}

response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
    print(f"Risk Score: {result['risk_score']}/10")
else:
    print(f"Error: {response.status_code}")
```

### JavaScript/Node.js
```javascript
const fetch = require('node-fetch');

const assessRisk = async () => {
  const response = await fetch('http://localhost:8000/assess-shipping-risk', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      departure_port: "Los Angeles",
      destination_port: "Shanghai", 
      departure_date: "2025-06-15",
      carrier_name: "COSCO",
      goods_type: "electronics"
    })
  });
  
  const data = await response.json();
  console.log(`Risk Score: ${data.risk_score}/10`);
};
```

### cURL
```bash
curl -X POST "http://localhost:8000/assess-shipping-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "departure_port": "Los Angeles",
    "destination_port": "Shanghai",
    "departure_date": "2025-06-15", 
    "carrier_name": "COSCO",
    "goods_type": "electronics"
  }'
```

---

## Rate Limiting & Performance

- **Default Rate Limit:** 100 requests per minute per IP
- **Typical Response Time:** 5-30 seconds (depends on AI processing)
- **Timeout:** 120 seconds
- **Weather Data:** Cached for 1 hour

---

## Authentication

Currently no authentication required for local development. For production deployment, implement API key authentication as needed.