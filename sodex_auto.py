#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SODEX Auto Bot - Optimized Version
Auto monitor Telegram and verify referral codes
"""
import os
import json
import time
import requests
import threading
import asyncio
import urllib3
from datetime import datetime
from telethon import TelegramClient, events
from eth_account import Account

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SoDEXAutoBot:
    def __init__(self):
        # Load config from .env file or use defaults
        self.load_config()
        
        # API settings
        self.url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Load wallets
        self.load_wallets()
        self.lock = threading.Lock()
        self.success_count = 0
        
        print(f"🚀 SODEX Auto Bot Started")
        print(f"💰 Loaded {len(self.wallets)} wallets")
        print(f"📱 Monitoring Group: {self.group_id}")
    
    def load_config(self):
        """Load configuration from .env file or use defaults"""
        self.api_id = "21208198"
        self.api_hash = "788973d196fc50bc1653732c1b9a6089"  
        self.phone = "+84944300848"
        self.group_id = int("1002509849601")
        
        # Try to load from .env file
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('TELEGRAM_API_ID='):
                        self.api_id = line.split('=', 1)[1]
                    elif line.startswith('TELEGRAM_API_HASH='):
                        self.api_hash = line.split('=', 1)[1]
                    elif line.startswith('TELEGRAM_PHONE='):
                        self.phone = line.split('=', 1)[1]
                    elif line.startswith('TELEGRAM_GROUP_ID='):
                        self.group_id = int(line.split('=', 1)[1])
        except Exception as e:
            print(f"⚠️ Could not load config from .env: {e}")
            print("📱 Using default Telegram settings")
        
        print(f"📱 Using API ID: {self.api_id}")
        print(f"📞 Using Phone: {self.phone}")
        print(f"👥 Target Group ID: {self.group_id}")
    
    def load_wallets(self):
        """Load wallets from private keys in .env file"""
        self.wallets = []
        all_keys = []
        
        # Try to read PRIVATE_KEY from .env file with multiple encodings
        encodings = ['utf-8', 'utf-16', 'utf-8-sig', 'cp1252', 'latin1']
        
        for encoding in encodings:
            try:
                with open('.env', 'r', encoding=encoding) as f:
                    content = f.read()
                    for line in content.split('\n'):
                        line = line.strip()
                        if 'PRIVATE_KEY=' in line and not line.startswith('#'):
                            key_value = line.split('=', 1)[1]
                            keys = [k.strip() for k in key_value.split(',') if k.strip() and len(k.strip()) == 64]
                            all_keys.extend(keys)
                            print(f"📝 Loaded {len(keys)} private keys from .env (encoding: {encoding})")
                    break  # Success, stop trying other encodings
            except Exception as e:
                if encoding == encodings[-1]:  # Last encoding failed
                    print(f"⚠️ All encoding attempts failed. Last error: {e}")
                continue
        
        # Create wallets from private keys
        for i, key in enumerate(all_keys, 1):
            try:
                account = Account.from_key(key)
                self.wallets.append({
                    'key': key,
                    'address': account.address,
                    'used': False,
                    'index': i
                })
            except Exception as e:
                print(f"❌ Invalid private key {i}: {key[:10]}... - {e}")
        
        if not self.wallets:
            print("⚠️ No valid private keys found in .env file!")
            print("💡 Please add private keys to .env file: PRIVATE_KEY=key1,key2,key3...")
        else:
            print(f"✅ Successfully loaded {len(self.wallets)} wallets from private keys")
    
    def remove_used_wallet(self, wallet_address):
        """Remove wallet from list after successful use"""
        with self.lock:
            self.wallets = [w for w in self.wallets if w['address'] != wallet_address]
            print(f"🗑️ Removed used wallet: {wallet_address[:10]}...")
    
    def get_available_wallet(self):
        """Get next available wallet"""
        with self.lock:
            if not self.wallets:
                print("⚠️ NO WALLETS LEFT! All wallets have been used and removed.")
                print("💡 Add more private keys to .env file to continue")
                return None
            
            # Return first wallet (they will be removed after successful use)
            return self.wallets[0]
    
    def add_wallet(self, private_key):
        """Add new wallet to the list"""
        try:
            account = Account.from_key(private_key)
            new_wallet = {
                'key': private_key,
                'address': account.address,
                'used': False
            }
            
            with self.lock:
                # Check if wallet already exists
                for wallet in self.wallets:
                    if wallet['address'] == account.address:
                        print(f"⚠️ Wallet already exists: {account.address}")
                        return False
                
                self.wallets.append(new_wallet)
                print(f"✅ Added new wallet: {account.address}")
                return True
                
        except Exception as e:
            print(f"❌ Invalid private key: {private_key[:10]}... - {e}")
            return False
    
    def mark_wallet_used(self, wallet_address):
        """Mark wallet as used (deprecated - now we remove wallets)"""
        # This method kept for compatibility but not used
        pass
    
    def verify_code(self, code):
        """Verify referral code with next available wallet and remove wallet after success"""
        wallet = self.get_available_wallet()
        if not wallet:
            print("❌ No available wallets!")
            return False
        
        payload = {
            "referralCode": code,
            "walletAddress": wallet['address']
        }
        
        try:
            response = requests.post(
                self.url,
                headers=self.headers, 
                data=json.dumps(payload),
                timeout=10,
                verify=False
            )
            result = response.json()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            wallet_short = wallet['address'][:10]
            
            if result.get("code") == 20003:
                print(f"[{timestamp}] [USED] ➤ {code} - {wallet_short}... (Code already used)")
                return False
            elif result.get("code") == 20002:
                print(f"[{timestamp}] [INVALID] ➤ {code} - {wallet_short}... (Code not found)")
                return False
            elif result.get("code") == 0 or result.get("success") == True:
                # SUCCESS - Remove wallet immediately and update counters
                print(f"[{timestamp}] [SUCCESS ✅] ➤ {code} - {wallet['address']}")
                print(f"🎉 Response: {result}")
                
                # IMMEDIATELY remove the wallet from available list
                self.remove_used_wallet(wallet['address'])
                self.success_count += 1
                
                # Log success with full details
                with open("success.txt", "a", encoding='utf-8') as f:
                    f.write(f"{timestamp} | {code} | {wallet['address']} | {json.dumps(result)}\n")
                
                # Show updated status
                remaining = len(self.wallets)
                print(f"�️ Wallet {wallet_short}... removed after successful verification")
                print(f"�💰 Remaining wallets: {remaining}")
                print(f"🎯 Total successful verifications: {self.success_count}")
                
                if remaining == 0:
                    print("⚠️ ALL WALLETS USED! Please add more private keys to .env file")
                else:
                    next_wallet = self.get_available_wallet()
                    if next_wallet:
                        print(f"➡️ Next wallet ready: {next_wallet['address'][:10]}...")
                
                return True
            else:
                print(f"[{timestamp}] [UNKNOWN] ➤ {code} - {wallet_short}... | Response: {result}")
                return False
                
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [ERROR] ➤ {code} - {wallet['address'][:8]}... | {e}")
            return False
    
    def is_valid_code(self, text):
        """Check if text is valid 8-char referral code - Enhanced detection"""
        # Remove any whitespace
        text = text.strip()
        
        # Must be exactly 8 characters
        if len(text) != 8:
            return False
        
        # Must be alphanumeric only
        if not text.isalnum():
            return False
        
        # Must contain both letters and numbers (more flexible check)
        has_letter = any(c.isalpha() for c in text)
        has_number = any(c.isdigit() for c in text)
        
        return has_letter and has_number
    
    def extract_codes_from_message(self, message):
        """Extract all potential codes from message text"""
        codes = []
        
        # Split by various separators
        import re
        # Split by spaces, commas, periods, newlines, etc.
        words = re.split(r'[\s,.\n\r\t;:!?()[\]{}]+', message)
        
        for word in words:
            if self.is_valid_code(word):
                codes.append(word.upper())  # Convert to uppercase for consistency
        
        # Also check for codes without separators but be more selective
        # Only look for patterns that are likely to be actual codes
        if len(message) <= 100:  # Only scan short messages for embedded codes
            for i in range(len(message) - 7):
                potential_code = message[i:i+8]
                if self.is_valid_code(potential_code):
                    # Only add if it's not already found and seems like a standalone code
                    if potential_code.upper() not in [c.upper() for c in codes]:
                        # Check if surrounded by separators or start/end of string
                        before_char = message[i-1] if i > 0 else ' '
                        after_char = message[i+8] if i+8 < len(message) else ' '
                        if not (before_char.isalnum() and after_char.isalnum()):
                            codes.append(potential_code.upper())
        
        # Remove duplicates while preserving order
        unique_codes = []
        for code in codes:
            if code not in unique_codes:
                unique_codes.append(code)
        
        return unique_codes
    
    async def start_telegram_monitor(self):
        """Start Telegram monitoring with session recreation if needed"""
        # Delete old session file if exists to force new login
        session_file = 'sodex_session'
        
        print("📱 Initializing Telegram connection...")
        client = TelegramClient(session_file, self.api_id, self.api_hash)
        
        try:
            print("🔐 Connecting to Telegram (may require phone verification)...")
            await client.start(phone=self.phone)
            
            # Test connection by getting self info
            me = await client.get_me()
            print(f"✅ Logged in as: {me.first_name} ({me.phone})")
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print("💡 If your session is locked, try:")
            print("   1. Use a different phone number")
            print("   2. Wait 24-48 hours before retrying")
            print("   3. Create new Telegram API credentials")
            return
        
        @client.on(events.NewMessage(chats=self.group_id))
        async def handle_message(event):
            try:
                message = event.message.message
                sender = await event.get_sender()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Log ALL messages from the group (no filtering)
                sender_name = getattr(sender, 'first_name', 'Unknown') or 'Unknown'
                sender_username = getattr(sender, 'username', None)
                sender_info = f"{sender_name}" + (f" (@{sender_username})" if sender_username else "")
                
                print(f"[{timestamp}] 📨 {sender_info}: {message}")
                
                # Real-time processing - scan for codes immediately using enhanced detection
                found_codes = self.extract_codes_from_message(message)
                
                if found_codes:
                    for code in found_codes:
                        print(f"[{timestamp}] 🎯 FOUND VALID CODE: {code}")
                        print(f"👤 From: {sender_info}")
                        
                        remaining = len(self.wallets)
                        print(f"💰 Available wallets: {remaining}")
                        
                        # Process immediately without any delay
                        if remaining > 0:
                            threading.Thread(
                                target=self.verify_code, 
                                args=(code,), 
                                daemon=True
                            ).start()
                        else:
                            print("❌ No wallets available for verification!")
                            print("💡 Add more private keys to .env file to continue")
                        
            except Exception as e:
                print(f"❌ Error processing message: {e}")
        
        print("✅ Telegram connected! Monitoring for codes...")
        print("🔥 OPTIMIZED FEATURES ENABLED:")
        print("   ⚡ Real-time message tracking (no delays)")
        print("   📨 All messages from group are monitored")
        print("   🎯 Enhanced code detection (multiple patterns)")
        print("   🗑️ Auto wallet removal after successful verification")
        print("   ➡️ Automatic rotation to next available wallet")
        print("   📊 Live status updates every 30 seconds")
        
        # Keep running
        await client.run_until_disconnected()
    
    def show_status(self):
        """Show enhanced periodic status with wallet rotation info"""
        while True:
            remaining = len(self.wallets)
            used = self.success_count
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if remaining > 0:
                current_wallet = self.get_available_wallet()
                current_addr = current_wallet['address'][:10] + "..." if current_wallet else "None"
                print(f"[{timestamp}] 📊 Status: {remaining} wallets remaining | {used} successful | Current: {current_addr}")
            else:
                print(f"[{timestamp}] 📊 Status: ALL WALLETS USED! | {used} total successful | Need more private keys!")
            
            time.sleep(30)  # Show status every 30 seconds
    
    def run(self):
        """Start the bot"""
        # Start status thread
        status_thread = threading.Thread(target=self.show_status, daemon=True)
        status_thread.start()
        
        print("🔄 Starting Telegram monitor...")
        print("⚡ Ready to process codes instantly!")
        print("Press Ctrl+C to stop\n")
        
        # Start Telegram monitoring
        try:
            asyncio.run(self.start_telegram_monitor())
        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user")
        except Exception as e:
            print(f"\n❌ Bot error: {e}")

if __name__ == "__main__":
    bot = SoDEXAutoBot()
    bot.run()
