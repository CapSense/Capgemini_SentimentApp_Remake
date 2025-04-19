# app.py

from f1_score import compute_f1_score, generate_model_evaluation_metrics
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Import CORS for cross-origin requests
import os


try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    print("WARNING: pyodbc module not available. Database functionality will be disabled.")
    PYODBC_AVAILABLE = False

from classifier_sentiment import classify_sentiment
from classifier_sarcasm import detect_sarcasm
from classifier_emotion import detect_emotion
# Where is aspect-based classifier?
from phi3resgen import generate_response

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Clear FeedbackResponses table on startup if it has data
def initialize_database():
    print("[INIT] Checking and cleaning FeedbackResponses table if needed...")
    conn = get_db_connection()
    if conn is None:
        print("[INIT ERROR] Could not connect to DB for initialization.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM FeedbackResponses;")
        row_count = cursor.fetchone()[0]
        print(f"[INIT] Found {row_count} records in FeedbackResponses.")
        if row_count > 0:
            print("[INIT] Clearing the table...")
            cursor.execute("DELETE FROM FeedbackResponses;")
            conn.commit()
            print("[INIT] Table cleared.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[INIT ERROR] Failed to initialize database: {str(e)}")


# Production DB config for Azure SQL
DB_CONFIG = {
    'server': '1sqlcapsenseserver.database.windows.net',
    'database': 'SentimentAnalysisDB',
    'username': 'capsenseadmin',
    'password': 'Access@Capsense1'
}

def get_db_connection():
    """
    Returns a database connection or None if pyodbc is not available
    """
    if not PYODBC_AVAILABLE:
        print("WARNING: Database connection requested but pyodbc is not available")
        return None
        
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"ERROR connecting to database: {str(e)}")
        return None


# Validation functions
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

# Updated static file serving paths
@app.route('/')
def serve_index():
    frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
    print(f"Attempting to serve index.html from: {frontend_dist_path}")
    return send_from_directory(frontend_dist_path, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist', 'assets'))
    print(f"Attempting to serve asset {filename} from: {assets_path}")
    return send_from_directory(assets_path, filename)

@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    """
    Processes user feedback on AI-generated responses (approve/reject).
    """
    try:
        payload = request.get_json(force=True)

        # Normalize input strings
        payload["original_text"] = payload["original_text"].strip().lower()
        payload["response_text"] = payload["response_text"].strip().lower()

        # Validate payload
        if not payload or not all(k in payload for k in ["original_text", "response_text", "feedback"]):
            return jsonify({"error": "Missing required fields"}), 400

        feedback_type = payload["feedback"].lower()
        if feedback_type not in ["approved", "rejected"]:
            return jsonify({"error": "Feedback must be either 'approved' or 'rejected'"}), 400

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Check if entry exists
                check_query = """
                SELECT Id FROM FeedbackResponses 
                WHERE LOWER(LTRIM(RTRIM(CustomerText))) = ? 
                AND LOWER(LTRIM(RTRIM(ResponseText))) = ?;
                """
                cursor.execute(check_query, (payload["original_text"], payload["response_text"]))
                row = cursor.fetchone()

                if row:
                    update_query = """
                    UPDATE FeedbackResponses 
                    SET approved = ?, FeedbackDate = GETDATE()
                    WHERE Id = ?;
                    """
                    cursor.execute(update_query, (1 if feedback_type == "approved" else 0, row[0]))
                else:
                    insert_query = """
                    INSERT INTO FeedbackResponses 
                        (CustomerText, ResponseText, approved, FeedbackDate)
                    VALUES (?, ?, ?, GETDATE());
                    """
                    cursor.execute(insert_query, (
                        payload["original_text"],
                        payload["response_text"],
                        1 if feedback_type == "approved" else 0
                    ))

                conn.commit()
                cursor.close()
                conn.close()

                return jsonify({
                    "message": f"Feedback ({feedback_type}) recorded successfully",
                    "status": "success"
                }), 200

            except Exception as db_error:
                print(f"[DB ERROR] Payload: {payload}")
                print(f"[DB ERROR] Exception: {str(db_error)}")
                return jsonify({"error": f"Database error: {str(db_error)}"}), 500
        else:
            return jsonify({
                "message": f"Feedback ({feedback_type}) received. DB not available, operation simulated.",
                "status": "success"
            }), 200

    except Exception as e:
        print(f"[GENERAL ERROR] Payload processing failed.")
        print(f"[GENERAL ERROR] Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Comment out single-line submission since it's no longer needed
"""
@app.route('/api/respond', methods=['POST'])
def respond_single():
    Processes a single piece of customer text.
    JSON payload example: {"customer_text": "..."}
    1) Validate input
    2) Classify sentiment, sarcasm, emotion
    3) Generate AI response
    4) Insert record into DB
    5) Return combined result
    
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
    
    # Calculate F1 score
    f1_score = compute_f1_score(sentiment_result)

    try:
        # Insert into DB
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            insert_query = '''
            INSERT INTO FeedbackResponses 
                (CustomerText, Sentiment, ResponseText, EmpathyScore, SarcasmDetected, Emotion, F1Score)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            '''
            cursor.execute(
                insert_query,
                (
                    customer_text,
                    classification_data["sentiment"],
                    ai_response["response_text"],
                    ai_response["empathy_score"],
                    classification_data["sarcasm"],
                    classification_data["emotion"],
                    f1_score
                )
            )
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Database error: {str(e)}")
        # Still return the response even if DB insertion fails

    # Return combined data with F1 score
    return jsonify({
        "classification": classification_data,
        "ai_response": ai_response,
        "f1_score": f1_score
    }), 200
"""

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
        if not payload or "customer_texts" not in payload:
            return jsonify({"error": "Field 'customer_texts' is required."}), 400

        texts = payload["customer_texts"]
        if not isinstance(texts, list):
            return jsonify({"error": "'customer_texts' must be a list of strings."}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    results = []
    
    # Get DB connection (might be None if not available)
    conn = get_db_connection()
    cursor = None
    
    try:
        # Only set up DB operations if connection is available
        if conn:
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO FeedbackResponses 
                (CustomerText, Sentiment, ResponseText, EmpathyScore, SarcasmDetected, Emotion, F1Score)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """
        else:
            print("Database connection not available - skipping DB operations")

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

            # Generate AI-based response
            ai_response = generate_response(text, classification_data)
            
            # Calculate F1 score
            f1_score = compute_f1_score(sentiment_result)

            # Insert in DB only if connection is available
            if conn and cursor:
                cursor.execute(
                    insert_query,
                    (
                        text,
                        classification_data["sentiment"],
                        ai_response["response_text"],
                        ai_response["empathy_score"],
                        classification_data["sarcasm"],
                        classification_data["emotion"],
                        f1_score
                    )
                )

            results.append({
                "input_text": text,
                "classification": classification_data,
                "ai_response": ai_response,
                "f1_score": f1_score
            })
        
        # Commit and close DB resources if they were opened
        if conn and cursor:
            conn.commit()
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing batch: {str(e)}")
        # Continue processing even if DB operations fail

    return jsonify(results), 200

@app.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyzes a single text without storing in DB.
    Used by the frontend for batch processing.
    """
    try:
        payload = request.get_json(force=True)
        if not payload or "text" not in payload:
            return jsonify({"error": "Field 'text' is required."}), 400

        text = payload["text"]
        
        # Classification
        sentiment_result = classify_sentiment(text)
        sarcasm_result = detect_sarcasm(text)
        emotion_result = detect_emotion(text)
        
        # Generate response
        classification_data = {
            "sentiment": sentiment_result["sentiment"],
            "sentiment_confidence": sentiment_result["confidence"],
            "sarcasm": sarcasm_result["sarcasm"],
            "sarcasm_confidence": sarcasm_result["confidence"],
            "emotion": emotion_result["emotion"],
            "emotion_confidence": emotion_result["confidence"]
        }
        
        ai_response = generate_response(text, classification_data)
        
        # Calculate F1 score
        f1_score = compute_f1_score(sentiment_result)
        
        # Note: This endpoint doesn't use the database at all, so no changes needed here
        
        return jsonify({
            "emotion": emotion_result["emotion"],
            "sarcasm": "Yes" if sarcasm_result["sarcasm"] else "No",
            "aspects": "Product quality, Customer service", # Placeholder
            "classification": sentiment_result["sentiment"],
            "response": ai_response["response_text"],
            "originalText": text,
            "f1Score": f1_score
        }), 200
        
    except Exception as e:
        print(f"Error in batch analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def view_dashboard():
    """
    Fetches recent feedback records from the DB.
    Adjust query/column names to match your actual table.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection not available"}), 503
            
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
        return jsonify({"error": f"Database error: {str(e)}"}), 500


if __name__ == '__main__':
    # Initialize the database on startup
    initialize_database()
    app.run(host='0.0.0.0', debug=True, port=5000)