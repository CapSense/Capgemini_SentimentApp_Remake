# apiflaskinputvaliderrorlog.py

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
