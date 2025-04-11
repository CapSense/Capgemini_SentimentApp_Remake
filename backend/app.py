# app.py
import pyodbc
from flask import Flask, request, jsonify, send_from_directory
import os
import traceback

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
        return None

def validate_request_payload(payload):
    """
    Checks if the payload is valid.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    """
    if not payload:
        return (False, "Payload is empty or missing.")

    if "customer_text" not in payload or not payload["customer_text"].strip():
        return (False, "Field 'customer_text' is required and cannot be empty.")

    return (True, None)

def log_invalid_input(error_message):
    """
    Logs the invalid request (to console or a file).
    """
    print(f"[INVALID INPUT] {error_message}")

@app.route('/')
def serve_index():
    print(f"Serving index.html from {FRONTEND_DIST_PATH}")
    return send_from_directory(FRONTEND_DIST_PATH, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    print(f"Serving asset {filename} from {FRONTEND_ASSETS_PATH}")
    return send_from_directory(FRONTEND_ASSETS_PATH, filename)

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

# [Rest of the file remains the same as the latest functional version]
# ... (Copy all the route handlers from the latest functional version)

if __name__ == '__main__':
    print(f"Starting Flask app with frontend path: {FRONTEND_DIST_PATH}")
    print(f"Assets path: {FRONTEND_ASSETS_PATH}")
    app.run(host='0.0.0.0', debug=True, port=5000)