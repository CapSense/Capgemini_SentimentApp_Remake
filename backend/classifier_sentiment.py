# classifier_sentiment.py

import joblib
import os

# Store and load the model/vectorizer from the 'models/' folder
MODEL_PATH = "models/sentiment_classifier.pkl"
VECTORIZER_PATH = "models/vectorizer.pkl"

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Loaded sentiment model and vectorizer from 'models/' folder.")
else:
    print("Warning: Sentiment model or vectorizer not found in 'models/' folder.")

def classify_sentiment(text):
    """
    Returns a dict like {"sentiment": "Positive", "confidence": 0.85} or similar.
    If you have a local Naive Bayes model, do:
      - vectorize text
      - predict with model
    """
    if model and vectorizer:
        X_vectorized = vectorizer.transform([text])
        sentiment_label = model.predict(X_vectorized)[0]
        confidence = 0.8  # placeholder or model.predict_proba
        return {
            "sentiment": sentiment_label,
            "confidence": confidence
        }
    else:
        # fallback or no model
        return {
            "sentiment": "Neutral",
            "confidence": 0.5
        }
