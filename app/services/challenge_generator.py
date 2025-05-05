import os
import json
import requests
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from app.config import GEMINI_API_KEY, SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID

# Configure Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

def load_prompt_template():
    path = Path(__file__).parent.parent / "prompts" / "challenge_prompt.txt"
    return path.read_text(encoding="utf-8")

def generate_challenges(city: str, style: str, date: str, count: int = 5):
    try:
        dt = datetime.strptime(date, "%y/%m/%d")
        weekday = dt.strftime("%A")
        full_date = dt.strftime("%Y-%m-%d (%A)")
    except ValueError:
        raise ValueError("Date format must be 'YY/MM/DD'. Example: '25/05/07'")

    template = load_prompt_template()
    prompt = template.format(city=city, style=style, date=full_date, count=count)

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    
    challenges = parse_response_to_dicts(response.text)

    #Add cultural background and image URL to each challenge
    for c in challenges:
        title = c.get("title", "")
        location = c.get("location", "")
        c["culture_background"] = search_cultural_background(city, title, location)
        c["image_url"] = search_image_url(title, location, city)

    return challenges

def search_cultural_background(city: str, title: str, location: str) -> str:
    query = f"cultural background of {title} at {location}, in {city}"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": SEARCH_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query,
        "num": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            snippet = data["items"][0].get("snippet", "")
            return summarize_text(snippet)
        else:
            return "No results found."
    except requests.exceptions.RequestException as req_err:
        return f"Request error: {str(req_err)}"
    except ValueError as val_err:
        return f"JSON parsing error: {str(val_err)}"

def search_image_url(title: str, location: str, city: str) -> str:
    query = f"{location} {title} in {city} photo"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": SEARCH_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query,
        "searchType": "image",  # Use this to search for images
        "num": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["link"]  # Image URL
        else:
            return "No image found."
    except Exception as e:
        return f"Image search error: {e}"

def summarize_text(text: str) -> str:
    prompt = (
        "You are a travel assistant specialized in cultural history.\n"
        "Summarize the following content into exactly 3 concise and informative sentences:\n"
        "- Focus only on cultural and historical background relevant to travelers\n"
        "- Avoid promotional or irrelevant details and Personal opinions aside.\n"
        "- Use a tone that is clear, factual, and helpful for understanding the local culture\n\n"
        f"Content:\n{text}\n\nCultural Summary (3 sentences):"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text.strip()


def parse_response_to_dicts(text: str):
    import re
    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        return json.loads(cleaned) if cleaned else []
    except Exception as e:
        print("⚠️ JSON parsing failed:", e)
        print("📄 Raw text:\n", text)
        return []
