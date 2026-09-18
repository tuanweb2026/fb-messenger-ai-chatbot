# 01_PLAN.MD - THIẾT KẾ HỆ THỐNG FACEBOOK AI CHATBOT + PDF KNOWLEDGE + REVIEW DASHBOARD
**Tác giả:** AGENT PLANNER
**Ngày tạo:** 2026-09-18

---

## 1. Kiến trúc Kỹ thuật
- **Ngôn ngữ & Framework:** Python Flask (hỗ trợ cả Webhook chuẩn Facebook Graph API và Giao diện Dashboard).
- **Cơ sở dữ liệu (Database):** SQLite (`fb_chatbot.db`) - nhẹ, độc lập, không cần cài server phức tạp.
- **Bộ máy Tri thức PDF (Knowledge Engine / RAG):**
  - Đọc và bóc tách các đoạn văn từ file PDF trong thư mục `docs/`.
  - Sử dụng thuật toán Semantic TF-IDF / Cosine Similarity (hoặc Embeddings) để truy xuất đoạn văn bản liên quan nhất khi khách hàng đặt câu hỏi, sau đó tổng hợp câu trả lời tự nhiên, thân thiện và chuẩn xác.
- **Cổng kết nối Facebook (Messenger Webhook):**
  - Endpoint `GET /webhook`: Dùng để xác minh Webhook với Facebook Meta (`hub.verify_token`, `hub.challenge`).
  - Endpoint `POST /webhook`: Nhận tin nhắn của khách hàng từ Facebook Messenger và gửi phản hồi tự động qua Facebook Graph API.
- **Giao diện Dashboard Review cho Sếp:**
  - Trang `/dashboard`: Hiển thị danh sách khách hàng, bộ lọc thời gian, xem chi tiết từng tin nhắn qua lại giữa khách và AI bot.
  - Trang `/simulator`: Giả lập Messenger ngay trên Web để bạn test bot trước khi gắn vào Fanpage.

## 2. Thiết kế Cơ sở dữ liệu SQLite
- `conversations`: id, sender_id, sender_name, started_at, last_message_at.
- `messages`: id, conversation_id, sender_id, sender_type ('user' or 'bot'), content, created_at.
- `knowledge_docs`: id, filename, content_chunk, updated_at.

## 3. Phân chia công việc cho Coder:
- `src/db.py`: Khởi tạo SQLite, hàm lưu tin nhắn, hàm lấy lịch sử cuộc trò chuyện.
- `src/pdf_knowledge.py`: Đọc file PDF, chunking, tìm kiếm thông tin liên quan và sinh câu trả lời.
- `src/fb_service.py`: Xử lý gửi tin nhắn lại cho Facebook qua Graph API.
- `src/server.py`: Khởi chạy Flask server, route webhook và dashboard.
- `templates/`: Giao diện Dashboard review và giao diện Simulator.
