from flask import Flask, request, jsonify, render_template, redirect, url_for
from src.db import init_db, save_message, get_all_conversations, get_conversation_history
from src.pdf_knowledge import PDFKnowledgeEngine
from src.fb_service import FacebookMessengerService
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "MY_SECURE_VERIFY_TOKEN_123")

# 1. LANDING PAGE CHÀO BÁN DỊCH VỤ
@app.route('/')
def home():
    return render_template('landing.html')

# 2. FACEBOOK WEBHOOK ENDPOINT
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Xác minh Webhook từ Facebook Meta Developer Portal
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("[FB Webhook] Xác thực thành công!")
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    # Tiếp nhận tin nhắn gửi đến từ Facebook Messenger
    if request.method == 'POST':
        data = request.get_json()
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for messaging_event in entry.get('messaging', []):
                    sender_id = messaging_event.get('sender', {}).get('id')
                    message = messaging_event.get('message', {})
                    
                    if sender_id and message.get('text'):
                        user_text = message['text']
                        
                        # 1. Lưu tin nhắn của khách vào SQLite
                        save_message(sender_id, f"Khách Facebook ({sender_id[-4:]})", 'user', user_text)
                        
                        # 2. AI tra cứu kiến thức từ tài liệu PDF/Doc
                        ai_reply = PDFKnowledgeEngine.query(user_text)
                        
                        # 3. Lưu phản hồi của bot vào SQLite
                        save_message(sender_id, f"Khách Facebook ({sender_id[-4:]})", 'bot', ai_reply)
                        
                        # 4. Gửi tin nhắn trả lời qua Facebook Messenger
                        FacebookMessengerService.send_message(sender_id, ai_reply)
                        
            return "EVENT_RECEIVED", 200
        return "Not a page event", 404

# 3. DASHBOARD REVIEW CHO SẾP
@app.route('/dashboard')
def dashboard():
    conversations = get_all_conversations()
    selected_sender = request.args.get('sender_id')
    messages = []
    
    if selected_sender:
        messages = get_conversation_history(selected_sender)
    elif len(conversations) > 0:
        selected_sender = conversations[0]['sender_id']
        messages = get_conversation_history(selected_sender)
        
    return render_template('dashboard.html', 
                           conversations=conversations, 
                           selected_sender=selected_sender, 
                           messages=messages)

# 4. GIẢ LẬP MESSENGER CHAT ĐỂ SẾP TEST THỬ
@app.route('/simulator')
def simulator():
    return render_template('simulator.html')

@app.route('/api/simulate_chat', methods=['POST'])
def simulate_chat():
    data = request.get_json()
    sender_id = data.get('sender_id', 'test_user_001')
    sender_name = data.get('sender_name', 'Khách Thử Nghiệm')
    user_text = data.get('message', '')
    
    # Lưu tin khách
    save_message(sender_id, sender_name, 'user', user_text)
    # AI trả lời từ file tài liệu
    ai_reply = PDFKnowledgeEngine.query(user_text)
    # Lưu tin bot
    save_message(sender_id, sender_name, 'bot', ai_reply)
    
    return jsonify({
        "user_message": user_text,
        "bot_reply": ai_reply
    })

if __name__ == '__main__':
    init_db()
    PDFKnowledgeEngine.load_documents()
    app.run(port=5006, debug=True)
