# classifier_sentiment.py

import joblib
import os

# Define the base directory for models using relative path to backend/models
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Store and load the model/vectorizer from the 'models/' folder
MODEL_PATH = os.path.join(BASE_DIR, "sentiment_classifier.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print(f"Loaded sentiment model from {MODEL_PATH}")
        print(f"Loaded sentiment vectorizer from {VECTORIZER_PATH}")
    except Exception as e:
        print(f"Error loading sentiment model or vectorizer: {str(e)}")
else:
    print(f"Warning: Sentiment model or vectorizer not found. Looked at {MODEL_PATH} and {VECTORIZER_PATH}")

def classify_sentiment(text):
    """
    Returns a dict like {"sentiment": "Positive", "confidence": 0.85} or similar.
    If you have a local Naive Bayes model, do:
      - vectorize text
      - predict with model
    """
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
        # fallback or no model
        return {
            "sentiment": "Neutral",
            "confidence": 0.5
        }