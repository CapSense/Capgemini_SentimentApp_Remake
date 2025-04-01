# phi3resgen.py
# Simple function to shape AI response. Real usage might call GPT or another LLM.

def generate_response(customer_text, classification_data):
    """
    classification_data can have keys: 'sentiment', 'sarcasm', 'emotion', etc.
    Return: {"response_text": "...", "empathy_score": 0.9}
    """
    sentiment = classification_data.get("sentiment", "Neutral")
    sarcasm = classification_data.get("sarcasm", False)

    if sentiment == "Negative":
        response_text = (
            "We’re sorry to hear about your experience. "
            "We value your feedback and want to make it right."
        )
        empathy_score = 0.9
    else:
        response_text = (
            "We’re glad to hear things are going well! "
            "Thanks for sharing your thoughts."
        )
        empathy_score = 0.8

    # If sarcasm is detected, tweak the response
    if sarcasm:
        response_text += " We sense you might be a bit sarcastic—let's clarify any misunderstanding."

    return {
        "response_text": response_text,
        "empathy_score": empathy_score
    }
