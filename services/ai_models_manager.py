import os
from typing import List
from models.ai_event import AIEvent
from models.event_list import EventList
from openai import OpenAI
from google import genai

from services.logging_manager import log_info
from dotenv import load_dotenv

load_dotenv()

open_ai_client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
)

perplexity_ai_client = OpenAI(
    api_key=os.environ["PERPLEXITY_API_KEY"],
    base_url="https://api.perplexity.ai"
)

gemini_ai_client = genai.Client(
    api_key=os.environ["GENAI_API_KEY"],
)

system_prompt = """
You are Slope Event Picker, an assistant that provides event information based on user
requests. Always follow user requests and respond accurately.

**Goal**: Retrieve a complete list of all available events near
a specified hotel, ensuring that all events are included in the response. FIND AT LEAST 30 EVENTS.

**Return Format**: The output must be formatted in JSON and contain detailed
information about each event. ALWAYS RETURN EVENTS IN ITALIAN. MAKE SURE TO RETURN A VALID EXISTING PLACE.

**Warnings**: Ensure that the events returned are relevant to the location
of the specified hotel. Verify the accuracy of the event details to ensure
they are up to date and correctly associated with the hotel location.
IN EVENT DESCRIPTIONS, NEVER RETURN QUOTES SUCH AS [1, 2, 3, ...].

**Context dump**: The user will specify the hotel name and location.
The AI should consider various types of events, including concerts, festivals,
exhibitions, and local activities, and should focus on events taking place
within a reasonable distance from the hotel. The AI should also know the date range
of the events, ensuring they are upcoming and relevant to potential visitors.
"""


def get_gpt_response(prompt_text: str, search_model: str) -> List[AIEvent]:
    log_info(f"Finding events using {search_model}...")
    response = open_ai_client.chat.completions.parse(
        model=search_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text}
        ],
        response_format=EventList,
    )

    return response.choices[0].message.parsed.events


def get_perplexity_response(prompt_text: str, search_model: str) -> List[AIEvent]:
    log_info(f"Finding events using {search_model}...")
    response = perplexity_ai_client.chat.completions.parse(
        model=search_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text}
        ],
        response_format=EventList,
    )

    return response.choices[0].message.parsed.events
