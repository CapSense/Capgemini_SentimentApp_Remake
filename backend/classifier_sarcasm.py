"""
classifier_sarcasm.py
Integrates a Hugging Face pipeline for sarcasm detection,
plus an optional local Naive Bayes fallback stored in 'models/'.
"""

import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from transformers import pipeline

# Initialize Hugging Face pipeline
try:
    sarcasm_detector = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony")
    print("Initialized Hugging Face sarcasm pipeline successfully")
except Exception as e:
    print(f"Warning: Failed to initialize Hugging Face pipeline: {str(e)}")
    sarcasm_detector = None

# Define the base directory for models using absolute path
BASE_DIR = '/home/azureuser/Capgemini_SentimentApp_Remake/backend/models'
MODEL_PATH = os.path.join(BASE_DIR, "sarcasm_classifier.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "sarcasm_vectorizer.pkl")

model = None
vectorizer = None
try:
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print(f"Loaded local sarcasm model from {MODEL_PATH}")
        print(f"Loaded local sarcasm vectorizer from {VECTORIZER_PATH}")
    else:
        print(f"Warning: Local sarcasm model not found at {MODEL_PATH} or {VECTORIZER_PATH}")
except Exception as e:
    print(f"Warning: Failed to load local sarcasm model: {str(e)}")
    model, vectorizer = None, None


def detect_sarcasm(text):
    """
    Returns {"sarcasm": bool, "confidence": float}
    """
    # Access global variables
    global model, vectorizer, sarcasm_detector
    
    # Make sure text is a string
    try:
        if isinstance(text, (int, float)) or hasattr(text, 'dtype'):  # Handle numpy types
            text = str(text)
        
        text = text.strip()
        if not text:
            return {"sarcasm": False, "confidence": 0.0}
    except Exception as e:
        print(f"Error converting input to string: {e}")
        return {"sarcasm": False, "confidence": 0.0}
    
    # Try the local model first
    if model and vectorizer:
        try:
            # Vectorize the text
            text_vectorized = vectorizer.transform([text])
            
            # Predict with the model
            pred_label = model.predict(text_vectorized)[0]
            confidence = float(model.predict_proba(text_vectorized)[0][1])  # Probability of class 1
            
            return {"sarcasm": bool(pred_label == 1), "confidence": confidence}
        except Exception as e:
            print(f"Error using local sarcasm model: {str(e)}")
            # Fall through to Hugging Face if local model fails
    
    # Use Hugging Face pipeline as backup
    if sarcasm_detector:
        try:
            result = sarcasm_detector(text)[0]
            label = result["label"]
            score = float(result["score"])
            is_sarcastic = (label.upper() == "IRONY") # Note: This model uses "IRONY" rather than "SARCASM"
            return {"sarcasm": is_sarcastic, "confidence": score}
        except Exception as e:
            print(f"Error using Hugging Face sarcasm model: {str(e)}")
    
    # Fallback if both methods fail
    return {"sarcasm": False, "confidence": 0.5}

def train_sarcasm_model(dataset_path="sarcasm_dataset.csv"):
    """
    Writes the trained model/vectorizer to the 'models/' folder.
    """
    if not os.path.exists(dataset_path):
        return {"error": f"Dataset file '{dataset_path}' not found."}

    # Try different encodings
    encodings_to_try = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
    data = None
    
    for encoding in encodings_to_try:
        try:
            print(f"Trying to read with {encoding} encoding...")
            data = pd.read_csv(dataset_path, encoding=encoding)
            print(f"Successfully read with {encoding} encoding")
            break
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding")
            continue
    
    if data is None:
        return {"error": "Could not read the dataset with any of the attempted encodings."}

    if "text" not in data.columns or "label" not in data.columns:
        # Try to guess columns if standard names aren't found
        print("Standard columns 'text' and 'label' not found. Available columns:")
        for col in data.columns:
            print(f"  {col}")
        return {"error": "Dataset must have 'text' and 'label' columns."}

    data = data.dropna(subset=["text", "label"])
    data = data[data["text"].str.strip() != ""]

    X = data["text"]
    y = data["label"]

    global model, vectorizer
    vectorizer = CountVectorizer(stop_words="english")
    X_vectorized = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_vectorized, y, test_size=0.2, random_state=42
    )

    model = MultinomialNB()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label=1)
    recall = recall_score(y_test, y_pred, pos_label=1)
    f1 = f1_score(y_test, y_pred, pos_label=1)

    os.makedirs(BASE_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return {
        "message": "Sarcasm model trained successfully",
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1)
    }