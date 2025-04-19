from ast import List
import re
from tempfile import NamedTemporaryFile
import openai
from openai import OpenAI
import os
import logging
from fpdf import FPDF
import asyncio
from ..config import config
from gtts import gTTS

def segment_text_by_sentence(text):
    sentence_boundaries = re.finditer(r'(?<=[.!?])\s+', text)
    boundaries_indices = [boundary.start() for boundary in sentence_boundaries]
    
    segments = []
    start = 0
    for boundary_index in boundaries_indices:
        segments.append(text[start:boundary_index + 1].strip())
        start = boundary_index + 1
    segments.append(text[start:].strip())

    return segments

def create_pdf(text: str, output_path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("FreeSerif", fname="./app/FreeSerif.ttf", uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("FreeSerif", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)

async def create_pdf_async(text: str, pdf_path: str):
    await asyncio.to_thread(create_pdf, text, pdf_path)
    
def format_response_distance_estimate_with_openai(response, transcribe, base64_image):
    try:
        if response is None or len(response) == 0:
            return "No objects detected at the moment."
            
        if not config.OPENAI_API_KEY:
            logging.error("OpenAI API key is missing")
            return str(response)

        logging.info(f"Processing response: {response}")

        openai.api_key = config.OPENAI_API_KEY
        client = OpenAI()

        system_prompt = """
            You are an expert in guiding visually impaired individuals to move safely and retrieve objects. Your task is to convert object detection data into clear, detailed, and safe movement instructions in English. Include the following:

            - Identify and describe the location of the requested object.
            - Provide clear step-by-step instructions on how to reach the object.
            - Highlight any potential hazards or obstacles and suggest how to avoid them.
            - Use precise directional language (e.g., left, right, forward, backward) and distances.
            - Ensure the instructions are easy to understand and prioritize safety.

            Example format:
            "To reach the [object], follow these steps:
            1. Move forward approximately [distance] inches.
            2. Turn [direction] and continue for [distance] inches.
            3. Watch out for [hazard] located at [location].
            4. The [object] is located at [final position]."
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {
                        "type": "text",
                        "text": str(response)
                    }, 
                    {
                        "type": "text",
                        "text": transcribe
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=0.9,
        )

        formatted_response = completion.choices[0].message.content.strip()
        
        logging.info(f"Formatted response: {formatted_response}")

        return formatted_response

    except openai.OpenAIError as openai_error:
        logging.error(f"OpenAI API Error: {openai_error}")
        return f"Processing error: {str(openai_error)}"

    except Exception as e:
        logging.error(f"Unexpected error in distance estimation: {e}")
        return str(response)
    
def format_response_product_recognition_with_openai(response):
    try:
        if not config.OPENAI_API_KEY:
            logging.error("OpenAI API key is missing")
            return response
        openai.api_key = config.OPENAI_API_KEY
        client = OpenAI()

        system_prompt = """
        Your task is to convert product information into a detailed, easy-to-understand, and engaging paragraph in English.

        Requirements:
        - Provide a full description of the product.
        - Explain nutritional information in a simple way.
        - Evaluate the nutritional value and potential use.
        - Use a friendly, professional tone.

        Example format:
        "[Product Name] by [Brand Name] – A unique culinary experience!

        Product Details:
        - Type: [Detailed description]
        - Weight: [Weight]
        - Category: [Relevant categories]

        Nutritional Value (In-depth analysis):
        [Detailed breakdown of energy, fat, carbohydrates, and protein]"
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(response)}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=0.9,
        )

        formatted_description = completion.choices[0].message.content.strip()
        
        return formatted_description

    except openai.OpenAIError as openai_error:
        logging.error(f"OpenAI API Error: {openai_error}")
        return f"Error processing product information: {str(openai_error)}"

    except Exception as e:
        logging.error(f"Unexpected error in product information processing: {e}")
        return str(response)

def format_response_music_detection_with_openai(response):
    pass

def format_response_general_question_answering_with_openai(response):
    pass

def format_audio_response(response, task):
    match(task):
        case "distance_estimate":
            full_text = f"The estimated distance to the object is approximately {response} meters."

        case "product_recognition":
            product_text = f"Product: {response['name']}, Brand: {response['brand']}, Quantity: {response['quantity']}."
            nutrition_text = " ".join(
                [f"{nutrient.replace('_', ' ')}: {amount}" for nutrient, amount in response['nutrition'].items()]
            )
            full_text = f"{product_text} Nutrition Information: {nutrition_text}"

        case "currency_detection":
            full_text = f"The total amount detected is {response['total_amount']} Vietnamese Dong."

        case "text_recognition":
            full_text = f"The text in the image says: {response}"

        case "image_captioning":
            full_text = f"This image can be described as: {response}"

        case "music_recognition":
            full_text = (
                f"You are listening to '{response['title']}' by {response['artist']}. "
                f"It was released in {response.get('year', 'an unknown year')}."
            )

        case "general_question_answering":
            full_text = response

        case _:
            full_text = "I'm sorry, I couldn't determine the type of response to generate."

    try:
        # Generate voice output using gTTS
        audio_file = NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(full_text, lang="en")
        tts.save(audio_file.name)

        return audio_file.name
    except Exception as e:
        logging.error(f"Error generating audio response: {e}")
        return None


def format_article_audio_response(response):
    try:
        # Generate voice output using gTTS

        full_text = f"Title: {response.title} \n\n Content: {response.text}"
        audio_file = NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(full_text, lang="en")
        tts.save(audio_file.name)

        full_text = f"Title: {response.title} \n\n Summary: {response.summary}"
        summary_audio_file = NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(full_text, lang="en")
        tts.save(summary_audio_file.name)

        return audio_file.name, summary_audio_file.name
    except Exception as e:
        logging.error(f"Error generating audio response: {e}")
        return None, None