import os
import joblib
import numpy as np

# Define the base directory for models using absolute path
BASE_DIR = '/home/azureuser/Capgemini_SentimentApp_Remake/backend/models'
MODEL_PATH = os.path.join(BASE_DIR, "sentiment_classifier.pkl")
# changed it from ...sentiment_vectorizer.pkl to just 'vectorizer.pkl' though i don't know if theres training in there

VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

# Initialize model and vectorizer as None
model = None
vectorizer = None

# Try to load the model and vectorizer if they exist
try:
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print(f"Loaded sentiment model from {MODEL_PATH}")
        print(f"Loaded sentiment vectorizer from {VECTORIZER_PATH}")
    else:
        print(f"Warning: Local sentiment model not found at {MODEL_PATH} or {VECTORIZER_PATH}")
except Exception as e:
    print(f"Warning: Failed to load local sentiment model: {str(e)}")
    model, vectorizer = None, None

def classify_sentiment(text):
    """
    Returns a dict like {"sentiment": "Positive", "confidence": 0.85} or similar.
    If local model is not available, provides a basic fallback.
    """
    # Access the global model and vectorizer
    global model, vectorizer
    
    # Make sure text is a string
    try:
        if isinstance(text, (int, float)) or hasattr(text, 'dtype'):  # Handle numpy types
            text = str(text)
        
        if not text or not text.strip():
            return {
                "sentiment": "Neutral",
                "confidence": 0.5
            }
    except Exception as e:
        print(f"Error converting input to string: {e}")
        return {
            "sentiment": "Neutral",
            "confidence": 0.5
        }
        
    if model and vectorizer:
        try:
            X_vectorized = vectorizer.transform([text])
            sentiment_label = model.predict(X_vectorized)[0]
            confidence = 0.8  # placeholder or model.predict_proba
            return {
                "sentiment": sentiment_label,
                "confidence": confidence
            }
        except Exception as e:
            print(f"Error classifying sentiment: {str(e)}")
            # fallback on error
            return {
                "sentiment": "Neutral",
                "confidence": 0.5
            }
    else:
        # Basic fallback logic if no model is available
        text_lower = text.lower()
        if any(word in text_lower for word in ["great", "love", "excellent", "amazing", "good", "happy"]):
            return {
                "sentiment": "positive",
                "confidence": 0.7
            }
        elif any(word in text_lower for word in ["terrible", "awful", "bad", "hate", "disappointed", "angry"]):
            return {
                "sentiment": "negative",
                "confidence": 0.7
            }
        else:
            return {
                "sentiment": "neutral",
                "confidence": 0.5
            }