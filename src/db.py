import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fb_chatbot.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Cuộc trò chuyện
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT UNIQUE NOT NULL,
        sender_name TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tin nhắn qua lại
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT NOT NULL,
        sender_type TEXT NOT NULL, -- 'user' or 'bot'
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES conversations(sender_id)
    )
    ''')

    # Chunks tri thức từ PDF
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def save_message(sender_id, sender_name, sender_type, content):
    conn = get_db()
    cursor = conn.cursor()
    
    # Cập nhật hoặc tạo conversation
    cursor.execute('''
    INSERT INTO conversations (sender_id, sender_name, last_message_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(sender_id) DO UPDATE SET 
        sender_name = COALESCE(excluded.sender_name, conversations.sender_name),
        last_message_at = CURRENT_TIMESTAMP
    ''', (sender_id, sender_name))
    
    # Lưu tin nhắn
    cursor.execute('''
    INSERT INTO messages (sender_id, sender_type, content)
    VALUES (?, ?, ?)
    ''', (sender_id, sender_type, content))
    
    conn.commit()
    conn.close()

def get_all_conversations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, 
           (SELECT content FROM messages WHERE sender_id = c.sender_id ORDER BY created_at DESC LIMIT 1) as latest_message,
           (SELECT COUNT(*) FROM messages WHERE sender_id = c.sender_id) as total_messages
    FROM conversations c
    ORDER BY c.last_message_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_conversation_history(sender_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM messages 
    WHERE sender_id = ? 
    ORDER BY created_at ASC
    ''', (sender_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages
