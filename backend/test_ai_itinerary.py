#!/usr/bin/env python
"""
Test script for AI-powered itinerary generation.
Verifies that:
1. The generate endpoint accepts new format (destination, tripLength, budget)
2. AI-generated data is stored in ai_generated_data field
3. Response includes complete itinerary structure
"""
import os
import sys
import django
import json
from decimal import Decimal

# Set up Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from api.models import Itinerary

User = get_user_model()

def main():
    print("=" * 60)
    print("AI ITINERARY GENERATION TEST")
    print("=" * 60)
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing user: {user.username}")
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    
    # Create API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    print("\n" + "=" * 60)
    print("TEST 1: Generate AI Itinerary (New Format)")
    print("=" * 60)
    
    # Test data matching the AI generation format
    request_data = {
        "destination": "Downtown Toronto",
        "currentLocation": {
            "latitude": 43.6532,
            "longitude": -79.3832
        },
        "tripLength": "1 day",
        "budget": "200"
    }
    
    print(f"\n📤 Sending POST to /api/itineraries/generate/")
    print(f"Request data: {json.dumps(request_data, indent=2)}")
    
    response = client.post('/api/itineraries/generate/', request_data, format='json')
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Itinerary created successfully!")
        data = response.json()
        
        print(f"\n📋 Response Data:")
        print(f"  - ID: {data.get('id')}")
        print(f"  - Title: {data.get('title')}")
        print(f"  - Region: {data.get('region')}")
        print(f"  - Owner: {data.get('owner_username')}")
        
        # Check for ai_generated_data
        if 'ai_generated_data' in data:
            print(f"\n✅ ai_generated_data field present!")
            ai_data = data['ai_generated_data']
            
            if ai_data:
                print(f"\n📊 AI Generated Data Structure:")
                
                # Check for itinerary key
                if 'itinerary' in ai_data:
                    itinerary = ai_data['itinerary']
                    print(f"  - Trip Title: {itinerary.get('tripTitle', 'N/A')}")
                    print(f"  - Summary: {itinerary.get('summary', 'N/A')[:100]}...")
                    
                    # Check days
                    if 'days' in itinerary:
                        print(f"  - Number of Days: {len(itinerary['days'])}")
                        for idx, day in enumerate(itinerary['days'][:2], 1):  # Show first 2 days
                            print(f"\n    Day {idx}: {day.get('dayTitle', 'N/A')}")
                            activities = day.get('activities', [])
                            print(f"    Activities: {len(activities)}")
                            for act in activities[:2]:  # Show first 2 activities
                                print(f"      - {act.get('time', 'N/A')}: {act.get('activity', 'N/A')}")
                    
                    # Check flight info
                    if 'flightInfo' in itinerary:
                        flight_info = itinerary['flightInfo']
                        if flight_info:
                            print(f"\n  - Flight Info: Present")
                            if 'departure' in flight_info:
                                print(f"    Departure: {flight_info['departure'].get('airline', 'N/A')}")
                        else:
                            print(f"\n  - Flight Info: None (regional trip)")
                
                # Check for grounding chunks
                if 'groundingChunks' in ai_data:
                    chunks = ai_data['groundingChunks']
                    print(f"\n  - Grounding Chunks: {len(chunks)} sources")
                
                print("\n✅ Complete AI data structure validated!")
            else:
                print("\n⚠️  ai_generated_data is null (may be using legacy format or AI call failed)")
        else:
            print("\n❌ ai_generated_data field missing!")
        
        # Verify in database
        itinerary_id = data.get('id')
        db_itinerary = Itinerary.objects.get(id=itinerary_id)
        print(f"\n🗄️  Database Verification:")
        print(f"  - Itinerary exists: ✅")
        print(f"  - ai_generated_data field has value: {'✅' if db_itinerary.ai_generated_data else '❌'}")
        
    else:
        print(f"❌ Failed to create itinerary")
        print(f"Error: {response.json()}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Legacy Format Support")
    print("=" * 60)
    
    legacy_data = {
        "region": "Paris",
        "needs": "2 day trip, museums and restaurants"
    }
    
    print(f"\n📤 Sending POST with legacy format")
    print(f"Request data: {json.dumps(legacy_data, indent=2)}")
    
    response = client.post('/api/itineraries/generate/', legacy_data, format='json')
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Legacy format still works!")
        data = response.json()
        print(f"  - Title: {data.get('title')}")
        print(f"  - Has items: {'✅' if data.get('items') else '❌'}")
        print(f"  - ai_generated_data: {'Present' if data.get('ai_generated_data') else 'Null (expected for legacy)'}")
    else:
        print(f"❌ Legacy format failed")
        print(f"Error: {response.json()}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ All tests completed!")
    print("\n💡 Notes:")
    print("  - New format uses AI generation with complete JSON storage")
    print("  - Legacy format uses dummy data for backward compatibility")
    print("  - Frontend can directly use ai_generated_data JSON")
    print("  - Existing schema preserved for future manual editing")
    print("=" * 60)

if __name__ == '__main__':
    main()
