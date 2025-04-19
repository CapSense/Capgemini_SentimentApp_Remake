# phi3resgen.py - Updated for Azure AI Foundry with improved error handling
import requests
import json
import os
import time
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("phi3resgen")

def generate_response(customer_text, classification_data):
    """
    Generates an empathetic response using Phi-3, based on:
    - Customer feedback text
    - Classifier outputs (sentiment, sarcasm, emotion)
    Returns: {"response_text": str, "empathy_score": float}
    """
    # Get environment variables
    phi3_endpoint = os.getenv("PHI3_ENDPOINT")
    phi3_key = os.getenv("PHI3_KEY")
    
    # Check if environment variables are properly set
    if not phi3_endpoint or not phi3_key:
        logger.warning("PHI3_ENDPOINT or PHI3_KEY environment variables not set. Using fallback response.")
        logger.info(f"PHI3_ENDPOINT is {'set' if phi3_endpoint else 'NOT SET'}")
        logger.info(f"PHI3_KEY is {'set (value hidden)' if phi3_key else 'NOT SET'}")
        return generate_fallback_response(customer_text, classification_data)
    
    # Log the environment variables (partially masked for security)
    logger.info(f"Using PHI3_ENDPOINT: {phi3_endpoint}")
    if phi3_key:
        masked_key = phi3_key[:5] + "..." + phi3_key[-5:] if len(phi3_key) > 10 else "***"
        logger.info(f"Using PHI3_KEY: {masked_key}")
    
    # If environment variables are properly set, use Azure AI
    try:
        # Prepare the prompt
        prompt = f"""
        As a customer service agent for Capgemini, respond to this feedback:
        
        **Customer Feedback**: "{customer_text}"
        **Sentiment**: {classification_data.get('sentiment', 'neutral')}
        **Emotion**: {classification_data.get('emotion', 'unknown')}
        **Sarcasm Detected**: {classification_data.get('sarcasm', False)}
        
        Write a concise, empathetic response (2-3 sentences):
        """
        
        # Prepare the payload for Azure AI Foundry
        payload = {
          "input_data": {
        	"input_string": [
            		{"role": "user", "content": prompt}
          ],
          "parameters": {
            "temperature": 0.7,
            "top_p": 1,
            "max_new_tokens": 150
          }
      }
  }
        
        # Using bearer token auth which seems to work
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {phi3_key}"
        }
        
        # Make the request to Azure AI Foundry
        logger.info(f"Calling PHI-3 API at {phi3_endpoint}")
        response = requests.post(
            phi3_endpoint, 
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check response status
        logger.info(f"Received status code: {response.status_code}")
        
        # If successful, process the response
        if response.status_code == 200:
            try:
                # Log the raw response text for debugging
                logger.info(f"Raw response text: {response.text[:200]}...")
                
                # Parse the JSON response
                if response.text.strip():
                    response_data = response.json()
                    logger.info(f"Response type: {type(response_data)}")
                    
                    # Check if we got usable data
                    if isinstance(response_data, dict) and response_data:
                        logger.info(f"Response keys: {list(response_data.keys())}")
                    elif isinstance(response_data, list):
                        logger.info(f"Response is a list with {len(response_data)} items")
                        
                    # Extract the response text using a simple approach
                    response_text = extract_response_text(response_data)
                    
                    if response_text:
                        logger.info(f"Successfully extracted response: {response_text[:50]}...")
                        empathy_score = calculate_empathy_score(response_text, classification_data)
                        return {
                            "response_text": response_text,
                            "empathy_score": empathy_score
                        }
                    else:
                        logger.warning("Could not extract text from response")
                else:
                    logger.warning("Empty response received")
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")
        else:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
        
        # If we get here, something went wrong, use fallback
        return generate_fallback_response(customer_text, classification_data)
            
    except Exception as e:
        logger.error(f"Error generating response with Azure AI: {str(e)}")
        return generate_fallback_response(customer_text, classification_data)

def extract_response_text(response_data):
    """
    Extracts response text from various possible response formats.
    Returns the text or None if it can't be found.
    """
    # If response is a string, return it directly
    if isinstance(response_data, str):
        return response_data
        
    # If response is a dict, check common patterns
    if isinstance(response_data, dict):
        # OpenAI-like format
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            elif "text" in choice:
                return choice["text"]
        
        # Direct content field
        if "content" in response_data:
            return response_data["content"]
            
        # Azure AI might use model_output
        if "model_output" in response_data:
            if isinstance(response_data["model_output"], dict) and "text" in response_data["model_output"]:
                return response_data["model_output"]["text"]
            elif isinstance(response_data["model_output"], str):
                return response_data["model_output"]
        
        # Last resort: try any string field that might contain text
        for key, value in response_data.items():
            if isinstance(value, str) and len(value) > 10:
                return value
    
    # If response is a list, check first item
    if isinstance(response_data, list) and len(response_data) > 0:
        first_item = response_data[0]
        # Recursively check the first item
        return extract_response_text(first_item)
    
    # Couldn't find any usable text
    return None

def generate_fallback_response(customer_text, classification_data):
    """
    Generates a fallback response when the Azure AI service is unavailable
    """
    logger.info("Using fallback response generation")
    sentiment = classification_data.get('sentiment', 'neutral').lower()
    emotion = classification_data.get('emotion', 'unknown').lower()
    is_sarcastic = classification_data.get('sarcasm', False)
    
    # Templates for different sentiment categories
    positive_templates = [
        "Thank you for your positive feedback! We're thrilled to hear you're enjoying our service. Your support means a lot to us.",
        "We appreciate your kind words and positive feedback. It's wonderful to know our efforts have led to a good experience for you.",
        "Thank you for sharing such positive thoughts with us. We're committed to maintaining the quality you've highlighted."
    ]
    
    negative_templates = [
        "We sincerely apologize for your negative experience. Your feedback is important to us, and we'd like to address your concerns to make things right.",
        "We're sorry to hear about your disappointing experience. We take your feedback seriously and will work to improve based on your comments.",
        "Thank you for bringing this issue to our attention. We apologize for the inconvenience and are committed to resolving this situation."
    ]
    
    neutral_templates = [
        "Thank you for your feedback. We value your input and will take your comments into consideration for future improvements.",
        "We appreciate you taking the time to share your thoughts with us. Your feedback helps us improve our services.",
        "Thank you for reaching out. We're constantly working to enhance our offerings based on customer input like yours."
    ]
    
    # Select template based on sentiment
    if sentiment == "positive":
        template = random.choice(positive_templates)
    elif sentiment == "negative":
        template = random.choice(negative_templates)
    else:
        template = random.choice(neutral_templates)
    
    # Add emotion-specific acknowledgment for negative sentiment
    if sentiment == "negative" and emotion in ["anger", "sadness", "fear", "disgust"]:
        emotional_acknowledgments = {
            "anger": "We understand this situation has been frustrating for you.",
            "sadness": "We understand this experience has been disappointing for you.",
            "fear": "We understand your concerns and take them very seriously.",
            "disgust": "We understand this experience has been unpleasant for you."
        }
        template += " " + emotional_acknowledgments.get(emotion, "")
    
    # Add sarcasm acknowledgment if detected
    if is_sarcastic:
        template += " We appreciate your candid feedback and want to address the underlying concerns."
    
    empathy_score = 0.7  # Reasonable default for templated responses
    
    logger.info(f"Generated fallback response: {template[:50]}...")
    return {
        "response_text": template,
        "empathy_score": empathy_score
    }

def calculate_empathy_score(response_text, classification_data):
    """
    Calculates an empathy score based on response length, sentiment acknowledgment,
    and presence of empathetic phrases
    """
    score = 0.5  # Base score
    
    # Length factor (longer responses often show more care, up to a point)
    length = len(response_text)
    if 50 <= length <= 200:
        score += 0.2
    elif length > 200:
        score += 0.1  # Very long responses might be less effective
    
    # Check for empathetic phrases
    empathy_phrases = [
        "understand", "appreciate", "sorry", "thank you", 
        "apologize", "help", "resolve", "assist",
        "feel", "concern", "important", "value"
    ]
    
    response_lower = response_text.lower()
    phrase_count = sum(1 for phrase in empathy_phrases if phrase in response_lower)
    phrase_score = min(0.3, phrase_count * 0.05)  # Cap at 0.3
    score += phrase_score
    
    # Round to 2 decimal places and ensure score is between 0 and 1
    return round(min(max(score, 0), 1), 2)