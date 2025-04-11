# app.py
import pyodbc
from flask import Flask, request, jsonify, send_from_directory
import os
import traceback

# REMOVED the import from apiflaskinputvaliderrorlog
# from apiflaskinputvaliderrorlog import validate_request_payload, log_invalid_input

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

# Define frontend paths with absolute paths
FRONTEND_DIST_PATH = '/home/azureuser/Capgemini_SentimentApp_Remake/frontend/dist'
FRONTEND_ASSETS_PATH = os.path.join(FRONTEND_DIST_PATH, 'assets')

def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        # Return None to indicate connection failure
        return None

# ---------------------------------------------------------------------
# The two small functions from apiflaskinputvaliderrorlog.py are copied
# directly into this file, so we can remove the import entirely.
# ---------------------------------------------------------------------
def validate_request_payload(payload):
    """
    Checks if the payload is valid.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    """
    if not payload:
        return (False, "Payload is empty or missing.")

    # Example: we want a 'customer_text' field
    if "customer_text" not in payload or not payload["customer_text"].strip():
        return (False, "Field 'customer_text' is required and cannot be empty.")

    # Add more checks here if needed
    return (True, None)

def log_invalid_input(error_message):
    """
    Logs the invalid request (to console or a file).
    """
    print(f"[INVALID INPUT] {error_message}")
# ---------------------------------------------------------------------

@app.route('/')
def serve_index():
    print(f"Serving index.html from {FRONTEND_DIST_PATH}")
    return send_from_directory(FRONTEND_DIST_PATH, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    print(f"Serving asset {filename} from {FRONTEND_ASSETS_PATH}")
    return send_from_directory(FRONTEND_ASSETS_PATH, filename)

# Serve all files in the dist directory
@app.route('/<path:path>')
def serve_dist(path):
    full_path = os.path.join(FRONTEND_DIST_PATH, path)
    print(f"Request for path: {path}, checking if exists at {full_path}")
    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            return serve_index()
        return send_from_directory(FRONTEND_DIST_PATH, path)
    else:
        print(f"Path not found, returning index.html")
        return serve_index()

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
    try:
        payload = request.json
        print(f"Received payload: {payload}")
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

        try:
            # Insert into DB if connection is successful
            conn = get_db_connection()
            if conn:
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
        except Exception as e:
            print(f"Database error: {str(e)}")
            # Continue without failing if DB has an issue

        # Return combined data
        return jsonify({
            "classification": classification_data,
            "ai_response": ai_response
        }), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in /api/respond: {str(e)}\n{error_traceback}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

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
    try:
        payload = request.get_json(force=True)
        print(f"Batch request payload: {payload}")
        
        if not payload:
            return jsonify({"error": "Empty payload received."}), 400
            
        if "customer_texts" not in payload:
            return jsonify({"error": "Field 'customer_texts' is required."}), 400

        texts = payload["customer_texts"]
        if not isinstance(texts, list):
            return jsonify({"error": "'customer_texts' must be a list of strings."}), 400
            
        if len(texts) == 0:
            return jsonify({"error": "No texts provided for analysis."}), 400
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error parsing batch request: {str(e)}\n{error_traceback}")
        return jsonify({"error": f"Invalid request format: {str(e)}"}), 400

    results = []
    # We'll skip database operations entirely for now
    
    try:
        for text in texts:
            if not text or not isinstance(text, str) or not text.strip():
                continue  # Skip empty texts or non-string items
                
            try:
                # Process this text item
                current_text = text.strip()
                print(f"Processing text: {current_text[:50]}...")
                
                sentiment_result = classify_sentiment(current_text)
                sarcasm_result = detect_sarcasm(current_text)
                emotion_result = detect_emotion(current_text)

                # Make sure all values are JSON serializable
                classification_data = {
                    "sentiment": str(sentiment_result["sentiment"]),
                    "sentiment_confidence": float(sentiment_result["confidence"]),
                    "sarcasm": bool(sarcasm_result["sarcasm"]),
                    "sarcasm_confidence": float(sarcasm_result["confidence"]),
                    "emotion": str(emotion_result["emotion"]),
                    "emotion_confidence": float(emotion_result["confidence"])
                }

                ai_response = generate_response(current_text, classification_data)

                # Add to results
                results.append({
                    "input_text": current_text,
                    "classification": classification_data,
                    "ai_response": ai_response
                })
                
            except Exception as item_err:
                print(f"Error processing text item: {str(item_err)}")
                # Add error info to results
                results.append({
                    "input_text": text if isinstance(text, str) else str(text),
                    "classification": {
                        "sentiment": "neutral",
                        "sentiment_confidence": 0.5,
                        "sarcasm": False,
                        "sarcasm_confidence": 0.5,
                        "emotion": "neutral",
                        "emotion_confidence": 0.5
                    },
                    "ai_response": {
                        "response_text": f"We appreciate your feedback and will review it carefully.",
                        "empathy_score": 0.5
                    },
                    "error": str(item_err)
                })
            
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in batch processing: {str(e)}\n{error_traceback}")
        return jsonify({"error": f"Error processing batch: {str(e)}"}), 500

    if not results:
        return jsonify({"error": "No valid texts were found for processing."}), 400
        
    return jsonify(results), 200

@app.route('/api/dashboard', methods=['GET'])
def view_dashboard():
    """
    Fetches recent feedback records from the DB.
    Adjust query/column names to match your actual table.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Unable to connect to database"}), 500
            
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
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in dashboard: {str(e)}\n{error_traceback}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"Starting Flask app with frontend path: {FRONTEND_DIST_PATH}")
    print(f"Assets path: {FRONTEND_ASSETS_PATH}")
    app.run(host='0.0.0.0', debug=True, port=5000)