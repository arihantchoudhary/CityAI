# Shipping Risk Mitigation API - Integration Guide

## 🚀 Overview

The Shipping Risk Mitigation API analyzes shipping risks and provides AI-powered mitigation strategies. It combines weather conditions, geopolitical factors, and shipping details to generate actionable recommendations for reducing shipping risks.

**Base URL**: `https://mitigation-api.onrender.com`

**API Features**:
- Weather-based risk analysis
- Geopolitical risk assessment  
- Alternative route suggestions
- Specific compliance document recommendations
- Cost-benefit analysis of mitigation strategies

---

## 📋 API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running and properly configured.

```bash
curl -X GET "https://your-app-name.onrender.com/health"
```

**Response**:
```json
{
  "status": "healthy",
  "grok_api_configured": true,
  "timestamp": "2025-06-09T14:30:00.000000"
}
```

### 2. Root Information
**GET** `/`

Get API information and available endpoints.

```bash
curl -X GET "https://your-app-name.onrender.com/"
```

**Response**:
```json
{
  "message": "Shipping Risk Mitigation API",
  "version": "1.0.0",
  "endpoints": {
    "/analyze-shipping-risk": "POST - Analyze shipping risks and get mitigation strategies",
    "/health": "GET - Health check endpoint"
  }
}
```

### 3. Analyze Shipping Risk
**POST** `/analyze-shipping-risk`

The main endpoint for risk analysis and mitigation strategy generation.

---

## 📝 Request Format

### Required Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `departure_port` | string | Yes | Name of departure port (2-100 chars) |
| `destination_port` | string | Yes | Name of destination port (2-100 chars) |
| `departure_date` | string | Yes | Date in YYYY-MM-DD format, future date within 1 year |
| `carrier_name` | string | Yes | Shipping carrier name (2-100 chars) |
| `goods_type` | string | Yes | Type of goods being shipped (2-100 chars) |
| `weather_conditions` | object | Yes | Weather-related risk information |
| `geopolitical_conditions` | object | Yes | Geopolitical risk information |

### Weather Conditions Object

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `risk_score` | integer | Yes | Risk score from 1 (lowest) to 10 (highest) |
| `risk_description` | string | Yes | Detailed risk explanation (1-1000 chars) |
| `weather_summary` | string | Yes | Summary of weather conditions (1-1000 chars) |
| `departure_weather` | object | Yes | Weather data for departure port |
| `destination_weather` | object | Yes | Weather data for destination port |
| `estimated_travel_days` | integer | Yes | Estimated travel time in days (1-365) |

### Weather Data Object

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `temperature` | float | No | Temperature in Celsius |
| `wind_speed` | float | No | Wind speed in knots |
| `wave_height` | float | No | Wave height in meters |
| `visibility` | float | No | Visibility in nautical miles |
| `conditions` | string | No | Weather conditions description |

### Geopolitical Conditions Object

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `risk_score` | integer | Yes | Risk score from 1 (lowest) to 10 (highest) |
| `risk_description` | string | Yes | Detailed risk explanation (1-1000 chars) |
| `geopolitical_summary` | string | Yes | Summary of geopolitical conditions (1-1000 chars) |
| `chokepoints` | array | No | List of maritime chokepoints on route |
| `security_zones` | array | No | List of security zones on route |
| `shipping_lanes` | string | Yes | Description of shipping lanes used |

---

## 📤 Response Format

### Success Response (200)

```json
{
  "overall_risk_assessment": "string",
  "recommended_action": "string",
  "strategies": [
    {
      "strategy_type": "string",
      "priority": "High|Medium|Low",
      "description": "string",
      "implementation_time": "string",
      "cost_impact": "string",
      "risk_reduction": "string"
    }
  ],
  "alternative_routes": ["string"],
  "timeline_recommendations": "string",
  "compliance_checks": ["string"]
}
```

### Error Responses

**400 Bad Request** - Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "departure_date"],
      "msg": "Departure date must be in the future",
      "type": "value_error"
    }
  ]
}
```

**500 Internal Server Error** - Server or AI processing errors:
```json
{
  "detail": "Error analyzing shipping risk: [specific error message]"
}
```

---

## 💻 Code Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function analyzeShippingRisk() {
  const apiUrl = 'https://your-app-name.onrender.com/analyze-shipping-risk';
  
  const requestData = {
    departure_port: "Port of Rotterdam",
    destination_port: "Port of Singapore",
    departure_date: "2025-08-15",
    carrier_name: "MSC Mediterranean",
    goods_type: "Automotive Parts",
    weather_conditions: {
      risk_score: 4,
      risk_description: "Low to moderate weather risk with seasonal monsoons",
      weather_summary: "Generally favorable conditions with potential monsoon delays",
      departure_weather: {
        temperature: 18.0,
        wind_speed: 12.0,
        wave_height: 1.8,
        visibility: 9.0,
        conditions: "Clear skies, light winds"
      },
      destination_weather: {
        temperature: 31.0,
        wind_speed: 18.0,
        wave_height: 2.5,
        visibility: 7.5,
        conditions: "Partly cloudy, monsoon season"
      },
      estimated_travel_days: 18
    },
    geopolitical_conditions: {
      risk_score: 5,
      risk_description: "Moderate risk due to Red Sea shipping disruptions",
      geopolitical_summary: "Alternative routes may be needed due to regional instability",
      chokepoints: ["Suez Canal", "Strait of Malacca"],
      security_zones: ["Red Sea", "Gulf of Aden"],
      shipping_lanes: "Europe-Asia main trade route"
    }
  };

  try {
    const response = await axios.post(apiUrl, requestData, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 60000 // 60 second timeout for AI processing
    });

    console.log('Risk Analysis Results:', response.data);
    
    // Extract key insights
    const { overall_risk_assessment, strategies, alternative_routes } = response.data;
    console.log('Overall Risk:', overall_risk_assessment);
    console.log('Number of Strategies:', strategies.length);
    console.log('Alternative Routes:', alternative_routes);
    
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    throw error;
  }
}

// Usage
analyzeShippingRisk()
  .then(result => {
    // Process the result
    console.log('Analysis completed successfully');
  })
  .catch(error => {
    console.error('Analysis failed:', error);
  });
```

### Python

```python
import requests
import json
from datetime import datetime, timedelta

def analyze_shipping_risk():
    api_url = "https://your-app-name.onrender.com/analyze-shipping-risk"
    
    # Calculate future date
    future_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    
    request_data = {
        "departure_port": "Port of Los Angeles",
        "destination_port": "Port of Shanghai",
        "departure_date": future_date,
        "carrier_name": "Maersk Line",
        "goods_type": "Electronics and Consumer Goods",
        "weather_conditions": {
            "risk_score": 6,
            "risk_description": "Moderate weather risk due to potential typhoon activity",
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
                "conditions": "Approaching weather system"
            },
            "estimated_travel_days": 14
        },
        "geopolitical_conditions": {
            "risk_score": 7,
            "risk_description": "Elevated geopolitical risk due to trade tensions",
            "geopolitical_summary": "Route traverses high-tension maritime zones",
            "chokepoints": ["South China Sea", "Taiwan Strait"],
            "security_zones": ["Taiwan Strait", "Spratly Islands"],
            "shipping_lanes": "Trans-Pacific main shipping corridor"
        }
    }
    
    try:
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60 second timeout
        )
        
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        
        print("Risk Analysis Results:")
        print(json.dumps(result, indent=2))
        
        # Extract key insights
        print(f"\nOverall Risk: {result.get('overall_risk_assessment')}")
        print(f"Recommended Action: {result.get('recommended_action')}")
        print(f"Number of Strategies: {len(result.get('strategies', []))}")
        
        # Show risk reduction percentages
        strategies = result.get('strategies', [])
        for i, strategy in enumerate(strategies, 1):
            print(f"Strategy {i}: {strategy.get('risk_reduction')}")
        
        return result
        
    except requests.exceptions.Timeout:
        print("Request timed out. The API might be processing a complex analysis.")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        raise
    except json.JSONDecodeError:
        print("Failed to parse JSON response")
        raise

# Usage
if __name__ == "__main__":
    try:
        result = analyze_shipping_risk()
        print("Analysis completed successfully!")
    except Exception as e:
        print(f"Analysis failed: {e}")
```

---

## ⚠️ Error Handling Best Practices

### 1. Timeout Handling
Always set appropriate timeouts (60+ seconds) as AI processing can take time:

```javascript
// JavaScript
axios.defaults.timeout = 60000;

// Python
requests.post(url, json=data, timeout=60)

// PHP
curl_setopt($curl, CURLOPT_TIMEOUT, 60);
```

### 2. Retry Logic for 502 Errors
Handle Render service cold starts:

```python
import time

def call_api_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=60)
            if response.status_code == 502 and attempt < max_retries - 1:
                print(f"Service starting up, retrying in 30 seconds...")
                time.sleep(30)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(10)
                continue
            raise
    raise Exception("Max retries exceeded")
```

### 3. Validation Error Handling
Handle validation errors gracefully:

```javascript
if (error.response && error.response.status === 400) {
  const validationErrors = error.response.data.detail;
  console.log('Validation errors:');
  validationErrors.forEach(err => {
    console.log(`${err.loc.join('.')}: ${err.msg}`);
  });
}
```

---

## 🔧 Best Practices

### 1. **Input Validation**
- Validate date formats before sending requests
- Ensure risk scores are between 1-10
- Check string length limits

### 2. **Error Handling**
- Implement retry logic for temporary failures
- Handle both network and API errors
- Log errors for debugging

### 3. **Performance**
- Cache results when appropriate
- Use connection pooling for multiple requests
- Consider async/await for non-blocking calls

### 4. **Security**
- Use HTTPS endpoints only
- Don't log sensitive shipping information
- Validate and sanitize user inputs

### 5. **Rate Limiting**
- Respect API limits (currently no enforced limits)
- Implement client-side throttling if needed
- Monitor response times

---

## 🚀 Production Considerations

### 1. **Environment Configuration**
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-prod-api.onrender.com'
  : 'http://localhost:8002';
```

### 2. **Logging and Monitoring**
```python
import logging

def analyze_risk_with_logging(shipping_data):
    try:
        result = call_api(shipping_data)
        logging.info(f"Risk analysis successful for route {shipping_data['departure_port']} -> {shipping_data['destination_port']}")
        return result
    except Exception as e:
        logging.error(f"Risk analysis failed: {e}")
        raise
```

### 3. **Response Caching**
```javascript
// Cache results for identical requests
const cache = new Map();
const cacheKey = JSON.stringify(requestData);

if (cache.has(cacheKey)) {
  return cache.get(cacheKey);
}

const result = await callAPI(requestData);
cache.set(cacheKey, result);
return result;
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Status Code | Solution |
|-------|-------------|----------|
| Service sleeping | 502 | Wait 30-60 seconds and retry |
| Invalid date format | 400 | Use YYYY-MM-DD format |
| Date in past | 400 | Use future date within 1 year |
| Timeout | - | Increase timeout to 60+ seconds |
| Validation error | 422 | Check required fields and formats |
| AI processing error | 500 | Check logs, may be temporary |

### Debug Steps

1. **Test health endpoint first**:
   ```bash
   curl https://your-app-name.onrender.com/health
   ```

2. **Check request format**:
   ```bash
   curl -X POST https://your-app-name.onrender.com/analyze-shipping-risk \
     -H "Content-Type: application/json" \
     -d '{"departure_port": "test"}' 
   ```

3. **Verify response structure**:
   ```javascript
   console.log('Response keys:', Object.keys(response.data));
   ```

### Getting Help

- Check the `/health` endpoint for service status
- Review validation error messages in 400/422 responses  
- Look for specific error details in 500 response messages
- Test with the provided examples first
- Ensure proper timeout and retry handling

---

## 📊 Response Time Expectations

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Health check | < 2 seconds | Quick status check |
| Risk analysis (warm) | 10-30 seconds | AI processing time |
| Risk analysis (cold start) | 30-90 seconds | Service startup + processing |
| Retry after 502 | 30-60 seconds | Service wake-up time |

---

## 📞 Support

For API integration support:
- Check this documentation first
- Review the troubleshooting section
- Test with provided examples
- Ensure proper error handling implementation

---

*Last updated: June 2025*