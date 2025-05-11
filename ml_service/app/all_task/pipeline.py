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
You are assisting a blind person with real-time navigation. Based on the following sensor data, generate a clear and concise spoken message that guides the user safely through their environment. Use calm and friendly language.

Sensor Data:

Obstacles and landmarks: [list with object type, approximate distance, and direction, e.g., "a trash can is 3 feet ahead to the left"]

Path info: [description of walkable path, e.g., "clear path continues forward for 10 feet"]

Actions needed: [any important immediate advice, e.g., "step slightly right", "stop and wait"]

Format the output as a single paragraph intended for audio transcription. Avoid technical jargon. Prioritize clarity and safety.

Example input:
Obstacles: A trash can 3 feet ahead to the left, a bench 5 feet ahead on the right.
Path info: Clear forward path for 10 feet.
Action: Step slightly to the right.

Expected output:
“There’s a trash can a few feet ahead on your left and a bench on the right. The path is clear straight ahead for about ten feet. Please step slightly to your right to stay clear of the obstacles.”
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
        "distance_estimation": NAVIGATION_ASSISTANCE_PROMPT,
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