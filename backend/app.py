# app.py
import pyodbc
from flask import Flask, request, jsonify

from apiflaskinputvaliderrorlog import validate_request_payload, log_invalid_input
from classifier_sentiment import classify_sentiment
from classifier_sarcasm import detect_sarcasm
from classifier_emotion import detect_emotion
from phi3resgen import generate_response

app = Flask(__name__)

# Production DB config for Azure SQL
DB_CONFIG = {
    'server': '1sqlcapsenseserver.database.windows.net',
    'database': 'SentimentAnalysisDB',
    'username': 'capsenseadmin',
    'password': 'Access@Capsense1'
}

def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

# Optional fallback local DB (commented out)
# from db_fallback import get_fallback_db_connection

@app.route('/api/respond', methods=['POST'])
def respond_single():
    """
    Processes a single piece of customer text.
    JSON payload example: {"customer_text": "..."}
    1) Validate input
    2) Classify sentiment, sarcasm, emotion
    3) Generate AI response
    4) Insert record into DB
    5) Return combined result
    """
    payload = request.json
    valid, error_message = validate_request_payload(payload)
    if not valid:
        log_invalid_input(error_message)
        return jsonify({"error": error_message}), 400

    customer_text = payload["customer_text"]

    # Classification
    sentiment_result = classify_sentiment(customer_text)
    sarcasm_result = detect_sarcasm(customer_text)
    emotion_result = detect_emotion(customer_text)

    # Merge classification data
    classification_data = {
        "sentiment": sentiment_result["sentiment"],
        "sentiment_confidence": sentiment_result["confidence"],
        "sarcasm": sarcasm_result["sarcasm"],
        "sarcasm_confidence": sarcasm_result["confidence"],
        "emotion": emotion_result["emotion"],
        "emotion_confidence": emotion_result["confidence"]
    }

    # Generate AI-based response
    ai_response = generate_response(customer_text, classification_data)

    # Insert into DB
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO FeedbackResponses 
        (CustomerText, Sentiment, ResponseText, EmpathyScore, SarcasmDetected, Emotion)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    cursor.execute(
        insert_query,
        (
            customer_text,
            classification_data["sentiment"],
            ai_response["response_text"],
            ai_response["empathy_score"],
            classification_data["sarcasm"],
            classification_data["emotion"]
        )
    )
    conn.commit()
    cursor.close()
    conn.close()

    # Return combined data
    return jsonify({
        "classification": classification_data,
        "ai_response": ai_response
    }), 200

@app.route('/api/respond_batch', methods=['POST'])
def respond_batch():
    """
    Processes multiple texts in a single request.
    JSON payload example: {"customer_texts": ["...", "..."]}
    1) Validate 'customer_texts' is a list
    2) Classify & respond to each text
    3) Insert each into DB
    4) Return array of results
    """
    payload = request.json
    if not payload or "customer_texts" not in payload:
        return jsonify({"error": "Field 'customer_texts' is required."}), 400

    texts = payload["customer_texts"]
    if not isinstance(texts, list):
        return jsonify({"error": "'customer_texts' must be a list of strings."}), 400

    results = []
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO FeedbackResponses 
        (CustomerText, Sentiment, ResponseText, EmpathyScore, SarcasmDetected, Emotion)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    for text in texts:
        sentiment_result = classify_sentiment(text)
        sarcasm_result = detect_sarcasm(text)
        emotion_result = detect_emotion(text)

        classification_data = {
            "sentiment": sentiment_result["sentiment"],
            "sentiment_confidence": sentiment_result["confidence"],
            "sarcasm": sarcasm_result["sarcasm"],
            "sarcasm_confidence": sarcasm_result["confidence"],
            "emotion": emotion_result["emotion"],
            "emotion_confidence": emotion_result["confidence"]
        }

        ai_response = generate_response(text, classification_data)

        # Insert in DB
        cursor.execute(
            insert_query,
            (
                text,
                classification_data["sentiment"],
                ai_response["response_text"],
                ai_response["empathy_score"],
                classification_data["sarcasm"],
                classification_data["emotion"]
            )
        )

        results.append({
            "input_text": text,
            "classification": classification_data,
            "ai_response": ai_response
        })

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(results), 200

@app.route('/api/dashboard', methods=['GET'])
def view_dashboard():
    """
    Fetches recent feedback records from the DB.
    Adjust query/column names to match your actual table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    select_query = """
    SELECT TOP 10 CustomerText, Sentiment, ResponseText, EmpathyScore, SarcasmDetected, Emotion, CreatedAt
    FROM FeedbackResponses
    ORDER BY CreatedAt DESC;
    """
    cursor.execute(select_query)
    rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            "customer_text": row[0],
            "sentiment": row[1],
            "response_text": row[2],
            "empathy_score": row[3],
            "sarcasm_detected": row[4],
            "emotion": row[5],
            "created_at": str(row[6])
        })

    cursor.close()
    conn.close()

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
