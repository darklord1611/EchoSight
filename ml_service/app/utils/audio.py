
from collections import OrderedDict
from sentence_transformers import SentenceTransformer, util


embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Initial unordered feature labels (prioritizing more distinct features first)
raw_feature_labels = OrderedDict({
    "News": [
        "article", "read", "news", "read article", "summary", "latest news", "news article", "current events", 
        "headlines", "news report", "summary of article", "find", "give", "search", "look for", "locate", "seek", "discover", "identify"
    ],
    "Chatbot": [
        "chat", "talk", "tell", "conversation", "ask", "question", "chatbot", "ask a question", 
        "speak to", "let's talk", "chat with", "conversation with assistant", "what"
    ],
    "Text": [
        "text", "document", "page", "story", "paragraph", "content", 
        "read aloud", "narrate", "text to speech"
    ],
    "Currency": [
        "money", "bill", "coin", "cash", "cost", "amount", "price", "total", "currency", 
        "value", "convert currency", "exchange rate"
    ],
    "Object": [
        "object", "describe", "thing", "what is this", "identify", "scan", 
        "detection", "look for", "object recognition"
    ],
    "Product": [
        "product", "brand", "logo", "item", "product name", "identify product", "check product", 
        "product details", "product information"
    ],
    "Distance": [
        "distance", "range", "how far", "measure", "long", "distance to", "how far is", 
        "how much is the distance", "measure distance", "range of"
    ],
    "Face": [
        "face", "who is this", "person", "identify person", "recognize face", "face recognition", 
        "who is the person", "show me the face"
    ],
    "Music": [
        "music", "track", "what's playing", "music track", "listen", "audio"
    ],
    "Play": [
        "play", "begin", "launch", "initiate", "start playback", "begin function", 
        "start process", "launch task", "begin operation"
    ],
    "Stop": [
        "stop", "pause", "halt", "end", "pause function", "halt process", "cancel", 
        "end task", "stop operation"
    ],
    "Detect": [
        "detect", "recognize", "scan surroundings", "recognize object", "detect object", "scan area", 
        "identify items",
    ],
    "Help": [
        "help", "assist", "guide", "support", "help me", "assist me", "I need help", 
        "provide assistance", "help with", "assist in", "guide me"
    ],
    "Capture": [
        "capture", "take a picture", "snap", "photo", "image", "snapshot", "take"
    ],
})

# Deduplicate keywords across features
used_keywords = set()
deduped_feature_labels = {}

for feature, keywords in raw_feature_labels.items():
    unique_keywords = []
    for keyword in keywords:
        lower_keyword = keyword.lower()
        if lower_keyword not in used_keywords:
            unique_keywords.append(keyword)
            used_keywords.add(lower_keyword)
    deduped_feature_labels[feature] = unique_keywords

FEATURE_LABELS = deduped_feature_labels


# --- Use the Navigation Triggers and Feature Names defined above ---
NAVIGATION_TRIGGERS = [
    "switch to", "go to", "open", "activate", "change to", "navigate to",
    "show me", "i want to use", "let's use", "start"
]

FEATURE_NAMES = { # Simplified for clarity, map name to canonical key
    "Text": ["text", "reading", "read aloud", "narrate"],
    "Currency": ["currency", "money", "exchange"],
    "Object": ["object", "thing", "item identification", "find"], # Added 'find' here
    "Product": ["product", "barcode", "logo", "brand"],
    "Distance": ["distance", "measurement", "how far", "range"],
    "Face": ["face", "person", "recognition", "who is this"],
    "Music": ["music", "song", "track", "audio", "listen"], # Added audio/listen
    "News": ["news", "articles", "headlines", "summary"],
    "Chatbot": ["chat", "talk", "ask", "question", "assistant"],
    "Help": ["help", "support", "guide", "assist"],
    "Capture": ["camera", "picture", "photo", "capture", "take"],
    "Play": ["play", "begin", "start playback", "launch"], # 'start'/'launch' could be navigation OR action
    "Stop": ["stop", "pause", "halt", "end", "cancel"],
    "Detect": ["detect", "scan", "recognize surroundings"] # 'recognize' could be nav or action
}

# Use your original detailed keywords for semantic matching *if* it's not a navigation command
FEATURE_KEYWORDS_FOR_SEMANTIC_MATCH = deduped_feature_labels # Use the deduplicated dict from your code

# --- Helper function to find navigation intent ---
def find_navigation_intent(text):
    text_lower = text.lower()
    for trigger in NAVIGATION_TRIGGERS:
        trigger_pattern = trigger.lower() + r"\s+" # Trigger followed by space
        if text_lower.startswith(trigger_pattern):
            # Extract what comes after the trigger
            potential_feature_phrase = text_lower[len(trigger_pattern):].strip()
            # Check if the rest matches a feature name/alias
            for feature_key, aliases in FEATURE_NAMES.items():
                for alias in aliases:
                    # Use simple startswith or exact match for the feature part
                    # Or consider fuzzy matching if needed
                    if potential_feature_phrase.startswith(alias.lower()):
                         # Found a navigation command!
                        return {
                            "intent": "navigate",
                            "target_feature": feature_key,
                            "confidence": 0.95 # High confidence for explicit match
                        }
            # If trigger matched but no known feature followed, maybe it's ambiguous
            # Or maybe it's a generic command like "start listening" (which might be 'Play' or 'Music')
            # For now, we'll assume if no feature matches after trigger, it's not navigation
            pass # Continue checking other triggers

    # Special case for commands that are just the feature name (less ideal but common)
    # This is lower confidence than explicit triggers
    for feature_key, aliases in FEATURE_NAMES.items():
        for alias in aliases:
            if text_lower == alias.lower():
                 return {
                    "intent": "navigate",
                    "target_feature": feature_key,
                    "confidence": 0.75 # Lower confidence for implicit navigation
                }

    return None # No clear navigation intent found

# --- Helper function for Semantic Query Routing ---
def route_query_semantically(query_text, embedder, feature_keywords):
    query_embed = embedder.encode(query_text, convert_to_tensor=True)
    best_match_feature, best_score = None, -1

    # Match against the *keywords* associated with each feature
    for feature_key, keywords in feature_keywords.items():
        # Maybe average embeddings of keywords, or check against each?
        # Checking against each is simpler for now
        feature_avg_score = 0
        if not keywords: continue # Skip features with no keywords

        for keyword in keywords:
            keyword_embed = embedder.encode(keyword, convert_to_tensor=True)
            score = util.cos_sim(query_embed, keyword_embed).item()
            feature_avg_score += score
            # Optional: Keep track of the best *single* keyword match score too

        feature_avg_score /= len(keywords) # Average score for the feature

        if feature_avg_score > best_score:
            best_match_feature, best_score = feature_key, feature_avg_score

    print(f"Best match feature: {best_match_feature}, Score: {best_score}")
    # Add a threshold - don't route if confidence is too low
    CONFIDENCE_THRESHOLD = 0.1 # Tune this value
    if best_score < CONFIDENCE_THRESHOLD:
        # If below threshold, maybe it's a general chatbot query?
        # Or an unknown intent. Defaulting to Chatbot might be safe.
        return {
            "intent": "query",
            "target_feature": "Chatbot", # Default fallback
            "query": query_text,
            "confidence": round(best_score, 3),
            "routing_fallback": True
        }

    return {
        "intent": "query",
        "target_feature": best_match_feature,
        "query": query_text,
        "confidence": round(best_score, 3),
        "routing_fallback": False
    }