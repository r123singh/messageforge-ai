from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

    def send_message(self, to_number, message):
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.from_number}',
                body=message,
                to=f'whatsapp:{to_number}'
            )
            return {
                'status': 'success',
                'message_id': message.sid,
                'to': to_number
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'to': to_number
            }

def send_whatsapp_message(contact_id, message_content):
    from .models import Contact
    
    contact = Contact.query.get(contact_id)
    if not contact:
        raise ValueError("Contact not found")
    
    whatsapp_service = WhatsAppService()
    return whatsapp_service.send_message(contact.phone_number, message_content) 