"""
Configuration management for the Shipping Risk Assessment API
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = Field(default="Shipping Weather Risk Assessment API")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # External API Keys
    weatherapi_key: str = Field(
        ..., 
        description="WeatherAPI.com API key"
    )
    openai_api_key: str = Field(
        ..., 
        description="OpenAI API key for LLM services"
    )
    
    # Weather API Configuration
    weatherapi_base_url: str = Field(
        default="http://api.weatherapi.com/v1",
        description="WeatherAPI.com base URL"
    )
    weather_request_timeout: int = Field(
        default=30,
        description="Weather API request timeout in seconds"
    )
    
    # OpenAI Configuration
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use for risk assessment"
    )
    openai_temperature: float = Field(
        default=0.3,
        description="Temperature setting for LLM (lower = more deterministic)"
    )
    openai_max_tokens: int = Field(
        default=1000,
        description="Maximum tokens for LLM response"
    )
    openai_request_timeout: int = Field(
        default=60,
        description="OpenAI API request timeout in seconds"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        description="Requests per minute per IP"
    )
    
    # Caching (if Redis is available)
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis URL for caching (optional)"
    )
    cache_weather_ttl: int = Field(
        default=3600,
        description="Weather data cache TTL in seconds (1 hour default)"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Security
    allowed_origins: list = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable examples
        fields = {
            'weatherapi_key': {'env': 'WEATHERAPI_KEY'},
            'openai_api_key': {'env': 'OPENAI_API_KEY'},
            'redis_url': {'env': 'REDIS_URL'},
            'debug': {'env': 'DEBUG'},
            'log_level': {'env': 'LOG_LEVEL'},
        }


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def validate_settings():
    """Validate that all required settings are present"""
    settings = get_settings()
    
    # Check required API keys
    if not settings.weatherapi_key:
        raise ValueError("WEATHERAPI_KEY environment variable is required")
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Validate OpenAI model
    valid_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    if settings.openai_model not in valid_models:
        raise ValueError(f"Invalid OpenAI model. Must be one of: {valid_models}")
    
    # Validate temperature range
    if not 0.0 <= settings.openai_temperature <= 2.0:
        raise ValueError("OpenAI temperature must be between 0.0 and 2.0")
    
    print(f"✅ Configuration validated successfully")
    print(f"   - Weather API: Configured")
    print(f"   - OpenAI Model: {settings.openai_model}")
    print(f"   - Debug Mode: {settings.debug}")
    print(f"   - Cache: {'Redis' if settings.redis_url else 'Disabled'}")
    
    return settings


# Development helper function
def print_settings():
    """Print current settings (without sensitive data)"""
    settings = get_settings()
    
    print("\n📋 Current Configuration:")
    print(f"   App Name: {settings.app_name}")
    print(f"   Debug: {settings.debug}")
    print(f"   Host: {settings.host}:{settings.port}")
    print(f"   Log Level: {settings.log_level}")
    print(f"   OpenAI Model: {settings.openai_model}")
    print(f"   Weather API Timeout: {settings.weather_request_timeout}s")
    print(f"   Rate Limit: {settings.rate_limit_requests} req/min")
    print(f"   Cache TTL: {settings.cache_weather_ttl}s")
    print(f"   Weather API Key: {'✅ Set' if settings.weatherapi_key else '❌ Missing'}")
    print(f"   OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    print(f"   Redis: {'✅ Configured' if settings.redis_url else '❌ Not configured'}")
    print()


if __name__ == "__main__":
    # Test configuration loading
    try:
        validate_settings()
        print_settings()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure to:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your API keys to .env")
        print("   3. Install requirements: pip install -r requirements.txt")