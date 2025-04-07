from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from fpdf import FPDF
from gtts import gTTS
import cv2
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_service.app.product_recognition.pipeline import BarcodeProcessor

app = FastAPI()

processor = BarcodeProcessor()

@app.post("/product_recognition")
async def product_recognition(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file format")
        
        # Detect barcode
        barcode = processor.detect_barcode(image)
        product_info = processor.get_product_info(barcode)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    # Create PDF
    pdf_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Product Information", ln=True, align="C")

    for key, value in product_info.items():
        if key == 'nutrition':
            pdf.cell(200, 10, txt="Nutritional Information (per 100g):", ln=True)
            for nutrient, amount in value.items():
                pdf.cell(200, 10, txt=f"  {nutrient.replace('_', ' ').title()}: {amount}", ln=True)
        else:
            pdf.cell(200, 10, txt=f"{key.capitalize()}: {value}", ln=True)

    pdf.output(pdf_file.name)

    # Generate voice output using gTTS
    audio_file = NamedTemporaryFile(delete=False, suffix=".mp3")
    product_text = f"Product: {product_info['name']}, Brand: {product_info['brand']}, Quantity: {product_info['quantity']}."
    nutrition_text = " ".join(
        [f"{nutrient.replace('_', ' ')}: {amount}" for nutrient, amount in product_info['nutrition'].items()]
    )
    full_text = f"{product_text} Nutrition Information: {nutrition_text}"
    tts = gTTS(full_text, lang="en")
    tts.save(audio_file.name)

    # Return the paths to the generated files
    return {
        "pdf_path": pdf_file.name,
        "audio_path": audio_file.name
    }

@app.get("/product_recognition/download_pdf")
async def download_pdf(pdf_path: str):
    return FileResponse(pdf_path, media_type="application/pdf", filename="product_info.pdf")

@app.get("/product_recognition/download_audio_barcode")
async def download_audio(audio_path: str):
    return FileResponse(audio_path, media_type="audio/mpeg", filename="product_info.mp3")
