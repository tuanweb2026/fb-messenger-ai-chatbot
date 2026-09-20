from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from src.db import init_db, save_message, get_all_conversations, get_conversation_history
from src.pdf_knowledge import PDFKnowledgeEngine, DOCS_DIR
from src.fb_service import FacebookMessengerService
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
app.secret_key = 'super_secret_boss_key_chatbot'

VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "MY_SECURE_VERIFY_TOKEN_123")
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 1. LANDING PAGE CHÀO BÁN DỊCH VỤ
@app.route('/')
def home():
    return render_template('landing.html')

# 2. FACEBOOK WEBHOOK ENDPOINT
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.get_json()
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for messaging_event in entry.get('messaging', []):
                    sender_id = messaging_event.get('sender', {}).get('id')
                    message = messaging_event.get('message', {})
                    if sender_id and message.get('text'):
                        user_text = message['text']
                        save_message(sender_id, f"Khách Facebook ({sender_id[-4:]})", 'user', user_text)
                        ai_reply = PDFKnowledgeEngine.query(user_text)
                        save_message(sender_id, f"Khách Facebook ({sender_id[-4:]})", 'bot', ai_reply)
                        FacebookMessengerService.send_message(sender_id, ai_reply)
            return "EVENT_RECEIVED", 200
        return "Not a page event", 404

# 3. DASHBOARD REVIEW & QUẢN LÝ TRI THỨC CHO SẾP
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
        
    loaded_docs = PDFKnowledgeEngine.get_loaded_files()
        
    return render_template('dashboard.html', 
                           conversations=conversations, 
                           selected_sender=selected_sender, 
                           messages=messages,
                           docs=loaded_docs)

# 4. TẢI LÊN TÀI LIỆU PDF MỚI
@app.route('/upload_knowledge', methods=['POST'])
def upload_knowledge():
    if 'document' not in request.files:
        flash("Vui lòng chọn file tài liệu!", "error")
        return redirect(url_for('dashboard'))
        
    file = request.files['document']
    if file.filename == '':
        flash("Chưa chọn file nào!", "error")
        return redirect(url_for('dashboard'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not filename:
            filename = "tai_lieu_" + file.filename
        filepath = os.path.join(DOCS_DIR, filename)
        file.save(filepath)
        PDFKnowledgeEngine.load_documents()
        flash(f"✅ Đã nạp thành công: {filename}. AI Agent đã được cập nhật tri thức chi tiết!", "success")
    else:
        flash("❌ Chỉ hỗ trợ định dạng file: .pdf, .txt, .md", "error")
        
    return redirect(url_for('dashboard'))

# 5. XÓA 1 FILE TÀI LIỆU CỤ THỂ
@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    if PDFKnowledgeEngine.delete_single_file(filename):
        flash(f"🗑️ Đã xóa file: {filename}.", "success")
    else:
        flash("Không tìm thấy file cần xóa!", "error")
    return redirect(url_for('dashboard'))

# 6. XÓA TOÀN BỘ TÀI LIỆU ĐÃ NẠP (CHUYỂN VỀ CHẾ ĐỘ TRẢ LỜI CƠ BẢN)
@app.route('/delete_all_knowledge', methods=['POST'])
def delete_all_knowledge():
    PDFKnowledgeEngine.delete_all_files()
    flash("🧹 Đã xóa sạch toàn bộ tài liệu! AI Agent hiện chuyển sang chế độ CHỈ TRẢ LỜI CƠ BẢN cho đến khi bạn nạp file mới.", "success")
    return redirect(url_for('dashboard'))

# 7. GIẢ LẬP MESSENGER CHAT ĐỂ SẾP TEST THỬ
@app.route('/simulator')
def simulator():
    return render_template('simulator.html')

@app.route('/api/simulate_chat', methods=['POST'])
def simulate_chat():
    data = request.get_json()
    sender_id = data.get('sender_id', 'test_user_001')
    sender_name = data.get('sender_name', 'Khách Thử Nghiệm')
    user_text = data.get('message', '')
    
    save_message(sender_id, sender_name, 'user', user_text)
    ai_reply = PDFKnowledgeEngine.query(user_text)
    save_message(sender_id, sender_name, 'bot', ai_reply)
    
    return jsonify({
        "user_message": user_text,
        "bot_reply": ai_reply
    })

if __name__ == '__main__':
    init_db()
    PDFKnowledgeEngine.load_documents()
    app.run(port=5006, debug=True)
