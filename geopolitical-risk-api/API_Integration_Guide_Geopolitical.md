# Geopolitical Risk Assessment API - Integration Guide

## 🌐 Live API
**Base URL:** `https://geopolitical-risk-api.onrender.com`

## 📋 Overview

This API provides AI-powered geopolitical risk assessment for shipping routes, analyzing political stability, security threats, trade relations, and real-time events to help make informed shipping decisions.

---

## 🚀 Quick Start

### Test the API
```bash
curl https://geopolitical-risk-api.onrender.com/health
```

### Sample Risk Assessment
```bash
curl -X POST "https://geopolitical-risk-api.onrender.com/assess-geopolitical-risk" \
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

## 📡 API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is operational.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "llm_service": "healthy",
    "news_service": "healthy", 
    "geopolitical_service": "healthy",
    "port_service": "healthy"
  },
  "timestamp": "2025-06-07T10:30:00Z"
}
```

### 2. Assess Geopolitical Risk (Main Endpoint)
**POST** `/assess-geopolitical-risk`

Comprehensive geopolitical risk assessment for shipping routes.

**Request Body:**
```json
{
  "departure_port": "string",
  "destination_port": "string",
  "departure_date": "YYYY-MM-DD",
  "carrier_name": "string", 
  "goods_type": "string"
}
```

**Field Requirements:**
- `departure_port`: Port name (2-100 characters)
- `destination_port`: Port name (2-100 characters)  
- `departure_date`: Future date within 1 year (YYYY-MM-DD format)
- `carrier_name`: Shipping carrier (2-100 characters)
- `goods_type`: Cargo type (2-100 characters)

**Response:**
```json
{
  "risk_score": 7,
  "risk_description": "Elevated geopolitical risk due to ongoing trade tensions...",
  "geopolitical_summary": "Route traverses high-tension maritime zones...",
  "departure_country_risk": {
    "country": "United States",
    "political_stability": 8,
    "trade_freedom": 85,
    "sanctions_status": "Sanctions issuer",
    "cargo_restrictions": "Technology export controls apply"
  },
  "destination_country_risk": {
    "country": "China", 
    "political_stability": 7,
    "sanctions_status": "Subject to some US sanctions"
  },
  "route_analysis": {
    "distance_km": 18500,
    "travel_days": 14,
    "chokepoints": ["South China Sea", "Panama Canal"],
    "security_zones": ["Taiwan Strait"],
    "shipping_lanes": "Trans-Pacific main line"
  },
  "recent_events": [
    {
      "title": "New technology export controls announced",
      "summary": "Additional trade controls implemented...",
      "source": "reuters.com",
      "relevance_score": 9,
      "severity": "high"
    }
  ],
  "travel_days": 14,
  "assessment_timestamp": "2025-06-07T10:30:00Z"
}
```

### 3. Country Risk Profile
**GET** `/countries/risk-profile?country={country}&goods_type={goods_type}`

Get detailed risk profile for a specific country.

**Parameters:**
- `country` (required): Country name
- `goods_type` (optional): Specific goods type analysis

**Example:**
```bash
curl "https://geopolitical-risk-api.onrender.com/countries/risk-profile?country=China&goods_type=electronics"
```

### 4. Route Analysis  
**GET** `/routes/chokepoints?departure_port={departure}&destination_port={destination}&goods_type={goods}`

Analyze chokepoints and security zones for a route.

**Example:**
```bash
curl "https://geopolitical-risk-api.onrender.com/routes/chokepoints?departure_port=Los%20Angeles&destination_port=Shanghai&goods_type=electronics"
```

### 5. Port Search
**GET** `/ports/search?query={search_term}&limit={number}`

Search for ports by name.

**Example:**
```bash
curl "https://geopolitical-risk-api.onrender.com/ports/search?query=Singapore&limit=5"
```

---

## 💻 Code Examples

### Python
```python
import requests
from datetime import date, timedelta

def assess_geopolitical_risk(departure_port, destination_port, goods_type):
    url = "https://geopolitical-risk-api.onrender.com/assess-geopolitical-risk"
    
    payload = {
        "departure_port": departure_port,
        "destination_port": destination_port,
        "departure_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "carrier_name": "Test Carrier",
        "goods_type": goods_type
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"Risk Score: {result['risk_score']}/10")
        print(f"Risk Level: {get_risk_level(result['risk_score'])}")
        print(f"Travel Days: {result['travel_days']}")
        print(f"Chokepoints: {', '.join(result['route_analysis']['chokepoints'])}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def get_risk_level(score):
    if score <= 2: return "Very Low"
    elif score <= 4: return "Low"
    elif score <= 6: return "Medium" 
    elif score <= 8: return "High"
    else: return "Very High"

# Example usage
risk = assess_geopolitical_risk("Los Angeles", "Shanghai", "electronics")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function assessGeopoliticalRisk(departurePort, destinationPort, goodsType) {
    const url = 'https://geopolitical-risk-api.onrender.com/assess-geopolitical-risk';
    
    const payload = {
        departure_port: departurePort,
        destination_port: destinationPort,
        departure_date: getDateInFuture(7), // 7 days from now
        carrier_name: 'Test Carrier',
        goods_type: goodsType
    };
    
    try {
        const response = await axios.post(url, payload, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 60000
        });
        
        const result = response.data;
        
        console.log(`Risk Score: ${result.risk_score}/10`);
        console.log(`Risk Level: ${getRiskLevel(result.risk_score)}`);
        console.log(`Travel Days: ${result.travel_days}`);
        console.log(`Chokepoints: ${result.route_analysis.chokepoints.join(', ')}`);
        
        return result;
        
    } catch (error) {
        console.error('API Error:', error.message);
        return null;
    }
}

function getDateInFuture(days) {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0]; // YYYY-MM-DD format
}

function getRiskLevel(score) {
    if (score <= 2) return 'Very Low';
    if (score <= 4) return 'Low';
    if (score <= 6) return 'Medium';
    if (score <= 8) return 'High';
    return 'Very High';
}

// Example usage
assessGeopoliticalRisk('Los Angeles', 'Shanghai', 'electronics');
```

### PHP
```php
<?php
function assessGeopoliticalRisk($departurePort, $destinationPort, $goodsType) {
    $url = 'https://geopolitical-risk-api.onrender.com/assess-geopolitical-risk';
    
    $payload = [
        'departure_port' => $departurePort,
        'destination_port' => $destinationPort,
        'departure_date' => date('Y-m-d', strtotime('+7 days')),
        'carrier_name' => 'Test Carrier',
        'goods_type' => $goodsType
    ];
    
    $options = [
        'http' => [
            'header' => "Content-type: application/json\r\n",
            'method' => 'POST',
            'content' => json_encode($payload),
            'timeout' => 60
        ]
    ];
    
    $context = stream_context_create($options);
    $response = file_get_contents($url, false, $context);
    
    if ($response === FALSE) {
        echo "API Error: Failed to get response\n";
        return null;
    }
    
    $result = json_decode($response, true);
    
    echo "Risk Score: " . $result['risk_score'] . "/10\n";
    echo "Travel Days: " . $result['travel_days'] . "\n";
    
    return $result;
}

// Example usage
$risk = assessGeopoliticalRisk('Los Angeles', 'Shanghai', 'electronics');
?>
```

### Java
```java
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.time.LocalDate;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import java.util.HashMap;

public class GeopoliticalRiskAPI {
    private static final String API_BASE_URL = "https://geopolitical-risk-api.onrender.com";
    private static final HttpClient client = HttpClient.newHttpClient();
    private static final ObjectMapper mapper = new ObjectMapper();
    
    public static Map<String, Object> assessGeopoliticalRisk(
            String departurePort, String destinationPort, String goodsType) {
        
        try {
            Map<String, String> payload = new HashMap<>();
            payload.put("departure_port", departurePort);
            payload.put("destination_port", destinationPort);
            payload.put("departure_date", LocalDate.now().plusDays(7).toString());
            payload.put("carrier_name", "Test Carrier");
            payload.put("goods_type", goodsType);
            
            String jsonPayload = mapper.writeValueAsString(payload);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_BASE_URL + "/assess-geopolitical-risk"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();
            
            HttpResponse<String> response = client.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                Map<String, Object> result = mapper.readValue(response.body(), Map.class);
                
                System.out.println("Risk Score: " + result.get("risk_score") + "/10");
                System.out.println("Travel Days: " + result.get("travel_days"));
                
                return result;
            } else {
                System.err.println("API Error: " + response.statusCode());
                return null;
            }
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            return null;
        }
    }
    
    public static void main(String[] args) {
        assessGeopoliticalRisk("Los Angeles", "Shanghai", "electronics");
    }
}
```

---

## 📊 Risk Score Interpretation

| Score | Level | Description | Recommendation |
|-------|-------|-------------|----------------|
| 1-2 | **Very Low** | Minimal geopolitical risks | Standard protocols |
| 3-4 | **Low** | Some political considerations | Standard monitoring |
| 5-6 | **Medium** | Moderate risks | Enhanced monitoring |
| 7-8 | **High** | Significant risks | Enhanced security measures |
| 9-10 | **Very High** | Critical risks | Consider alternatives |

---

## ⚠️ Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid input)
- **429**: Rate Limited (too many requests)
- **500**: Internal Server Error

### Error Response Format
```json
{
  "detail": "Error description",
  "error_type": "ValidationError",
  "timestamp": "2025-06-07T10:30:00Z"
}
```

### Best Practices
```python
import requests
import time

def safe_api_call(url, payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited - wait and retry
                time.sleep(10)
                continue
            else:
                print(f"API Error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(5)
            
    return None
```

---

## 🌍 Supported Ports

### Major Ports (50+ supported)
- **Asia**: Shanghai, Shenzhen, Singapore, Busan, Hong Kong, Tokyo, Kaohsiung
- **North America**: Los Angeles, Long Beach, New York, Seattle, Oakland, Savannah
- **Europe**: Rotterdam, Antwerp, Hamburg, Felixstowe, Le Havre
- **Middle East**: Dubai, Jebel Ali
- **Others**: Santos, Melbourne, Sydney, Cape Town

### Port Search
```bash
curl "https://geopolitical-risk-api.onrender.com/ports/search?query=Singapore"
```

---

## 🚚 Goods Types with Special Analysis

### High-Risk Categories
- **Electronics/Technology**: Export controls, tech transfer restrictions
- **Semiconductors**: Advanced technology restrictions
- **Military/Defense**: Strict export controls, arms embargoes
- **Energy Products**: Sanctions considerations
- **Chemicals**: Dual-use restrictions

### Standard Categories
- **Textiles**: Standard trade regulations
- **Food Products**: Health and safety regulations
- **Consumer Goods**: General trade compliance
- **Machinery**: Potential dual-use considerations

---

## 🔒 Rate Limits & Performance

- **Rate Limit**: 100 requests per minute
- **Timeout**: 120 seconds max response time
- **Typical Response Time**: 10-60 seconds
- **Caching**: Country and route data cached for better performance

---

## 📈 Integration Examples

### Supply Chain Risk Management
```python
def evaluate_supply_chain_routes(routes):
    """Evaluate multiple shipping routes for risk comparison"""
    results = []
    
    for route in routes:
        risk = assess_geopolitical_risk(
            route['departure'], 
            route['destination'], 
            route['goods']
        )
        
        if risk:
            results.append({
                'route': f"{route['departure']} → {route['destination']}",
                'risk_score': risk['risk_score'],
                'chokepoints': risk['route_analysis']['chokepoints'],
                'recommendation': get_recommendation(risk['risk_score'])
            })
    
    # Sort by risk score
    return sorted(results, key=lambda x: x['risk_score'])
```

### Real-time Monitoring
```javascript
// Monitor route risks periodically
setInterval(async () => {
    const risk = await assessGeopoliticalRisk('Los Angeles', 'Shanghai', 'electronics');
    
    if (risk && risk.risk_score >= 8) {
        // Alert for high-risk conditions
        console.alert(`HIGH RISK ALERT: Route risk score is ${risk.risk_score}/10`);
        // Send notification, update dashboard, etc.
    }
}, 3600000); // Check every hour
```

---

## 📞 Support & Resources

- **API Documentation**: https://geopolitical-risk-api.onrender.com/docs
- **Health Check**: https://geopolitical-risk-api.onrender.com/health
- **Status Page**: Monitor API uptime and performance

### Quick Test
```bash
# Verify API is working
curl -s https://geopolitical-risk-api.onrender.com/health | jq .status
```

---

**Built for safer global shipping through AI-powered geopolitical intelligence.**