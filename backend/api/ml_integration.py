"""
Example ML Integration for Itinerary Generation

This file shows you how to integrate your ML model with the API.
Replace this dummy implementation with your actual ML model.

Usage:
1. Import this in api/views.py:
   from .ml_integration import generate_itinerary_with_ml

2. Replace the dummy data in ItineraryViewSet.generate() with:
   generated_data = generate_itinerary_with_ml(region, needs)
"""


def generate_itinerary_with_ml(region: str, needs: str) -> list[dict]:
    """
    Generate an itinerary using your ML model.
    
    Args:
        region (str): The region/location for the trip (e.g., "Toronto")
        needs (str): User's requirements (e.g., "3 day trip, love museums")
    
    Returns:
        list[dict]: A list of itinerary items in the format:
            [
                {
                    "desc": "Activity description",
                    "loc": "Location name",
                    "order": 0
                },
                ...
            ]
    
    Example:
        >>> generate_itinerary_with_ml("Toronto", "2 days, food and culture")
        [
            {"desc": "Visit CN Tower", "loc": "CN Tower", "order": 0},
            {"desc": "Explore ROM", "loc": "Royal Ontario Museum", "order": 1},
            {"desc": "Dinner at St. Lawrence Market", "loc": "St. Lawrence Market", "order": 2}
        ]
    """
    
    # ============================================
    # REPLACE THIS WITH YOUR ML MODEL
    # ============================================
    
    # Example: If you're using OpenAI, Anthropic, or local LLM:
    # prompt = f"Generate a detailed itinerary for {region} with the following requirements: {needs}"
    # response = your_llm_client.generate(prompt)
    # parsed_items = parse_llm_response(response)
    # return parsed_items
    
    # Example: If you're using a trained model:
    # model_input = prepare_input(region, needs)
    # predictions = your_model.predict(model_input)
    # formatted_items = format_predictions(predictions)
    # return formatted_items
    
    # ============================================
    # DUMMY IMPLEMENTATION (Remove this!)
    # ============================================
    
    dummy_activities = [
        {
            "desc": f"AI Generated: Start your journey in {region}",
            "loc": f"{region} Downtown",
            "order": 0
        },
        {
            "desc": f"AI Generated: Explore famous landmarks",
            "loc": "Main Attraction",
            "order": 1
        },
        {
            "desc": f"AI Generated: Experience local cuisine",
            "loc": "Popular Restaurant District",
            "order": 2
        },
    ]
    
    # You can make this smarter based on 'needs'
    if "museum" in needs.lower():
        dummy_activities.append({
            "desc": f"AI Generated: Visit a museum in {region}",
            "loc": f"{region} Museum",
            "order": 3
        })
    
    if "food" in needs.lower() or "restaurant" in needs.lower():
        dummy_activities.append({
            "desc": f"AI Generated: Dine at a local restaurant",
            "loc": "Recommended Restaurant",
            "order": len(dummy_activities)
        })
    
    return dummy_activities


def parse_llm_response(response: str) -> list[dict]:
    """
    Helper function to parse LLM response into structured format.
    
    Example:
        If your LLM returns:
        "1. Visit CN Tower at 301 Front St W
         2. Explore ROM at 100 Queens Park"
        
        This should return:
        [
            {"desc": "Visit CN Tower", "loc": "301 Front St W", "order": 0},
            {"desc": "Explore ROM", "loc": "100 Queens Park", "order": 1}
        ]
    """
    # TODO: Implement your parsing logic
    items = []
    # Parse the response...
    return items


# ============================================
# Example Integration Code (Copy to views.py)
# ============================================

"""
In api/views.py, replace the dummy data section in ItineraryViewSet.generate():

# Before (current dummy code):
generated_data = [
    {"desc": "...", "loc": "...", "order": 0},
]

# After (with ML integration):
from .ml_integration import generate_itinerary_with_ml

generated_data = generate_itinerary_with_ml(region, needs)
"""
