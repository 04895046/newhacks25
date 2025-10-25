import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Define the final, updated structured response schema
ITINERARY_SCHEMA = {
    "type": "array",
    "description": "A detailed, ordered itinerary composed of alternating destination and journey segments. The FIRST and LAST segments MAY be a JOURNEY segment for travel to and from the starting city, but must be omitted if the starting city is the same as the destination city.",
    "items": {
        "type": "object",
        "description": "A single segment of the itinerary, which can be a Destination or a Journey.",
        "properties": {
            "segment_type": {
                "type": "string",
                "enum": [
                    "DESTINATION",
                    "JOURNEY"
                ],
                "description": "Identifies whether the segment is a location to be visited or a trip between locations."
            },
            "destination_details": {
                "type": "object",
                "description": "Details for a DESTINATION segment. Present only when segment_type is 'DESTINATION'.",
                "properties": {
                    "location_name": {
                        "type": "string",
                        "description": "The common name of the destination (e.g., 'Louvre Museum')."
                    },
                    "location_coordinates": {
                        "type": "object",
                        "description": "The geographical coordinates in decimal degrees.",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "format": "float",
                                "description": "The latitude (e.g., 48.8606)."
                            },
                            "longitude": {
                                "type": "number",
                                "format": "float",
                                "description": "The longitude (e.g., 2.3376)."
                            }
                        },
                        "required": [
                            "latitude",
                            "longitude"
                        ]
                    },
                    "address": {
                        "type": "string",
                        "description": "The physical street address of the destination."
                    },
                    "price": {
                        "type": "integer",
                        "description": "The estimated price of admission or visit, represented as an integer string (e.g., '15', '0' for free). Omit currency symbols."
                    },
                    "description": {
                        "type": "string",
                        "description": "A brief summary of the location."
                    },
                    "visit_duration_hours": {
                        "type": "number",
                        "format": "float",
                        "description": "The estimated time needed for the visit, in hours (e.g., 2.5)."
                    }
                },
                "required": [
                    "location_name",
                    "location_coordinates",
                    "address",
                    "price",
                    "description",
                    "visit_duration_hours"
                ]
            },
            "journey_details": {
                "type": "object",
                "description": "Details for a JOURNEY segment. Present only when segment_type is 'JOURNEY'.",
                "properties": {
                    "transport_type": {
                        "type": "string",
                        "description": "The method of transportation (e.g., 'Flight', 'Train', 'Car', 'Walk')."
                    },
                    "start_point": {
                        "type": "string",
                        "description": "The name of the journey's origin (e.g., 'Toronto Pearson Airport')."
                    },
                    "end_point": {
                        "type": "string",
                        "description": "The name of the journey's destination."
                    },
                    "route_polyline": {
                        "type": "string",
                        "description": "An encoded polyline string from a map API representing the route path/curve."
                    },
                    "price": {
                        "type": "integer",
                        "description": "The estimated cost of the journey, represented as an integer string (e.g., '500', '0' for free). Omit currency symbols."
                    },
                    "expected_duration_hours": {
                        "type": "number",
                        "format": "float",
                        "description": "The estimated time needed for the journey, in hours (e.g., 8.5 for a flight, 0.25 for a 15-minute walk)."
                    }
                },
                "required": [
                    "transport_type",
                    "start_point",
                    "end_point",
                    "price",
                    "expected_duration_hours"
                ]
            }
        },
        "required": [
            "segment_type"
        ]
    }
}


def generate_structured_itinerary(currLocation: str, destRegion: str, details: str):
    """
    Calls the Gemini API to generate a structured itinerary, enforcing the integer price (as string)
    without currency and the conditional start/end journey segments.

    Args:
        currLocation: The user's current city (e.g., 'Toronto').
        destRegion: The main city to visit (e.g., 'Paris' or 'Toronto').
        details: Specifics for the itinerary (e.g., '3 days, focus on art').
    """
    # 2. Crafting a highly specific prompt to enforce all constraints
    travel_segments_instruction = f"""
    1. The first segment of the array should be a JOURNEY segment from the user's current city, {currLocation}, to the first destination unless they are the same region.
    2. The last segment of the array should be a JOURNEY segment from the last detination back to {currLocation} unless they are the same region.
    """

    # 3. Explicitly instructing on the price and duration formats
    format_instruction = """
    CRITICAL FORMATTING RULES:
    - All 'price' fields MUST be represented as an integer string (e.g., '15', '500'). OMIT ALL CURRENCY SYMBOLS. Use '0' if the price is free.
    - All journey and visit durations MUST be in 'hours' and represented as a float (e.g., 8.5, 0.25).
    """

    prompt = f"""
    Create a detailed travel itinerary for a trip to {destRegion}.
    The itinerary must follow the structured JSON schema and these rules:

    {travel_segments_instruction}

    All other segments within the array must alternate between DESTINATION and local JOURNEY segments within the city.

    {format_instruction}

    Trip details: {details}.
    """

    # Client initialization and API call logic
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        print("Please ensure the GEMINI_API_KEY environment variable is set.")
        return

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ITINERARY_SCHEMA,
    )

    print(f"Sending prompt to Gemini with structured output request...")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config,
        )

        print("\n--- Structured Itinerary Response (JSON) ---")
        parsed_json = json.loads(response.text)
        print(json.dumps(parsed_json, indent=2))
        print("------------------------------------------")

    except Exception as e:
        print(f"An error occurred during the API call: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("\n GEMINI_API_KEY environment variable not found.")
    else:
        # Example demonstrating integer price (no currency) and float duration
        currLocation = "Toronto, Canada"
        destRegion = "Paris, France"
        details = "A 2-day itinerary focusing on major landmarks and food, showing prices and travel times."

        generate_structured_itinerary(currLocation, destRegion, details)
