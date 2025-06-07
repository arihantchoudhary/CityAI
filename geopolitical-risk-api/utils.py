"""
Utility scripts and helper tools for Geopolitical Risk Assessment API
"""

import asyncio
import json
import csv
import argparse
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import logging
import requests
from pathlib import Path

# Try to import the client SDK
try:
    from client_sdk import GeopoliticalRiskClient, assess_shipping_risk
except ImportError:
    print("Warning: client_sdk.py not found. Some features may not work.")
    GeopoliticalRiskClient = None


class RiskReportGenerator:
    """Generate comprehensive risk reports"""
    
    def __init__(self, api_url: str = "http://localhost:8001", api_key: Optional[str] = None):
        self.api_url = api_url
        self.api_key = api_key
        if GeopoliticalRiskClient:
            self.client = GeopoliticalRiskClient(api_url, api_key)
        else:
            self.client = None
    
    def generate_route_report(
        self,
        departure_port: str,
        destination_port: str,
        departure_date: str,
        carrier_name: str,
        goods_type: str,
        output_file: Optional[str] = None
    ) -> str:
        """Generate detailed route risk report"""
        if not self.client:
            raise RuntimeError("Client SDK not available")
        
        try:
            # Get risk assessment
            assessment = self.client.assess_risk(
                departure_port, destination_port, departure_date, carrier_name, goods_type
            )
            
            # Generate report
            report = self._create_route_report(assessment, {
                "departure_port": departure_port,
                "destination_port": destination_port,
                "departure_date": departure_date,
                "carrier_name": carrier_name,
                "goods_type": goods_type
            })
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(report)
                print(f"Report saved to: {output_file}")
            else:
                print(report)
            
            return report
            
        except Exception as e:
            error_msg = f"Failed to generate report: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _create_route_report(self, assessment, route_info: Dict[str, str]) -> str:
        """Create formatted route report"""
        report = f"""
=============================================================================
                    GEOPOLITICAL RISK ASSESSMENT REPORT
=============================================================================

Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

ROUTE INFORMATION
-----------------
Departure Port:     {route_info['departure_port']}
Destination Port:   {route_info['destination_port']}
Departure Date:     {route_info['departure_date']}
Carrier:           {route_info['carrier_name']}
Cargo Type:        {route_info['goods_type']}
Estimated Transit: {assessment.travel_days} days

RISK ASSESSMENT SUMMARY
-----------------------
Overall Risk Score: {assessment.risk_score}/10 ({assessment.risk_level})
{'⚠️  HIGH RISK ROUTE' if assessment.is_high_risk else '✅ ACCEPTABLE RISK LEVEL'}

Risk Description:
{assessment.risk_description}

Geopolitical Summary:
{assessment.geopolitical_summary}

COUNTRY RISK PROFILES
---------------------

Departure Country: {assessment.departure_country_risk['country']}
- Political Stability: {assessment.departure_country_risk['political_stability']}/10
- Trade Freedom: {assessment.departure_country_risk['trade_freedom']}/100
- Security Threat: {assessment.departure_country_risk['security_threat']}
- Sanctions Status: {assessment.departure_country_risk['sanctions_status']}
- Port Security: {assessment.departure_country_risk['port_security']}
- Cargo Restrictions: {assessment.departure_country_risk['cargo_restrictions']}

Destination Country: {assessment.destination_country_risk['country']}
- Political Stability: {assessment.destination_country_risk['political_stability']}/10
- Trade Freedom: {assessment.destination_country_risk['trade_freedom']}/100
- Security Threat: {assessment.destination_country_risk['security_threat']}
- Sanctions Status: {assessment.destination_country_risk['sanctions_status']}
- Port Security: {assessment.destination_country_risk['port_security']}
- Cargo Restrictions: {assessment.destination_country_risk['cargo_restrictions']}

ROUTE ANALYSIS
--------------
Distance: {assessment.route_analysis['distance_km']} km
Primary Shipping Lanes: {assessment.route_analysis['shipping_lanes']}

Critical Chokepoints:
{chr(10).join(['- ' + cp for cp in assessment.chokepoints]) if assessment.chokepoints else 'None identified'}

Security Risk Zones:
{chr(10).join(['- ' + sz for sz in assessment.security_zones]) if assessment.security_zones else 'None identified'}

Seasonal Factors: {assessment.route_analysis['seasonal_factors']}
Alternative Routes: {assessment.route_analysis['alternative_routes']}
Goods-Specific Risks: {assessment.route_analysis['goods_specific_risks']}

RECENT INTELLIGENCE
-------------------
Total Events Monitored: {len(assessment.recent_events)}
High-Impact Events: {len(assessment.high_impact_events)}

"""
        
        # Add recent events details
        if assessment.recent_events:
            report += "Recent Events:\n"
            for i, event in enumerate(assessment.recent_events[:5], 1):  # Top 5 events
                report += f"\n{i}. {event['title']}"
                report += f"\n   Source: {event['source']}"
                report += f"\n   Relevance: {event['relevance_score']}/10"
                report += f"\n   Summary: {event['summary'][:200]}..."
                if i < len(assessment.recent_events[:5]):
                    report += "\n"
        
        report += f"""

RECOMMENDATIONS
---------------
"""
        
        if assessment.risk_score >= 8:
            report += """
🚨 CRITICAL RISK - IMMEDIATE ACTION REQUIRED
- Consider postponing shipment until conditions improve
- Implement maximum security protocols
- Arrange for armed escort/security services
- Monitor situation continuously
- Have contingency plans for route changes
"""
        elif assessment.risk_score >= 6:
            report += """
⚠️  ELEVATED RISK - ENHANCED PRECAUTIONS RECOMMENDED
- Implement enhanced security measures
- Monitor geopolitical developments closely
- Prepare contingency routing plans
- Consider cargo insurance adjustments
- Coordinate with carrier security teams
"""
        else:
            report += """
✅ ACCEPTABLE RISK - STANDARD PROTOCOLS APPLY
- Follow standard security procedures
- Monitor routine intelligence updates
- Maintain normal operational protocols
- Standard cargo insurance sufficient
"""
        
        report += f"""

DISCLAIMER
----------
This assessment is based on current available information and AI analysis.
Geopolitical situations can change rapidly. This report should be used as
one factor in shipping decisions alongside other intelligence sources.

Report ID: {assessment.assessment_timestamp.strftime('%Y%m%d_%H%M%S')}
=============================================================================
"""
        return report
    
    def generate_bulk_report(self, routes_file: str, output_dir: str = "reports"):
        """Generate reports for multiple routes from CSV file"""
        if not self.client:
            raise RuntimeError("Client SDK not available")
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Read routes from CSV
        routes = []
        with open(routes_file, 'r') as f:
            reader = csv.DictReader(f)
            routes = list(reader)
        
        print(f"Processing {len(routes)} routes...")
        
        summary_data = []
        
        for i, route in enumerate(routes, 1):
            print(f"Processing route {i}/{len(routes)}: {route['departure_port']} -> {route['destination_port']}")
            
            try:
                # Generate individual report
                output_file = os.path.join(
                    output_dir, 
                    f"risk_report_{route['departure_port']}_{route['destination_port']}_{datetime.now().strftime('%Y%m%d')}.txt"
                )
                
                report = self.generate_route_report(
                    route['departure_port'],
                    route['destination_port'], 
                    route['departure_date'],
                    route['carrier_name'],
                    route['goods_type'],
                    output_file
                )
                
                # Collect summary data
                assessment = self.client.assess_risk(
                    route['departure_port'],
                    route['destination_port'],
                    route['departure_date'],
                    route['carrier_name'],
                    route['goods_type']
                )
                
                summary_data.append({
                    'route': f"{route['departure_port']} -> {route['destination_port']}",
                    'risk_score': assessment.risk_score,
                    'risk_level': assessment.risk_level,
                    'travel_days': assessment.travel_days,
                    'chokepoints': ', '.join(assessment.chokepoints),
                    'high_impact_events': len(assessment.high_impact_events)
                })
                
            except Exception as e:
                print(f"Failed to process route {i}: {str(e)}")
                summary_data.append({
                    'route': f"{route['departure_port']} -> {route['destination_port']}",
                    'risk_score': 'ERROR',
                    'risk_level': 'ERROR',
                    'travel_days': 'ERROR',
                    'chokepoints': 'ERROR',
                    'high_impact_events': 'ERROR'
                })
        
        # Generate summary report
        summary_file = os.path.join(output_dir, f"risk_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(summary_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['route', 'risk_score', 'risk_level', 'travel_days', 'chokepoints', 'high_impact_events'])
            writer.writeheader()
            writer.writerows(summary_data)
        
        print(f"\n✅ Bulk report generation completed!")
        print(f"Individual reports: {output_dir}/")
        print(f"Summary report: {summary_file}")


class ConfigValidator:
    """Validate API configuration and dependencies"""
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self.issues = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("🔍 Validating API configuration...")
        
        self.check_env_file()
        self.check_required_vars()
        self.check_optional_vars()
        self.check_api_connectivity()
        self.check_dependencies()
        
        # Print results
        if self.issues:
            print(f"\n❌ {len(self.issues)} Configuration Issues Found:")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ All configuration checks passed!")
            return True
        elif not self.issues:
            print("\n✅ Configuration is valid (warnings can be ignored)")
            return True
        else:
            print("\n❌ Configuration has issues that must be resolved")
            return False
    
    def check_env_file(self):
        """Check if .env file exists"""
        if not os.path.exists(self.config_file):
            self.issues.append(f"{self.config_file} file not found. Copy .env.example to .env")
    
    def check_required_vars(self):
        """Check required environment variables"""
        required_vars = ['OPENAI_API_KEY']
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self.issues.append(f"Required environment variable {var} not set")
            elif value == f"your_{var.lower()}_here":
                self.issues.append(f"Environment variable {var} still has placeholder value")
    
    def check_optional_vars(self):
        """Check optional environment variables"""
        optional_vars = {
            'NEWSAPI_KEY': 'Real-time news intelligence will be limited',
            'REDIS_URL': 'Caching will use in-memory storage',
            'ANTHROPIC_API_KEY': 'No backup LLM service available'
        }
        
        for var, consequence in optional_vars.items():
            if not os.getenv(var):
                self.warnings.append(f"Optional {var} not set: {consequence}")
    
    def check_api_connectivity(self):
        """Check API connectivity"""
        api_url = os.getenv('API_URL', 'http://localhost:8001')
        
        try:
            response = requests.get(f"{api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API connectivity: {health_data['status']}")
                
                # Check service statuses
                services = health_data.get('services', {})
                for service, status in services.items():
                    if status != 'healthy':
                        self.warnings.append(f"Service {service} is {status}")
            else:
                self.issues.append(f"API returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.warnings.append(f"Could not connect to API at {api_url} (API may not be running)")
        except Exception as e:
            self.issues.append(f"API health check failed: {str(e)}")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        required_packages = ['fastapi', 'uvicorn', 'openai', 'aiohttp', 'pydantic']
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.issues.append(f"Required package '{package}' not installed")


class DataExporter:
    """Export and backup utilities"""
    
    def __init__(self, api_url: str = "http://localhost:8001"):
        self.api_url = api_url
    
    def export_port_database(self, output_file: str = "ports_export.json"):
        """Export port database"""
        try:
            response = requests.get(f"{self.api_url}/ports/search?query=&limit=1000", timeout=30)
            response.raise_for_status()
            
            ports_data = response.json()
            
            with open(output_file, 'w') as f:
                json.dump(ports_data, f, indent=2)
            
            print(f"✅ Port database exported to {output_file}")
            print(f"   Total ports: {len(ports_data.get('ports', []))}")
            
        except Exception as e:
            print(f"❌ Failed to export port database: {str(e)}")
    
    def backup_configuration(self, backup_dir: str = "backup"):
        """Backup configuration files"""
        Path(backup_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Files to backup
        files_to_backup = [
            '.env',
            'config.py', 
            'docker-compose.yml',
            'requirements.txt'
        ]
        
        backed_up = []
        
        for file in files_to_backup:
            if os.path.exists(file):
                backup_file = os.path.join(backup_dir, f"{file}_{timestamp}")
                try:
                    import shutil
                    shutil.copy2(file, backup_file)
                    backed_up.append(backup_file)
                except Exception as e:
                    print(f"Failed to backup {file}: {str(e)}")
        
        if backed_up:
            print(f"✅ Configuration backup completed:")
            for file in backed_up:
                print(f"   • {file}")
        else:
            print("❌ No files were backed up")


def create_sample_routes_csv(filename: str = "sample_routes.csv"):
    """Create sample routes CSV for testing"""
    sample_routes = [
        {
            "departure_port": "Los Angeles",
            "destination_port": "Shanghai",
            "departure_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "carrier_name": "COSCO",
            "goods_type": "electronics"
        },
        {
            "departure_port": "Rotterdam",
            "destination_port": "Singapore", 
            "departure_date": (date.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "carrier_name": "Maersk",
            "goods_type": "machinery"
        },
        {
            "departure_port": "Dubai",
            "destination_port": "New York",
            "departure_date": (date.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "carrier_name": "MSC",
            "goods_type": "textiles"
        },
        {
            "departure_port": "Hamburg", 
            "destination_port": "Tokyo",
            "departure_date": (date.today() + timedelta(days=21)).strftime("%Y-%m-%d"),
            "carrier_name": "Hapag-Lloyd",
            "goods_type": "automobiles"
        }
    ]
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['departure_port', 'destination_port', 'departure_date', 'carrier_name', 'goods_type'])
        writer.writeheader()
        writer.writerows(sample_routes)
    
    print(f"✅ Sample routes CSV created: {filename}")
    return filename


def quick_risk_check(departure_port: str, destination_port: str, goods_type: str = "general"):
    """Quick risk check for a route"""
    try:
        departure_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        assessment = assess_shipping_risk(
            departure_port=departure_port,
            destination_port=destination_port,
            departure_date=departure_date,
            carrier_name="Test Carrier",
            goods_type=goods_type
        )
        
        print(f"\n🚢 Quick Risk Check: {departure_port} -> {destination_port}")
        print(f"Risk Score: {assessment.risk_score}/10 ({assessment.risk_level})")
        print(f"Travel Time: {assessment.travel_days} days")
        
        if assessment.chokepoints:
            print(f"Chokepoints: {', '.join(assessment.chokepoints)}")
        
        if assessment.high_impact_events:
            print(f"High-Impact Events: {len(assessment.high_impact_events)}")
        
        if assessment.is_high_risk:
            print("⚠️  HIGH RISK - Enhanced security recommended")
        else:
            print("✅ Acceptable risk level")
        
        return assessment
        
    except Exception as e:
        print(f"❌ Quick risk check failed: {str(e)}")
        return None


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Geopolitical Risk API Utilities")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate API configuration')
    validate_parser.add_argument('--config', default='.env', help='Configuration file path')
    
    # Report commands
    report_parser = subparsers.add_parser('report', help='Generate risk report')
    report_parser.add_argument('--departure', required=True, help='Departure port')
    report_parser.add_argument('--destination', required=True, help='Destination port') 
    report_parser.add_argument('--date', required=True, help='Departure date (YYYY-MM-DD)')
    report_parser.add_argument('--carrier', required=True, help='Carrier name')
    report_parser.add_argument('--goods', required=True, help='Goods type')
    report_parser.add_argument('--output', help='Output file path')
    
    # Bulk report command
    bulk_parser = subparsers.add_parser('bulk-report', help='Generate bulk reports from CSV')
    bulk_parser.add_argument('--input', required=True, help='Input CSV file')
    bulk_parser.add_argument('--output-dir', default='reports', help='Output directory')
    
    # Quick check command
    quick_parser = subparsers.add_parser('quick', help='Quick risk check')
    quick_parser.add_argument('--departure', required=True, help='Departure port')
    quick_parser.add_argument('--destination', required=True, help='Destination port')
    quick_parser.add_argument('--goods', default='general', help='Goods type')
    
    # Export commands
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('--type', choices=['ports', 'config'], required=True, help='Export type')
    export_parser.add_argument('--output', help='Output file/directory')
    
    # Sample data command
    sample_parser = subparsers.add_parser('sample', help='Create sample data')
    sample_parser.add_argument('--type', choices=['routes'], required=True, help='Sample data type')
    sample_parser.add_argument('--output', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        if args.command == 'validate':
            validator = ConfigValidator(args.config)
            success = validator.validate_all()
            sys.exit(0 if success else 1)
        
        elif args.command == 'report':
            generator = RiskReportGenerator()
            generator.generate_route_report(
                args.departure, args.destination, args.date,
                args.carrier, args.goods, args.output
            )
        
        elif args.command == 'bulk-report':
            generator = RiskReportGenerator()
            generator.generate_bulk_report(args.input, args.output_dir)
        
        elif args.command == 'quick':
            quick_risk_check(args.departure, args.destination, args.goods)
        
        elif args.command == 'export':
            exporter = DataExporter()
            if args.type == 'ports':
                output_file = args.output or 'ports_export.json'
                exporter.export_port_database(output_file)
            elif args.type == 'config':
                output_dir = args.output or 'backup'
                exporter.backup_configuration(output_dir)
        
        elif args.command == 'sample':
            if args.type == 'routes':
                output_file = args.output or 'sample_routes.csv'
                create_sample_routes_csv(output_file)
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()