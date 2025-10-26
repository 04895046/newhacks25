import json
import os

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
                        "description": "The estimated price of admission or visit, represented as an integer (e.g., 15, 0 for free). Omit currency symbols."
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
                        "description": "The estimated cost of the journey, represented as an integer (e.g., 500, 0 for free). Omit currency symbols."
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

TRAVEL_RATING_SCHEMA = {
    "type": "object",
    "description": "A comprehensive travel rating and advisory system for a given destination.",
    "properties": {
        "destination_name": {
            "type": "string",
            "description": "The name of the country or specific region being rated."
        },
        "cultural_historical": {
            "type": "object",
            "description": "Rating and explanation for cultural/historical value.",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 (low) to 5 (high) based on cultural and historical significance."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation justifying the cultural and historical value rating."
                }
            },
            "required": ["value", "explanation"]
        },
        "natural_beauty": {
            "type": "object",
            "description": "Rating and explanation for natural beauty.",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 (low) to 5 (high) based on scenic/nature quality and natural (parks, vistas) attractions."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation justifying the natural beauty rating."
                }
            },
            "required": ["value", "explanation"]
        },
        "relaxation": {
            "type": "object",
            "description": "Rating and explanation for relaxation.",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 (low) to 5 (high) based on opportunities for rest, peace, and low-stress environment."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation justifying the relaxation rating."
                }
            },
            "required": ["value", "explanation"]
        },
        "shopping": {
            "type": "object",
            "description": "Rating and explanation for shopping.",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 (low) to 5 (high) based on the quality and variety of shopping experiences."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation justifying the shopping rating."
                }
            },
            "required": ["value", "explanation"]
        },
        "entertainment_nightlife": {
            "type": "object",
            "description": "Rating and explanation for entertainment/nightlife.",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 (low) to 5 (high) based on the vibrancy and diversity of nightlife and entertainment options."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation justifying the entertainment and nightlife rating."
                }
            },
            "required": ["value", "explanation"]
        },
        "budget_friendliness": {
            "type": "object",
            "description": "Rating and explanation for budget friendliness.",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 (expensive) to 5 (very affordable) for general travel costs."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation justifying the budget friendliness rating."
                }
            },
            "required": ["value", "explanation"]
        },
        "safety": {
            "type": "object",
            "description": "Safety advisory status and explanation.",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [
                        "Take normal security precautions",
                        "Exercise a high degree of caution",
                        "Avoid non-essential travel",
                        "Avoid all travel"
                    ],
                    "description": "The concise official travel advisory status, restricted to one of four options based on travel.gc.ca."
                },
                "explanation": {
                    "type": "string",
                    "description": "A short, distinct explanation justifying the safety_status, based on travel.gc.ca advisories."
                }
            },
            "required": ["status", "explanation"]
        }
    },
    "required": [
        "destination_name",
        "cultural_historical",
        "natural_beauty",
        "relaxation",
        "shopping",
        "entertainment_nightlife",
        "budget_friendliness",
        "safety"
    ]
}

def get_travel_ratings_list(destinations: list[str]):
    """
    Generates structured travel ratings for multiple destinations, enforcing source
    constraints using search queries embedded in the user prompt.

    Args:
        destinations: A list of country or sub-national areas to rate.
    """
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return []

    all_ratings = []  # List to store all results

    # 2. Define the Prompt with all constraints and grounding instructions embedded
    # This will be done *inside* the loop

    # 3. Configure the generation request for JSON output and search grounding
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=TRAVEL_RATING_SCHEMA,
    )

    # --- Loop through each destination ---
    for destination in destinations:
        prompt_text = f"""
        You are an expert travel analyst. Your task is to provide a comprehensive rating for the destination: {destination}.
        STRICTLY follow these rules for populating the JSON schema:

        1. For ALL fields ending in '_explanation', provide a short, distinct justification for the corresponding integer rating.

        2. For the 'safety_status' field, you MUST provide only the concise status phrase from the following four, and ONLY these four, options. Select the most appropriate option based on the EXACT URL: https://travel.gc.ca/travelling/advisories.
        The detailed reasoning MUST go into the 'safety_explanation' field. To find the correct status, use Google Search and specifically check the official travel advisory from travel.gc.ca for {destination}.
            - "Take normal security precautions"
            - "Exercise a high degree of caution"
            - "Avoid non-essential travel"
            - "Avoid all travel"

        3. For all other fields (the 1-5 ratings and explanations), you MUST ONLY use information from either https://travel.gc.ca/travelling/advisories or wikipedia.org. If you need context for cultural/natural/etc., prioritize Wikipedia.

        4. Ensure all ratings are integers (1-5).

        Provide the travel rating and advisory data for the destination: {destination}.
        """

        print(f"\n--- API Call: Travel Ratings for {destination} (No System Instruction) ---")

        # 5. Make the API call, passing the prompt_text string directly as contents
        try:
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt_text,
                config=config,
            )

            # 6. Process and display the structured response
            print(f"\n--- Structured Travel Rating Response (JSON) for {destination} ---")
            parsed_json = json.loads(response.text)
            print(json.dumps(parsed_json, indent=2))
            print("------------------------------------------")
            all_ratings.append(parsed_json)

        except Exception as e:
            print(f"An error occurred during the API call for {destination}: {e}")
            all_ratings.append(None)  # Add None on failure for this item

    return all_ratings  # Return the list of results

def get_travel_ratings(destination: str):
    """
    Generates structured travel ratings for a destination, enforcing source
    constraints using search queries embedded in the user prompt.

    Args:
        destination: The country or sub-national area to rate.
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("FATAL ERROR: GEMINI_API_KEY environment variable not found. Cannot run API call.")
        return

    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return

    # 2. Define the Prompt with all constraints and grounding instructions embedded
    prompt_text = f"""
    You are an expert travel analyst. Your task is to provide a comprehensive rating for the destination: {destination}.
    STRICTLY follow these rules for populating the JSON schema:

    1. For ALL fields ending in '_explanation', provide a short, distinct justification for the corresponding integer rating.

    2. For the 'safety_status' field, you MUST provide only the concise status phrase from the following four, and ONLY these four, options. Select the most appropriate option based on the EXACT URL: https://travel.gc.ca/travelling/advisories.
    The detailed reasoning MUST go into the 'safety_explanation' field. To find the correct status, use Google Search and specifically check the official travel advisory from travel.gc.ca for {destination}.
        - "Take normal security precautions"
        - "Exercise a high degree of caution"
        - "Avoid non-essential travel"
        - "Avoid all travel"

    3. For all other fields (the 1-5 ratings and explanations), you MUST ONLY use information from either https://travel.gc.ca/travelling/advisories or wikipedia.org. If you need context for cultural/natural/etc., prioritize Wikipedia.

    4. Ensure all ratings are integers (1-5).

    Provide the travel rating and advisory data for the destination: {destination}.
    """

    # 3. Configure the generation request for JSON output and search grounding
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=TRAVEL_RATING_SCHEMA,
    )

    print(f"\n--- API Call: Travel Ratings for {destination} ---")

    # 6. Make the API call
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt_text,
            config=config,
        )

        # 6. Process and display the structured response
        print("\n--- Structured Travel Rating Response (JSON) ---")
        parsed_json = json.loads(response.text)
        print(json.dumps(parsed_json, indent=2))
        print("------------------------------------------")

        return parsed_json  # Return the data

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        return None


def generate_structured_itinerary(currLocation: str, destRegion: str, details: str):
    """
    Calls the Gemini API to generate a structured itinerary.

    Args:
        currLocation: The user's current city (e.g., 'Toronto').
        destRegion: The main city to visit (e.g., 'Paris' or 'Toronto').
        details: Specifics for the itinerary (e.g., '3 days, focus on art').
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("FATAL ERROR: GEMINI_API_KEY environment variable not found. Cannot run API call.")
        return

    # 2. Crafting a highly specific prompt to enforce all constraints
    travel_segments_instruction = ""
    if currLocation.lower().strip() == destRegion.lower().strip():
        travel_segments_instruction = "The user is already in the destination city. DO NOT include any JOURNEY segments to or from the start city. The itinerary must only contain alternating DESTINATION and local JOURNEY segments."
    else:
        travel_segments_instruction = f"""
        1. The first segment of the array MUST be a JOURNEY segment from the user's current city, {currLocation}, to the first destination.
        2. The last segment of the array MUST be a JOURNEY segment from the last destination back to {currLocation}.
        """

    # 3. Explicitly instructing on the price and duration formats
    format_instruction = """
    CRITICAL FORMATTING RULES:
    - All 'price' fields MUST be integers (e.g., 15, 500). Use 0 if the price is free.
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
        return

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ITINERARY_SCHEMA,
    )

    print(f"\n--- API Call: Itinerary to {destRegion} ---")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=config,
        )

        print("\n--- Structured Itinerary Response (JSON) ---")
        parsed_json = json.loads(response.text)
        print(json.dumps(parsed_json, indent=2))
        print("------------------------------------------")
        return parsed_json

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        return None


# --- Example Usage ---
if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("\n GEMINI_API_KEY environment variable not found.")
    else:
        # Example demonstrating integer price (no currency) and float duration
        currLocation = "Toronto, Canada"
        destRegion = "Erbil"
        details = "A 2-day itinerary focusing on general tourist attractions."
        # generate_structured_itinerary(currLocation, destRegion, details)
        generate_structured_itinerary(currLocation, "Toronto", details)
