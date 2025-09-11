#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SODEX Auto Bot - Clean Version
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
                    'index': i
                })
            except Exception as e:
                print(f"❌ Invalid private key {i}: {key[:10]}... - {e}")
        
        if not self.wallets:
            print("❌ No valid private keys found in .env file!")
            print("💡 Please add private keys to .env file:")
            print("   PRIVATE_KEY=key1,key2,key3...")
            exit(1)

        print(f"✅ Successfully loaded {len(self.wallets)} wallets from private keys")

    def get_available_wallet(self):
        """Get next available wallet"""
        with self.lock:
            if self.wallets:
                return self.wallets[0]  # Always return first wallet
                    
            # If no available wallet, warn user
            print("⚠️ NO AVAILABLE WALLETS! All wallets have been used successfully.")
            print("💡 Add more private keys to .env file to continue")
            return None

    def remove_used_wallet(self, wallet_address):
        """Remove wallet from list after successful verification"""
        with self.lock:
            self.wallets = [w for w in self.wallets if w['address'] != wallet_address]
            print(f"🗑️ Removed used wallet: {wallet_address[:10]}...")

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
                
                # Remove wallet from list (already used successfully)
                self.remove_used_wallet(wallet['address'])
                self.success_count += 1
                
                # Log to file with full details
                with open("success.txt", "a", encoding='utf-8') as f:
                    f.write(f"{timestamp} | {code} | {wallet['address']} | {json.dumps(result)}\n")
                
                # Show remaining wallets
                print(f"💰 Remaining wallets: {len(self.wallets)}")
                
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
                    
                    # Show available wallets count before processing
                    print(f"💰 Available wallets: {len(self.wallets)}")
                    
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
        """Show periodic status every 5 seconds"""
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📊 Status: {len(self.wallets)} wallets available | {self.success_count} success")
            
            time.sleep(5)  # Show status every 5 seconds
    
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
