#!/usr/bin/env python3
"""
SoDEX Bot - Phiên bản đơn giản không cần Telegram API
Chỉ cần nhập code thủ công
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from eth_account import Account

# Load environment variables
load_dotenv()

class SoDEXBot:
    def __init__(self):
        self.url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Load private keys
        private_keys = os.getenv('PRIVATE_KEY', '').split(',')
        self.wallets = []
        
        for key in private_keys:
            key = key.strip()
            if key and key != 'your_private_key_here':
                try:
                    account = Account.from_key(key)
                    self.wallets.append({
                        'key': key,
                        'address': account.address,
                        'used': False
                    })
                    print(f"✅ Loaded wallet: {account.address}")
                except Exception as e:
                    print(f"❌ Invalid private key: {key[:10]}... - {e}")
        
        if not self.wallets:
            print("❌ Không có ví hợp lệ nào!")
            exit(1)
        
        print(f"🎯 Đã load {len(self.wallets)} ví")

    def verify_code(self, code, wallet):
        """Verify referral code với một wallet"""
        payload = {
            "referralCode": code,
            "walletAddress": wallet['address']
        }
        
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=10
            )
            result = response.json()
            
            if result.get("code") == 20003:
                print(f"[USED]     ➤ {code} - {wallet['address'][:10]}... (ĐÃ SỬ DỤNG)")
                return "used"
            elif result.get("code") == 20002:
                print(f"[INVALID]  ➤ {code} - {wallet['address'][:10]}... (KHÔNG TỒN TẠI)")
                return "invalid"
            else:
                print(f"[SUCCESS ✅] ➤ {code} - {wallet['address']} | RESPONSE: {result}")
                with open("success.txt", "a") as f:
                    f.write(f"{code} - {wallet['address']} - {result}\n")
                return "success"
                
        except Exception as e:
            print(f"[ERROR] ➤ {code} - {wallet['address'][:10]}... | Error: {e}")
            return "error"

    def run_manual(self):
        """Chế độ nhập code thủ công"""
        print("\n🚀 CHẠY CHỂ ĐỘ THỦ CÔNG")
        print("Nhập 'quit' để thoát")
        print("=" * 40)
        
        while True:
            # Kiểm tra còn ví nào chưa dùng
            available_wallets = [w for w in self.wallets if not w['used']]
            if not available_wallets:
                print("❌ Tất cả ví đã được sử dụng!")
                break
            
            print(f"\n💼 Còn {len(available_wallets)} ví available")
            code = input("Nhập referral code (8 ký tự): ").strip()
            
            if code.lower() == 'quit':
                break
            
            if len(code) != 8:
                print("❌ Code phải có đúng 8 ký tự!")
                continue
            
            # Lấy ví đầu tiên chưa dùng
            wallet = available_wallets[0]
            result = self.verify_code(code, wallet)
            
            if result == "success":
                wallet['used'] = True
                print(f"🎉 Thành công! Ví {wallet['address'][:10]}... đã được verify")
            elif result in ["used", "invalid"]:
                print("🔄 Thử ví tiếp theo...")

if __name__ == "__main__":
    bot = SoDEXBot()
    bot.run_manual()
