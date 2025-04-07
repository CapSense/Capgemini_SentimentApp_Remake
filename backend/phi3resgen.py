# phi3resgen.py (UPDATED - Azure AI Studio Version)(FINAL VERSION)
from azure.ai.inference import ChatCompletionsClient
import os

def generate_response(customer_text, classification_data):
    """
    Generates an empathetic response using Phi-3, based on:
    - Customer feedback text
    - Classifier outputs (sentiment, sarcasm, emotion)
    Returns: {"response_text": str, "empathy_score": float}
    """
    client = ChatCompletionsClient(
        endpoint=os.getenv("PHI3_ENDPOINT"),
        credential=os.getenv("PHI3_KEY")
    )

    prompt = f"""
    As a customer service agent, respond to this feedback:
    
    **Customer Feedback**: "{customer_text}"
    **Sentiment**: {classification_data.get('sentiment', 'neutral')}
    **Emotion**: {classification_data.get('emotion', 'unknown')}
    **Sarcasm Detected**: {classification_data.get('sarcasm', False)}
    
    Write a concise, empathetic response (2-3 sentences):
    """

    response = client.complete(
        model="phi-3-mini-4k-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = response.choices[0].message.content
    empathy_score = min(len(response_text) / 150, 1.0)  # Better placeholder logic
    
    return {
        "response_text": response_text,
        "empathy_score": round(empathy_score, 2)
    }