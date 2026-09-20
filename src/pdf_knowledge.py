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
    def delete_all_files():
        """
        Xóa toàn bộ file trong thư mục docs/ và làm sạch database tri thức.
        """
        if os.path.exists(DOCS_DIR):
            for f in os.listdir(DOCS_DIR):
                if f.endswith('.txt') or f.endswith('.md') or f.endswith('.pdf'):
                    try:
                        os.remove(os.path.join(DOCS_DIR, f))
                    except Exception as e:
                        print(f"Error removing file {f}: {e}")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_chunks")
        conn.commit()
        conn.close()
        print("[Knowledge Base] Đã xóa toàn bộ tài liệu và làm sạch database.")

    @staticmethod
    def delete_single_file(filename):
        """
        Xóa 1 file cụ thể khỏi docs/ và cập nhật lại database.
        """
        filepath = os.path.join(DOCS_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            PDFKnowledgeEngine.load_documents()
            return True
        return False

    @staticmethod
    def query(user_question):
        """
        - Khi KHÔNG CÓ file tri thức (hoặc đã xóa hết): AI chỉ trả lời cơ bản, xã giao, lịch sự và xin thông tin liên hệ.
        - Khi ĐÃ NẠP file: AI dựa sát vào tài liệu để trả lời chi tiết, chuyên nghiệp.
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, content FROM knowledge_chunks")
        rows = cursor.fetchall()
        conn.close()
        
        # CHẾ ĐỘ 1: CHƯA CÓ HOẶC ĐÃ XÓA HẾT TÀI LIỆU -> CHỈ TRẢ LỜI CƠ BẢN
        if not rows:
            q_lower = user_question.lower()
            if any(greet in q_lower for greet in ['chào', 'hello', 'hi', 'alo', 'bạn ơi', 'shop ơi']):
                return "Dạ chào bạn ạ! Cảm ơn bạn đã nhắn tin cho shop. Hiện tại hệ thống chưa nạp tài liệu bảng giá chi tiết. Bạn cần tìm hiểu dịch vụ gì, có thể để lại Số Điện Thoại để nhân viên bên mình gọi tư vấn cụ thể cho bạn nhé ạ!"
            elif any(ask in q_lower for ask in ['giá', 'nhiêu', 'chi phí', 'bảng giá']):
                return "Dạ hiện tại bảng giá chi tiết đang được cập nhật ạ. Bạn vui lòng để lại Số Điện Thoại hoặc nhắn rõ dịch vụ bạn đang quan tâm, tư vấn viên bên mình sẽ liên hệ báo giá ưu đãi tốt nhất cho bạn ngay nhé ạ!"
            elif any(loc in q_lower for loc in ['ở đâu', 'địa chỉ', 'chi nhánh']):
                return "Dạ shop xin chào bạn ạ! Hiện thông tin địa chỉ cụ thể đang được đồng bộ. Bạn để lại SĐT hoặc khu vực bạn đang ở để shop hướng dẫn chi nhánh thuận tiện nhất cho bạn nhé ạ!"
            else:
                return "Dạ cảm ơn bạn đã quan tâm đến shop ạ! Tin nhắn của bạn đã được ghi nhận. Vì chưa có tài liệu hướng dẫn cụ thể cho câu hỏi này, bạn vui lòng để lại SĐT để bên mình hỗ trợ trực tiếp cho bạn nhé ạ! ❤️"

        # CHẾ ĐỘ 2: ĐÃ NẠP TÀI LIỆU -> TRẢ LỜI CHI TIẾT DỰA VÀO TÀI LIỆU
        keywords = [w for w in re.findall(r'\w+', user_question.lower()) if len(w) > 1]
        scored_chunks = []
        for r in rows:
            chunk = r['content']
            chunk_lower = chunk.lower()
            score = sum(2 if kw in chunk_lower else 0 for kw in keywords)
            for core in ['giá', 'bao nhiêu', 'chi phí', 'địa chỉ', 'ở đâu', 'hoàn tiền', 'bảo hành', 'hotline', 'giờ', 'thời gian', 'liên hệ', 'trả góp', 'nhổ', 'implant', 'niềng', 'khôn', 'sứ']:
                if core in user_question.lower() and core in chunk_lower:
                    score += 3
            if score > 0:
                scored_chunks.append((score, chunk, r['filename']))
                
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        if scored_chunks and scored_chunks[0][0] >= 2:
            best_chunk = scored_chunks[0][1]
            return f"Dạ chào bạn! Cảm ơn bạn đã nhắn tin cho shop ạ.\n\nVề thắc mắc của bạn, shop xin gửi thông tin chi tiết từ tài liệu chuyên môn:\n\n{best_chunk}\n\n👉 Bạn để lại Số Điện Thoại hoặc Khung giờ rảnh để shop hỗ trợ tư vấn kỹ hơn và xếp lịch ưu tiên cho bạn ngay nhé ạ! ❤️"
        else:
            return "Dạ cảm ơn bạn đã quan tâm đến shop ạ! Dạ nội dung câu hỏi của bạn hiện chưa được đề cập cụ thể trong tài liệu hướng dẫn có sẵn của shop. Bạn vui lòng để lại Số Điện Thoại, tư vấn viên trực tiếp sẽ liên hệ giải đáp chi tiết cho bạn ngay sau ít phút nhé ạ! ❤️"
