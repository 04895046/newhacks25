import os
import json
import re
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Type definitions (you'll need to define these based on your types module)
# from types import TravelPreferences, Itinerary, Geolocation, GroundingChunk
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=os.getenv("API_KEY"))


def build_itinerary_prompt(preferences: Dict[str, Any]) -> str:
    """
    Build the itinerary prompt from travel preferences.

    Args:
        preferences: Dictionary containing destination, currentLocation, tripLength, budget
    """
    return f"""
    You are an expert travel planner. Create a detailed travel itinerary based on the following preferences.
    Based on the user's current location, if needed, find suitable round-trip flight options and include them in the "flightInfo" object. Use Google Search for up-to-date flight information.
    Your response MUST be a single, valid JSON object. Do not include any text, explanation, or markdown formatting before or after the JSON object.

    Preferences:
    - Destination: {preferences['destination']}
    - Current Location: {preferences['currentLocation']}
    - Trip Length: {preferences['tripLength']} days
    - Budget: {preferences['budget']}

    The JSON object must follow this exact structure:
    {{
      "tripTitle": "A creative and exciting title for the trip to {preferences['destination']}",
      "summary": "A brief, engaging summary of the trip.",
      "flightInfo": {{
        "departure": {{
            "airline": "Airline Name",
            "flightNumber": "Flight Number",
            "departureAirport": "Airport Code/Name",
            "arrivalAirport": "Airport Code/Name",
            "departureTime": "YYYY-MM-DDTHH:MM:SSZ",
            "arrivalTime": "YYYY-MM-DDTHH:MM:SSZ",
            "duration": "Xh Ym",
            "departureCoordinates": {{"latitude": float, "longitude": float}},
            "arrivalCoordinates": {{"latitude": float, "longitude": float}}
        }},
        "return": {{
            "airline": "Airline Name",
            "flightNumber": "Flight Number",
            "departureAirport": "Airport Code/Name",
            "arrivalAirport": "Airport Code/Name",
            "departureTime": "YYYY-MM-DDTHH:MM:SSZ",
            "arrivalTime": "YYYY-MM-DDTHH:MM:SSZ",
            "duration": "Xh Ym",
            "departureCoordinates": {{"latitude": float, "longitude": float}},
            "arrivalCoordinates": {{"latitude": float, "longitude": float}}
        }},
        "price": "Estimated price for round trip (e.g., ~$1200 USD)",
        "bookingLink": "A URL to a flight search engine like Google Flights with the search pre-filled."
      }},
      "dailyPlan": [
        {{
          "day": 1,

          "activities": [
            {{
              "duration": "Duration of the activity, in hours, float.",
              "description": "Detailed description of the activity.",
              "name": "Specific name and address of the location.",
              "location": "Coordinates of the activity, two floats.",
              "description": "Additional practical information.",
              "price": "Price in the local currency, integer.",
              "bookingLink": "An optional URL for booking tickets or reservations if available."
            }},
            {{
              "type": "transport",
              "transportationType": "transportation method type",
              "startPoint": "Name and address of starting location",
              "endPoint": "Name and address of ending location",
              "startCoordinates": {{"latitude": float, "longitude": float}},
              "endCoordinates": {{"latitude": float, "longitude": float}},
              "duration": float,
              "price": integer,
              "description": "Brief description of the journey"
            }},
            {{
              "duration": float,
              "description": "Another activity description.",
              "name": "Another specific location name and address.",
              "coordinates": {{"latitude": float, "longitude": float}},
              "price": integer,
              "bookingLink": null
            }}
          ]
        }}
      ]
    }}

    IMPORTANT RULES:
    1. Include a transport segment between EVERY activity (unless they are at the exact same location).
    2. Transport segments should have "type": "transport" to distinguish them from activity segments.
    3. Each transport segment MUST include:
       - transportationType: one of ["walk", "metro", "train", "bus", "taxi", "ferry", "tram", "bicycle", "car", "flight"]
       - startPoint: name and address of starting location (string)
       - endPoint: name and address of ending location (string)
       - startCoordinates: {{"latitude": float, "longitude": float}}
       - endCoordinates: {{"latitude": float, "longitude": float}}
       - duration: time in hours (float)
       - price: cost in local currency (integer, 0 for walking)
       - description: brief description of the journey
    4. Activity segments should NOT have "type" field (or can have "type": "activity").
    5. The startCoordinates of each transport segment should match the coordinates of the previous activity.
    6. The endCoordinates of each transport segment should match the coordinates of the next activity.
    7. Use realistic transportation methods based on distance and local infrastructure.
    8. For walks under 15 minutes (0.25 hours), use "walk" as transportation.
    9. Ensure the number of objects in the "dailyPlan" array matches the trip length of {preferences['tripLength']} days.
    10. Use your knowledge, grounded by Google Search and Maps, to provide realistic and high-quality suggestions for locations, activities, restaurants, and transportation options.
    11. Include realistic prices in the local currency for all transportation and activities.
  """


def extract_and_parse_json(text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from the response text.

    Args:
        text: The response text containing JSON

    Returns:
        Parsed JSON as a dictionary (Itinerary)
    """
    json_regex = r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})'
    match = re.search(json_regex, text)

    if not match:
        raise ValueError("Failed to find a JSON object in the response.")

    # Use the first capturing group that has content
    json_string = match.group(1) or match.group(2)

    if not json_string:
        raise ValueError("Extracted JSON string is empty.")

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as error:
        print(f"Failed to parse JSON: {json_string}")
        raise ValueError(f"Invalid JSON format: {str(error)}")


def validate_itinerary(itinerary: Dict[str, Any]) -> bool:
    """
    Validate the itinerary structure and transport segments.

    Args:
        itinerary: The parsed itinerary dictionary

    Returns:
        True if valid, raises ValueError otherwise
    """
    if 'dailyPlan' not in itinerary:
        raise ValueError("Itinerary missing 'dailyPlan'")

    for day_plan in itinerary['dailyPlan']:
        if 'activities' not in day_plan:
            raise ValueError(f"Day {day_plan.get('day', '?')} missing 'activities'")

        activities = day_plan['activities']
        prev_coords = None

        for i, activity in enumerate(activities):
            # Check if it's a transport segment
            if activity.get('type') == 'transport':
                required_fields = [
                    'transportationType', 'startPoint', 'endPoint',
                    'startCoordinates', 'endCoordinates', 'duration', 'price'
                ]

                for field in required_fields:
                    if field not in activity:
                        raise ValueError(
                            f"Transport segment on day {day_plan['day']}, "
                            f"activity {i} missing field '{field}'"
                        )

                # Validate coordinates structure
                for coord_field in ['startCoordinates', 'endCoordinates']:
                    coords = activity[coord_field]
                    if 'latitude' not in coords or 'longitude' not in coords:
                        raise ValueError(
                            f"Invalid coordinates in {coord_field} on day "
                            f"{day_plan['day']}, activity {i}"
                        )

                # Check continuity with previous activity
                if prev_coords:
                    start_coords = activity['startCoordinates']
                    if (abs(start_coords['latitude'] - prev_coords['latitude']) > 0.01 or
                            abs(start_coords['longitude'] - prev_coords['longitude']) > 0.01):
                        print(
                            f"Warning: Transport start coordinates don't match "
                            f"previous activity on day {day_plan['day']}, activity {i}"
                        )

                prev_coords = activity['endCoordinates']
            else:
                # Regular activity
                if 'coordinates' in activity:
                    prev_coords = activity['coordinates']

    return True


def generate_itinerary(
        preferences: Dict[str, Any],
        location: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Generate a travel itinerary based on preferences.

    Args:
        preferences: Dictionary with destination, currentLocation, tripLength, budget
        location: Optional dictionary with 'latitude' and 'longitude' keys

    Returns:
        Dictionary with 'itinerary' and 'groundingChunks' keys
    """
    prompt = build_itinerary_prompt(preferences)

    # Build tools configuration
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
        types.Tool(google_maps=types.GoogleMaps())
    ]

    # Build tool config with location if provided
    tool_config = None
    if location:
        tool_config = types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(
                    latitude=location['latitude'],
                    longitude=location['longitude']
                )
            )
        )

    # Generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=tools,
            tool_config=tool_config
        )
    )

    itinerary = extract_and_parse_json(response.text)

    # Validate the itinerary structure
    try:
        validate_itinerary(itinerary)
    except ValueError as e:
        print(f"Warning: Itinerary validation failed: {e}")

    # Extract grounding chunks
    grounding_chunks = []
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            grounding_chunks = candidate.grounding_metadata.grounding_chunks or []

    return {
        'itinerary': itinerary,
        'groundingChunks': grounding_chunks
    }


def start_chat(initial_context: str):
    """
    Start a chat session with the given initial context.

    Args:
        initial_context: System instruction for the chat

    Returns:
        Chat session object
    """
    return client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=initial_context
        )
    )


def calculate_total_transport_cost(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate total transportation costs and breakdown by type.

    Args:
        itinerary: The itinerary dictionary

    Returns:
        Dictionary with total cost and breakdown by transportation type
    """
    total_cost = 0
    transport_breakdown = {}

    for day_plan in itinerary.get('dailyPlan', []):
        for activity in day_plan.get('activities', []):
            if activity.get('type') == 'transport':
                transport_type = activity.get('transportationType', 'unknown')
                price = activity.get('price', 0)

                total_cost += price
                transport_breakdown[transport_type] = transport_breakdown.get(transport_type, 0) + price

    return {
        'totalCost': total_cost,
        'breakdown': transport_breakdown
    }


def get_daily_summary(itinerary: Dict[str, Any], day: int) -> Dict[str, Any]:
    """
    Get a summary of activities and transport for a specific day.

    Args:
        itinerary: The itinerary dictionary
        day: Day number to summarize

    Returns:
        Dictionary with day summary including activity count, transport segments, and total time
    """
    day_plan = next(
        (d for d in itinerary.get('dailyPlan', []) if d.get('day') == day),
        None
    )

    if not day_plan:
        return {'error': f'Day {day} not found'}

    activities = []
    transports = []
    total_duration = 0

    for item in day_plan.get('activities', []):
        duration = item.get('duration', 0)
        total_duration += duration

        if item.get('type') == 'transport':
            transports.append({
                'type': item.get('transportationType'),
                'from': item.get('startPoint'),
                'to': item.get('endPoint'),
                'duration': duration,
                'price': item.get('price', 0)
            })
        else:
            activities.append({
                'name': item.get('name'),
                'duration': duration,
                'price': item.get('price', 0)
            })

    return {
        'day': day,
        'theme': day_plan.get('theme'),
        'activityCount': len(activities),
        'transportCount': len(transports),
        'totalDuration': total_duration,
        'activities': activities,
        'transports': transports
    }

if __name__ == "__main__":
    preferences = {"destination": "Singapore", "tripLength": "3 days", "budget": "10000", "currentLocation": {"latitude": 43.0, "longitude": 79.0}}
    location = {"latitude": 43.0, "longitude": -79.0}
    print(generate_itinerary(preferences, location))
