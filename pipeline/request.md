# YÊU CẦU DỰ ÁN (USER REQUEST)

## Mục tiêu
Xây dựng một hệ thống **Facebook Messenger AI Chatbot** thông minh:
1. **Kết nối Facebook Messenger**: Nhận tin nhắn qua Webhook từ Fanpage Facebook của bạn.
2. **AI Trả lời thông minh dựa trên file PDF (RAG - Knowledge Base)**:
   - Cho phép bạn đưa vào các file tài liệu PDF (chính sách, bảng giá, FAQ, giới thiệu sản phẩm/dịch vụ).
   - Chatbot tự động bóc tách kiến thức và chỉ trả lời đúng phạm vi thông tin có trong tài liệu.
3. **Lưu trữ toàn bộ hội thoại vào Cơ sở dữ liệu (SQLite)**:
   - Lưu thông tin người gửi (sender_id, tên nếu có), tin nhắn của khách, câu trả lời của bot, thời gian gửi.
4. **Dashboard Đơn Giản Cho Sếp Review Hội Thoại**:
   - Giao diện web trực quan để bạn vào đọc lại toàn bộ lịch sử chat giữa khách và bot bất kỳ lúc nào.
   - Thống kê số lượng khách nhắn, các chủ đề khách quan tâm nhiều nhất.
5. **Chế độ Giả Lập Chat Test (Simulator)**:
   - Cho phép bạn test thử ngay trên trình duyệt mà không cần phải kết nối webhook Facebook thật ngay lập tức.
