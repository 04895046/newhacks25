import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- 1. SCHEMAS (Updated ITINERARY_SCHEMA to match user's request) ---

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
                                "description": "The longitude (e.3376)."
                            }
                        },
                        "required": [
                            "latitude",
                            "longitude"
                        ]
                    },
                    # Additional fields added to destination_details to match JS supplemental needs
                    "address": {
                        "type": "string",
                        "description": "The full physical street address."
                    },
                    "description": {
                        "type": "string",
                        "description": "A concise summary of the location and its fame."
                    },
                    "price": {
                        "type": "integer",
                        "description": "The estimated price of admission or visit, represented as an integer (e.g., 15, 0 for free). Omit currency symbols."
                    },
                    "visit_duration_hours": {
                        "type": "number",
                        "format": "float",
                        "description": "The estimated time needed for the visit, in hours (e.g., 2.5)."
                    },
                    "bookingLink": {
                        "type": "string",
                        "description": "Use Google Search to find the official booking URL for this specific activity. If none exists, set to null."
                    }
                },
                "required": [
                    "location_name",
                    "location_coordinates",
                    "price",
                    "visit_duration_hours",
                    "address",  # Now required as it will be filled by a grounded model
                    "description",  # Now required as it will be filled by a grounded model
                    "bookingLink"
                ]
            },
            "journey_details": {
                "type": "object",
                "description": "Details for a JOURNEY segment. Present only when segment_type is 'JOURNEY'.",
                "properties": {
                    "start_point": {
                        "type": "string",
                        "description": "The name of the journey's origin (e.g., 'Toronto Pearson Airport')."
                    },
                    "end_point": {
                        "type": "string",
                        "description": "The name of the journey's destination."
                    },
                    "transport_type": {
                        "type": "string",
                        "description": "The method of transportation (e.g., Flight, Train, Car, Walk). If available, include a flight or train number."
                    },
                    "expected_duration_hours": {
                        "type": "number",
                        "format": "float",
                        "description": "The expected duration in hours, as a float (e.g., 8.5, 0.25)."
                    },
                    "price": {
                        "type": "integer",
                        "description": "The estimated price of the journey in USD (e.g., 500, 0 for free)."
                    },
                    "route_polyline": {
                        "type": "string",
                        "description": "An encoded polyline string from a map API representing the route path/curve."
                    },
                    "bookingLink" : {
                        "type": "string",
                        "description": "Use Google Search to create a pre-filled Google Flights URL (or similar for other methods of transportation) for the specified route."
                    }
                },
                "required": [
                    "start_point",
                    "end_point",
                    "route_polyline",
                    "transport_type",  # Now required as it will be filled by a grounded model
                    "expected_duration_hours",  # Now required as it will be filled by a grounded model
                    "price",  # Now required as it will be filled by a grounded model
                    "bookingLink"
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


# --- 2. HELPER FUNCTIONS ---

def _extract_attributions(response: types.GenerateContentResponse) -> list[dict]:
    """
    Extracts web grounding attributions (URI and title) from a Gemini response.
    """
    attributions = []
    if not response.candidates:
        return attributions

    candidate = response.candidates[0]

    # Safely check for grounding_metadata and attributions
    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:

        if (hasattr(candidate.grounding_metadata, 'grounding_chunks') and
                candidate.grounding_metadata.grounding_chunks):

            for chunk in candidate.grounding_metadata.grounding_chunks:
                if chunk.web:
                    attributions.append({
                        "uri": chunk.web.uri,
                        "title": chunk.web.title
                    })
                elif chunk.maps:
                    attributions.append({
                        "uri": chunk.maps.uri,
                        "title": chunk.maps.title
                    })
        # Removed the diagnostic print here to keep the function clean,
        # relying on the calling function to report success/failure.

    return attributions


def _extract_and_parse_json(text: str, schema_name: str) -> dict:
    """
    Extracts JSON wrapped in a markdown block (```json) from a text response.
    """
    json_regex = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)
    match = json_regex.search(text)

    if not match:
        # Fallback for when the model skips the markdown wrapper
        print(f"   [WARNING] Failed to find JSON markdown block. Attempting raw parse for {schema_name}.")
        # Use the entire text as a fallback, trimming common pre/post-text
        json_string = text.strip()
    else:
        json_string = match.group(1).strip()

    if not json_string:
        raise ValueError(f"Extracted JSON string is empty for {schema_name}.")

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"   [ERROR] Failed to parse JSON for {schema_name}: {e}")
        # Print the problematic string for debugging
        print(f"   [ERROR] Problematic string: {json_string[:500]}...")
        raise ValueError(f"Invalid JSON format for {schema_name}.")


# --- 3. MAIN API HANDLER FUNCTIONS ---


def get_travel_ratings_list(destinations: list[str], location: dict = None):
    """
    Generates structured travel ratings for multiple destinations using
    flexible text output (JSON in markdown) to encourage grounding.
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("FATAL ERROR: GEMINI_API_KEY environment variable not found. Cannot run API call.")
        return []

    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return []

    all_ratings = []

    # Configuration for text output with search tool
    config = types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        # Tool config with geolocation context (same pattern as JS for future use)
        tool_config={
            "retrieval_config": {
                "lat_lng": location
            }
        } if location else None
    )

    for destination in destinations:
        prompt_text = f"""
        You are an expert travel analyst. Your task is to provide a comprehensive rating for the destination: {destination}.
        Your final output MUST be a single JSON object that strictly follows the provided schema.

        To ensure stability, wrap the JSON object in a single ````json` markdown block. DO NOT include any text, explanation, or markdown formatting outside of this block.

        STRICTLY follow these rules for populating the JSON schema:

        1. For ALL rating categories (cultural_historical, natural_beauty, relaxation, shopping, entertainment_nightlife, budget_friendliness), you MUST provide a nested JSON object containing:
           - "value": An integer rating from 1 to 5.
           - "explanation": A short string justification for the rating.

        2. For the 'safety' field, you MUST provide a nested JSON object containing:
           - "status": You MUST provide only the concise status phrase from the following four, and ONLY these four, options. Select the most appropriate option based on the EXACT URL: [https://travel.gc.ca/travelling/advisories](https://travel.gc.ca/travelling/advisories).
                - "Take normal security precautions"
                - "Exercise a high degree of caution"
                - "Avoid non-essential travel"
                - "Avoid all travel"
           - "explanation": The detailed reasoning MUST go into this field.

        To find the correct status for the 'safety.status' field, use Google Search and specifically check the official travel advisory from travel.gc.ca for {destination}.

        3. For all other fields (the 1-5 ratings and explanations), you MUST ONLY use information from either [https://travel.gc.ca/travelling/advisories](https://travel.gc.ca/travelling/advisories) or wikipedia.org. If you need context for cultural/natural/etc., prioritize Wikipedia.

        4. Ensure all integer ratings are integers (1-5).

        Provide the travel rating and advisory data for the destination: {destination}.
        """

        print(f"\n--- API Call: Travel Ratings for {destination} (Now using flexible JSON output) ---")

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_text,
                config=config,
            )

            # Use the new flexible extractor
            parsed_json = _extract_and_parse_json(response.text, "Travel Rating")
            attributions = _extract_attributions(response)

            print(f"\n--- Structured Travel Rating Response (JSON) for {destination} ---")
            print(json.dumps(parsed_json, indent=2))
            print(f"--- Attributions Found: {len(attributions)} ---")
            if attributions:
                for attr in attributions:
                    print(f"Title: {attr['title']} | URI: {attr['uri']}")
            print("------------------------------------------")

            all_ratings.append({
                "rating_data": parsed_json,
                "attributions": attributions
            })

        except Exception as e:
            print(f"An error occurred during the API call for {destination}: {e}")
            all_ratings.append({"rating_data": None, "attributions": []})

    return all_ratings

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

    # print(f"\n--- API Call: Travel Ratings for {destination} ---")

    # 6. Make the API call
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=config,
        )

        # 6. Process and display the structured response
        # print("\n--- Structured Travel Rating Response (JSON) ---")
        parsed_json = json.loads(response.text)
        print(json.dumps(parsed_json, indent=2) + ",")
        # print("------------------------------------------")

        return parsed_json  # Return the data

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        return None



def generate_structured_itinerary(currLocation: str, destRegion: str, details: str, location: dict = None):
    """
    Generates a full itinerary in a single, robust, grounded API call,
    mimicking the successful JS configuration.
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("FATAL ERROR: GEMINI_API_KEY environment variable not found. Cannot run API call.")
        return

    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return

    # --- Configuration: Use multiple tools and Geolocation Context (like JS) ---
    config = types.GenerateContentConfig(
        # Use both search and maps for enhanced grounding
        tools=[{"google_search": {}}, {"google_maps": {}}],
        # Pass the geolocation object if available
        tool_config={
            "retrieval_config": {
                "lat_lng": location
            }
        } if location else None
    )

    travel_segments_instruction = ""
    if currLocation.lower().strip() == destRegion.lower().strip():
        travel_segments_instruction = "The user is already in the destination city. DO NOT include any JOURNEY segments to or from the start city. The itinerary must only contain alternating DESTINATION and local JOURNEY segments."
    else:
        travel_segments_instruction = f"""
        1. The first segment of the array MUST be a JOURNEY segment from the user's current city, {currLocation}, to the first destination.
        2. The last segment of the array MUST be a JOURNEY segment from the last destination back to {currLocation}.
        """

    prompt = f"""
    Create a detailed travel itinerary for a trip to {destRegion}.
    Your final output MUST be a single JSON object that strictly follows the provided schema.

    To ensure stability and maximize grounding, wrap the JSON object in a single ````json` markdown block. DO NOT include any text, explanation, or markdown formatting outside of this block.

    Itinerary Rules:
    {travel_segments_instruction}

    All other segments within the array must alternate between DESTINATION and local JOURNEY segments within the city.

    IMPORTANT: You MUST populate ALL required fields in the schema (location_name, coordinates, price, duration, address, description, etc.) using up-to-date, real-world data found through your available tools.

    Trip details: {details}.
    
    Ensure the number of objects in the array matches the trip length specified. 
    Use your knowledge, grounded by Google Search and Maps, to provide realistic and high-quality suggestions for locations, activities, and restaurants.
    """

    print(f"\n--- API Call: Generating Itinerary for {destRegion} (Single grounded call) ---")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config,
        )

        # Use the new flexible extractor
        final_itinerary = _extract_and_parse_json(response.text, "Itinerary")
        total_attributions = _extract_attributions(response)

    except Exception as e:
        print(f"An error occurred during Itinerary Generation: {e}")
        return {"itinerary_data": None, "attributions": []}

    # --- Final Output ---
    print("\n--- FINAL STRUCTURED ITINERARY (Combined Steps) ---")
    print(json.dumps(final_itinerary, indent=2))
    print(f"--- Total Attributions Found: {len(total_attributions)} ---")
    if total_attributions:
        for attr in total_attributions:
            print(f"Title: {attr['title']} | URI: {attr['uri']}")
    print("------------------------------------------")

    return {
        "itinerary_data": final_itinerary,
        "attributions": total_attributions
    }


# --- Example Usage ---
if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("\n WARNING: GEMINI_API_KEY environment variable not found.")
    else:
        # Example 2: Generate an Itinerary (Now uses single, grounded call with multiple tools)
        currLocation = "Toronto, Canada"
        destRegion = "Gros Morne, Newfoundland"
        details = "A 3-day itinerary focusing on major hikes."
        # Dummy location data to test geolocation context
        user_location_context = {"latitude": 43.6532, "longitude": -79.3832}
        print(f"\n\n\n--- RUNNING SINGLE-CALL GROUNDED ITINERARY GENERATION ---")
        itinerary_result = generate_structured_itinerary(currLocation, destRegion, details,
                                                         location=user_location_context)
