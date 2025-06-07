"""
Monitoring and analytics utilities for Geopolitical Risk Assessment API
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics
from collections import defaultdict, deque
import csv


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: datetime
    endpoint: str
    method: str
    response_time: float
    status_code: int
    risk_score: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class SystemHealth:
    """System health metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time_avg: float
    request_count: int
    error_rate: float
    cache_hit_rate: float


class APIMonitor:
    """Comprehensive API monitoring and analytics"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.metrics: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.health_metrics: deque = deque(maxlen=1000)
        self.is_monitoring = False
        self.logger = logging.getLogger(__name__)
    
    async def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring"""
        self.is_monitoring = True
        self.logger.info(f"Starting API monitoring (interval: {interval}s)")
        
        while self.is_monitoring:
            try:
                health_data = await self.collect_health_metrics()
                self.health_metrics.append(health_data)
                
                # Log summary
                self.logger.info(
                    f"Health Check - Response Time: {health_data.response_time_avg:.2f}s, "
                    f"Error Rate: {health_data.error_rate:.1%}"
                )
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.logger.info("Monitoring stopped")
    
    async def collect_health_metrics(self) -> SystemHealth:
        """Collect current system health metrics"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(f"{self.base_url}/health")
                response_time = time.time() - start_time
                
                # Calculate metrics from recent data
                recent_metrics = list(self.metrics)[-100:]  # Last 100 requests
                
                avg_response_time = statistics.mean(
                    [m.response_time for m in recent_metrics]
                ) if recent_metrics else response_time
                
                error_rate = len([m for m in recent_metrics if m.status_code >= 400]) / len(recent_metrics) if recent_metrics else 0
                
                return SystemHealth(
                    timestamp=datetime.utcnow(),
                    cpu_usage=0.0,  # Would need psutil for real CPU monitoring
                    memory_usage=0.0,  # Would need psutil for real memory monitoring
                    response_time_avg=avg_response_time,
                    request_count=len(recent_metrics),
                    error_rate=error_rate,
                    cache_hit_rate=0.0  # Would need Redis monitoring
                )
                
        except Exception as e:
            self.logger.error(f"Health metrics collection failed: {str(e)}")
            return SystemHealth(
                timestamp=datetime.utcnow(),
                cpu_usage=0.0,
                memory_usage=0.0,
                response_time_avg=999.0,  # High response time indicates failure
                request_count=0,
                error_rate=1.0,  # 100% error rate if we can't connect
                cache_hit_rate=0.0
            )
    
    async def test_endpoint_performance(self, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 10):
        """Test specific endpoint performance"""
        self.logger.info(f"Testing {method} {endpoint} performance ({iterations} iterations)")
        
        metrics = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    if method.upper() == "GET":
                        response = await session.get(f"{self.base_url}{endpoint}")
                    elif method.upper() == "POST":
                        response = await session.post(f"{self.base_url}{endpoint}", json=data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    response_time = time.time() - start_time
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    metric = PerformanceMetric(
                        timestamp=datetime.utcnow(),
                        endpoint=endpoint,
                        method=method.upper(),
                        response_time=response_time,
                        status_code=response.status,
                        risk_score=response_data.get('risk_score') if 'risk_score' in response_data else None
                    )
                    
                    metrics.append(metric)
                    self.metrics.append(metric)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    metric = PerformanceMetric(
                        timestamp=datetime.utcnow(),
                        endpoint=endpoint,
                        method=method.upper(),
                        response_time=999.0,
                        status_code=500,
                        error_message=str(e)
                    )
                    metrics.append(metric)
                    self.metrics.append(metric)
        
        # Analyze results
        response_times = [m.response_time for m in metrics if m.status_code < 400]
        success_rate = len(response_times) / len(metrics)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
        else:
            avg_time = median_time = min_time = max_time = 0
        
        self.logger.info(f"Performance Results for {method} {endpoint}:")
        self.logger.info(f"  Success Rate: {success_rate:.1%}")
        self.logger.info(f"  Avg Response Time: {avg_time:.2f}s")
        self.logger.info(f"  Median Response Time: {median_time:.2f}s")
        self.logger.info(f"  Min/Max Response Time: {min_time:.2f}s / {max_time:.2f}s")
        
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "success_rate": success_rate,
            "avg_response_time": avg_time,
            "median_response_time": median_time,
            "min_response_time": min_time,
            "max_response_time": max_time,
            "metrics": [asdict(m) for m in metrics]
        }
    
    async def load_test(self, concurrent_users: int = 5, duration_minutes: int = 5):
        """Run load test with concurrent users"""
        self.logger.info(f"Starting load test: {concurrent_users} concurrent users for {duration_minutes} minutes")
        
        # Test data for different endpoints
        test_scenarios = [
            {
                "endpoint": "/health",
                "method": "GET",
                "weight": 0.3
            },
            {
                "endpoint": "/ports/search",
                "method": "GET",
                "params": "?query=Singapore&limit=5",
                "weight": 0.2
            },
            {
                "endpoint": "/assess-geopolitical-risk",
                "method": "POST",
                "data": {
                    "departure_port": "Singapore",
                    "destination_port": "Rotterdam",
                    "departure_date": "2025-06-15",
                    "carrier_name": "Maersk",
                    "goods_type": "containers"
                },
                "weight": 0.5
            }
        ]
        
        end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        tasks = []
        
        # Create concurrent user tasks
        for user_id in range(concurrent_users):
            task = asyncio.create_task(
                self._simulate_user(user_id, test_scenarios, end_time)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Analyze load test results
        return self.analyze_load_test_results(duration_minutes)
    
    async def _simulate_user(self, user_id: int, scenarios: List[Dict], end_time: datetime):
        """Simulate a single user's behavior"""
        import random
        
        async with aiohttp.ClientSession() as session:
            while datetime.utcnow() < end_time:
                # Choose random scenario based on weights
                scenario = random.choices(
                    scenarios,
                    weights=[s['weight'] for s in scenarios]
                )[0]
                
                start_time = time.time()
                
                try:
                    if scenario['method'] == 'GET':
                        url = f"{self.base_url}{scenario['endpoint']}"
                        if 'params' in scenario:
                            url += scenario['params']
                        response = await session.get(url)
                    elif scenario['method'] == 'POST':
                        response = await session.post(
                            f"{self.base_url}{scenario['endpoint']}",
                            json=scenario['data']
                        )
                    
                    response_time = time.time() - start_time
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    metric = PerformanceMetric(
                        timestamp=datetime.utcnow(),
                        endpoint=scenario['endpoint'],
                        method=scenario['method'],
                        response_time=response_time,
                        status_code=response.status,
                        risk_score=response_data.get('risk_score')
                    )
                    
                    self.metrics.append(metric)
                    
                except Exception as e:
                    metric = PerformanceMetric(
                        timestamp=datetime.utcnow(),
                        endpoint=scenario['endpoint'],
                        method=scenario['method'],
                        response_time=999.0,
                        status_code=500,
                        error_message=str(e)
                    )
                    self.metrics.append(metric)
                
                # Random delay between requests (0.5 to 3 seconds)
                await asyncio.sleep(random.uniform(0.5, 3.0))
    
    def analyze_load_test_results(self, duration_minutes: int) -> Dict[str, Any]:
        """Analyze load test results"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes + 1)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"error": "No metrics collected during load test"}
        
        # Overall statistics
        total_requests = len(recent_metrics)
        successful_requests = len([m for m in recent_metrics if m.status_code < 400])
        success_rate = successful_requests / total_requests
        
        response_times = [m.response_time for m in recent_metrics if m.status_code < 400]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = max_response_time = 0
        
        # Per-endpoint analysis
        endpoint_stats = defaultdict(list)
        for metric in recent_metrics:
            endpoint_stats[metric.endpoint].append(metric)
        
        endpoint_analysis = {}
        for endpoint, metrics in endpoint_stats.items():
            success_count = len([m for m in metrics if m.status_code < 400])
            endpoint_analysis[endpoint] = {
                "total_requests": len(metrics),
                "successful_requests": success_count,
                "success_rate": success_count / len(metrics),
                "avg_response_time": statistics.mean([m.response_time for m in metrics if m.status_code < 400]) if success_count > 0 else 0
            }
        
        # Requests per second
        rps = total_requests / (duration_minutes * 60)
        
        results = {
            "duration_minutes": duration_minutes,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "requests_per_second": rps,
            "avg_response_time": avg_response_time,
            "median_response_time": median_response_time,
            "p95_response_time": p95_response_time,
            "max_response_time": max_response_time,
            "endpoint_analysis": endpoint_analysis
        }
        
        self.logger.info("Load Test Results:")
        self.logger.info(f"  Total Requests: {total_requests}")
        self.logger.info(f"  Success Rate: {success_rate:.1%}")
        self.logger.info(f"  Requests/Second: {rps:.2f}")
        self.logger.info(f"  Avg Response Time: {avg_response_time:.2f}s")
        self.logger.info(f"  95th Percentile: {p95_response_time:.2f}s")
        
        return results
    
    def export_metrics(self, filename: str = None):
        """Export metrics to CSV file"""
        if not filename:
            filename = f"metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            if not self.metrics:
                self.logger.warning("No metrics to export")
                return
            
            fieldnames = ['timestamp', 'endpoint', 'method', 'response_time', 'status_code', 'risk_score', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for metric in self.metrics:
                writer.writerow(asdict(metric))
        
        self.logger.info(f"Metrics exported to {filename}")
        return filename
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"error": f"No metrics found for the last {hours} hours"}
        
        # Calculate summary statistics
        total_requests = len(recent_metrics)
        successful_requests = len([m for m in recent_metrics if m.status_code < 400])
        error_requests = total_requests - successful_requests
        
        response_times = [m.response_time for m in recent_metrics if m.status_code < 400]
        
        # Risk score analysis
        risk_scores = [m.risk_score for m in recent_metrics if m.risk_score is not None]
        
        summary = {
            "time_period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_requests": error_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "requests_per_hour": total_requests / hours if hours > 0 else 0
        }
        
        if risk_scores:
            summary["risk_score_analysis"] = {
                "total_assessments": len(risk_scores),
                "avg_risk_score": statistics.mean(risk_scores),
                "median_risk_score": statistics.median(risk_scores),
                "high_risk_assessments": len([r for r in risk_scores if r >= 7]),
                "low_risk_assessments": len([r for r in risk_scores if r <= 3])
            }
        
        return summary


class AlertManager:
    """Alert management for monitoring"""
    
    def __init__(self, monitor: APIMonitor):
        self.monitor = monitor
        self.alert_thresholds = {
            "response_time": 10.0,  # seconds
            "error_rate": 0.1,      # 10%
            "success_rate": 0.95    # 95%
        }
        self.alerts_sent = set()
        self.logger = logging.getLogger(__name__)
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        if not self.monitor.health_metrics:
            return alerts
        
        latest_health = self.monitor.health_metrics[-1]
        
        # Response time alert
        if latest_health.response_time_avg > self.alert_thresholds["response_time"]:
            alert = {
                "type": "HIGH_RESPONSE_TIME",
                "severity": "WARNING",
                "message": f"Average response time is {latest_health.response_time_avg:.2f}s (threshold: {self.alert_thresholds['response_time']}s)",
                "timestamp": latest_health.timestamp
            }
            alerts.append(alert)
        
        # Error rate alert
        if latest_health.error_rate > self.alert_thresholds["error_rate"]:
            alert = {
                "type": "HIGH_ERROR_RATE",
                "severity": "CRITICAL",
                "message": f"Error rate is {latest_health.error_rate:.1%} (threshold: {self.alert_thresholds['error_rate']:.1%})",
                "timestamp": latest_health.timestamp
            }
            alerts.append(alert)
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]):
        """Send alert (implement your preferred notification method)"""
        alert_key = f"{alert['type']}_{alert['timestamp'].strftime('%H')}"
        
        if alert_key not in self.alerts_sent:
            self.logger.warning(f"ALERT [{alert['severity']}]: {alert['message']}")
            self.alerts_sent.add(alert_key)
            
            # Here you could implement:
            # - Email notifications
            # - Slack/Discord webhooks
            # - SMS alerts
            # - PagerDuty integration


async def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Geopolitical Risk Assessment API")
    parser.add_argument("--url", default="http://localhost:8001", help="API base URL")
    parser.add_argument("--command", choices=["monitor", "test", "load", "summary"], default="monitor", help="Command to run")
    parser.add_argument("--duration", type=int, default=5, help="Duration for load test (minutes)")
    parser.add_argument("--users", type=int, default=5, help="Concurrent users for load test")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval (seconds)")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    monitor = APIMonitor(args.url)
    
    if args.command == "monitor":
        print(f"🔍 Starting continuous monitoring of {args.url}")
        print("Press Ctrl+C to stop")
        try:
            await monitor.start_monitoring(args.interval)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("\n✅ Monitoring stopped")
    
    elif args.command == "test":
        print(f"🧪 Testing API performance at {args.url}")
        
        # Test main endpoint
        test_data = {
            "departure_port": "Singapore",
            "destination_port": "Rotterdam", 
            "departure_date": "2025-06-15",
            "carrier_name": "Maersk",
            "goods_type": "containers"
        }
        
        results = await monitor.test_endpoint_performance(
            "/assess-geopolitical-risk", 
            "POST", 
            test_data, 
            iterations=5
        )
        
        print("\n📊 Test Results:")
        print(f"Success Rate: {results['success_rate']:.1%}")
        print(f"Average Response Time: {results['avg_response_time']:.2f}s")
    
    elif args.command == "load":
        print(f"⚡ Starting load test: {args.users} users for {args.duration} minutes")
        results = await monitor.load_test(args.users, args.duration)
        
        print("\n📈 Load Test Results:")
        print(f"Total Requests: {results['total_requests']}")
        print(f"Success Rate: {results['success_rate']:.1%}")
        print(f"Requests/Second: {results['requests_per_second']:.2f}")
        print(f"Average Response Time: {results['avg_response_time']:.2f}s")
    
    elif args.command == "summary":
        print(f"📋 Performance Summary for {args.url}")
        summary = monitor.get_performance_summary(hours=24)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
        else:
            print(f"Total Requests (24h): {summary['total_requests']}")
            print(f"Success Rate: {summary['success_rate']:.1%}")
            print(f"Average Response Time: {summary['avg_response_time']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())