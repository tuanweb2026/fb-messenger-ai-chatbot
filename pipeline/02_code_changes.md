# 02_CODE_CHANGES.MD - BÁO CÁO MÃ NGUỒN CHATBOT
**Tác giả:** AGENT CODER
**Trạng thái:** HOÀN THÀNH

---

1. `src/db.py`: Tạo database SQLite `fb_chatbot.db` với 3 bảng: `conversations`, `messages`, `knowledge_chunks`.
2. `src/pdf_knowledge.py`: Bộ máy nạp tài liệu từ thư mục `docs/` (hỗ trợ .md, .txt, .pdf) và truy xuất câu trả lời tự động.
3. `src/fb_service.py`: Xử lý gửi tin nhắn Messenger qua Facebook Graph API.
4. `src/server.py`: Webhook tiếp nhận tin nhắn từ Facebook và dashboard server.
5. Giao diện:
   - `templates/dashboard.html`: Nơi "Sếp" xem lại toàn bộ lịch sử chat giữa khách và AI.
   - `templates/simulator.html`: Giả lập Messenger để test thực tế ngay trên máy tính.
