import requests
import json
import threading
import time
import os
import random
from eth_account import Account
import warnings

# Tắt warning SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class SodexAutoVerify:
    def __init__(self):
        self.url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
        self.wallet_address = None
        self.private_key = None
        self.lock = threading.Lock()
        self.found_valid = False
        
        # Headers mặc định
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Content-Type': 'application/json',
            'Origin': 'https://testnet.sodex.dev',
            'Referer': 'https://testnet.sodex.dev/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        
        self.setup_wallet()
    
    def setup_wallet(self):
        """Setup wallet từ private key"""
        try:
            # Đọc private key từ .env hoặc input
            if os.path.exists('.env'):
                with open('.env', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('PRIVATE_KEY='):
                            self.private_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
            
            if not self.private_key:
                self.private_key = input("Nhập private key: ").strip()
            
            # Tạo wallet address từ private key
            if self.private_key.startswith('0x'):
                self.private_key = self.private_key[2:]
            
            account = Account.from_key(self.private_key)
            self.wallet_address = account.address
            
            print(f"✅ Wallet setup thành công: {self.wallet_address}")
            
        except Exception as e:
            print(f"❌ Lỗi setup wallet: {e}")
            exit(1)
    
    def verify_code(self, code, proxy=None):
        """Verify một referral code"""
        payload = {
            "referralCode": code,
            "walletAddress": self.wallet_address
        }
        
        try:
            res = requests.post(
                self.url,
                headers=self.headers,
                data=json.dumps(payload),
                proxies=proxy,
                timeout=10,
                verify=False
            )
            result = res.json()
            
            with self.lock:
                # Nếu đã tìm thấy code hợp lệ thì stop
                if self.found_valid:
                    return
                
                # Nếu là mã đã dùng
                if result.get("code") == 20003:
                    print(f"[USED]     ➤ {code} (ĐÃ SỬ DỤNG)")
                    with open("used.txt", "a", encoding='utf-8') as f:
                        f.write(code + "\n")
                
                # Nếu là mã không tồn tại
                elif result.get("code") == 20002:
                    print(f"[INVALID]  ➤ {code} (KHÔNG TỒN TẠI)")
                    with open("used.txt", "a", encoding='utf-8') as f:
                        f.write(code + "\n")
                
                # Nếu là mã hợp lệ khác → GHI VÀ THOÁT
                else:
                    print(f"[FOUND ✅]  ➤ {code} | RESPONSE: {result}")
                    with open("valid.txt", "a", encoding='utf-8') as f:
                        f.write(f"{code} | {json.dumps(result)}\n")
                    print("🔴 Mã hợp lệ đã tìm thấy, dừng toàn bộ tool.")
                    self.found_valid = True
                    os._exit(0)  # Dừng toàn bộ threads ngay lập tức
                    
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT]  ➤ {code}")
        except Exception as e:
            print(f"[ERROR]    ➤ {code} | {str(e)}")
    
    def generate_random_codes(self, count=1000):
        """Generate random 8-character codes"""
        codes = []
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        
        for _ in range(count):
            # Generate code với ít nhất 1 chữ và 1 số
            code = ""
            for i in range(8):
                if i < 4:  # 4 ký tự đầu random
                    code += random.choice(chars)
                else:  # 4 ký tự sau đảm bảo có mix chữ số
                    if random.random() < 0.5:
                        code += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    else:
                        code += random.choice("0123456789")
            
            # Shuffle để random hơn
            code_list = list(code)
            random.shuffle(code_list)
            final_code = ''.join(code_list)
            
            # Đảm bảo không phải toàn số hoặc toàn chữ
            if not (final_code.isdigit() or final_code.isalpha()):
                codes.append(final_code)
        
        return codes
    
    def load_codes_from_file(self, filename):
        """Load codes từ file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                codes = [line.strip() for line in f if line.strip()]
            return codes
        except FileNotFoundError:
            print(f"❌ File {filename} không tồn tại")
            return []
    
    def run_brute_force(self, codes, max_threads=50):
        """Chạy brute force với nhiều threads"""
        print(f"🚀 Bắt đầu brute force với {len(codes)} codes, {max_threads} threads")
        print(f"🎯 Target URL: {self.url}")
        print(f"👛 Wallet: {self.wallet_address}")
        print("-" * 60)
        
        def worker():
            while codes and not self.found_valid:
                try:
                    code = codes.pop(0)
                    self.verify_code(code)
                    time.sleep(0.1)  # Delay nhỏ để tránh spam
                except IndexError:
                    break
        
        # Tạo và start threads
        threads = []
        for _ in range(min(max_threads, len(codes))):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Đợi threads hoàn thành
        for t in threads:
            t.join()
        
        if not self.found_valid:
            print("🔴 Đã test hết codes, không tìm thấy mã hợp lệ")

def main():
    print("="*60)
    print("🎯 SODEX AUTO VERIFY TOOL")
    print("="*60)
    
    bot = SodexAutoVerify()
    
    print("\nChọn chế độ:")
    print("1. Load codes từ file")
    print("2. Generate random codes")
    print("3. Test một code cụ thể")
    
    choice = input("\nLựa chọn (1-3): ").strip()
    
    if choice == "1":
        filename = input("Nhập tên file chứa codes (mặc định: codes.txt): ").strip()
        if not filename:
            filename = "codes.txt"
        
        codes = bot.load_codes_from_file(filename)
        if codes:
            threads = int(input("Số threads (mặc định 50): ") or "50")
            bot.run_brute_force(codes, threads)
    
    elif choice == "2":
        count = int(input("Số codes generate (mặc định 1000): ") or "1000")
        threads = int(input("Số threads (mặc định 50): ") or "50")
        
        print(f"\n🔄 Generating {count} random codes...")
        codes = bot.generate_random_codes(count)
        bot.run_brute_force(codes, threads)
    
    elif choice == "3":
        code = input("Nhập code cần test: ").strip().upper()
        if len(code) == 8:
            print(f"\n🔍 Testing code: {code}")
            bot.verify_code(code)
        else:
            print("❌ Code phải có đúng 8 ký tự")
    
    else:
        print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    main()
