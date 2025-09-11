"""
Module theo dõi Telegram để lấy referral codes
"""
import requests
import re
import time
import threading
from datetime import datetime

class TelegramMonitor:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.last_update_id = 0
        self.running = False
        
    def get_updates(self):
        """Lấy tin nhắn mới từ Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'limit': 100,
                'timeout': 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi Telegram API: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi kết nối Telegram: {e}")
            return None
    
    def extract_codes(self, text):
        """Trích xuất codes 8 ký tự từ text"""
        # Pattern: 8 ký tự gồm chữ và số, không phải toàn chữ hoặc toàn số
        pattern = r'\b[A-Z0-9]{8}\b'
        matches = re.findall(pattern, text.upper())
        
        valid_codes = []
        for code in matches:
            # Loại bỏ code toàn số hoặc toàn chữ
            if not (code.isdigit() or code.isalpha()):
                valid_codes.append(code)
        
        return valid_codes
    
    def monitor(self, callback=None):
        """Theo dõi Telegram liên tục"""
        print(f"🔍 Bắt đầu theo dõi Telegram chat: {self.chat_id}")
        self.running = True
        
        while self.running:
            try:
                updates = self.get_updates()
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            message = update['message']
                            
                            # Kiểm tra có phải từ chat target không
                            chat_id = str(message['chat']['id'])
                            if chat_id == self.chat_id or f"-{chat_id}" == self.chat_id:
                                
                                text = message.get('text', '')
                                timestamp = datetime.fromtimestamp(message['date']).strftime('%H:%M:%S')
                                sender = message.get('from', {}).get('first_name', 'Unknown')
                                
                                codes = self.extract_codes(text)
                                
                                if codes:
                                    print(f"\n📨 [{timestamp}] {sender}: {text[:50]}...")
                                    for code in codes:
                                        print(f"🎯 Tìm thấy code: {code}")
                                        
                                        # Callback để xử lý code
                                        if callback:
                                            callback(code)
                
                time.sleep(2)  # Delay để tránh spam API
                
            except KeyboardInterrupt:
                print("\n🔴 Dừng theo dõi Telegram...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Lỗi monitor: {e}")
                time.sleep(5)
    
    def start_monitoring(self, callback=None):
        """Bắt đầu theo dõi trong thread riêng"""
        monitor_thread = threading.Thread(target=self.monitor, args=(callback,))
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread

def test_telegram():
    """Test Telegram monitor với token demo"""
    print("🔍 Test Telegram Pattern Extraction...")
    
    # Test messages
    test_messages = [
        "Hey everyone! Just a quick reminder about how we share referral codes ABC12345 and links in the community.",
        "I have code but only give ABCD1234 for you",
        "can u give me code XYZ98765",
        "Check this out: https://sodex.dev/ref/CODE123X",
        "My code is: BONUS789",  # Toàn chữ, sẽ bị loại
        "Use code: 12345678",    # Toàn số, sẽ bị loại
        "Valid codes: TEST1234, DEMO5678, WORK9ABC"
    ]
    
    monitor = TelegramMonitor("demo_token", "demo_chat")
    
    for msg in test_messages:
        codes = monitor.extract_codes(msg)
        if codes:
            print(f"📨 Message: {msg}")
            print(f"🎯 Extracted codes: {codes}")
            print("-" * 50)

if __name__ == "__main__":
    test_telegram()
