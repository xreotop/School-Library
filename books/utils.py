import requests
from django.conf import settings

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception:
        return False
