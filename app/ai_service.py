from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client without proxies
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.openai.com/v1"  # Explicitly set the base URL
)

def generate_message(prompt):
    """
    Generate a WhatsApp message using OpenAI's GPT model
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates professional and engaging WhatsApp messages for marketing campaigns. Keep the messages concise and effective."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error generating message: {str(e)}")

def analyze_response(message_content):
    """
    Analyze the sentiment and effectiveness of a message response
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing message effectiveness and sentiment."},
                {"role": "user", "content": f"Analyze this message response: {message_content}"}
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error analyzing response: {str(e)}") 