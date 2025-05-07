from pathlib import Path
import json
import re
import logging
import google.generativeai as genai
from app.config import GEMINI_API_KEY

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)
logger = logging.getLogger(__name__)

def load_journal_prompt():
    path = Path(__file__).parent.parent / "prompts" / "journal_prompt.txt"
    return path.read_text(encoding="utf-8")

def extract_json_from_code_block(text: str) -> dict:
    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.warning("Failed to parse Gemini response as JSON: %s", e)
        logger.debug("Raw response text:\n%s", text)
        return []

def generate_travel_journal(title: str, description: str, mission: str, city: str) -> dict:
    prompt_template = load_journal_prompt()
    prompt = prompt_template.format(
        title=title,
        description=description,
        mission=mission,
        city=city
    )

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    logger.debug("AI Journal Raw Output: %s", response.text)

    journal = extract_json_from_code_block(response.text)
    return journal
