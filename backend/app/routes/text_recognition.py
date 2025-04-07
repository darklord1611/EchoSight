import sys
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from fpdf import FPDF
from PIL import Image
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_service.app.text_recognition.provider.ocr import OcrRecognition

router = APIRouter()

ocr_recognition = OcrRecognition()

@router.post("/document_recognition")
async def document_recognition(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    # Process image with OCR
    try:
        image = Image.open(file.file)
        result = ocr_recognition.recognize_text(image, language="vie")
        if not result.text:
            raise HTTPException(status_code=400, detail="Text not recognized in the image.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

    # Convert text to PDF
    pdf_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, result.text)
    pdf.output(pdf_file.name)
    
    # Generate speech from text
    audio_file = NamedTemporaryFile(delete=False, suffix=".mp3")
    try:
        # Assuming you have TTS library (e.g., gTTS) for converting text to speech
        from gtts import gTTS
        tts = gTTS(result.text, lang="vi")
        tts.save(audio_file.name)
    except Exception as e:
        pdf_file.close()
        os.unlink(pdf_file.name)
        raise HTTPException(status_code=500, detail=f"Text-to-speech conversion failed: {str(e)}")

    # Prepare response
    response = {
        "pdf_path": pdf_file.name,
        "audio_path": audio_file.name,
        "confidence": result.confidence
    }
    
    return response

@router.get("/document_recognition/download_pdf")
async def download_pdf(pdf_path: str):
    return FileResponse(pdf_path, media_type="application/pdf", filename="document.pdf")

@router.get("/document_recognition/download_audio")
async def download_audio(audio_path: str):
    return FileResponse(audio_path, media_type="audio/mpeg", filename="document.mp3")

