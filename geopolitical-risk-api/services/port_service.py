"""
Port service for managing port information and route calculations
"""

import logging
from typing import Dict, Any, List, Optional
import math
import asyncio

logger = logging.getLogger(__name__)


class PortService:
    """Service for port information, coordinates, and route calculations"""
    
    def __init__(self):
        self.port_cache = {}
        self._init_port_database()
    
    def _init_port_database(self):
        """Initialize comprehensive port database with geopolitical context"""
        self.ports = {
            # North America - United States West Coast
            "Los Angeles": {
                "name": "Port of Los Angeles", "country": "United States", "code": "USLAX",
                "latitude": 33.7361, "longitude": -118.2922, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Long Beach": {
                "name": "Port of Long Beach", "country": "United States", "code": "USLGB",
                "latitude": 33.7543, "longitude": -118.2139, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Oakland": {
                "name": "Port of Oakland", "country": "United States", "code": "USOAK",
                "latitude": 37.7955, "longitude": -122.3120, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Seattle": {
                "name": "Port of Seattle", "country": "United States", "code": "USSEA",
                "latitude": 47.6062, "longitude": -122.3321, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Tacoma": {
                "name": "Port of Tacoma", "country": "United States", "code": "USTAC",
                "latitude": 47.2529, "longitude": -122.4443, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "San Francisco": {
                "name": "Port of San Francisco", "country": "United States", "code": "USSFO",
                "latitude": 37.7749, "longitude": -122.4194, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # North America - United States East Coast & Gulf
            "New York": {
                "name": "Port of New York and New Jersey", "country": "United States", "code": "USNYC",
                "latitude": 40.6892, "longitude": -74.0445, "region": "North America",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Savannah": {
                "name": "Port of Savannah", "country": "United States", "code": "USSAV",
                "latitude": 32.0835, "longitude": -81.0998, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Charleston": {
                "name": "Port of Charleston", "country": "United States", "code": "USCHS",
                "latitude": 32.7767, "longitude": -79.9311, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Miami": {
                "name": "Port of Miami", "country": "United States", "code": "USMIA",
                "latitude": 25.7617, "longitude": -80.1918, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Houston": {
                "name": "Port of Houston", "country": "United States", "code": "USHOU",
                "latitude": 29.7604, "longitude": -95.3698, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "New Orleans": {
                "name": "Port of New Orleans", "country": "United States", "code": "USMSY",
                "latitude": 29.9511, "longitude": -90.0715, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Baltimore": {
                "name": "Port of Baltimore", "country": "United States", "code": "USBAL",
                "latitude": 39.2904, "longitude": -76.6122, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Norfolk": {
                "name": "Port of Norfolk", "country": "United States", "code": "USNFK",
                "latitude": 36.8468, "longitude": -76.2951, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            
            # North America - Canada
            "Vancouver": {
                "name": "Port of Vancouver", "country": "Canada", "code": "CAVAN",
                "latitude": 49.2827, "longitude": -123.1207, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Montreal": {
                "name": "Port of Montreal", "country": "Canada", "code": "CAMTR",
                "latitude": 45.5017, "longitude": -73.5673, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Halifax": {
                "name": "Port of Halifax", "country": "Canada", "code": "CAHAL",
                "latitude": 44.6488, "longitude": -63.5752, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Prince Rupert": {
                "name": "Port of Prince Rupert", "country": "Canada", "code": "CAPRP",
                "latitude": 54.3150, "longitude": -130.3208, "region": "North America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # Asia - China
            "Shanghai": {
                "name": "Port of Shanghai", "country": "China", "code": "CNSHA",
                "latitude": 31.2304, "longitude": 121.4737, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Shenzhen": {
                "name": "Port of Shenzhen", "country": "China", "code": "CNSZX",
                "latitude": 22.5431, "longitude": 114.0579, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Ningbo": {
                "name": "Port of Ningbo", "country": "China", "code": "CNNGB",
                "latitude": 29.8683, "longitude": 121.5440, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Qingdao": {
                "name": "Port of Qingdao", "country": "China", "code": "CNTAO",
                "latitude": 36.0986, "longitude": 120.3719, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Tianjin": {
                "name": "Port of Tianjin", "country": "China", "code": "CNTSN",
                "latitude": 39.1042, "longitude": 117.2009, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Guangzhou": {
                "name": "Port of Guangzhou", "country": "China", "code": "CNGZH",
                "latitude": 23.1291, "longitude": 113.2644, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Dalian": {
                "name": "Port of Dalian", "country": "China", "code": "CNDLC",
                "latitude": 38.9140, "longitude": 121.6147, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Xiamen": {
                "name": "Port of Xiamen", "country": "China", "code": "CNXMN",
                "latitude": 24.4798, "longitude": 118.0819, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Suzhou": {
                "name": "Port of Suzhou", "country": "China", "code": "CNSUZ",
                "latitude": 31.2983, "longitude": 120.5831, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            
            # Asia - India
            "Mumbai": {
                "name": "Port of Mumbai", "country": "India", "code": "INMAA",
                "latitude": 19.0760, "longitude": 72.8777, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Chennai": {
                "name": "Port of Chennai", "country": "India", "code": "INMAA",
                "latitude": 13.0827, "longitude": 80.2707, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Kolkata": {
                "name": "Port of Kolkata", "country": "India", "code": "INCCU",
                "latitude": 22.5726, "longitude": 88.3639, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            "Kochi": {
                "name": "Port of Kochi", "country": "India", "code": "INCOK",
                "latitude": 9.9312, "longitude": 76.2673, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Visakhapatnam": {
                "name": "Port of Visakhapatnam", "country": "India", "code": "INVTZ",
                "latitude": 17.6868, "longitude": 83.2185, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Jawaharlal Nehru": {
                "name": "Jawaharlal Nehru Port", "country": "India", "code": "INNSA",
                "latitude": 18.9480, "longitude": 72.9881, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Very Good"
            },
            
            # Asia - Southeast Asia
            "Singapore": {
                "name": "Port of Singapore", "country": "Singapore", "code": "SGSIN",
                "latitude": 1.2966, "longitude": 103.8517, "region": "Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Bangkok": {
                "name": "Port of Bangkok", "country": "Thailand", "code": "THBKK",
                "latitude": 13.7563, "longitude": 100.5018, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Ho Chi Minh City": {
                "name": "Port of Ho Chi Minh City", "country": "Vietnam", "code": "VNSGN",
                "latitude": 10.8231, "longitude": 106.6297, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Jakarta": {
                "name": "Port of Jakarta", "country": "Indonesia", "code": "IDJKT",
                "latitude": -6.1087, "longitude": 106.3694, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            "Manila": {
                "name": "Port of Manila", "country": "Philippines", "code": "PHMNL",
                "latitude": 14.5995, "longitude": 120.9842, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            "Haiphong": {
                "name": "Port of Haiphong", "country": "Vietnam", "code": "VNHPH",
                "latitude": 20.8449, "longitude": 106.6881, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Kuala Lumpur": {
                "name": "Port of Kuala Lumpur", "country": "Malaysia", "code": "MYKUL",
                "latitude": 3.1390, "longitude": 101.6869, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            
            # Asia - East Asia (Japan, South Korea, Taiwan, Hong Kong)
            "Busan": {
                "name": "Port of Busan", "country": "South Korea", "code": "KRPUS",
                "latitude": 35.1796, "longitude": 129.0756, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Hong Kong": {
                "name": "Port of Hong Kong", "country": "Hong Kong", "code": "HKHKG",
                "latitude": 22.3193, "longitude": 114.1694, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Kobe": {
                "name": "Port of Kobe", "country": "Japan", "code": "JPUKB",
                "latitude": 34.6901, "longitude": 135.1956, "region": "Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Yokohama": {
                "name": "Port of Yokohama", "country": "Japan", "code": "JPYOK",
                "latitude": 35.4437, "longitude": 139.6380, "region": "Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Tokyo": {
                "name": "Port of Tokyo", "country": "Japan", "code": "JPTYO",
                "latitude": 35.6762, "longitude": 139.6503, "region": "Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Kaohsiung": {
                "name": "Port of Kaohsiung", "country": "Taiwan", "code": "TWKHH",
                "latitude": 22.6273, "longitude": 120.3014, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Nagoya": {
                "name": "Port of Nagoya", "country": "Japan", "code": "JPNGO",
                "latitude": 35.1815, "longitude": 136.9066, "region": "Asia",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Incheon": {
                "name": "Port of Incheon", "country": "South Korea", "code": "KRICN",
                "latitude": 37.4563, "longitude": 126.7052, "region": "Asia",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            
            # Europe - Northern Europe
            "Rotterdam": {
                "name": "Port of Rotterdam", "country": "Netherlands", "code": "NLRTM",
                "latitude": 51.9225, "longitude": 4.4792, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Excellent"
            },
            "Antwerp": {
                "name": "Port of Antwerp", "country": "Belgium", "code": "BEANR",
                "latitude": 51.2993, "longitude": 4.4014, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Hamburg": {
                "name": "Port of Hamburg", "country": "Germany", "code": "DEHAM",
                "latitude": 53.5511, "longitude": 9.9937, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Felixstowe": {
                "name": "Port of Felixstowe", "country": "United Kingdom", "code": "GBFXT",
                "latitude": 51.9640, "longitude": 1.3518, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Le Havre": {
                "name": "Port of Le Havre", "country": "France", "code": "FRLEH",
                "latitude": 49.4944, "longitude": 0.1079, "region": "Europe",
                "security_level": "High", "labor_stability": "Fair", "infrastructure": "Very Good"
            },
            "Bremen": {
                "name": "Port of Bremen", "country": "Germany", "code": "DEBRE",
                "latitude": 53.0793, "longitude": 8.8017, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "London": {
                "name": "Port of London", "country": "United Kingdom", "code": "GBLON",
                "latitude": 51.5074, "longitude": -0.1278, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Gothenburg": {
                "name": "Port of Gothenburg", "country": "Sweden", "code": "SEGOT",
                "latitude": 57.7089, "longitude": 11.9746, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Very Good"
            },
            "Oslo": {
                "name": "Port of Oslo", "country": "Norway", "code": "NOOSL",
                "latitude": 59.9139, "longitude": 10.7522, "region": "Europe",
                "security_level": "Very High", "labor_stability": "Excellent", "infrastructure": "Very Good"
            },
            
            # Europe - Southern Europe
            "Genoa": {
                "name": "Port of Genoa", "country": "Italy", "code": "ITGOA",
                "latitude": 44.4056, "longitude": 8.9463, "region": "Europe",
                "security_level": "High", "labor_stability": "Fair", "infrastructure": "Very Good"
            },
            "Barcelona": {
                "name": "Port of Barcelona", "country": "Spain", "code": "ESBCN",
                "latitude": 41.3851, "longitude": 2.1734, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Valencia": {
                "name": "Port of Valencia", "country": "Spain", "code": "ESVLC",
                "latitude": 39.4699, "longitude": -0.3763, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Piraeus": {
                "name": "Port of Piraeus", "country": "Greece", "code": "GRPIR",
                "latitude": 37.9755, "longitude": 23.7348, "region": "Europe",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Marseille": {
                "name": "Port of Marseille", "country": "France", "code": "FRMRS",
                "latitude": 43.2965, "longitude": 5.3698, "region": "Europe",
                "security_level": "High", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Naples": {
                "name": "Port of Naples", "country": "Italy", "code": "ITNAP",
                "latitude": 40.8518, "longitude": 14.2681, "region": "Europe",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Algeciras": {
                "name": "Port of Algeciras", "country": "Spain", "code": "ESALG",
                "latitude": 36.1408, "longitude": -5.4526, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Gioia Tauro": {
                "name": "Port of Gioia Tauro", "country": "Italy", "code": "ITGIT",
                "latitude": 38.4244, "longitude": 15.8897, "region": "Europe",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            
            # Middle East
            "Dubai": {
                "name": "Port of Dubai", "country": "UAE", "code": "AEDXB",
                "latitude": 25.2048, "longitude": 55.2708, "region": "Middle East",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Jebel Ali": {
                "name": "Port of Jebel Ali", "country": "UAE", "code": "AEJEA",
                "latitude": 25.0118, "longitude": 55.0618, "region": "Middle East",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Excellent"
            },
            "Abu Dhabi": {
                "name": "Port of Abu Dhabi", "country": "UAE", "code": "AEAUH",
                "latitude": 24.4539, "longitude": 54.3773, "region": "Middle East",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Jeddah": {
                "name": "Port of Jeddah", "country": "Saudi Arabia", "code": "SAJED",
                "latitude": 21.4858, "longitude": 39.1925, "region": "Middle East",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Dammam": {
                "name": "Port of Dammam", "country": "Saudi Arabia", "code": "SADMM",
                "latitude": 26.4207, "longitude": 50.0888, "region": "Middle East",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Bandar Abbas": {
                "name": "Port of Bandar Abbas", "country": "Iran", "code": "IRBND",
                "latitude": 27.1865, "longitude": 56.2808, "region": "Middle East",
                "security_level": "Low", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            "Sohar": {
                "name": "Port of Sohar", "country": "Oman", "code": "OMSOH",
                "latitude": 24.3415, "longitude": 56.7539, "region": "Middle East",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Kuwait": {
                "name": "Port of Kuwait", "country": "Kuwait", "code": "KWKWI",
                "latitude": 29.3759, "longitude": 47.9774, "region": "Middle East",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # Africa - North Africa
            "Alexandria": {
                "name": "Port of Alexandria", "country": "Egypt", "code": "EGALX",
                "latitude": 31.2001, "longitude": 29.9187, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            "Suez": {
                "name": "Port of Suez", "country": "Egypt", "code": "EGSUZ",
                "latitude": 29.9668, "longitude": 32.5498, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Casablanca": {
                "name": "Port of Casablanca", "country": "Morocco", "code": "MACAS",
                "latitude": 33.5731, "longitude": -7.5898, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Tunis": {
                "name": "Port of Tunis", "country": "Tunisia", "code": "TNTUN",
                "latitude": 36.8065, "longitude": 10.1815, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            
            # Africa - West Africa
            "Lagos": {
                "name": "Port of Lagos", "country": "Nigeria", "code": "NGLOS",
                "latitude": 6.5244, "longitude": 3.3792, "region": "Africa",
                "security_level": "Low", "labor_stability": "Poor", "infrastructure": "Fair"
            },
            "Tema": {
                "name": "Port of Tema", "country": "Ghana", "code": "GHTEM",
                "latitude": 5.6037, "longitude": -0.0163, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Abidjan": {
                "name": "Port of Abidjan", "country": "Ivory Coast", "code": "CIABJ",
                "latitude": 5.3600, "longitude": -4.0083, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Dakar": {
                "name": "Port of Dakar", "country": "Senegal", "code": "SNDKR",
                "latitude": 14.6937, "longitude": -17.4441, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # Africa - East & South Africa
            "Durban": {
                "name": "Port of Durban", "country": "South Africa", "code": "ZADUR",
                "latitude": -29.8587, "longitude": 31.0218, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Very Good"
            },
            "Cape Town": {
                "name": "Port of Cape Town", "country": "South Africa", "code": "ZACPT",
                "latitude": -33.9249, "longitude": 18.4241, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Very Good"
            },
            "Dar es Salaam": {
                "name": "Port of Dar es Salaam", "country": "Tanzania", "code": "TZDAR",
                "latitude": -6.7924, "longitude": 39.2083, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            "Mombasa": {
                "name": "Port of Mombasa", "country": "Kenya", "code": "KEMBA",
                "latitude": -4.0435, "longitude": 39.6682, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Port Elizabeth": {
                "name": "Port of Port Elizabeth", "country": "South Africa", "code": "ZAPLZ",
                "latitude": -33.9580, "longitude": 25.6022, "region": "Africa",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            
            # South America
            "Santos": {
                "name": "Port of Santos", "country": "Brazil", "code": "BRSSZ",
                "latitude": -23.9618, "longitude": -46.3322, "region": "South America",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Buenos Aires": {
                "name": "Port of Buenos Aires", "country": "Argentina", "code": "ARBUE",
                "latitude": -34.6118, "longitude": -58.3960, "region": "South America",
                "security_level": "Medium", "labor_stability": "Poor", "infrastructure": "Fair"
            },
            "Callao": {
                "name": "Port of Callao", "country": "Peru", "code": "PECLL",
                "latitude": -12.0464, "longitude": -77.1428, "region": "South America",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Cartagena": {
                "name": "Port of Cartagena", "country": "Colombia", "code": "COCTG",
                "latitude": 10.3910, "longitude": -75.4794, "region": "South America",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Rio de Janeiro": {
                "name": "Port of Rio de Janeiro", "country": "Brazil", "code": "BRRIO",
                "latitude": -22.9068, "longitude": -43.1729, "region": "South America",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Valparaiso": {
                "name": "Port of Valparaiso", "country": "Chile", "code": "CLVAP",
                "latitude": -33.0472, "longitude": -71.6127, "region": "South America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Montevideo": {
                "name": "Port of Montevideo", "country": "Uruguay", "code": "UYMVD",
                "latitude": -34.9011, "longitude": -56.1645, "region": "South America",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Fortaleza": {
                "name": "Port of Fortaleza", "country": "Brazil", "code": "BRFOR",
                "latitude": -3.7172, "longitude": -38.5433, "region": "South America",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Fair"
            },
            
            # Australia & Oceania
            "Sydney": {
                "name": "Port of Sydney", "country": "Australia", "code": "AUSYD",
                "latitude": -33.8688, "longitude": 151.2093, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Melbourne": {
                "name": "Port of Melbourne", "country": "Australia", "code": "AUMEL",
                "latitude": -37.8136, "longitude": 144.9631, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Brisbane": {
                "name": "Port of Brisbane", "country": "Australia", "code": "AUBNE",
                "latitude": -27.4698, "longitude": 153.0251, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Fremantle": {
                "name": "Port of Fremantle", "country": "Australia", "code": "AUFRE",
                "latitude": -32.0569, "longitude": 115.7445, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Adelaide": {
                "name": "Port of Adelaide", "country": "Australia", "code": "AUADL",
                "latitude": -34.9285, "longitude": 138.6007, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Auckland": {
                "name": "Port of Auckland", "country": "New Zealand", "code": "NZAKL",
                "latitude": -36.8485, "longitude": 174.7633, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Tauranga": {
                "name": "Port of Tauranga", "country": "New Zealand", "code": "NZTAU",
                "latitude": -37.6870, "longitude": 176.1651, "region": "Oceania",
                "security_level": "Very High", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # Caribbean & Central America
            "Kingston": {
                "name": "Port of Kingston", "country": "Jamaica", "code": "JMKIN",
                "latitude": 17.9712, "longitude": -76.7928, "region": "Caribbean",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            },
            "Colon": {
                "name": "Port of Colon", "country": "Panama", "code": "PACLN",
                "latitude": 9.3547, "longitude": -79.9009, "region": "Caribbean",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "San Juan": {
                "name": "Port of San Juan", "country": "Puerto Rico", "code": "PRSJU",
                "latitude": 18.4655, "longitude": -66.1057, "region": "Caribbean",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Freeport": {
                "name": "Port of Freeport", "country": "Bahamas", "code": "BSFPO",
                "latitude": 26.5285, "longitude": -78.6957, "region": "Caribbean",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Good"
            },
            
            # Russia & Eastern Europe
            "St Petersburg": {
                "name": "Port of St Petersburg", "country": "Russia", "code": "RULED",
                "latitude": 59.9311, "longitude": 30.3609, "region": "Europe",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Novorossiysk": {
                "name": "Port of Novorossiysk", "country": "Russia", "code": "RUNVS",
                "latitude": 44.7230, "longitude": 37.7687, "region": "Europe",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Good"
            },
            "Vladivostok": {
                "name": "Port of Vladivostok", "country": "Russia", "code": "RUVVO",
                "latitude": 43.1056, "longitude": 131.8735, "region": "Asia",
                "security_level": "Medium", "labor_stability": "Good", "infrastructure": "Fair"
            },
            "Gdansk": {
                "name": "Port of Gdansk", "country": "Poland", "code": "PLGDN",
                "latitude": 54.3520, "longitude": 18.6466, "region": "Europe",
                "security_level": "High", "labor_stability": "Good", "infrastructure": "Very Good"
            },
            "Constanta": {
                "name": "Port of Constanta", "country": "Romania", "code": "ROCND",
                "latitude": 44.1598, "longitude": 28.6348, "region": "Europe",
                "security_level": "Medium", "labor_stability": "Fair", "infrastructure": "Good"
            }
        }
        
        # Create search index for port names
        self.port_search_index = {}
        for key, port in self.ports.items():
            # Index by various name variations
            search_terms = [
                key.lower(),
                port["name"].lower(),
                port["code"].lower(),
                port["country"].lower() + " " + key.lower()
            ]
            
            for term in search_terms:
                if term not in self.port_search_index:
                    self.port_search_index[term] = []
                self.port_search_index[term].append(port)
    
    async def get_port_info(self, port_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive port information including geopolitical context"""
        try:
            # Check exact match first
            if port_name in self.ports:
                return self.ports[port_name]
            
            # Search for partial matches
            port_name_lower = port_name.lower()
            
            # Try direct search in index
            if port_name_lower in self.port_search_index:
                return self.port_search_index[port_name_lower][0]
            
            # Try fuzzy matching
            best_match = self._fuzzy_search_port(port_name_lower)
            if best_match:
                return best_match
            
            logger.warning(f"Port not found: {port_name}")
            return None
            
        except Exception as e:
            logger.error(f"Port info lookup failed for {port_name}: {str(e)}")
            return None
    
    async def get_port_coordinates(self, port_name: str) -> Optional[Dict[str, float]]:
        """Get port coordinates (latitude, longitude)"""
        port_info = await self.get_port_info(port_name)
        if port_info:
            return {
                "lat": port_info["latitude"],
                "lon": port_info["longitude"]
            }
        return None
    
    async def search_ports(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for ports by name with ranking"""
        try:
            query_lower = query.lower()
            matches = []
            
            for port_key, port_info in self.ports.items():
                score = self._calculate_search_score(query_lower, port_info)
                if score > 0:
                    match = port_info.copy()
                    match["match_score"] = score
                    matches.append(match)
            
            # Sort by match score and limit results
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Port search failed for query '{query}': {str(e)}")
            return []
    
    def estimate_travel_time(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any], 
        goods_type: str
    ) -> int:
        """Estimate travel time in days considering route and cargo factors"""
        try:
            # Calculate distance
            distance_km = self._calculate_distance(
                departure_info["latitude"], departure_info["longitude"],
                destination_info["latitude"], destination_info["longitude"]
            )
            
            # Base speed calculation (container ship average: 20-25 knots)
            avg_speed_knots = 22
            avg_speed_kmh = avg_speed_knots * 1.852  # Convert to km/h
            
            # Route factor (actual routes are longer than great circle distance)
            route_factor = self._get_route_factor(departure_info, destination_info)
            actual_distance = distance_km * route_factor
            
            # Speed adjustments based on cargo type
            speed_factor = self._get_speed_factor(goods_type)
            
            # Efficiency factor (weather, port delays, etc.)
            efficiency_factor = 0.65  # 65% efficiency accounting for all delays
            
            # Calculate travel time
            effective_speed = avg_speed_kmh * speed_factor * efficiency_factor
            travel_hours = actual_distance / effective_speed
            travel_days = max(1, int(travel_hours / 24))
            
            # Add port time (loading/unloading)
            port_days = self._estimate_port_time(departure_info, destination_info, goods_type)
            
            return travel_days + port_days
            
        except Exception as e:
            logger.error(f"Travel time estimation failed: {str(e)}")
            return 14  # Default 2 weeks
    
    def _fuzzy_search_port(self, query: str) -> Optional[Dict[str, Any]]:
        """Perform fuzzy search for port names"""
        best_match = None
        best_score = 0
        
        for port_info in self.ports.values():
            score = self._calculate_search_score(query, port_info)
            if score > best_score:
                best_score = score
                best_match = port_info
        
        # Return match only if score is reasonable
        return best_match if best_score >= 0.3 else None
    
    def _calculate_search_score(self, query: str, port_info: Dict[str, Any]) -> float:
        """Calculate search relevance score"""
        score = 0.0
        
        port_name = port_info["name"].lower()
        port_code = port_info["code"].lower()
        country = port_info["country"].lower()
        
        # Exact matches
        if query == port_name:
            score += 1.0
        elif query == port_code:
            score += 0.9
        elif query in port_name:
            score += 0.8
        elif query in country:
            score += 0.3
        
        # Partial matches
        query_words = query.split()
        port_words = port_name.split()
        
        for q_word in query_words:
            for p_word in port_words:
                if q_word in p_word:
                    score += 0.2
                elif p_word.startswith(q_word):
                    score += 0.4
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points in kilometers"""
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def _get_route_factor(self, departure_info: Dict[str, Any], destination_info: Dict[str, Any]) -> float:
        """Get route factor to account for actual shipping routes vs great circle"""
        dept_region = departure_info.get("region", "")
        dest_region = destination_info.get("region", "")
        
        # Trans-oceanic routes have higher route factors
        if dept_region != dest_region:
            if ("Asia" in dept_region and "Europe" in dest_region) or ("Europe" in dept_region and "Asia" in dest_region):
                return 1.4  # Via Suez Canal or around Africa
            elif ("Asia" in dept_region and "America" in dest_region) or ("America" in dept_region and "Asia" in dest_region):
                return 1.3  # Trans-Pacific routes
            elif ("Europe" in dept_region and "America" in dest_region) or ("America" in dept_region and "Europe" in dest_region):
                return 1.2  # Trans-Atlantic routes
            else:
                return 1.3  # Other international routes
        else:
            return 1.1  # Regional routes
    
    def _get_speed_factor(self, goods_type: str) -> float:
        """Get speed factor based on cargo type"""
        goods_lower = goods_type.lower()
        
        if goods_lower in ["perishables", "food", "pharmaceuticals"]:
            return 1.1  # Faster for time-sensitive cargo
        elif goods_lower in ["hazardous", "chemicals", "oil", "gas"]:
            return 0.9  # Slower for safety
        elif goods_lower in ["automobiles", "machinery", "heavy"]:
            return 0.95  # Slightly slower for heavy cargo
        else:
            return 1.0  # Standard speed
    
    def _estimate_port_time(
        self, 
        departure_info: Dict[str, Any], 
        destination_info: Dict[str, Any], 
        goods_type: str
    ) -> int:
        """Estimate port time (loading/unloading) in days"""
        base_port_time = 2  # Base 2 days for port operations
        
        # Adjust based on port infrastructure
        dept_infra = departure_info.get("infrastructure", "Good")
        dest_infra = destination_info.get("infrastructure", "Good")
        
        infra_factor = 1.0
        if dept_infra == "Poor" or dest_infra == "Poor":
            infra_factor = 1.5
        elif dept_infra == "Fair" or dest_infra == "Fair":
            infra_factor = 1.2
        elif dept_infra == "Excellent" and dest_infra == "Excellent":
            infra_factor = 0.8
        
        # Adjust based on labor conditions
        dept_labor = departure_info.get("labor_stability", "Good")
        dest_labor = destination_info.get("labor_stability", "Good")
        
        labor_factor = 1.0
        if dept_labor == "Poor" or dest_labor == "Poor":
            labor_factor = 1.3
        elif dept_labor == "Fair" or dest_labor == "Fair":
            labor_factor = 1.1
        
        # Adjust based on cargo type
        cargo_factor = 1.0
        goods_lower = goods_type.lower()
        
        if goods_lower in ["hazardous", "chemicals"]:
            cargo_factor = 1.4  # Extra handling time for dangerous goods
        elif goods_lower in ["automobiles", "machinery"]:
            cargo_factor = 1.2  # Special handling equipment needed
        elif goods_lower in ["bulk", "containers"]:
            cargo_factor = 0.9  # Standardized handling
        
        total_port_time = base_port_time * infra_factor * labor_factor * cargo_factor
        return max(1, int(total_port_time))
    
    def get_regional_ports(self, region: str) -> List[Dict[str, Any]]:
        """Get all ports in a specific region"""
        return [port for port in self.ports.values() if port.get("region") == region]
    
    def get_country_ports(self, country: str) -> List[Dict[str, Any]]:
        """Get all ports in a specific country"""
        return [port for port in self.ports.values() if port.get("country") == country]
    
    def assess_port_security_risk(self, port_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess security risk factors for a specific port"""
        try:
            security_assessment = {
                "overall_security_level": port_info.get("security_level", "Unknown"),
                "labor_stability": port_info.get("labor_stability", "Unknown"),
                "infrastructure_quality": port_info.get("infrastructure", "Unknown"),
                "country": port_info.get("country", "Unknown"),
                "region": port_info.get("region", "Unknown")
            }
            
            # Calculate risk score based on factors
            risk_score = 5  # Base medium risk
            
            security_level = port_info.get("security_level", "Medium")
            if security_level == "Very High":
                risk_score -= 2
            elif security_level == "High":
                risk_score -= 1
            elif security_level == "Low":
                risk_score += 2
            elif security_level == "Very Low":
                risk_score += 3
            
            labor_stability = port_info.get("labor_stability", "Fair")
            if labor_stability == "Excellent":
                risk_score -= 1
            elif labor_stability == "Poor":
                risk_score += 2
            
            infrastructure = port_info.get("infrastructure", "Fair")
            if infrastructure == "Excellent":
                risk_score -= 1
            elif infrastructure == "Poor":
                risk_score += 1
            
            security_assessment["risk_score"] = max(1, min(risk_score, 10))
            
            return security_assessment
            
        except Exception as e:
            logger.error(f"Port security assessment failed: {str(e)}")
            return {
                "overall_security_level": "Unknown",
                "risk_score": 5,
                "error": str(e)
            }