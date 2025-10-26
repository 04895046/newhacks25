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


def build_prompt(country) -> str:
    """
    Build the itinerary prompt from travel preferences.

    Args:
    """
    return "Return a brief (a few sentences) introduction about " + country + " for tourists, and include within some famous tourist attractions or points of interest."





def get_intro(country: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_prompt(country)
    )
    print(response.text)
