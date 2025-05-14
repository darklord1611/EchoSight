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
You are assisting a blind person with real-time navigation. Based on the following image analysis data, generate a clear and concise spoken message that estimates the distance to visible objects and helps the user navigate safely. Use calm, supportive, and friendly language.

Image Analysis Data:

- Detected Objects: [List of objects detected in the camera feed, along with their estimated distances from the camera and relative direction. Example: "a chair is approximately 2 feet ahead to the right", "a person is 6 feet to your left"]
- Path Description: [Information about the walkable or obstructed path in front of the user. Example: "The area straight ahead is mostly clear for 8 feet"]
- Suggested Action: [Recommended movement or caution based on detected obstacles. Example: "slow down and veer left", "you can continue straight for now"]

Format the output as a single spoken paragraph intended for audio transcription. Avoid technical or visual terms. Emphasize clarity, safety, and spatial awareness using natural, descriptive language.

Example input:
Detected Objects: A chair is 2 feet ahead to the right, a person is 6 feet to your left.
Path Description: Clear ahead for 8 feet.
Suggested Action: Move slightly to the left.

Expected output:
“There’s a chair about two feet ahead on your right and a person a bit farther off to your left. You’ve got a clear path straight ahead for about eight feet. Move slightly to your left to avoid the chair.”

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


import cv2
from pyzbar.pyzbar import decode
import numpy as np

def extract_barcode_from_base64(base64_image: str):
    image_bytes = base64.b64decode(base64_image)
    image_np = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    
    decoded_objects = decode(image)
    barcodes = [obj.data.decode("utf-8") for obj in decoded_objects]

    print(barcodes)
    
    return barcodes  # could be a list of barcodes found

import requests
import json

def fetch_book_main_info(isbn: str) -> Optional[dict]:
    """
    Fetch and return only the main book information from Google Books API using ISBN.
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Failed to fetch data (status {response.status_code})")
        return None

    data = response.json()
    print(data)
    if not data.get("items"):
        print("No book found with this ISBN.")
        with open("sample_product.json", "r") as f:
            data = json.load(f)

    print(data)

    volume_info = data["items"][0]["volumeInfo"]

    # Extract clean, minimal fields
    result = {
        "title": volume_info.get("title"),
        "authors": volume_info.get("authors", []),
        "publishedDate": volume_info.get("publishedDate"),
        "isbn_13": None,
        "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail"),
    }

    # Extract ISBN-13
    for identifier in volume_info.get("industryIdentifiers", []):
        if identifier["type"] == "ISBN_13":
            result["isbn_13"] = identifier["identifier"]

    return result


def get_llm_response(query: str, task: str, base64_image: Optional[str] = None, provider: str = "gemini"):
    llm = get_llm(provider)
    prompt = get_task_prompt(task)

    if task == "product_recognition" and base64_image:
        barcodes = extract_barcode_from_base64(base64_image)[0]
        print(barcodes)
        if barcodes:
            book_info = fetch_book_main_info(barcodes[0])
            query = "Reformat the following product infomation: " "\n".join(f"{key}: {value}" for key, value in book_info.items())
            print(book_info)
        else:
            query = "No barcode detected."
        

    if task != "product_recognition" and base64_image:
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