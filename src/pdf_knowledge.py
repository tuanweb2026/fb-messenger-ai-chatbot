import os
import re
from src.db import get_db

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')

class PDFKnowledgeEngine:
    @staticmethod
    def load_documents():
        """
        Đọc tất cả các tài liệu (.txt, .md, .pdf) trong thư mục docs/ và nạp vào database.
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
                    
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
            for p in paragraphs:
                cursor.execute("INSERT INTO knowledge_chunks (filename, content) VALUES (?, ?)", (filename, p))
                
        conn.commit()
        conn.close()
        print(f"[Knowledge Base] Đã nạp thành công {len(files)} tài liệu.")

    @staticmethod
    def get_loaded_files():
        """
        Lấy danh sách các tài liệu hiện có trong docs/
        """
        if not os.path.exists(DOCS_DIR):
            return []
        file_list = []
        for f in os.listdir(DOCS_DIR):
            if f.endswith('.txt') or f.endswith('.md') or f.endswith('.pdf'):
                path = os.path.join(DOCS_DIR, f)
                size_kb = round(os.path.getsize(path) / 1024, 1)
                file_list.append({"name": f, "size": f"{size_kb} KB"})
        return file_list

    @staticmethod
    def query(user_question):
        """
        Tìm kiếm thông tin chính xác nhất từ tài liệu PDF/Doc và sinh câu trả lời chuyên nghiệp.
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, content FROM knowledge_chunks")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "Dạ chào bạn! Hiện tại hệ thống đang được cập nhật tài liệu kiến thức mới. Bạn vui lòng để lại số điện thoại hoặc nhu cầu cụ thể, tư vấn viên của shop sẽ liên hệ hỗ trợ bạn ngay nhé ạ! ❤️"

        # Tách từ khóa tìm kiếm (loại bỏ từ nối đơn giản)
        keywords = [w for w in re.findall(r'\w+', user_question.lower()) if len(w) > 1]
        
        scored_chunks = []
        for r in rows:
            chunk = r['content']
            chunk_lower = chunk.lower()
            # Tính điểm tương đồng từ khóa
            score = sum(2 if kw in chunk_lower else 0 for kw in keywords)
            # Điểm cộng nếu chứa các từ cốt lõi
            for core in ['giá', 'bao nhiêu', 'chi phí', 'địa chỉ', 'ở đâu', 'hoàn tiền', 'bảo hành', 'hotline', 'giờ', 'thời gian', 'liên hệ']:
                if core in user_question.lower() and core in chunk_lower:
                    score += 3
            if score > 0:
                scored_chunks.append((score, chunk, r['filename']))
                
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        if scored_chunks and scored_chunks[0][0] >= 2:
            best_chunk = scored_chunks[0][1]
            return f"Dạ chào bạn! Cảm ơn bạn đã nhắn tin cho shop ạ.\n\nVề thắc mắc của bạn, shop xin gửi thông tin chi tiết:\n\n{best_chunk}\n\n👉 Bạn cần shop hỗ trợ tư vấn thêm chi tiết nào nữa không ạ? Bạn cứ nhắn thoải mái nhé!"
        else:
            return "Dạ cảm ơn bạn đã quan tâm đến shop ạ! Dạ câu hỏi của bạn hiện chưa có sẵn trong danh mục hướng dẫn nhanh. Shop đã ghi nhận tin nhắn và tư vấn viên trực tiếp sẽ nhắn lại cho bạn ngay sau ít phút nhé ạ! ❤️"
