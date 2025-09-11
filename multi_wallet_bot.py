"""
SODEX Multi-Wallet Auto Verify Bot
Hỗ trợ nhiều ví, check liên tục, loại bỏ ví đã dùng
"""
import os
import json
import time
import requests
import threading
from dotenv import load_dotenv
from queue import Queue
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

class WalletManager:
    def __init__(self):
        self.wallets_file = "wallets.json"
        self.load_wallets()
        self.lock = threading.Lock()
    
    def load_wallets(self):
        """Load wallets from file"""
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
        """Save wallets to file"""
        data = {
            'available': self.available_wallets,
            'used': self.used_wallets,
            'reserved': self.reserved_wallets
        }
        with open(self.wallets_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_available_wallets(self):
        """Get list of available wallets"""
        return [w for w in self.available_wallets if w not in self.reserved_wallets]
    
    def reserve_wallet(self, wallet_address):
        """Temporarily reserve a wallet"""
        if wallet_address not in self.reserved_wallets:
            self.reserved_wallets.append(wallet_address)
    
    def release_wallet(self, wallet_address):
        """Release a reserved wallet"""
        if wallet_address in self.reserved_wallets:
            self.reserved_wallets.remove(wallet_address)
    
    def mark_wallet_used(self, wallet_address):
        """Mark wallet as permanently used"""
        if wallet_address in self.available_wallets:
            self.available_wallets.remove(wallet_address)
        if wallet_address in self.reserved_wallets:
            self.reserved_wallets.remove(wallet_address)
        if wallet_address not in self.used_wallets:
            self.used_wallets.append(wallet_address)
        self.save_wallets()
        print(f"💰 Wallet marked as used: {wallet_address[:10]}...")
    
    def add_wallet(self, private_key):
        """Add new wallet from private key"""
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
        """Show wallet status"""
        print(f"\n📊 WALLET STATUS:")
        print(f"Available: {len(self.available_wallets)}")
        print(f"Used: {len(self.used_wallets)}")
        print(f"Reserved: {len(self.reserved_wallets)}")
        
        print(f"\n💰 Available Wallets:")
        for i, wallet in enumerate(self.available_wallets[:5], 1):
            status = "(RESERVED)" if wallet in self.reserved_wallets else ""
            print(f"  {i}. {wallet[:10]}...{wallet[-6:]} {status}")
        if len(self.available_wallets) > 5:
            print(f"  ... and {len(self.available_wallets) - 5} more")

class VerifyAPI:
    def __init__(self):
        self.url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def verify_code(self, code, wallet_address):
        """Verify referral code with wallet address"""
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
            
            # Process response based on code
            if result.get("code") == 20003:
                return {"success": False, "message": "Code đã được sử dụng", "code": 20003}
            elif result.get("code") == 20002:
                return {"success": False, "message": "Code không tồn tại", "code": 20002}
            elif result.get("code") == 0 or result.get("success"):
                return {"success": True, "message": "Verify thành công!", "data": result}
            else:
                return {"success": False, "message": f"Lỗi khác: {result}", "code": result.get("code")}
                
        except Exception as e:
            return {"success": False, "message": f"Lỗi kết nối: {e}"}

class TelegramMonitor:
    def __init__(self):
        self.codes = []
        self.last_check = 0
    
    def get_new_codes(self):
        """Simulate getting codes from Telegram - replace with real implementation"""
        # Tạm thời return empty, bạn sẽ tích hợp Telegram API thật ở đây
        import random
        
        # Simulate random codes for testing
        if random.random() < 0.1:  # 10% chance of new code
            test_codes = ["ABC12345", "DEF67890", "GHI13579", "JKL24680"]
            return [random.choice(test_codes)]
        return []

class MultiWalletBot:
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.verify_api = VerifyAPI()
        self.telegram_monitor = TelegramMonitor()
        self.running = True
        self.code_queue = Queue()
        self.processed_codes = set()
        self.lock = threading.Lock()
        
        # Stats
        self.total_processed = 0
        self.successful_verifies = 0
        
    def start(self):
        print("🚀 Starting Multi-Wallet Auto Verify Bot...")
        
        # Check if we have wallets
        available_wallets = self.wallet_manager.get_available_wallets()
        if not available_wallets:
            print("❌ No available wallets! Please add wallets first.")
            return
        
        print(f"💰 Loaded {len(available_wallets)} available wallets")
        self.wallet_manager.show_status()
        
        # Start threads
        threads = []
        
        # Telegram monitoring thread
        telegram_thread = threading.Thread(target=self.monitor_telegram)
        telegram_thread.daemon = True
        threads.append(telegram_thread)
        
        # Multiple worker threads
        num_workers = min(3, len(available_wallets))  # Max 3 workers or number of wallets
        for i in range(num_workers):
            worker_thread = threading.Thread(target=self.worker, args=(i,))
            worker_thread.daemon = True
            threads.append(worker_thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        print(f"🔄 Started {num_workers} worker threads")
        print("📱 Monitoring for codes... Press Ctrl+C to stop")
        
        # Main monitoring loop
        try:
            while self.running:
                available_wallets = self.wallet_manager.get_available_wallets()
                
                if not available_wallets:
                    print("❌ No more available wallets! All wallets have been used.")
                    break
                
                # Print status every 10 seconds
                print(f"📊 Status: {len(available_wallets)} wallets | {self.code_queue.qsize()} codes queued | {self.successful_verifies} success")
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping bot...")
            self.running = False
    
    def monitor_telegram(self):
        """Monitor Telegram for new codes"""
        print("📱 Telegram monitor started...")
        
        while self.running:
            try:
                codes = self.telegram_monitor.get_new_codes()
                
                for code in codes:
                    # Validate code format (8 characters, mix of letters and numbers)
                    if len(code) == 8 and code.isalnum() and not code.isdigit() and not code.isalpha():
                        with self.lock:
                            if code not in self.processed_codes:
                                self.code_queue.put(code)
                                self.processed_codes.add(code)
                                print(f"🆕 New valid code queued: {code}")
                
                time.sleep(0.5)  # Check every 0.5 seconds
                
            except Exception as e:
                print(f"❌ Telegram monitor error: {e}")
                time.sleep(1)
    
    def worker(self, worker_id):
        """Worker thread to process codes quickly"""
        print(f"👷 Worker {worker_id} started")
        
        while self.running:
            try:
                # Get code from queue
                code = self.code_queue.get(timeout=1)
                
                print(f"🔍 Worker {worker_id}: Processing {code}")
                success = self.process_code_fast(code, worker_id)
                
                with self.lock:
                    self.total_processed += 1
                    if success:
                        self.successful_verifies += 1
                
                self.code_queue.task_done()
                
            except:
                continue  # Queue timeout, continue
    
    def process_code_fast(self, code, worker_id):
        """Process code with fastest available wallet"""
        wallet_address = None
        
        # Get and reserve wallet atomically
        with self.lock:
            available_wallets = self.wallet_manager.get_available_wallets()
            
            if not available_wallets:
                print(f"❌ Worker {worker_id}: No wallets available for {code}")
                return False
            
            # Get first available wallet and reserve it
            wallet_address = available_wallets[0]
            self.wallet_manager.reserve_wallet(wallet_address)
        
        try:
            # Quick verify attempt
            result = self.verify_api.verify_code(code, wallet_address)
            
            with self.lock:
                if result['success']:
                    print(f"✅ SUCCESS Worker {worker_id}: {code} ← {wallet_address[:10]}...")
                    
                    # Mark wallet as used permanently
                    self.wallet_manager.mark_wallet_used(wallet_address)
                    
                    # Log success
                    with open("success.txt", "a", encoding='utf-8') as f:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"{timestamp} | {code} | {wallet_address}\n")
                    
                    return True
                    
                else:
                    # Handle different error codes
                    if result.get('code') == 20003:
                        print(f"⚠️ Worker {worker_id}: {code} already used")
                        # Log used codes
                        with open("used.txt", "a", encoding='utf-8') as f:
                            f.write(f"{code}\n")
                    elif result.get('code') == 20002:
                        print(f"⚠️ Worker {worker_id}: {code} invalid")
                        with open("invalid.txt", "a", encoding='utf-8') as f:
                            f.write(f"{code}\n")
                    else:
                        print(f"❌ Worker {worker_id}: {code} failed - {result['message']}")
                    
                    # Release wallet for reuse
                    self.wallet_manager.release_wallet(wallet_address)
                    return False
                    
        except Exception as e:
            print(f"❌ Worker {worker_id} error: {e}")
            with self.lock:
                if wallet_address:
                    self.wallet_manager.release_wallet(wallet_address)
            return False
    
    def add_wallets_interactive(self):
        """Interactive wallet addition"""
        print("\n💰 ADD WALLETS")
        print("Enter private keys (one per line, empty line to finish):")
        
        while True:
            private_key = input("Private Key: ").strip()
            if not private_key:
                break
            
            if self.wallet_manager.add_wallet(private_key):
                print("✅ Wallet added successfully!")
            
        self.wallet_manager.show_status()

def main():
    print("=== SODEX MULTI-WALLET AUTO VERIFY ===")
    print("1. 🚀 Start Bot")
    print("2. 💰 Add Wallets") 
    print("3. 📊 Show Wallet Status")
    print("4. 🧪 Test API")
    print("5. 🗑️ Reset Used Wallets")
    
    choice = input("\nChoose option: ").strip()
    
    bot = MultiWalletBot()
    
    if choice == "1":
        bot.start()
    elif choice == "2":
        bot.add_wallets_interactive()
    elif choice == "3":
        bot.wallet_manager.show_status()
    elif choice == "4":
        # Test API
        print("🧪 Testing API...")
        result = bot.verify_api.verify_code("TEST1234", "0x1234567890123456789012345678901234567890")
        print(f"Result: {result}")
    elif choice == "5":
        # Reset used wallets
        confirm = input("⚠️ Reset all used wallets to available? (y/N): ").lower()
        if confirm == 'y':
            bot.wallet_manager.available_wallets.extend(bot.wallet_manager.used_wallets)
            bot.wallet_manager.used_wallets = []
            bot.wallet_manager.save_wallets()
            print("✅ All wallets reset to available!")
        else:
            print("❌ Reset cancelled")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
