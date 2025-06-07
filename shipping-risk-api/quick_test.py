#!/usr/bin/env python3
"""
Quick test to see if OpenAI returns valid JSON
"""

import asyncio
from openai import AsyncOpenAI
from config import get_settings

async def test_openai_json():
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    print("🧪 Testing OpenAI JSON response...")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that ALWAYS responds in valid JSON format."
                },
                {
                    "role": "user",
                    "content": """Please assess this shipping risk and respond ONLY with valid JSON:
                    
Route: Los Angeles to Shanghai
Weather: Departure is sunny, destination is rainy
Cargo: Electronics

Respond with this exact JSON format:
{
  "risk_score": 5,
  "risk_description": "Your assessment here",
  "weather_summary": "Your weather summary here"
}"""
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        print(f"✅ OpenAI Response:")
        print(ai_response)
        print(f"\n📏 Response length: {len(ai_response)} characters")
        
        # Try to parse JSON
        import json
        try:
            parsed = json.loads(ai_response)
            print(f"✅ JSON parsing successful!")
            print(f"   Risk Score: {parsed.get('risk_score')}")
            print(f"   Has Description: {'risk_description' in parsed}")
            print(f"   Has Summary: {'weather_summary' in parsed}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print("   OpenAI returned text instead of JSON")
            return False
        
    except Exception as e:
        print(f"❌ OpenAI call failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai_json())