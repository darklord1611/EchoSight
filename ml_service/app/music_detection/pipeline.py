from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer, util
import tempfile
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
import logging
from enum import Enum
import torch
from pydantic import BaseModel

app = FastAPI()

# Initialize sentence transformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandType(str, Enum):
    FEATURE = "feature"  # Selecting a feature
    ACTION = "action"    # Performing an action within a feature

class MatchResult(BaseModel):
    command: str
    command_type: CommandType
    confidence: float
    original_transcript: str

# Define features with their associated keywords and actions
FEATURES = {
    "Text": {
        "keywords": ["text", "document", "page", "story", "paragraph", "article", "content"],
        "actions": {
            "read": ["read", "read aloud", "narrate", "text to speech", "speak this"],
            "translate": ["translate", "convert language", "change language"],
            "save": ["save", "store", "remember", "keep", "bookmark"]
        }
    },
    
    "Currency": {
        "keywords": ["money", "bill", "coin", "cash", "currency", "dollar", "euro", "yen"],
        "actions": {
            "identify": ["identify", "what is this", "how much", "value"],
            "convert": ["convert", "exchange", "calculate", "change to"]
        }
    },
    
    "Object": {
        "keywords": ["object", "thing", "item", "what is this", "identify this"],
        "actions": {
            "identify": ["identify", "what is this", "recognize", "detect", "scan"],
            "describe": ["describe", "details", "tell me about", "information"]
        }
    },
    
    "Product": {
        "keywords": ["product", "brand", "logo", "item", "goods", "merchandise"],
        "actions": {
            "identify": ["identify", "what product", "recognize", "scan"],
            "price": ["price", "cost", "how much", "value"],
            "reviews": ["reviews", "ratings", "stars", "feedback"]
        }
    },
    
    "Distance": {
        "keywords": ["distance", "range", "far", "measure", "length", "space"],
        "actions": {
            "measure": ["measure", "how far", "distance to", "length of"],
            "compare": ["compare", "difference", "between"]
        }
    },
    
    "Face": {
        "keywords": ["face", "person", "who is", "people", "individual"],
        "actions": {
            "identify": ["identify", "who is this", "recognize", "name"],
            "remember": ["remember", "save", "store", "add person"]
        }
    },
    
    "Music": {
        "keywords": ["song", "music", "track", "tune", "audio", "listen", "melody"],
        "actions": {
            "detect": ["detect", "what song", "identify song", "recognize song", "what's playing"],
            "play": ["play", "start", "begin", "resume", "continue"],
            "pause": ["pause", "stop", "halt", "mute", "silence"]
        }
    },
    
    "Article": {
        "keywords": ["article", "news", "post", "blog", "story", "report"],
        "actions": {
            "summarize": ["summarize", "summary", "brief", "key points"],
            "read": ["read", "read aloud", "narrate", "speak"]
        }
    },
    
    "Chatbot": {
        "keywords": ["chat", "talk", "conversation", "assistant", "help", "speak"],
        "actions": {
            "ask": ["ask", "question", "query", "inquire"],
            "chat": ["chat", "talk", "speak", "converse"]
        }
    },
}

# Create consolidated embeddings for each feature and action
feature_embeddings = {}
action_embeddings = {}

def initialize_embeddings():
    """Precompute embeddings for features and actions"""
    for feature, config in FEATURES.items():
        # Combine feature name and all keywords for richer feature representation
        feature_text = f"{feature} " + " ".join(config["keywords"])
        feature_embeddings[feature] = embedder.encode(feature_text, convert_to_tensor=True)
        
        # Create embeddings for each action in this feature
        action_embeddings[feature] = {}
        for action, phrases in config["actions"].items():
            # Combine action name and all phrases for richer action representation
            action_text = f"{action} " + " ".join(phrases)
            action_embeddings[feature][action] = embedder.encode(action_text, convert_to_tensor=True)

# Initialize embeddings on startup
initialize_embeddings()

def preprocess_transcript(transcript: str) -> str:
    """Clean and normalize transcript text"""
    # Convert to lowercase
    text = transcript.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove punctuation that might interfere with matching
    text = re.sub(r'[,.!?;:]', '', text)
    return text

def detect_command(transcript: str, active_feature: Optional[str] = None) -> MatchResult:
    """
    Detect whether the transcript contains a feature selection or an action command
    
    Args:
        transcript: The transcribed text from speech recognition
        active_feature: Currently active feature (if any)
        
    Returns:
        MatchResult object with command, type, and confidence score
    """
    # Preprocess the transcript
    clean_transcript = preprocess_transcript(transcript)
    transcript_embedding = embedder.encode(clean_transcript, convert_to_tensor=True)
    
    # If we have an active feature, first check if this is an action for that feature
    if active_feature and active_feature in FEATURES:
        # Check for actions in the active feature
        best_action, best_action_score = find_best_action(
            transcript_embedding, 
            active_feature
        )
        
        # If we found a good action match, return it
        if best_action_score > 0.6:  # Threshold for action confidence
            return MatchResult(
                command=best_action,
                command_type=CommandType.ACTION,
                confidence=float(best_action_score),
                original_transcript=transcript
            )
    
    # Check for feature match
    best_feature, best_feature_score = find_best_feature(transcript_embedding)
    
    # Always default to checking for an explicit feature mention first
    # Only if confidence is high enough, consider it a feature selection
    if best_feature_score > 0.6:  # Threshold for feature confidence
        return MatchResult(
            command=best_feature,
            command_type=CommandType.FEATURE,
            confidence=float(best_feature_score),
            original_transcript=transcript
        )
    
    # If nothing matched with high confidence, check for direct phrase matches
    direct_match = check_direct_phrase_match(clean_transcript)
    if direct_match:
        return direct_match
    
    # If we reach here, we couldn't determine a clear command
    return MatchResult(
        command="unknown",
        command_type=CommandType.FEATURE if active_feature is None else CommandType.ACTION,
        confidence=0.0,
        original_transcript=transcript
    )

def find_best_feature(transcript_embedding: torch.Tensor) -> Tuple[str, float]:
    """Find the best matching feature for a transcript embedding"""
    best_feature, best_score = None, -1
    
    for feature, embedding in feature_embeddings.items():
        score = float(util.cos_sim(transcript_embedding, embedding).item())
        if score > best_score:
            best_feature, best_score = feature, score
    
    return best_feature, best_score

def find_best_action(transcript_embedding: torch.Tensor, feature: str) -> Tuple[str, float]:
    """Find the best matching action for a transcript embedding within a feature"""
    best_action, best_score = None, -1
    
    for action, embedding in action_embeddings[feature].items():
        score = float(util.cos_sim(transcript_embedding, embedding).item())
        if score > best_score:
            best_action, best_score = action, score
    
    return best_action, best_score

def check_direct_phrase_match(transcript: str) -> Optional[MatchResult]:
    """Check for direct matches of feature or action phrases in the transcript"""
    # First check for exact feature matches
    for feature, config in FEATURES.items():
        # Check feature name itself
        if feature.lower() in transcript:
            return MatchResult(
                command=feature,
                command_type=CommandType.FEATURE,
                confidence=1.0,  # Direct match gets highest confidence
                original_transcript=transcript
            )
        
        # Check feature keywords
        for keyword in config["keywords"]:
            if keyword.lower() in transcript:
                return MatchResult(
                    command=feature,
                    command_type=CommandType.FEATURE,
                    confidence=0.9,  # Keyword match gets high confidence
                    original_transcript=transcript
                )
        
        # Check action phrases
        for action, phrases in config["actions"].items():
            for phrase in phrases:
                if phrase.lower() in transcript:
                    return MatchResult(
                        command=action,
                        command_type=CommandType.ACTION,
                        confidence=0.85,  # Action phrase match gets good confidence
                        original_transcript=transcript
                    )
    
    return None

@app.post("/transcribe_audio")
async def voice_command(file: UploadFile = File(...), active_feature: Optional[str] = None):
    """
    Process audio file to detect commands
    
    Args:
        file: Uploaded audio file
        active_feature: Currently active feature (if any)
    """
    # Save uploaded audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Transcribe audio (assuming this function exists)
        transcript_result = transcribe_audio(tmp_path)
        transcript = transcript_result["transcript"]
        
        # Log the transcription for debugging
        logger.info(f"Transcribed: '{transcript}'")
        
        # Detect command
        result = detect_command(transcript, active_feature)
        
        # Log the result
        logger.info(f"Detected: {result.command} ({result.command_type}) with confidence {result.confidence}")
        
        return {
            "transcript": transcript,
            "command": result.command,
            "command_type": result.command_type,
            "confidence": result.confidence
        }
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

@app.post("/music_detection")
async def music_detection(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(await file.file.read())
            temp_path = temp.name

        audio_path = format_audio_response(temp_path, "music_recognition")
        if audio_path:
            return JSONResponse(content={
                "audio_path": audio_path,
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio response")

    except Exception as e:
        logger.error(f"Error in music detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# This function needs to be implemented based on your audio transcription setup
def transcribe_audio(audio_path):
    """
    Transcribe audio file to text.
    This is a placeholder - you'll need to implement actual transcription.
    """
    # Implement your transcription logic here (e.g., using Whisper or other ASR)
    # This is just a mock implementation
    return {"transcript": "example transcript"}

# This function needs to be implemented based on your audio response system
def format_audio_response(audio_path, operation_type):
    """
    Format audio for response.
    This is a placeholder - you'll need to implement actual processing.
    """
    # Implement your audio processing logic here
    # This is just a mock implementation
    return f"/processed_audio/{operation_type}_{audio_path.split('/')[-1]}"

# Test endpoint for debugging command detection
@app.post("/test_command_detection")
async def test_command_detection(text: str, active_feature: Optional[str] = None):
    """Test endpoint to verify command detection without audio processing"""
    result = detect_command(text, active_feature)
    return {
        "transcript": text,
        "command": result.command,
        "command_type": result.command_type,
        "confidence": result.confidence
    }