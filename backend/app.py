"""
app.py
Main Flask app that:
1. Exposes routes for sentiment analysis / AI-based response generation
2. Connects to Azure SQL (production)
3. (Optional) Could connect to fallback DB if needed
"""

import pyodbc
from flask import Flask, request, jsonify
import phi3resgen
from f1_score import compute_f1_score

app = Flask(__name__)

# Production DB config for Azure SQL
DB_CONFIG = {
    'server': '1sqlcapsenseserver.database.windows.net',
    'database': 'SentimentAnalysisDB',
    'username': 'capsenseadmin',
    'password': 'Access@Capsense1'
}

def get_db_connection():
    """
    Azure SQL connection using pyodbc.
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

# If you need a fallback local DB for quick testing, import from db_fallback:
# from db_fallback import get_fallback_db_connection


@app.route('/api/respond', methods=['POST'])
def respond_to_feedback():
    """
    Endpoint: /api/respond
    Expects JSON:
    {
      "customer_text": "User's feedback here..."
    }
    Steps:
    1) Run classification (phi3resgen.classify_sentiment).
    2) Generate AI-based response (phi3resgen.generate_response).
    3) Compute F1 or other metrics (optional).
    4) Insert into Azure SQL for record-keeping.
    5) Return results to the frontend.
    """
    data = request.json
    if not data or "customer_text" not in data:
        return jsonify({"error": "No customer_text provided"}), 400

    customer_text = data["customer_text"]

    # 1. Classify sentiment
    sentiment_results = phi3resgen.classify_sentiment(customer_text)

    # 2. Generate AI response
    ai_response = phi3resgen.generate_response(customer_text, sentiment_results)

    # 3. Compute F1 (or other metrics)
    f1_value = compute_f1_score(sentiment_results)

    # 4. Store results in Azure SQL
    conn = get_db_connection()
    cursor = conn.cursor()

    # Make sure this table matches your actual schema in Azure:
    insert_query = """
    INSERT INTO FeedbackResponses (CustomerText, Sentiment, ResponseText, F1Score, EmpathyScore)
    VALUES (?, ?, ?, ?, ?);
    """

    cursor.execute(
        insert_query,
        (
            customer_text,
            sentiment_results.get("sentiment", ""),
            ai_response.get("response_text", ""),
            f1_value,
            ai_response.get("empathy_score", 0.0)
        )
    )

    conn.commit()
    cursor.close()
    conn.close()

    # 5. Send it back to the frontend
    return jsonify({
        "sentiment_results": sentiment_results,
        "ai_response": ai_response,
        "f1_score": f1_value
    }), 200


@app.route('/api/dashboard', methods=['GET'])
def view_dashboard():
    """
    Endpoint: /api/dashboard
    Returns a list of recent feedback entries from Azure SQL
    so the frontend can display them in a dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Example: selecting the latest 10 entries
    select_query = """
    SELECT TOP 10 CustomerText, Sentiment, ResponseText, F1Score, CreatedAt 
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
            "f1_score": row[3],
            "created_at": str(row[4])  # Convert datetime to string
        })

    cursor.close()
    conn.close()

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
