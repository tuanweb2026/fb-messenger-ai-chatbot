import requests
import os

PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "YOUR_FB_PAGE_ACCESS_TOKEN")
GRAPH_API_URL = "https://graph.facebook.com/v19.0/me/messages"

class FacebookMessengerService:
    @staticmethod
    def send_message(recipient_id, message_text):
        """
        Gửi tin nhắn phản hồi về Facebook Messenger của khách hàng qua Graph API.
        """
        if PAGE_ACCESS_TOKEN == "YOUR_FB_PAGE_ACCESS_TOKEN":
            print(f"[DEV MODE - No Token] Giả lập gửi tới FB recipient {recipient_id}: {message_text[:60]}...")
            return True
            
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        params = {"access_token": PAGE_ACCESS_TOKEN}
        headers = {"Content-Type": "application/json"}
        
        try:
            res = requests.post(GRAPH_API_URL, params=params, json=payload, headers=headers, timeout=10)
            return res.status_code == 200
        except Exception as e:
            print(f"Error sending FB message: {e}")
            return False
