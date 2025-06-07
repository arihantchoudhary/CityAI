"""
News service for gathering real-time geopolitical intelligence and events
"""

import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import re

from config import get_settings

logger = logging.getLogger(__name__)


class NewsService:
    """Service for gathering real-time geopolitical news and intelligence"""
    
    def __init__(self):
        self.settings = get_settings()
        self.news_cache = {}
        self.session = None
        
        # News source priorities (higher score = more reliable)
        self.source_reliability = {
            'reuters.com': 10,
            'bloomberg.com': 10,
            'ft.com': 9,
            'wsj.com': 9,
            'bbc.com': 8,
            'cnn.com': 7,
            'associated-press': 9,
            'maritimeexecutive.com': 8,
            'tradewinds.no': 8,
            'lloydslist.com': 9,
            'joc.com': 8
        }
    
    async def health_check(self) -> str:
        """Check if news service is operational"""
        try:
            # Simple test to verify news gathering capability
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Test with a simple search
                test_result = await self._search_news(session, "shipping news", max_results=1)
                if test_result:
                    return "healthy"
                else:
                    return "unhealthy (no results)"
        except Exception as e:
            logger.error(f"News service health check failed: {str(e)}")
            return f"unhealthy (error: {str(e)})"
    
    async def get_route_intelligence(
        self,
        departure_country: str,
        destination_country: str,
        chokepoints: List[str],
        goods_type: str
    ) -> Dict[str, Any]:
        """
        Gather comprehensive geopolitical intelligence for a shipping route
        
        Args:
            departure_country: Departure country name
            destination_country: Destination country name
            chokepoints: List of critical chokepoints on the route
            goods_type: Type of goods being shipped
            
        Returns:
            Dict containing events, sentiment analysis, and intelligence summary
        """
        try:
            # Check cache first
            cache_key = f"{departure_country}_{destination_country}_{hash(str(chokepoints))}_{goods_type}"
            if cache_key in self.news_cache:
                cached_time = self.news_cache[cache_key].get('cached_at')
                if cached_time and (datetime.utcnow() - cached_time).seconds < 1800:  # 30 min cache
                    logger.info("Returning cached news intelligence")
                    return self.news_cache[cache_key]['data']
            
            logger.info(f"Gathering geopolitical intelligence for {departure_country} -> {destination_country}")
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            ) as session:
                
                # Gather intelligence from multiple angles
                tasks = [
                    self._get_country_news(session, departure_country),
                    self._get_country_news(session, destination_country),
                    self._get_chokepoint_news(session, chokepoints),
                    self._get_trade_news(session, departure_country, destination_country),
                    self._get_maritime_security_news(session),
                    self._get_sanctions_news(session, departure_country, destination_country),
                    self._get_goods_specific_news(session, goods_type)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Combine and analyze results
                all_events = []
                for result in results:
                    if isinstance(result, list):
                        all_events.extend(result)
                    elif isinstance(result, Exception):
                        logger.warning(f"News gathering task failed: {str(result)}")
                
                # Process and prioritize events
                processed_events = self._process_and_rank_events(
                    all_events, departure_country, destination_country, chokepoints, goods_type
                )
                
                # Analyze sentiment and confidence
                sentiment_analysis = self._analyze_sentiment(processed_events)
                
                intelligence = {
                    'events': processed_events[:10],  # Top 10 most relevant
                    'sentiment': sentiment_analysis['overall_sentiment'],
                    'confidence': sentiment_analysis['confidence_level'],
                    'summary': self._generate_intelligence_summary(processed_events),
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                # Cache the result
                self.news_cache[cache_key] = {
                    'data': intelligence,
                    'cached_at': datetime.utcnow()
                }
                
                logger.info(f"Gathered {len(processed_events)} relevant geopolitical events")
                return intelligence
                
        except Exception as e:
            logger.error(f"Route intelligence gathering failed: {str(e)}")
            return self._get_fallback_intelligence(departure_country, destination_country)
    
    async def _get_country_news(self, session: aiohttp.ClientSession, country: str) -> List[Dict[str, Any]]:
        """Get recent news about a specific country"""
        try:
            search_terms = [
                f"{country} political news",
                f"{country} sanctions trade",
                f"{country} security threat",
                f"{country} port strike",
                f"{country} diplomatic relations"
            ]
            
            events = []
            for term in search_terms:
                results = await self._search_news(session, term, max_results=3)
                events.extend(results)
            
            return events
            
        except Exception as e:
            logger.error(f"Country news gathering failed for {country}: {str(e)}")
            return []
    
    async def _get_chokepoint_news(self, session: aiohttp.ClientSession, chokepoints: List[str]) -> List[Dict[str, Any]]:
        """Get news about specific maritime chokepoints"""
        try:
            events = []
            
            for chokepoint in chokepoints:
                search_terms = [
                    f"{chokepoint} shipping",
                    f"{chokepoint} security",
                    f"{chokepoint} blockage",
                    f"{chokepoint} conflict"
                ]
                
                for term in search_terms:
                    results = await self._search_news(session, term, max_results=2)
                    for event in results:
                        event['chokepoint_related'] = chokepoint
                    events.extend(results)
            
            return events
            
        except Exception as e:
            logger.error(f"Chokepoint news gathering failed: {str(e)}")
            return []
    
    async def _get_trade_news(self, session: aiohttp.ClientSession, country1: str, country2: str) -> List[Dict[str, Any]]:
        """Get bilateral trade and diplomatic news"""
        try:
            search_terms = [
                f"{country1} {country2} trade relations",
                f"{country1} {country2} diplomatic",
                f"{country1} {country2} sanctions",
                f"{country1} {country2} dispute"
            ]
            
            events = []
            for term in search_terms:
                results = await self._search_news(session, term, max_results=2)
                for event in results:
                    event['bilateral_relevance'] = f"{country1}-{country2}"
                events.extend(results)
            
            return events
            
        except Exception as e:
            logger.error(f"Trade news gathering failed: {str(e)}")
            return []
    
    async def _get_maritime_security_news(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Get general maritime security news"""
        try:
            search_terms = [
                "maritime security threats",
                "shipping piracy attacks",
                "naval incidents commercial",
                "port security breach",
                "maritime terrorism"
            ]
            
            events = []
            for term in search_terms:
                results = await self._search_news(session, term, max_results=2)
                for event in results:
                    event['security_related'] = True
                events.extend(results)
            
            return events
            
        except Exception as e:
            logger.error(f"Maritime security news gathering failed: {str(e)}")
            return []
    
    async def _get_sanctions_news(self, session: aiohttp.ClientSession, country1: str, country2: str) -> List[Dict[str, Any]]:
        """Get sanctions and trade restriction news"""
        try:
            search_terms = [
                f"new sanctions {country1}",
                f"new sanctions {country2}",
                "trade restrictions shipping",
                "export controls update",
                "embargo shipping impact"
            ]
            
            events = []
            for term in search_terms:
                results = await self._search_news(session, term, max_results=2)
                for event in results:
                    event['sanctions_related'] = True
                events.extend(results)
            
            return events
            
        except Exception as e:
            logger.error(f"Sanctions news gathering failed: {str(e)}")
            return []
    
    async def _get_goods_specific_news(self, session: aiohttp.ClientSession, goods_type: str) -> List[Dict[str, Any]]:
        """Get news related to specific goods type"""
        try:
            if goods_type.lower() in ['electronics', 'technology', 'semiconductors']:
                search_terms = [
                    "technology export controls",
                    "semiconductor trade restrictions",
                    "electronics trade war"
                ]
            elif goods_type.lower() in ['energy', 'oil', 'gas']:
                search_terms = [
                    "energy sanctions",
                    "oil trade restrictions",
                    "gas export controls"
                ]
            elif goods_type.lower() in ['military', 'defense']:
                search_terms = [
                    "defense export controls",
                    "military equipment restrictions",
                    "arms embargo"
                ]
            else:
                search_terms = [
                    f"{goods_type} trade restrictions",
                    f"{goods_type} export controls"
                ]
            
            events = []
            for term in search_terms:
                results = await self._search_news(session, term, max_results=2)
                for event in results:
                    event['goods_specific'] = goods_type
                events.extend(results)
            
            return events
            
        except Exception as e:
            logger.error(f"Goods-specific news gathering failed: {str(e)}")
            return []
    
    async def _search_news(self, session: aiohttp.ClientSession, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for news using web search APIs or scraping
        This is a simplified implementation - in production, use proper news APIs
        """
        try:
            # For demo purposes, simulate news search results
            # In production, integrate with real news APIs like NewsAPI, Bing News, etc.
            
            # Simulate realistic news results based on query
            simulated_results = self._generate_simulated_news(query, max_results)
            
            # Add realistic metadata
            for result in simulated_results:
                result.update({
                    'search_query': query,
                    'fetched_at': datetime.utcnow().isoformat(),
                    'source_reliability': self._get_source_reliability(result.get('source', '')),
                    'relevance_score': self._calculate_relevance_score(result, query)
                })
            
            return simulated_results
            
        except Exception as e:
            logger.error(f"News search failed for query '{query}': {str(e)}")
            return []
    
    def _generate_simulated_news(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate realistic simulated news for demo purposes"""
        # This would be replaced with actual news API calls in production
        
        news_templates = {
            'political': [
                {
                    'title': 'Political tensions rise in {country} ahead of trade negotiations',
                    'summary': 'Diplomatic sources report increased political tensions that could impact trade relations.',
                    'source': 'reuters.com',
                    'severity': 'medium'
                },
                {
                    'title': 'Government stability concerns in {country} affect market confidence',
                    'summary': 'Recent political developments raise questions about regulatory continuity.',
                    'source': 'bloomberg.com',
                    'severity': 'medium'
                }
            ],
            'sanctions': [
                {
                    'title': 'New trade restrictions announced affecting {country} exports',
                    'summary': 'Additional trade controls implemented on technology and dual-use goods.',
                    'source': 'ft.com',
                    'severity': 'high'
                },
                {
                    'title': 'Sanctions compliance updates for shipping industry',
                    'summary': 'Maritime trade faces new compliance requirements under updated sanctions regime.',
                    'source': 'lloydslist.com',
                    'severity': 'high'
                }
            ],
            'security': [
                {
                    'title': 'Maritime security alert issued for {chokepoint}',
                    'summary': 'Increased naval activity and security concerns in critical shipping lane.',
                    'source': 'maritimeexecutive.com',
                    'severity': 'high'
                },
                {
                    'title': 'Piracy incidents reported in {region} shipping routes',
                    'summary': 'Commercial vessels advised to maintain enhanced security protocols.',
                    'source': 'tradewinds.no',
                    'severity': 'medium'
                }
            ],
            'trade': [
                {
                    'title': 'Trade relations between {country1} and {country2} show signs of improvement',
                    'summary': 'Diplomatic progress may lead to reduced trade barriers and enhanced cooperation.',
                    'source': 'wsj.com',
                    'severity': 'low'
                },
                {
                    'title': 'Commercial shipping rates affected by {factor}',
                    'summary': 'Market analysis shows impact on freight costs and route preferences.',
                    'source': 'joc.com',
                    'severity': 'medium'
                }
            ]
        }
        
        # Select appropriate templates based on query
        selected_templates = []
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['political', 'government', 'diplomatic']):
            selected_templates.extend(news_templates['political'])
        if any(word in query_lower for word in ['sanctions', 'embargo', 'restrictions']):
            selected_templates.extend(news_templates['sanctions'])
        if any(word in query_lower for word in ['security', 'piracy', 'threat', 'conflict']):
            selected_templates.extend(news_templates['security'])
        if any(word in query_lower for word in ['trade', 'relations', 'bilateral']):
            selected_templates.extend(news_templates['trade'])
        
        # If no specific category, use general templates
        if not selected_templates:
            selected_templates = news_templates['trade']
        
        # Generate results
        results = []
        for i, template in enumerate(selected_templates[:max_results]):
            result = template.copy()
            
            # Add realistic timestamp (within last 30 days)
            import random
            days_ago = random.randint(1, 30)
            result['published_date'] = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
            
            # Add URL
            result['url'] = f"https://{result['source']}/article-{random.randint(1000, 9999)}"
            
            results.append(result)
        
        return results
    
    def _get_source_reliability(self, source: str) -> int:
        """Get reliability score for a news source"""
        for domain, score in self.source_reliability.items():
            if domain in source.lower():
                return score
        return 5  # Default reliability score
    
    def _calculate_relevance_score(self, article: Dict[str, Any], query: str) -> int:
        """Calculate relevance score for an article"""
        score = 5  # Base score
        
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        query_words = query.lower().split()
        
        # Boost score for query word matches
        for word in query_words:
            if word in title:
                score += 2
            if word in summary:
                score += 1
        
        # Boost for severity
        severity = article.get('severity', 'medium')
        if severity == 'high':
            score += 2
        elif severity == 'medium':
            score += 1
        
        # Boost for source reliability
        reliability = article.get('source_reliability', 5)
        if reliability >= 9:
            score += 2
        elif reliability >= 7:
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _process_and_rank_events(
        self,
        events: List[Dict[str, Any]],
        departure_country: str,
        destination_country: str,
        chokepoints: List[str],
        goods_type: str
    ) -> List[Dict[str, Any]]:
        """Process and rank events by relevance"""
        
        # Remove duplicates based on title similarity
        unique_events = self._deduplicate_events(events)
        
        # Enhance relevance scoring
        for event in unique_events:
            event['final_relevance_score'] = self._calculate_final_relevance(
                event, departure_country, destination_country, chokepoints, goods_type
            )
        
        # Sort by relevance score (descending)
        ranked_events = sorted(unique_events, key=lambda x: x.get('final_relevance_score', 0), reverse=True)
        
        return ranked_events
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on title similarity"""
        unique_events = []
        seen_titles = set()
        
        for event in events:
            title = event.get('title', '').lower()
            
            # Simple deduplication - could be improved with fuzzy matching
            title_key = re.sub(r'[^\w\s]', '', title)[:50]  # First 50 chars, alphanumeric only
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_events.append(event)
        
        return unique_events
    
    def _calculate_final_relevance(
        self,
        event: Dict[str, Any],
        departure_country: str,
        destination_country: str,
        chokepoints: List[str],
        goods_type: str
    ) -> int:
        """Calculate final relevance score considering route specifics"""
        base_score = event.get('relevance_score', 5)
        
        title = event.get('title', '').lower()
        summary = event.get('summary', '').lower()
        
        # Boost for direct country mentions
        if departure_country.lower() in title or departure_country.lower() in summary:
            base_score += 3
        if destination_country.lower() in title or destination_country.lower() in summary:
            base_score += 3
        
        # Boost for chokepoint mentions
        for chokepoint in chokepoints:
            if chokepoint.lower() in title or chokepoint.lower() in summary:
                base_score += 4
                break
        
        # Boost for goods-specific relevance
        if goods_type.lower() in title or goods_type.lower() in summary:
            base_score += 2
        
        # Boost for recent events (last 7 days)
        published_date = event.get('published_date', '')
        if published_date:
            try:
                pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                days_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).days
                if days_old <= 7:
                    base_score += 2
                elif days_old <= 30:
                    base_score += 1
            except:
                pass
        
        # Severity boost
        severity = event.get('severity', 'medium')
        if severity == 'high':
            base_score += 3
        elif severity == 'medium':
            base_score += 1
        
        return min(base_score, 10)
    
    def _analyze_sentiment(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall sentiment of events"""
        if not events:
            return {
                'overall_sentiment': 'neutral',
                'confidence_level': 'low'
            }
        
        sentiment_scores = []
        
        for event in events:
            title = event.get('title', '').lower()
            summary = event.get('summary', '').lower()
            
            # Simple keyword-based sentiment analysis
            negative_keywords = ['conflict', 'threat', 'sanctions', 'piracy', 'attack', 'tensions', 'dispute', 'crisis']
            positive_keywords = ['improvement', 'agreement', 'cooperation', 'stable', 'secure', 'peaceful', 'progress']
            
            score = 0
            for keyword in negative_keywords:
                if keyword in title or keyword in summary:
                    score -= 1
            
            for keyword in positive_keywords:
                if keyword in title or keyword in summary:
                    score += 1
            
            sentiment_scores.append(score)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        if avg_sentiment < -0.5:
            overall_sentiment = 'negative'
        elif avg_sentiment > 0.5:
            overall_sentiment = 'positive'
        else:
            overall_sentiment = 'neutral'
        
        # Confidence based on number of events and source reliability
        avg_reliability = sum(event.get('source_reliability', 5) for event in events) / len(events)
        
        if len(events) >= 5 and avg_reliability >= 7:
            confidence = 'high'
        elif len(events) >= 3 and avg_reliability >= 5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence_level': confidence
        }
    
    def _generate_intelligence_summary(self, events: List[Dict[str, Any]]) -> str:
        """Generate a concise intelligence summary"""
        if not events:
            return "No significant geopolitical events identified affecting this route."
        
        high_impact_events = [e for e in events if e.get('final_relevance_score', 0) >= 7]
        
        if high_impact_events:
            summary = f"Intelligence identifies {len(high_impact_events)} high-impact events affecting route security and trade conditions. "
            
            # Categorize events
            security_events = [e for e in high_impact_events if e.get('security_related')]
            sanctions_events = [e for e in high_impact_events if e.get('sanctions_related')]
            chokepoint_events = [e for e in high_impact_events if e.get('chokepoint_related')]
            
            if security_events:
                summary += f"Security concerns: {len(security_events)} incidents. "
            if sanctions_events:
                summary += f"Trade restrictions: {len(sanctions_events)} updates. "
            if chokepoint_events:
                summary += f"Chokepoint alerts: {len(chokepoint_events)} issues. "
            
            summary += "Recommend enhanced monitoring and contingency planning."
        else:
            summary = f"Monitoring {len(events)} geopolitical developments. Current threat level appears manageable with standard security protocols."
        
        return summary
    
    def _get_fallback_intelligence(self, departure_country: str, destination_country: str) -> Dict[str, Any]:
        """Provide fallback intelligence when news gathering fails"""
        return {
            'events': [],
            'sentiment': 'neutral',
            'confidence': 'low',
            'summary': f"Unable to gather current intelligence for {departure_country} -> {destination_country} route. Manual intelligence review recommended.",
            'last_updated': datetime.utcnow().isoformat()
        }