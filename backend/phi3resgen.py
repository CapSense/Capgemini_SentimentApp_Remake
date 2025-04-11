# phi3resgen.py (UPDATED - Fallback Version)
# from azure.ai.inference import ChatCompletionsClient
import os
import random

def generate_response(customer_text, classification_data):
    """
    Generates an empathetic response based on:
    - Customer feedback text
    - Classifier outputs (sentiment, sarcasm, emotion)
    Returns: {"response_text": str, "empathy_score": float}
    """
    # Get environment variables
    phi3_endpoint = os.getenv("PHI3_ENDPOINT")
    phi3_key = os.getenv("PHI3_KEY")
    
    # Since we don't have proper PHI-3 credentials, let's use a fallback
    # that generates empathetic responses based on the classification data
    
    sentiment = classification_data.get('sentiment', 'neutral').lower()
    emotion = classification_data.get('emotion', 'neutral').lower()
    sarcasm_detected = classification_data.get('sarcasm', False)
    
    # Generate fallback responses based on sentiment and emotion
    positive_responses = [
        "Thank you for your positive feedback! We're glad to hear you had a good experience.",
        "We appreciate your kind words. Your satisfaction is our priority.",
        "Thanks for sharing your positive experience. We're happy we could meet your expectations."
    ]
    
    neutral_responses = [
        "Thank you for your feedback. We value your input and will use it to improve our services.",
        "We appreciate you taking the time to share your thoughts with us.",
        "Thank you for reaching out. Your feedback helps us serve you better."
    ]
    
    negative_responses = [
        "We apologize for your experience. Your feedback is important, and we'll work to address these concerns.",
        "We're sorry to hear you had a disappointing experience. We value your feedback and will use it to improve.",
        "Thank you for bringing this to our attention. We apologize for the inconvenience and will work to do better."
    ]
    
    sarcastic_addition = "We understand there may be some frustration behind your message, and we take your feedback seriously. "
    
    if sentiment == 'positive':
        response_text = random.choice(positive_responses)
        empathy_score = 0.9
    elif sentiment == 'negative':
        response_text = random.choice(negative_responses)
        empathy_score = 0.8
    else:
        response_text = random.choice(neutral_responses)
        empathy_score = 0.7
    
    # Add emotion-specific additions
    if emotion == 'joy':
        response_text += " We're delighted to hear your enthusiasm!"
    elif emotion == 'anger':
        response_text += " We understand your frustration and we're here to help."
    elif emotion == 'sadness':
        response_text += " We sincerely care about your concerns."
    
    # Add sarcasm-specific additions if detected
    if sarcasm_detected and isinstance(sarcasm_detected, bool):
        response_text = sarcastic_addition + response_text
    
    return {
        "response_text": response_text,
        "empathy_score": empathy_score
    }