import google.generativeai as genai
from app.config import GEMINI_API_KEY
from pathlib import Path

genai.configure(api_key=GEMINI_API_KEY)

def load_prompt_template():
    path = Path(__file__).parent.parent / "prompts" / "refine_prompt.txt"
    return path.read_text(encoding="utf-8")  # <- 인코딩을 명시적으로 UTF-8로 설정

def refine_description(raw_text: str) -> str:
    prompt_template = load_prompt_template()
    prompt = prompt_template.format(raw_text=raw_text)

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    return response.text.strip()
