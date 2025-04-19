import joblib
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK data is available
nltk.download('punkt')
nltk.download('stopwords')

# Load model and vectorizer
BASE_DIR = '/home/azureuser/Capgemini_SentimentApp_Remake/backend/models'
MODEL_PATH = os.path.join(BASE_DIR, 'emotion_classifier.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'emotion_vectorizer.pkl')

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except Exception as e:
    print(f"[Emotion Classifier] Failed to load model or vectorizer: {e}")
    model, vectorizer = None, None

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return ' '.join([word for word in words if word.isalnum() and word not in stop_words])

def detect_emotion(text):
    """
    Returns: {"emotion": label, "confidence": 0.8} or fallback.
    """
    if not model or not vectorizer:
        return {"emotion": "neutral", "confidence": 0.5}
    
    try:
        processed = preprocess_text(text)
        X = vectorizer.transform([processed])
        prediction = model.predict(X)[0]
        return {"emotion": prediction, "confidence": 0.8}
    except Exception as e:
        print(f"[Emotion Classifier] Error: {e}")
        return {"emotion": "neutral", "confidence": 0.5}
