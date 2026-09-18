import os
import re
from src.db import get_db

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')

class PDFKnowledgeEngine:
    @staticmethod
    def load_documents():
        """
        Đọc các tài liệu văn bản / PDF trong thư mục docs/ và lưu vào database knowledge_chunks.
        """
        if not os.path.exists(DOCS_DIR):
            os.makedirs(DOCS_DIR)
            
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_chunks")
        
        files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.txt') or f.endswith('.md') or f.endswith('.pdf')]
        
        for filename in files:
            filepath = os.path.join(DOCS_DIR, filename)
            text = ""
            if filename.endswith('.pdf'):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(filepath)
                    for page in reader.pages:
                        text += (page.extract_text() or "") + "\n"
                except Exception as e:
                    print(f"Error reading PDF {filename}: {e}")
            else:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    
            # Tách thành từng đoạn văn (Paragraph chunks)
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 30]
            for p in paragraphs:
                cursor.execute("INSERT INTO knowledge_chunks (filename, content) VALUES (?, ?)", (filename, p))
                
        conn.commit()
        conn.close()

    @staticmethod
    def query(user_question):
        """
        Tìm kiếm đoạn tài liệu phù hợp nhất và sinh câu trả lời cho khách.
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM knowledge_chunks")
        chunks = [row['content'] for row in cursor.fetchall()]
        conn.close()
        
        if not chunks:
            return "Chào bạn! Hiện tại hệ thống đang cập nhật tài liệu kiến thức. Vui lòng để lại số điện thoại hoặc câu hỏi, shop sẽ liên hệ hỗ trợ bạn sớm nhất nhé!"

        # Tìm kiếm dựa trên từ khóa / relevance matching
        keywords = re.findall(r'\w+', user_question.lower())
        best_chunk = ""
        best_score = 0
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for kw in keywords if kw in chunk_lower)
            if score > best_score:
                best_score = score
                best_chunk = chunk
                
        if best_score > 0 and best_chunk:
            return f"Chào bạn, theo thông tin từ tài liệu của chúng tôi:\n\n{best_chunk}\n\nNếu bạn cần hỗ trợ thêm thông tin gì khác, cứ nhắn cho mình nhé!"
        else:
            return "Cảm ơn bạn đã liên hệ! Câu hỏi của bạn chưa có trong tài liệu hướng dẫn sẵn có. Tư vấn viên của chúng tôi sẽ xem lại lịch sử và phản hồi lại bạn ngay ít phút nữa nhé!"
