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
        # Hardcoded config
        self.api_id = "21208198"
        self.api_hash = "788973d196fc50bc1653732c1b9a6089"  
        self.phone = "+84944300848"
        self.group_id = int("1002509849601")
        
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
            print("⚠️ No valid private keys found, using demo keys")
            # Demo fallback keys
            demo_keys = [
                "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
                "59c6995e998f97436c6005777ac073d908686e16b2c46f8c38e2ac58c50f8ea9",
                "5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
            ]
            for i, key in enumerate(demo_keys, 1):
                account = Account.from_key(key)
                self.wallets.append({
                    'key': key,
                    'address': account.address,  
                    'used': False,
                    'index': i
                })
        
        print(f"✅ Successfully loaded {len(self.wallets)} wallets from private keys")
        
        # Fallback to demo wallets if wallets.json fails
        print("⚠️ Using demo wallets as fallback")
        demo_keys = [
            "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            "59c6995e998f97436c6005777ac073d908686e16b2c46f8c38e2ac58c50f8ea9", 
            "5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
        ]
        
        for key in demo_keys:
            try:
                account = Account.from_key(key)
                self.wallets.append({
                    'key': key,
                    'address': account.address,
                    'used': False
                })
            except Exception as e:
                print(f"❌ Invalid key: {key[:10]}... - {e}")
    
    def get_available_wallet(self):
        """Get next available wallet"""
        with self.lock:
            for wallet in self.wallets:
                if not wallet['used']:
                    return wallet
                    
            # If no available wallet, warn user
            print("⚠️ NO AVAILABLE WALLETS! All wallets have been used successfully.")
            print("💡 Add more private keys to .env file to continue")
            return None
    
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
        """Mark wallet as used"""
        with self.lock:
            for wallet in self.wallets:
                if wallet['address'] == wallet_address:
                    wallet['used'] = True
                    break
    
    def verify_code(self, code):
        """Verify referral code with next available wallet"""
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
            
            if result.get("code") == 20003:
                print(f"[{timestamp}] [USED] ➤ {code} - {wallet['address'][:10]}... (Code already used)")
                return False
            elif result.get("code") == 20002:
                print(f"[{timestamp}] [INVALID] ➤ {code} - {wallet['address'][:10]}... (Code not found)")
                return False
            else:
                print(f"[{timestamp}] [SUCCESS ✅] ➤ {code} - {wallet['address']}")
                print(f"🎉 Full Response: {result}")
                
                # Mark wallet as used and log success
                self.mark_wallet_used(wallet['address'])
                self.success_count += 1
                
                # Log to file with full details
                with open("success.txt", "a", encoding='utf-8') as f:
                    f.write(f"{timestamp} | {code} | {wallet['address']} | {json.dumps(result)}\n")
                
                # Show remaining wallets
                available = sum(1 for w in self.wallets if not w['used'])
                print(f"💰 Remaining wallets: {available}")
                
                return True
                
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [ERROR] ➤ {code} - {wallet['address'][:8]}... | {e}")
            return False
    
    def is_valid_code(self, text):
        """Check if text is valid 8-char referral code"""
        if len(text) != 8:
            return False
        
        # Must contain both letters and numbers
        has_letter = any(c.isalpha() for c in text)
        has_number = any(c.isdigit() for c in text)
        
        return has_letter and has_number and text.isalnum()
    
    async def start_telegram_monitor(self):
        """Start Telegram monitoring"""
        client = TelegramClient('sodex_session', self.api_id, self.api_hash)
        
        @client.on(events.NewMessage(chats=self.group_id))
        async def handle_message(event):
            message = event.message.message
            sender = await event.get_sender()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Log all messages for debugging
            print(f"[{timestamp}] 📨 Message from {sender.first_name}: {message[:50]}...")
            
            words = message.split()
            
            for word in words:
                if self.is_valid_code(word):
                    print(f"[{timestamp}] 🎯 FOUND VALID CODE: {word}")
                    print(f"👤 From: {sender.first_name} (@{sender.username})")
                    
                    # Get available wallets count before processing
                    available = sum(1 for w in self.wallets if not w['used'])
                    print(f"� Available wallets: {available}")
                    
                    # Verify immediately in background
                    threading.Thread(
                        target=self.verify_code, 
                        args=(word,), 
                        daemon=True
                    ).start()
        
        print("📱 Connecting to Telegram...")
        await client.start(phone=self.phone)
        print("✅ Telegram connected! Monitoring for codes...")
        
        # Keep running
        await client.run_until_disconnected()
    
    def show_status(self):
        """Show periodic status"""
        while True:
            available = sum(1 for w in self.wallets if not w['used'])
            used = sum(1 for w in self.wallets if w['used'])
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📊 Status: {available} available | {used} used | {self.success_count} success")
            
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
