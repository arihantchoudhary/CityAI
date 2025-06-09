import time
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials (replace with your actual credentials)
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
recipient_phone_number = os.getenv('RECIPIENT_PHONE_NUMBER')
client = Client(account_sid, auth_token)

def send_text_message():
    message = client.messages.create(
        body="Hello Arihant, this is your scheduled message.",
        from_=twilio_phone_number,
        to=recipient_phone_number
    )
    print(f"Message sent: {message.sid}")

while True:
    send_text_message()
    time.sleep(15 * 60)  # Sleep for 15 minutes