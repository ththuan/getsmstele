"""
SODEX Auto Verify Tool - Tích hợp hoàn chỉnh
Tự động theo dõi Telegram và verify referral codes
"""
import os
import time
import threading
from telegram_monitor import TelegramMonitor
from main import SodexAutoVerify

class SodexAutoBot:
    def __init__(self):
        self.sodex = SodexAutoVerify()
        self.telegram = None
        self.processed_codes = set()
        
        # Load config từ .env
        self.load_telegram_config()
    
    def load_telegram_config(self):
        """Load cấu hình Telegram từ .env"""
        # Load từ file .env
        bot_token = None
        chat_id = None
        
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TELEGRAM_BOT_TOKEN='):
                        bot_token = line.split('=', 1)[1].strip().strip('"\'')
                    elif line.startswith('TELEGRAM_CHAT_ID='):
                        chat_id = line.split('=', 1)[1].strip().strip('"\'')
        
        # Fallback to environment variables
        if not bot_token:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not chat_id:
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if bot_token and chat_id and bot_token != 'your_telegram_bot_token_here':
            self.telegram = TelegramMonitor(bot_token, chat_id)
            print(f"✅ Telegram config loaded - Chat: {chat_id}")
        else:
            print("⚠️  Telegram config chưa được setup (sẽ chỉ chạy manual mode)")
    
    def handle_new_code(self, code):
        """Xử lý code mới từ Telegram"""
        if code in self.processed_codes:
            print(f"⏭️  Code {code} đã được xử lý, bỏ qua...")
            return
        
        self.processed_codes.add(code)
        
        print(f"\n🚀 Xử lý code mới từ Telegram: {code}")
        self.sodex.verify_code(code)
        
        # Lưu code đã xử lý
        with open("processed.txt", "a", encoding='utf-8') as f:
            f.write(f"{code}\n")
    
    def run_auto_mode(self):
        """Chạy chế độ tự động với Telegram"""
        if not self.telegram:
            print("❌ Telegram chưa được cấu hình!")
            return False
        
        print("="*60)
        print("🤖 CHẠY CHẾ ĐỘ TỰ ĐỘNG - THEO DÕI TELEGRAM")
        print("="*60)
        print(f"👛 Wallet: {self.sodex.wallet_address}")
        print(f"🎯 Target URL: {self.sodex.url}")
        print(f"📱 Telegram Chat: {self.telegram.chat_id}")
        print("="*60)
        
        try:
            # Bắt đầu theo dõi Telegram
            monitor_thread = self.telegram.start_monitoring(self.handle_new_code)
            
            print("✅ Bot đang chạy... Nhấn Ctrl+C để dừng")
            
            # Giữ cho main thread chạy
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🔴 Dừng bot...")
            self.telegram.running = False
            return True
    
    def run_manual_mode(self):
        """Chạy chế độ manual như cũ"""
        print("="*60)
        print("🎯 SODEX AUTO VERIFY TOOL - MANUAL MODE")
        print("="*60)
        
        print("\nChọn chế độ:")
        print("1. Load codes từ file")
        print("2. Generate random codes")
        print("3. Test một code cụ thể")
        print("4. Brute force với pattern")
        
        choice = input("\nLựa chọn (1-4): ").strip()
        
        if choice == "1":
            filename = input("Nhập tên file chứa codes (mặc định: codes.txt): ").strip()
            if not filename:
                filename = "codes.txt"
            
            codes = self.sodex.load_codes_from_file(filename)
            if codes:
                threads = int(input("Số threads (mặc định 50): ") or "50")
                self.sodex.run_brute_force(codes, threads)
        
        elif choice == "2":
            count = int(input("Số codes generate (mặc định 1000): ") or "1000")
            threads = int(input("Số threads (mặc định 50): ") or "50")
            
            print(f"\n🔄 Generating {count} random codes...")
            codes = self.sodex.generate_random_codes(count)
            self.sodex.run_brute_force(codes, threads)
        
        elif choice == "3":
            code = input("Nhập code cần test: ").strip().upper()
            if len(code) == 8:
                print(f"\n🔍 Testing code: {code}")
                self.sodex.verify_code(code)
            else:
                print("❌ Code phải có đúng 8 ký tự")
        
        elif choice == "4":
            self.run_pattern_brute_force()
        
        else:
            print("❌ Lựa chọn không hợp lệ")
    
    def run_pattern_brute_force(self):
        """Brute force theo pattern cụ thể"""
        print("\n🎯 Pattern Brute Force Mode")
        print("Ví dụ patterns:")
        print("- ABCD**** (4 ký tự đầu cố định)")
        print("- ****1234 (4 ký tự cuối cố định)")
        print("- AB**CD** (mix cố định và random)")
        
        pattern = input("\nNhập pattern (* = random): ").strip().upper()
        
        if len(pattern) != 8 or '*' not in pattern:
            print("❌ Pattern phải có 8 ký tự và chứa ít nhất 1 dấu *")
            return
        
        count = int(input("Số codes generate từ pattern (mặc định 1000): ") or "1000")
        threads = int(input("Số threads (mặc định 50): ") or "50")
        
        codes = self.generate_pattern_codes(pattern, count)
        print(f"\n🔄 Generated {len(codes)} codes từ pattern: {pattern}")
        
        self.sodex.run_brute_force(codes, threads)
    
    def generate_pattern_codes(self, pattern, count):
        """Generate codes theo pattern"""
        import random
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        codes = set()
        
        while len(codes) < count:
            code = ""
            for char in pattern:
                if char == '*':
                    code += random.choice(chars)
                else:
                    code += char
            
            # Đảm bảo không phải toàn số hoặc toàn chữ
            if not (code.isdigit() or code.isalpha()):
                codes.add(code)
        
        return list(codes)

def main():
    print("="*60)
    print("🤖 SODEX AUTO VERIFY BOT")
    print("="*60)
    
    bot = SodexAutoBot()
    
    if bot.telegram:
        print("\nChọn chế độ:")
        print("1. 🤖 Auto Mode (Theo dõi Telegram)")
        print("2. 🎯 Manual Mode (Brute force thủ công)")
        
        choice = input("\nLựa chọn (1-2): ").strip()
        
        if choice == "1":
            bot.run_auto_mode()
        elif choice == "2":
            bot.run_manual_mode()
        else:
            print("❌ Lựa chọn không hợp lệ")
    else:
        # Chỉ có manual mode nếu Telegram chưa setup
        bot.run_manual_mode()

if __name__ == "__main__":
    main()
