"""
Configuration management for the Geopolitical Risk Assessment API
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, List, Union
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = Field(default="Shipping Geopolitical Risk Assessment API")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)  # Different port from weather API
    
    # External API Keys
    openai_api_key: str = Field(
        ..., 
        description="OpenAI API key for LLM services"
    )
    
    # Optional: Additional intelligence sources
    newsapi_key: Optional[str] = Field(
        default=None,
        description="NewsAPI.com API key for real-time news (optional)"
    )
    
    # Optional: Alternative AI models
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude models (optional backup)"
    )
    
    # OpenAI Configuration
    openai_model: str = Field(
        default="gpt-4-1106-preview",
        description="OpenAI model to use for geopolitical risk assessment"
    )
    openai_temperature: float = Field(
        default=0.3,
        description="Temperature setting for LLM (lower = more deterministic)"
    )
    openai_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for LLM response (higher for detailed geopolitical analysis)"
    )
    openai_request_timeout: int = Field(
        default=90,
        description="OpenAI API request timeout in seconds (longer for complex analysis)"
    )
    
    # News Service Configuration
    news_request_timeout: int = Field(
        default=30,
        description="News API request timeout in seconds"
    )
    news_cache_ttl: int = Field(
        default=1800,
        description="News data cache TTL in seconds (30 minutes default)"
    )
    max_news_results: int = Field(
        default=50,
        description="Maximum news results to process per query"
    )
    
    # Intelligence Sources Configuration
    enable_web_scraping: bool = Field(
        default=False,
        description="Enable web scraping for additional intelligence (use with caution)"
    )
    
    intelligence_sources: str = Field(
        default="reuters.com,bloomberg.com,ft.com,wsj.com,bbc.com,maritimeexecutive.com,lloydslist.com,tradewinds.no,joc.com",
        description="Trusted news sources for geopolitical intelligence (comma-separated)"
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
    cache_country_risk_ttl: int = Field(
        default=7200,
        description="Country risk data cache TTL in seconds (2 hours default)"
    )
    cache_route_analysis_ttl: int = Field(
        default=3600,
        description="Route analysis cache TTL in seconds (1 hour default)"
    )
    
    # Security Configuration
    api_key_header: str = Field(
        default="X-API-Key",
        description="Header name for API key authentication"
    )
    
    internal_api_key: Optional[str] = Field(
        default=None,
        description="Internal API key for service authentication (optional)"
    )
    
    # Risk Assessment Configuration
    default_risk_score: int = Field(
        default=5,
        description="Default risk score when assessment fails"
    )
    
    max_risk_events: int = Field(
        default=10,
        description="Maximum number of risk events to return in response"
    )
    
    risk_score_weights: dict = Field(
        default={
            "political_stability": 0.25,
            "sanctions_impact": 0.30,
            "security_threats": 0.20,
            "chokepoint_risks": 0.15,
            "recent_events": 0.10
        },
        description="Weight factors for risk score calculation"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    log_requests: bool = Field(
        default=True,
        description="Enable request/response logging"
    )
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="*",
        description="CORS allowed origins (comma-separated)"
    )
    
    allowed_methods: str = Field(
        default="GET,POST,OPTIONS",
        description="CORS allowed methods (comma-separated)"
    )
    
    # Performance Configuration
    max_concurrent_requests: int = Field(
        default=10,
        description="Maximum concurrent external API requests"
    )
    
    request_retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for failed requests"
    )
    
    request_backoff_factor: float = Field(
        default=2.0,
        description="Exponential backoff factor for retries"
    )
    
    # Data Sources Configuration
    fallback_mode_enabled: bool = Field(
        default=True,
        description="Enable fallback assessments when primary services fail"
    )
    
    require_news_intelligence: bool = Field(
        default=False,
        description="Require news intelligence for assessments (may cause failures)"
    )
    
    # Development Configuration
    mock_news_data: bool = Field(
        default=False,
        description="Use mock news data for development/testing"
    )
    
    enable_detailed_logging: bool = Field(
        default=False,
        description="Enable detailed logging for debugging"
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @field_validator('allowed_origins')
    @classmethod
    def parse_origins(cls, v):
        """Parse comma-separated origins into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('allowed_methods')  
    @classmethod
    def parse_methods(cls, v):
        """Parse comma-separated methods into list"""
        if isinstance(v, str):
            return [method.strip() for method in v.split(',')]
        return v
    
    @field_validator('intelligence_sources')
    @classmethod  
    def parse_sources(cls, v):
        """Parse comma-separated sources into list"""
        if isinstance(v, str):
            return [source.strip() for source in v.split(',')]
        return v


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
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Validate OpenAI model
    valid_models = [
        "gpt-4", "gpt-4-turbo", "gpt-4-1106-preview", 
        "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
    ]
    if settings.openai_model not in valid_models:
        print(f"Warning: OpenAI model '{settings.openai_model}' not in validated list: {valid_models}")
    
    # Validate temperature range
    if not 0.0 <= settings.openai_temperature <= 2.0:
        raise ValueError("OpenAI temperature must be between 0.0 and 2.0")
    
    # Validate risk score weights
    weight_sum = sum(settings.risk_score_weights.values())
    if abs(weight_sum - 1.0) > 0.01:  # Allow small floating point errors
        print(f"Warning: Risk score weights sum to {weight_sum}, should be 1.0")
    
    print(f"✅ Geopolitical API configuration validated successfully")
    print(f"   - OpenAI Model: {settings.openai_model}")
    print(f"   - News API: {'Configured' if settings.newsapi_key else 'Mock mode'}")
    print(f"   - Debug Mode: {settings.debug}")
    print(f"   - Cache: {'Redis' if settings.redis_url else 'In-memory'}")
    print(f"   - Fallback Mode: {'Enabled' if settings.fallback_mode_enabled else 'Disabled'}")
    
    return settings


def print_settings():
    """Print current settings (without sensitive data)"""
    settings = get_settings()
    
    print("\n📋 Geopolitical API Configuration:")
    print(f"   App Name: {settings.app_name}")
    print(f"   Debug: {settings.debug}")
    print(f"   Host: {settings.host}:{settings.port}")
    print(f"   Log Level: {settings.log_level}")
    print(f"   OpenAI Model: {settings.openai_model}")
    print(f"   Max Tokens: {settings.openai_max_tokens}")
    print(f"   News Cache TTL: {settings.news_cache_ttl}s")
    print(f"   Country Risk Cache TTL: {settings.cache_country_risk_ttl}s")
    print(f"   Rate Limit: {settings.rate_limit_requests} req/min")
    print(f"   Max News Results: {settings.max_news_results}")
    print(f"   OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    print(f"   News API Key: {'✅ Set' if settings.newsapi_key else '❌ Missing (using mock data)'}")
    print(f"   Anthropic API Key: {'✅ Set' if settings.anthropic_api_key else '❌ Missing (optional)'}")
    print(f"   Redis: {'✅ Configured' if settings.redis_url else '❌ Not configured'}")
    print(f"   Fallback Mode: {'✅ Enabled' if settings.fallback_mode_enabled else '❌ Disabled'}")
    print(f"   Mock News: {'✅ Enabled' if settings.mock_news_data else '❌ Disabled'}")
    
    print(f"\n🔍 Intelligence Sources ({len(settings.intelligence_sources)}):")
    sources_list = settings.intelligence_sources if isinstance(settings.intelligence_sources, list) else settings.intelligence_sources.split(',')
    for source in sources_list[:5]:  # Show first 5
        print(f"   - {source.strip()}")
    if len(sources_list) > 5:
        print(f"   ... and {len(sources_list) - 5} more")
    
    print(f"\n⚖️ Risk Score Weights:")
    for factor, weight in settings.risk_score_weights.items():
        print(f"   - {factor}: {weight:.2%}")
    print()


def get_risk_assessment_config():
    """Get configuration specific to risk assessment"""
    settings = get_settings()
    
    return {
        "default_risk_score": settings.default_risk_score,
        "max_risk_events": settings.max_risk_events,
        "risk_score_weights": settings.risk_score_weights,
        "fallback_mode_enabled": settings.fallback_mode_enabled,
        "require_news_intelligence": settings.require_news_intelligence
    }


def get_external_api_config():
    """Get configuration for external API calls"""
    settings = get_settings()
    
    return {
        "openai": {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "temperature": settings.openai_temperature,
            "max_tokens": settings.openai_max_tokens,
            "timeout": settings.openai_request_timeout
        },
        "news": {
            "api_key": settings.newsapi_key,
            "timeout": settings.news_request_timeout,
            "max_results": settings.max_news_results,
            "cache_ttl": settings.news_cache_ttl
        },
        "performance": {
            "max_concurrent": settings.max_concurrent_requests,
            "retry_attempts": settings.request_retry_attempts,
            "backoff_factor": settings.request_backoff_factor
        }
    }


if __name__ == "__main__":
    # Test configuration loading
    try:
        validate_settings()
        print_settings()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Setup instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenAI API key to .env:")
        print("      OPENAI_API_KEY=your_openai_key_here")
        print("   3. Optionally add NewsAPI key for real-time data:")
        print("      NEWSAPI_KEY=your_newsapi_key_here")
        print("   4. Install requirements: pip install -r requirements.txt")
        print("   5. Run: python main.py")