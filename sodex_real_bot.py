"""
SODEX MULTI-WALLET BOT with TELEGRAM INTEGRATION
Complete bot with multiple wallets, continuous check, remove used wallets, real Telegram integration
"""
import os
import json
import time
import requests
import threading
import asyncio
from dotenv import load_dotenv
from queue import Queue
from telegram_real import TelegramRealMonitor, run_telegram_monitor
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# load_dotenv()  # Tạm thời comment để tránh lỗi encoding

class WalletManager:
    def __init__(self):
        self.wallets_file = "wallets.json"
        self.load_wallets()
        self.lock = threading.Lock()
    
    def load_wallets(self):
        if os.path.exists(self.wallets_file):
            with open(self.wallets_file, 'r') as f:
                data = json.load(f)
                self.available_wallets = data.get('available', [])
                self.used_wallets = data.get('used', [])
                self.reserved_wallets = data.get('reserved', [])
        else:
            self.available_wallets = []
            self.used_wallets = []
            self.reserved_wallets = []
            self.save_wallets()
    
    def save_wallets(self):
        data = {
            'available': self.available_wallets,
            'used': self.used_wallets,
            'reserved': self.reserved_wallets
        }
        with open(self.wallets_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_available_wallets(self):
        return [w for w in self.available_wallets if w not in self.reserved_wallets]
    
    def reserve_wallet(self, wallet_address):
        if wallet_address not in self.reserved_wallets:
            self.reserved_wallets.append(wallet_address)
    
    def release_wallet(self, wallet_address):
        if wallet_address in self.reserved_wallets:
            self.reserved_wallets.remove(wallet_address)
    
    def mark_wallet_used(self, wallet_address):
        if wallet_address in self.available_wallets:
            self.available_wallets.remove(wallet_address)
        if wallet_address in self.reserved_wallets:
            self.reserved_wallets.remove(wallet_address)
        if wallet_address not in self.used_wallets:
            self.used_wallets.append(wallet_address)
        self.save_wallets()
        print(f"💰 Wallet marked as used: {wallet_address[:10]}...")
    
    def add_wallet(self, private_key):
        try:
            from eth_account import Account
            account = Account.from_key(private_key)
            wallet_address = account.address
            
            if wallet_address not in self.available_wallets and wallet_address not in self.used_wallets:
                self.available_wallets.append(wallet_address)
                self.save_wallets()
                print(f"✅ Added wallet: {wallet_address}")
                return True
            else:
                print(f"⚠️ Wallet already exists: {wallet_address}")
                return False
        except Exception as e:
            print(f"❌ Invalid private key: {e}")
            return False
    
    def show_status(self):
        print(f"\n📊 WALLET STATUS:")
        print(f"Available: {len(self.available_wallets)}")
        print(f"Used: {len(self.used_wallets)}")
        print(f"Reserved: {len(self.reserved_wallets)}")

class VerifyAPI:
    def __init__(self):
        self.url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def verify_code(self, code, wallet_address):
        payload = {
            "referralCode": code,
            "walletAddress": wallet_address
        }
        
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=10,
                verify=False
            )
            result = response.json()
            
            if result.get("code") == 20003:
                return {"success": False, "message": "Code already used", "code": 20003}
            elif result.get("code") == 20002:
                return {"success": False, "message": "Code không tồn tại", "code": 20002}
            elif result.get("code") == 0 or result.get("success"):
                return {"success": True, "message": "Verify successful!", "data": result}
            else:
                return {"success": False, "message": f"Lỗi khác: {result}", "code": result.get("code")}
                
        except Exception as e:
            return {"success": False, "message": f"Lỗi kết nối: {e}"}

class SodexRealBot:
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.verify_api = VerifyAPI()
        self.telegram_monitor = None
        self.running = True
        self.code_queue = Queue()
        self.processed_codes = set()
        self.lock = threading.Lock()
        
        # Stats
        self.total_processed = 0
        self.successful_verifies = 0
        
        # Load Telegram config
        self.load_telegram_config()
    
    def load_telegram_config(self):
        """Load Telegram configuration from .env"""
        # Hardcode config để test
        self.api_id = "21208198"
        self.api_hash = "788973d196fc50bc1653732c1b9a6089"
        self.phone = "+84944300848"
        self.group_id = "1002509849601_205194"
        
        print(f"📱 Telegram Config:")
        print(f"API ID: {self.api_id}")
        print(f"Phone: {self.phone}")
        print(f"Group ID: {self.group_id}")
    
    def start(self):
        """Start the complete bot"""
        print("🚀 Starting SODEX Real-Time Multi-Wallet Bot...")
        
        # Check wallets
        available_wallets = self.wallet_manager.get_available_wallets()
        if not available_wallets:
            print("❌ No available wallets! Please add wallets first.")
            return
        
        print(f"💰 Loaded {len(available_wallets)} available wallets")
        
        # Check Telegram config
        if not all([self.api_id, self.api_hash, self.phone, self.group_id]) or \
           'your_' in str(self.api_id) or 'your_' in str(self.api_hash):
            print("❌ Missing Telegram configuration in .env file!")
            print("Please set: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, TELEGRAM_GROUP_ID")
            print("Use option 5 - Setup Telegram for instructions")
            return
        
        try:
            group_id_int = int(self.group_id)
        except ValueError:
            print("❌ Invalid TELEGRAM_GROUP_ID format!")
            print("Group ID should be a number like: -1001234567890")
            return
        
        # Initialize Telegram monitor
        self.telegram_monitor = TelegramRealMonitor(
            self.api_id, 
            self.api_hash, 
            self.phone, 
            group_id_int
        )
        
        # Start threads
        threads = []
        
        # Telegram monitoring thread
        telegram_thread = threading.Thread(target=run_telegram_monitor, args=(self.telegram_monitor,))
        telegram_thread.daemon = True
        threads.append(telegram_thread)
        
        # Code processing thread
        process_thread = threading.Thread(target=self.monitor_codes)
        process_thread.daemon = True
        threads.append(process_thread)
        
        # Worker threads
        num_workers = min(3, len(available_wallets))
        for i in range(num_workers):
            worker_thread = threading.Thread(target=self.worker, args=(i,))
            worker_thread.daemon = True
            threads.append(worker_thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        print(f"🔄 Started {num_workers} worker threads")
        print("📱 Real-time Telegram monitoring active...")
        print("⚡ Rapid code processing enabled...")
        print("Press Ctrl+C to stop")
        
        # Main monitoring loop
        try:
            while self.running:
                available_wallets = self.wallet_manager.get_available_wallets()
                
                if not available_wallets:
                    print("❌ No more available wallets! All wallets have been used.")
                    break
                
                # Status every 30 seconds
                print(f"📊 Status: {len(available_wallets)} wallets | {self.code_queue.qsize()} codes queued | {self.successful_verifies} success")
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping bot...")
            self.running = False
            if self.telegram_monitor:
                self.telegram_monitor.stop()
    
    def monitor_codes(self):
        """Monitor codes from Telegram"""
        print("🔍 Code monitor started...")
        
        while self.running:
            try:
                if self.telegram_monitor:
                    codes = self.telegram_monitor.get_new_codes()
                    
                    for code in codes:
                        with self.lock:
                            if code not in self.processed_codes:
                                self.code_queue.put(code)
                                self.processed_codes.add(code)
                                print(f"🆕 URGENT: New code queued: {code}")
                
                time.sleep(0.1)  # Very fast checking - 10 times per second
                
            except Exception as e:
                print(f"❌ Code monitor error: {e}")
                time.sleep(1)
    
    def worker(self, worker_id):
        """High-speed worker for instant processing"""
        print(f"⚡ Speed Worker {worker_id} started")
        
        while self.running:
            try:
                code = self.code_queue.get(timeout=1)
                
                print(f"🚀 Worker {worker_id}: PROCESSING {code} (URGENT)")
                success = self.process_code_instant(code, worker_id)
                
                with self.lock:
                    self.total_processed += 1
                    if success:
                        self.successful_verifies += 1
                
                self.code_queue.task_done()
                
            except:
                continue
    
    def process_code_instant(self, code, worker_id):
        """Instant code processing - fastest possible"""
        wallet_address = None
        
        # Get wallet instantly
        with self.lock:
            available_wallets = self.wallet_manager.get_available_wallets()
            
            if not available_wallets:
                print(f"❌ Worker {worker_id}: No wallets for {code}")
                return False
            
            wallet_address = available_wallets[0]
            self.wallet_manager.reserve_wallet(wallet_address)
        
        try:
            # Instant verify
            result = self.verify_api.verify_code(code, wallet_address)
            
            with self.lock:
                if result['success']:
                    print(f"🎉 SUCCESS Worker {worker_id}: {code} ← {wallet_address[:10]}...")
                    
                    # Mark wallet as used
                    self.wallet_manager.mark_wallet_used(wallet_address)
                    
                    # Log success with full details
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    success_line = f"{timestamp} | {code} | {wallet_address} | Worker-{worker_id}\n"
                    
                    with open("success.txt", "a", encoding='utf-8') as f:
                        f.write(success_line)
                    
                    # Also log to console
                    print(f"💰 PROFIT: {code} successfully claimed!")
                    
                    return True
                    
                else:
                    # Handle errors efficiently
                    if result.get('code') == 20003:
                        print(f"⚠️ Worker {worker_id}: {code} already used")
                        with open("used.txt", "a", encoding='utf-8') as f:
                            f.write(f"{code}\n")
                    elif result.get('code') == 20002:
                        print(f"⚠️ Worker {worker_id}: {code} invalid")
                        with open("invalid.txt", "a", encoding='utf-8') as f:
                            f.write(f"{code}\n")
                    else:
                        print(f"❌ Worker {worker_id}: {code} failed - {result['message']}")
                    
                    # Release wallet instantly
                    self.wallet_manager.release_wallet(wallet_address)
                    return False
                    
        except Exception as e:
            print(f"❌ Worker {worker_id} error: {e}")
            with self.lock:
                if wallet_address:
                    self.wallet_manager.release_wallet(wallet_address)
            return False

def main():
    print("=== SODEX REAL-TIME MULTI-WALLET BOT ===")
    print("1. 🚀 Start Real-Time Bot")
    print("2. 💰 Add Wallets") 
    print("3. 📊 Show Wallet Status")
    print("4. 🧪 Test API")
    print("5. ⚙️ Setup Telegram")
    
    choice = input("\nChoose option: ").strip()
    
    if choice == "1":
        bot = SodexRealBot()
        bot.start()
    elif choice == "2":
        # Add wallets
        wallet_manager = WalletManager()
        print("\n💰 ADD WALLETS")
        print("Enter private keys (one per line, empty line to finish):")
        
        while True:
            private_key = input("Private Key: ").strip()
            if not private_key:
                break
            if wallet_manager.add_wallet(private_key):
                print("✅ Wallet added!")
        
        wallet_manager.show_status()
    elif choice == "3":
        WalletManager().show_status()
    elif choice == "4":
        # Test API
        api = VerifyAPI()
        result = api.verify_code("TEST1234", "0x1234567890123456789012345678901234567890")
        print(f"API Test Result: {result}")
    elif choice == "5":
        # Setup Telegram
        print("\n⚙️ TELEGRAM SETUP")
        print("1. Go to https://my.telegram.org/auth")
        print("2. Login and go to 'API Development tools'")
        print("3. Create an app and get API ID and API Hash")
        print("4. Add your phone number and group chat ID to .env")
        print("\nRequired .env variables:")
        print("TELEGRAM_API_ID=your_api_id")
        print("TELEGRAM_API_HASH=your_api_hash")
        print("TELEGRAM_PHONE=your_phone_number")
        print("TELEGRAM_GROUP_ID=group_chat_id")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
