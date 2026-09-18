# Facebook Messenger AI Chatbot (RAG từ PDF + SQLite Review Dashboard)

Hệ thống AI Chatbot tự động trả lời tin nhắn Facebook Messenger của khách hàng dựa trên file tài liệu / PDF bạn cung cấp, đồng thời lưu trữ toàn bộ lịch sử vào database để Sếp review.

---

## 🌟 Tính Năng Chính
1. **Kết Nối Facebook Messenger Webhook**:
   - Endpoint: `/webhook` hỗ trợ đầy đủ `hub.verify_token`, `hub.challenge` và tiếp nhận sự kiện tin nhắn thời gian thực.
2. **Học & Trả Lời Dựa Trên Tài Liệu PDF (RAG Knowledge Engine)**:
   - Bạn chỉ cần thả file tài liệu (`.pdf`, `.md`, `.txt`) vào thư mục `docs/`.
   - AI sẽ tự động phân tích và chỉ trả lời đúng nội dung trong tài liệu (giá cả, địa chỉ, giờ làm việc, chính sách hoàn tiền...).
3. **Database Lưu Trữ Cuộc Trò Chuyện (SQLite)**:
   - Lưu trữ toàn bộ tin nhắn của khách và phản hồi của bot vào `fb_chatbot.db`.
4. **Sếp Review Center (`/dashboard`)**:
   - Giao diện trực quan xem danh sách khách hàng, số lượng tin nhắn, thời gian nhắn và nội dung chi tiết từng cuộc hội thoại.
5. **Giả Lập Chat Test (`/simulator`)**:
   - Khung chat mô phỏng Messenger thực tế để bạn test độ thông minh của bot ngay trên máy tính mà chưa cần gắn Webhook thật.

---

## 🚀 Cách Chạy & Trải Nghiệm Ngay

### 1. Truy cập Simulator để Chat thử với AI:
👉 **http://localhost:5006/simulator**
- Thử nhắn: *"Các gói dịch vụ giá bao nhiêu?"* hoặc *"Chính sách hoàn tiền thế nào?"*.
- AI sẽ tự động tra cứu file trong `docs/` và trả lời chuẩn xác.

### 2. Truy cập Dashboard để Sếp Review lịch sử:
👉 **http://localhost:5006/dashboard**
- Xem danh sách khách vừa nhắn tin, đọc lại toàn bộ cuộc hội thoại.

---

## 🔗 Cách Kết Nối Đến Facebook Fanpage Thật
1. Tạo một Facebook App trên [Meta for Developers](https://developers.facebook.com/).
2. Chọn sản phẩm **Messenger**.
3. Cài đặt Webhook:
   - **Callback URL:** `https://your-domain.com/webhook` *(Dùng ngrok hoặc Cloudflare Tunnel để đưa cổng 5006 ra Internet: `ngrok http 5006`)*.
   - **Verify Token:** `MY_SECURE_VERIFY_TOKEN_123` (hoặc cấu hình biến môi trường `FB_VERIFY_TOKEN`).
4. Lấy **Page Access Token** từ Fanpage của bạn và đặt vào biến môi trường:
   ```bash
   export FB_PAGE_ACCESS_TOKEN="EAA..."
   ```
5. Bật quyền `messages` và `messaging_postbacks` cho Webhook trên Page.
