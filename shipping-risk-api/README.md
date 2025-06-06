# Shipping Weather Risk Assessment API

A FastAPI-based service that analyzes weather-related risks for shipping routes using AI. The API fetches weather data for departure and destination ports, then uses OpenAI's GPT models to provide intelligent risk assessments.

## 🚀 Features

- **AI-Powered Risk Assessment**: Uses OpenAI GPT-4 for intelligent weather risk analysis
- **Comprehensive Weather Data**: Integrates with WeatherAPI.com for detailed maritime weather
- **Global Port Coverage**: Supports 50+ major international ports
- **RESTful API**: Well-documented FastAPI with automatic OpenAPI/Swagger docs
- **Detailed Risk Scoring**: 1-10 risk scale with detailed explanations
- **Production Ready**: Proper error handling, logging, and validation

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **WeatherAPI.com account** (free tier available)
- **OpenAI account** with API access
- Basic knowledge of Python and APIs

## 🛠️ Installation & Setup

### 1. Clone or Download the Project

Create a new directory and add all the provided files:

```bash
mkdir shipping-risk-api
cd shipping-risk-api
```

### 2. Create the Project Structure

```
shipping-risk-api/
├── main.py
├── models.py
├── config.py
├── requirements.txt
├── .env.example
├── .env                 # You'll create this
├── README.md
└── services/
    ├── __init__.py      # Create empty file
    ├── weather_service.py
    ├── llm_service.py
    └── port_service.py
```

Create the services directory and empty `__init__.py`:
```bash
mkdir services
touch services/__init__.py
```

### 3. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Get API Keys

#### WeatherAPI.com (Free)
1. Go to [WeatherAPI.com](https://www.weatherapi.com/signup.aspx)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes: 1M calls/month, 7-day history, 14-day forecast

#### OpenAI (Paid)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and add billing information
3. Get your API key from [API Keys page](https://platform.openai.com/api-keys)
4. Estimated cost: ~$0.01-0.05 per risk assessment

### 5. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Edit `.env` file:
```bash
WEATHERAPI_KEY=your_actual_weatherapi_key_here
OPENAI_API_KEY=your_actual_openai_key_here
```

### 6. Test the Configuration

```bash
python config.py
```

You should see:
```
✅ Configuration validated successfully
   - Weather API: Configured
   - OpenAI Model: gpt-4
   - Debug Mode: False
   - Cache: Disabled
```

## 🚀 Running the API

### Development Mode

```bash
# Run with auto-reload for development
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
# Run with multiple workers for production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Assess Shipping Risk

```bash
curl -X POST "http://localhost:8000/assess-shipping-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "departure_port": "Port of Los Angeles",
    "destination_port": "Port of Shanghai",
    "departure_date": "2025-06-15",
    "carrier_name": "COSCO Shipping",
    "goods_type": "electronics"
  }'
```

### Search Ports

```bash
curl "http://localhost:8000/ports/search?query=shanghai&limit=5"
```

## 📊 Response Format

The API returns structured risk assessments:

```json
{
  "risk_score": 7,
  "risk_description": "High risk due to severe weather conditions expected along the Pacific route. Strong winds and high waves could cause delays and potential cargo damage. Electronics cargo requires dry conditions.",
  "weather_summary": "Departure: Clear skies, moderate winds. Route: Storm system expected. Destination: Heavy precipitation forecast.",
  "departure_weather": {
    "temperature_c": 22.5,
    "wind_speed_kph": 15.2,
    "condition": "Partly cloudy",
    "is_forecast": true
  },
  "destination_weather": {
    "temperature_c": 18.3,
    "wind_speed_kph": 45.7,
    "condition": "Heavy rain",
    "is_forecast": true
  },
  "estimated_travel_days": 14,
  "assessment_timestamp": "2025-06-05T10:30:00Z"
}
```

## 🌍 Supported Ports

The API supports 50+ major international ports including:

**Asia**: Shanghai, Shenzhen, Singapore, Busan, Hong Kong, Tokyo  
**North America**: Los Angeles, New York, Seattle, Houston, Vancouver  
**Europe**: Rotterdam, Hamburg, Antwerp, Felixstowe, Barcelona  
**Middle East**: Dubai, Jebel Ali  
**Other**: Santos, Sydney, Durban, Cape Town

## ⚙️ Configuration Options

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `WEATHERAPI_KEY` | Required | WeatherAPI.com API key |
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4` | OpenAI model to use |
| `OPENAI_TEMPERATURE` | `0.3` | Model creativity (0.0-2.0) |
| `DEBUG` | `false` | Enable debug mode |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Formatting

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## 📈 Usage Costs

**WeatherAPI.com**: Free tier (1M calls/month)  
**OpenAI GPT-4**: ~$0.01-0.05 per assessment  
**Monthly estimates** (100 assessments/day):
- Weather API: Free
- OpenAI: $30-150/month

## 🔒 Security Considerations

- Keep API keys secure and never commit them to version control
- Use environment variables for all sensitive configuration
- Consider rate limiting for production use
- Implement authentication if needed
- Review OpenAI usage regularly to monitor costs

## 🚨 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Make sure you're in the right directory and virtual environment is activated
cd shipping-risk-api
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

**API key errors:**
```bash
# Test your configuration
python config.py
```

**Weather API errors:**
- Check your WeatherAPI.com quota at their dashboard
- Verify your API key is correct
- Ensure you're not exceeding rate limits

**OpenAI errors:**
- Verify billing is set up on your OpenAI account
- Check your API key permissions
- Monitor your usage dashboard

### Logs

Check logs for detailed error information:
```bash
# Run with debug mode
DEBUG=true python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check API service status (WeatherAPI.com, OpenAI)
4. Open an issue with detailed error logs

---

**Happy shipping! ⚓️**