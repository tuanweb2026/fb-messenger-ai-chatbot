import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import init_db, save_message, get_all_conversations, get_conversation_history
from src.pdf_knowledge import PDFKnowledgeEngine

class TestFacebookChatbot(unittest.TestCase):
    def setUp(self):
        init_db()
        PDFKnowledgeEngine.load_documents()

    def test_pdf_knowledge_query_price(self):
        # Khách hỏi giá
        reply = PDFKnowledgeEngine.query("Cho tôi hỏi giá các gói dịch vụ là bao nhiêu?")
        self.assertIn("500.000", reply)
        self.assertIn("1.200.000", reply)

    def test_pdf_knowledge_query_refund(self):
        # Khách hỏi hoàn tiền
        reply = PDFKnowledgeEngine.query("Chính sách hoàn tiền thế nào?")
        self.assertIn("hoàn tiền 100%", reply.lower())

    def test_save_and_retrieve_messages(self):
        test_sender = "user_test_fb_888"
        save_message(test_sender, "Anh Nam", "user", "Shop ở đâu vậy?")
        save_message(test_sender, "Anh Nam", "bot", "Địa chỉ tại Tòa nhà Bitexco...")

        history = get_conversation_history(test_sender)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['content'], "Shop ở đâu vậy?")
        self.assertEqual(history[1]['content'], "Địa chỉ tại Tòa nhà Bitexco...")

if __name__ == '__main__':
    unittest.main()
