"""
LLM service for AI-powered geopolitical risk assessment using OpenAI
"""

from openai import AsyncOpenAI
import asyncio
import logging
import json
from datetime import date
from typing import Dict, Any

from config import get_settings


logger = logging.getLogger(__name__)


class LLMService:
    """Service for AI-powered geopolitical risk assessment using OpenAI"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model
        self.temperature = self.settings.openai_temperature
        self.max_tokens = self.settings.openai_max_tokens
        
    async def health_check(self) -> str:
        """Check if OpenAI API is accessible"""
        try:
            # Test with a simple completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10
            )
            
            if response and response.choices:
                return "healthy"
            else:
                return "unhealthy (no response)"
                
        except Exception as e:
            logger.error(f"OpenAI API health check failed: {str(e)}")
            return f"unhealthy (error: {str(e)})"
    
    async def assess_geopolitical_risk(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: date,
        carrier_name: str,
        goods_type: str,
        departure_country_risk: Dict[str, Any],
        destination_country_risk: Dict[str, Any],
        route_analysis: Dict[str, Any],
        news_analysis: Dict[str, Any],
        travel_days: int
    ) -> Dict[str, Any]:
        """
        Use AI to assess geopolitical shipping risk based on comprehensive analysis
        
        Args:
            departure_port: Name of departure port
            destination_port: Name of destination port
            departure_date: Date of departure
            carrier_name: Shipping carrier name
            goods_type: Type of goods being shipped
            departure_country_risk: Risk analysis for departure country
            destination_country_risk: Risk analysis for destination country
            route_analysis: Analysis of route chokepoints and security zones
            news_analysis: Real-time news and events analysis
            travel_days: Estimated travel time in days
            
        Returns:
            Dict containing risk_score, risk_description, and geopolitical_summary
        """
        try:
            # Construct detailed prompt for geopolitical risk assessment
            prompt = self._build_geopolitical_assessment_prompt(
                departure_port=departure_port,
                destination_port=destination_port,
                departure_date=departure_date,
                carrier_name=carrier_name,
                goods_type=goods_type,
                departure_country_risk=departure_country_risk,
                destination_country_risk=destination_country_risk,
                route_analysis=route_analysis,
                news_analysis=news_analysis,
                travel_days=travel_days
            )
            
            logger.info(f"Sending geopolitical assessment prompt to OpenAI (length: {len(prompt)} chars)")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.settings.openai_request_timeout
            )
            
            logger.info(f"OpenAI API call successful, response received")
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            logger.info(f"AI response length: {len(ai_response)} chars")
            logger.info(f"AI response preview: {ai_response[:200]}...")
            
            parsed_result = self._parse_ai_response(ai_response)
            logger.info(f"Successfully parsed AI response with risk score: {parsed_result.get('risk_score', 'unknown')}")
            return parsed_result
            
        except Exception as e:
            logger.error(f"LLM geopolitical risk assessment failed: {str(e)}")
            logger.error(f"LLM error type: {type(e).__name__}")
            # Return fallback assessment with error details
            fallback = self._fallback_risk_assessment(
                departure_country_risk, destination_country_risk, route_analysis, news_analysis
            )
            fallback["risk_description"] = f"[OpenAI API Error: {str(e)}] {fallback['risk_description']}"
            return fallback
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role and behavior"""
        return """You are an expert geopolitical risk analyst specializing in maritime security and international trade. You have deep knowledge of:

- International relations and political stability indicators
- Maritime security threats and piracy zones
- Trade sanctions, embargoes, and export controls
- Regional conflicts and territorial disputes
- Port security protocols and labor relations
- Shipping route chokepoints and strategic waterways
- Country-specific political risks and regulatory environments
- Cargo-specific trade restrictions and security concerns
- Economic warfare and supply chain disruptions

Your task is to analyze shipping routes and provide accurate geopolitical risk assessments based on political conditions, security threats, trade relations, and current events.

You must respond in a specific JSON format with:
1. A risk score from 1-10 (1 = minimal political/security risk, 10 = extreme risk)
2. A detailed risk description explaining your reasoning and specific threats
3. A geopolitical summary highlighting key factors and recent developments

Consider these factors in your assessment:
- Political stability of departure and destination countries
- Bilateral trade relations and diplomatic tensions
- Active sanctions, embargoes, or trade restrictions
- Maritime security threats (piracy, terrorism, naval conflicts)
- Route-specific chokepoints and their current security status
- Labor disputes, strikes, or port security issues
- Cargo-specific restrictions (technology transfers, dual-use goods, etc.)
- Recent geopolitical events that could affect the route
- Carrier reputation and flag state considerations
- Seasonal security patterns and threat levels

Be comprehensive in your analysis - consider both immediate risks and emerging threats that could develop during the voyage. Focus on actionable intelligence for shipping decision-makers."""

    def _build_geopolitical_assessment_prompt(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: date,
        carrier_name: str,
        goods_type: str,
        departure_country_risk: Dict[str, Any],
        destination_country_risk: Dict[str, Any],
        route_analysis: Dict[str, Any],
        news_analysis: Dict[str, Any],
        travel_days: int
    ) -> str:
        """Build a comprehensive prompt for geopolitical risk assessment"""
        
        # Format data for the prompt
        departure_risk_text = self._format_country_risk_for_prompt(departure_country_risk, "departure")
        destination_risk_text = self._format_country_risk_for_prompt(destination_country_risk, "destination")
        route_text = self._format_route_analysis_for_prompt(route_analysis)
        news_text = self._format_news_analysis_for_prompt(news_analysis)
        
        prompt = f"""Please assess the geopolitical and security risk for this cargo shipment:

ROUTE INFORMATION:
- Departure Port: {departure_port}
- Destination Port: {destination_port}
- Departure Date: {departure_date.strftime('%Y-%m-%d')}
- Estimated Travel Time: {travel_days} days
- Carrier: {carrier_name}
- Cargo Type: {goods_type}

DEPARTURE COUNTRY RISK PROFILE:
{departure_risk_text}

DESTINATION COUNTRY RISK PROFILE:
{destination_risk_text}

ROUTE ANALYSIS:
{route_text}

RECENT GEOPOLITICAL INTELLIGENCE:
{news_text}

ASSESSMENT REQUIREMENTS:
Please analyze this shipping scenario comprehensively and provide a geopolitical risk assessment considering:

1. Political stability and bilateral relations between countries
2. Current sanctions, trade restrictions, or diplomatic tensions
3. Maritime security threats along the route (piracy, naval conflicts, terrorism)
4. Chokepoint security and control (Suez Canal, Strait of Hormuz, etc.)
5. Port security, labor conditions, and operational risks
6. Cargo-specific restrictions or sensitivities ({goods_type})
7. Carrier reputation and flag state considerations
8. Recent events that could impact route security or trade relations
9. Regulatory changes or emerging restrictions
10. Timeline considerations for the {travel_days}-day voyage

Respond in JSON format:
{{
  "risk_score": <integer 1-10>,
  "risk_description": "<detailed explanation of geopolitical risks, specific threats, and risk mitigation recommendations>",
  "geopolitical_summary": "<concise summary of key political and security factors affecting this route>"
}}

Focus on actionable intelligence and be specific about current threats and political considerations that could impact this shipment."""

        return prompt
    
    def _format_country_risk_for_prompt(self, country_risk: Dict[str, Any], location: str) -> str:
        """Format country risk data for inclusion in the AI prompt"""
        return f"""- Country: {country_risk.get('country', 'Unknown')}
- Political Stability Score: {country_risk.get('political_stability', 'N/A')}/10
- Trade Freedom Index: {country_risk.get('trade_freedom', 'N/A')}/100
- Corruption Level: {country_risk.get('corruption_level', 'Unknown')}
- Security Threat Level: {country_risk.get('security_threat', 'Unknown')}
- Sanctions Status: {country_risk.get('sanctions_status', 'None known')}
- Port Security Rating: {country_risk.get('port_security', 'Unknown')}
- Labor Relations: {country_risk.get('labor_conditions', 'Unknown')}
- Regulatory Environment: {country_risk.get('regulatory_stability', 'Unknown')}
- Cargo-Specific Risks: {country_risk.get('cargo_restrictions', 'None identified')}"""

    def _format_route_analysis_for_prompt(self, route_analysis: Dict[str, Any]) -> str:
        """Format route analysis data for inclusion in the AI prompt"""
        chokepoints = route_analysis.get('chokepoints', [])
        security_zones = route_analysis.get('security_zones', [])
        
        chokepoints_text = "\n".join([f"  • {cp}" for cp in chokepoints]) if chokepoints else "  • None identified"
        security_zones_text = "\n".join([f"  • {sz}" for sz in security_zones]) if security_zones else "  • None identified"
        
        return f"""- Route Distance: {route_analysis.get('distance_km', 'Unknown')} km
- Estimated Duration: {route_analysis.get('travel_days', 'Unknown')} days
- Primary Shipping Lanes: {route_analysis.get('shipping_lanes', 'Standard commercial routes')}
- Critical Chokepoints:
{chokepoints_text}
- Security Risk Zones:
{security_zones_text}
- Alternative Routes Available: {route_analysis.get('alternative_routes', 'Unknown')}
- Seasonal Considerations: {route_analysis.get('seasonal_factors', 'None identified')}"""

    def _format_news_analysis_for_prompt(self, news_analysis: Dict[str, Any]) -> str:
        """Format news analysis data for inclusion in the AI prompt"""
        events = news_analysis.get('events', [])
        if not events:
            return "- No significant recent events identified affecting this route"
        
        events_text = []
        for event in events[:5]:  # Limit to top 5 most relevant events
            events_text.append(f"  • {event.get('title', 'Unknown event')}")
            if event.get('summary'):
                events_text.append(f"    Summary: {event['summary'][:200]}...")
            if event.get('relevance_score'):
                events_text.append(f"    Relevance: {event['relevance_score']}/10")
        
        return f"""- Recent Events Analysis:
{chr(10).join(events_text)}
- Overall News Sentiment: {news_analysis.get('sentiment', 'Neutral')}
- Intelligence Confidence Level: {news_analysis.get('confidence', 'Medium')}"""

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data"""
        try:
            logger.info(f"Parsing AI response: {ai_response[:300]}...")
            
            # Clean the response - sometimes AI adds extra text before/after JSON
            ai_response = ai_response.strip()
            
            # Try to find JSON in the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                logger.info(f"Extracted JSON string: {json_str}")
                
                parsed_response = json.loads(json_str)
                logger.info(f"Successfully parsed JSON: {parsed_response}")
                
                # Validate the response structure
                if self._validate_ai_response(parsed_response):
                    logger.info("AI response validation passed")
                    return parsed_response
                else:
                    logger.error(f"AI response validation failed: {parsed_response}")
                    raise ValueError("Invalid response structure")
            else:
                logger.error(f"No JSON found in AI response: {ai_response}")
                raise ValueError("No JSON found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Failed to parse: {ai_response}")
            # Attempt to extract information manually
            return self._extract_fallback_response(ai_response)
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            logger.error(f"AI response was: {ai_response}")
            
            # Attempt to extract information manually
            return self._extract_fallback_response(ai_response)
    
    def _validate_ai_response(self, response: Dict[str, Any]) -> bool:
        """Validate that the AI response has the required structure"""
        required_fields = ["risk_score", "risk_description", "geopolitical_summary"]
        
        # Check all required fields exist
        missing_fields = [field for field in required_fields if field not in response]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return False
            
        # Validate risk score is an integer between 1-10
        risk_score = response.get("risk_score")
        if not isinstance(risk_score, int):
            logger.error(f"Risk score is not an integer: {risk_score} (type: {type(risk_score)})")
            return False
            
        if not 1 <= risk_score <= 10:
            logger.error(f"Risk score out of range: {risk_score}")
            return False
            
        # Validate text fields are non-empty strings
        for field in ["risk_description", "geopolitical_summary"]:
            value = response.get(field)
            if not isinstance(value, str):
                logger.error(f"Field {field} is not a string: {value} (type: {type(value)})")
                return False
            if len(value.strip()) < 10:
                logger.error(f"Field {field} too short: {len(value)} chars")
                return False
                
        return True
    
    def _extract_fallback_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract risk assessment info when JSON parsing fails"""
        # Simple keyword-based extraction as fallback
        risk_score = 5  # Default medium risk
        
        # Look for risk indicators in the response
        response_lower = ai_response.lower()
        
        # High-risk geopolitical keywords
        if any(word in response_lower for word in ["war", "conflict", "sanctions", "embargo", "terrorism", "piracy", "critical", "extreme"]):
            risk_score = 9
        elif any(word in response_lower for word in ["high", "significant", "tensions", "unstable", "threat"]):
            risk_score = 7
        elif any(word in response_lower for word in ["moderate", "medium", "caution", "elevated"]):
            risk_score = 5
        elif any(word in response_lower for word in ["low", "minor", "stable", "peaceful"]):
            risk_score = 3
        elif any(word in response_lower for word in ["minimal", "negligible", "secure"]):
            risk_score = 1
        
        return {
            "risk_score": risk_score,
            "risk_description": f"AI assessment parsing failed. Raw response: {ai_response[:500]}...",
            "geopolitical_summary": "Geopolitical analysis incomplete due to parsing error."
        }
    
    def _fallback_risk_assessment(
        self, 
        departure_country_risk: Dict[str, Any],
        destination_country_risk: Dict[str, Any],
        route_analysis: Dict[str, Any],
        news_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide a basic risk assessment when AI service fails"""
        
        # Simple rule-based assessment as fallback
        risk_factors = []
        risk_score = 1
        
        # Check departure country risks
        dept_stability = departure_country_risk.get('political_stability', 5)
        if dept_stability <= 3:
            risk_factors.append("Political instability at departure country")
            risk_score += 3
        elif dept_stability <= 5:
            risk_factors.append("Moderate political concerns at departure")
            risk_score += 1
            
        # Check destination country risks
        dest_stability = destination_country_risk.get('political_stability', 5)
        if dest_stability <= 3:
            risk_factors.append("Political instability at destination country")
            risk_score += 3
        elif dest_stability <= 5:
            risk_factors.append("Moderate political concerns at destination")
            risk_score += 1
        
        # Check for sanctions
        if 'sanctions' in departure_country_risk.get('sanctions_status', '').lower():
            risk_factors.append("Sanctions affecting departure country")
            risk_score += 4
        if 'sanctions' in destination_country_risk.get('sanctions_status', '').lower():
            risk_factors.append("Sanctions affecting destination country")
            risk_score += 4
            
        # Check route chokepoints
        chokepoints = route_analysis.get('chokepoints', [])
        high_risk_chokepoints = ['suez canal', 'strait of hormuz', 'south china sea', 'malacca strait']
        for chokepoint in chokepoints:
            if any(hrcp in chokepoint.lower() for hrcp in high_risk_chokepoints):
                risk_factors.append(f"High-risk chokepoint: {chokepoint}")
                risk_score += 2
                break
        
        # Check recent events
        events = news_analysis.get('events', [])
        if events:
            high_severity_events = [e for e in events if e.get('relevance_score', 0) >= 7]
            if high_severity_events:
                risk_factors.append("High-impact recent geopolitical events")
                risk_score += 2
        
        # Cap the risk score at 10
        risk_score = min(risk_score, 10)
        
        # Generate description
        if not risk_factors:
            description = "No significant geopolitical risks identified. Standard security protocols recommended."
        else:
            description = f"Geopolitical concerns identified: {', '.join(risk_factors)}. Enhanced due diligence and monitoring recommended."
        
        geopolitical_summary = f"Route assessment: {len(chokepoints)} chokepoints, {len(events)} recent events analyzed. Countries: {departure_country_risk.get('country', 'Unknown')} -> {destination_country_risk.get('country', 'Unknown')}."
        
        return {
            "risk_score": risk_score,
            "risk_description": f"[Fallback Assessment] {description}",
            "geopolitical_summary": geopolitical_summary
        }