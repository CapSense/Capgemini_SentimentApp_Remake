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

sarcasm_detector = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony")

MODEL_PATH = "models/sarcasm_classifier.pkl"
VECTORIZER_PATH = "models/sarcasm_vectorizer.pkl"

model = None
vectorizer = None
try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Loaded local sarcasm model from 'models/' folder.")
except Exception:
    print("Warning: No local sarcasm model found in 'models/' folder, defaulting to Hugging Face pipeline.")
    model, vectorizer = None, None


def detect_sarcasm(text):
    """
    Returns {"sarcasm": bool, "confidence": float}
    """
    text = text.strip()
    if not text:
        return {"sarcasm": False, "confidence": 0.0}

    if model and vectorizer:
        text_vectorized = vectorizer.transform([text])
        prediction = model.predict(text_vectorized)
        is_sarcastic = (prediction[0] == 1)
        sarcasm_conf = 0.8 if is_sarcastic else 0.2
        return {"sarcasm": is_sarcastic, "confidence": sarcasm_conf}
    else:
        result = sarcasm_detector(text)[0]
        label = result["label"]
        score = float(result["score"])
        is_sarcastic = (label.upper() == "SARCASM")
        return {"sarcasm": is_sarcastic, "confidence": score}


def train_sarcasm_model(dataset_path="sarcasm_dataset.csv"):
    """
    Writes the trained model/vectorizer to the 'models/' folder.
    """
    if not os.path.exists(dataset_path):
        return {"error": f"Dataset file '{dataset_path}' not found."}

    data = pd.read_csv(dataset_path)
    if "text" not in data.columns or "label" not in data.columns:
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

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return {
        "message": "Sarcasm model trained successfully",
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1)
    }
