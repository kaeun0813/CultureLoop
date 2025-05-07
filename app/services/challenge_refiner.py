import json
import re
import requests
from pathlib import Path
import google.generativeai as genai
from app.config import GEMINI_API_KEY, SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID
import logging

# 로그 설정
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

# Load prompt template for challenge refinement
def load_refine_prompt():
    path = Path(__file__).parent.parent / "prompts" / "refine_prompt.txt"
    return path.read_text(encoding="utf-8")


# Main function: refine a local challenge
def refine_challenge(title: str, description: str, city: str) -> dict:
    prompt_template = load_refine_prompt()
    prompt = prompt_template.format(title=title, city=city, description=description)

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    # 로그 출력
    logger.debug("Raw response text: %s", response.text)

    refined = parse_json_response(response.text)
    if "error" in refined:
        raise ValueError(refined["error"])

    refined["cultural_background"] = search_cultural_background(title, city)
    return refined

def refine_challenge(title: str, description: str, city: str) -> dict:
    prompt_template = load_refine_prompt()
    prompt = prompt_template.format(title=title, city=city, description=description)

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    # 응답 로그 추가
    logger.debug("Raw response text: %s", response.text)
    
    # ```json 또는 { 로 시작하는 응답 허용  -> (선택사항)
    if not re.search(r"^\s*(\{|\`\`\`json)", response.text):
        logger.error("Invalid response format: %s", response.text)
        raise ValueError(f"Invalid response format: {response.text}")
    
    refined = parse_json_response(response.text)
    
    if "error" in refined:
        raise ValueError(refined["error"])

    refined["cultural_background"] = search_cultural_background(title, city)
    return refined


# Search cultural background using Google Custom Search
def search_cultural_background(title: str, city: str) -> str:
    query = f"cultural background of {title} in {city}"
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
    except Exception as e:
        return f"Search error: {str(e)}"

# Summarize cultural background into 3 factual sentences
def summarize_text(text: str) -> str:
    prompt = (
        "You are a travel assistant specialized in cultural history.\n"
        "Summarize the following content into exactly 3 concise and informative sentences:\n"
        "- Focus on cultural and historical background\n"
        "- Avoid promotional or irrelevant details and personal opinions\n"
        "- Use a clear, factual tone\n\n"
        f"Content:\n{text}\n\nCultural Summary:"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text.strip()


# Clean and parse Gemini JSON response safely
'''def parse_json_response(text: str) -> dict:
    import re
    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        cleaned = cleaned.replace("\n", "").strip()
        if not cleaned:  # If cleaned response is empty, return an error
            return {"error": "Empty response received from Gemini"}
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("⚠️ JSON parsing failed:", e)
        print("📄 Raw text:\n", text)
        return {"error": "Invalid JSON format from LLM response."}
    except Exception as e:
        print("⚠️ Unexpected error:", e)
        return {"error": f"Unexpected error occurred: {str(e)}"}'''

def parse_json_response(text: str) -> dict:
    import re
    try:
        # JSON이 아닌 부분을 제거하는 작업
        cleaned = re.sub(r"```json|```", "", text).strip()
        cleaned = cleaned.replace("\n", "").strip()
        
        # Cleaned text가 비어 있는 경우
        if not cleaned:  
            logger.error("Empty response text: %s", text)  # 추가 로깅
            return {"error": "Empty response received from Gemini"}
        
        logger.debug("Cleaned text: %s", cleaned)  # Cleaned text 확인

        # JSON 파싱
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("⚠️ JSON parsing failed: %s", e)
        logger.error("📄 Raw text:\n%s", text)
        return {"error": "Invalid JSON format from LLM response."}
    except Exception as e:
        logger.error("⚠️ Unexpected error: %s", e)
        return {"error": f"Unexpected error occurred: {str(e)}"}


