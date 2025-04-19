import os
from typing import Optional
from dotenv import load_dotenv
import base64

# LangChain Models
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Load env vars
load_dotenv()

# Prompt Templates
TEXT_RECOGNITION_PROMPT = """
You are a helpful assistant. You will be given an image of a text document. Your task is to extract the text from the image and return it in a structured format.
The text should be returned as a single string, without any additional information or formatting.
"""

GENERAL_QA_PROMPT = (
    "You are an intelligent assistant designed to help blind users. "
    "Answer the question clearly, concisely, and in plain language. "
    "Avoid referring to visuals. Speak as if you're reading out loud."
)

IMAGE_CAPTIONING_PROMPT = (
    "You are assisting a visually impaired person. Provide a brief, concise description of the image in one sentence, including key details. Respond succinctly."
)

PRODUCT_RECOGNITION_PROMPT = """
You are an assistant that identifies consumer products from images.

Instructions:
- Look for a visible and readable barcode (UPC, EAN) or recognizable product packaging.
- If found, determine the product's name, brand, category, and any relevant consumer information (e.g., nutrition facts, allergens, dietary labels).
- Summarize this information in a single, informative sentence.
- If no barcode or identifiable product is visible, return: "No barcode detected."

Output:
- Summary: [e.g., "Organic almond milk by Silk, lactose-free and vegan-friendly, ideal for plant-based diets."]
"""

CURRENCY_DETECTION_PROMPT = """
You are a financial assistant that detects and summarizes currency information from images.

Instructions:
- Extract all visible prices from the image.
- Identify the currency used and calculate the total amount.
- Include the currency name, symbol, and likely country.
- Return a single sentence summarizing this information.
- If no monetary values are found, return: "No price detected."

Output:
- Summary: [e.g., "Detected 3 prices totaling 125,000 VND in Vietnamese Dong."]
"""

NAVIGATION_ASSISTANCE_PROMPT = """
You are an assistant helping a blind person navigate toward a specific object or location using a photo taken from their perspective.

Your goals:
- Describe the surrounding environment clearly and briefly.
- Identify objects or landmarks that might help guide the user (e.g., doors, signs, chairs, people, crosswalks).
- If possible, explain where the target object or location is located (e.g., "the red door is directly ahead", "the exit sign is to the left").
- Use simple directional language (left, right, straight ahead, near, far).
- Do not refer to anything the user wouldn't be able to interpret through guidance (avoid "as seen in the top-right").

Output format:
Direction: ...
Key Landmark(s): ...
Suggested Action: ...
"""


# ---------------------------
# Unified LLM Handler
# ---------------------------

def get_llm(provider: str):
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.2, google_api_key=os.getenv("GOOGLE_API_KEY"))
    elif provider == "groq":
        return ChatGroq(model="llama3-8b-8192", groq_api_key=os.getenv("GROQ_API_KEY"))
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# ---------------------------
# Task Handler
# ---------------------------

def get_task_prompt(task: str) -> str:
    prompts = {
        "text_recognition": TEXT_RECOGNITION_PROMPT,
        "general_question_answering": GENERAL_QA_PROMPT,
        "image_captioning": IMAGE_CAPTIONING_PROMPT,
        "product_recognition": PRODUCT_RECOGNITION_PROMPT,
        "currency_detection": CURRENCY_DETECTION_PROMPT,
    }
    return prompts.get(task, "Describe the image.")

from typing import Optional

def get_llm_response(query: str, task: str, base64_image: Optional[str] = None, provider: str = "gemini"):
    llm = get_llm(provider)
    prompt = get_task_prompt(task)

    if base64_image:
        image_url = f"data:image/jpeg;base64,{base64_image}"
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]}
        ]
    
    else:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
    
    response = llm.invoke(messages)
    
    return response.content.strip()

if __name__ == "__main__":
    # Example usage
    task = "image_captioning"
    provider = "gemini"
    image_path = "./examples/image_captioning.png"

    base64_image = base64.b64encode(open(image_path, "rb").read()).decode("utf-8")

    response = get_llm_response("Extract text from this image.", provider, task, base64_image)
    print(response)