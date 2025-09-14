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
import queue
from datetime import datetime
from telethon import TelegramClient, events
from eth_account import Account
from concurrent.futures import ThreadPoolExecutor

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
        
        # Queue system for fast processing
        self.code_queue = queue.Queue(maxsize=1000)
        self.processed_codes = set()  # Avoid duplicate processing
        self.executor = ThreadPoolExecutor(max_workers=5)  # Parallel processing
        
        print(f"🚀 SODEX Auto Bot Started")
        print(f"💰 Loaded {len(self.wallets)} wallets")
        print(f"📱 Monitoring Group: {self.group_id}")
        print(f"⚡ Queue system initialized for instant processing")
    
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
        """Verify referral code with next available wallet - with retry"""
        wallet = self.get_available_wallet()
        if not wallet:
            print("❌ No available wallets!")
            return False
        
        payload = {
            "referralCode": code,
            "walletAddress": wallet['address']
        }
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.url,
                    headers=self.headers, 
                    data=json.dumps(payload),
                    timeout=5,  # Reduced timeout for faster response
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
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏱️ Timeout attempt {attempt + 1}/{max_retries} for {code}, retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    print(f"❌ Timeout after {max_retries} attempts for {code}")
                    return False
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Error attempt {attempt + 1}/{max_retries} for {code}: {e}, retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] [ERROR] ➤ {code} - {wallet['address'][:8]}... | {e}")
                    return False
        
        return False

    def process_code_queue(self):
        """Worker thread to process codes from queue"""
        while True:
            try:
                code = self.code_queue.get(timeout=1)
                if code in self.processed_codes:
                    print(f"⏭️ Skipping duplicate code: {code}")
                    self.code_queue.task_done()
                    continue
                
                self.processed_codes.add(code)
                print(f"🔄 Processing code: {code}")
                self.verify_code(code)
                self.code_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Queue processing error: {e}")
                time.sleep(0.1)
    
    def is_valid_code(self, text):
        """Check if text is valid referral code - optimized for speed"""
        # Quick length check first - more flexible now
        if not (6 <= len(text) <= 12):
            return False
        
        # Must be alphanumeric only (fastest check)
        if not text.isalnum():
            return False
        
        # Skip common username patterns (blacklist)
        blacklist_patterns = [
            'duasutu', 'complex', 'username', 'kirutikvasan', 
            'telegram', 'channel', 'message', 'welcome',
            'admin', 'group', 'hello', 'please', 'thanks'
        ]
        if text.lower() in blacklist_patterns:
            return False
        
        # Count letters and numbers in one pass
        letter_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        
        # Enhanced logic based on user requirement:
        # 1. For 8-char codes: accept ALL letters OR mixed alphanumeric
        # 2. For 7-char codes: accept ALL letters OR mixed
        # 3. For other lengths: must be mixed OR mostly uppercase (referral pattern)
        
        if len(text) == 8:
            # For 8-char codes: accept if all letters OR mixed alphanumeric
            return letter_count >= 6 or (letter_count >= 2 and digit_count >= 2)
        elif len(text) == 7:
            # For 7-char codes: also accept all letters
            return letter_count >= 5 or (letter_count >= 2 and digit_count >= 2)
        elif len(text) >= 9:
            # For longer codes: prefer uppercase pattern (common in referrals)
            uppercase_count = sum(1 for c in text if c.isupper())
            return (letter_count >= 2 and digit_count >= 2) or (uppercase_count >= len(text) * 0.7)
        else:
            # For 6-char codes: must be mixed
            return letter_count >= 2 and digit_count >= 2
    
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
            
            # Quick processing - split and check all words instantly
            words = message.split()
            found_codes = []
            
            for word in words:
                # Remove common punctuation that might be attached - enhanced cleaning
                clean_word = word.strip('.,!?;:"()[]{}/@#$%^&*-_=+|\\`~<>')
                
                # Also try without cleaning for edge cases
                candidates = [clean_word, word]
                
                for candidate in candidates:
                    if candidate and self.is_valid_code(candidate) and candidate not in found_codes:
                        found_codes.append(candidate)
                        break  # Found valid code, stop checking variants
            
            # Process all found codes immediately
            for code in found_codes:
                try:
                    print(f"[{timestamp}] 🎯 FOUND VALID CODE: {code}")
                    print(f"👤 From: {sender.first_name} (@{sender.username})")
                    print(f"💰 Available wallets: {len(self.wallets)}")
                    
                    # Add to queue for instant processing
                    self.code_queue.put_nowait(code)
                    print(f"⚡ Code {code} added to queue for instant processing")
                    
                except queue.Full:
                    print(f"⚠️ Queue full! Skipping code: {code}")
                except Exception as e:
                    print(f"❌ Error adding code to queue: {e}")
        
        print("📱 Connecting to Telegram...")
        await client.start(phone=self.phone)
        print("✅ Telegram connected! Monitoring for codes...")
        
        # Keep running
        await client.run_until_disconnected()
    
    def show_status(self):
        """Show periodic status every 3 seconds"""
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            queue_size = self.code_queue.qsize()
            processed_count = len(self.processed_codes)
            
            print(f"[{timestamp}] 📊 Status: {len(self.wallets)} wallets | {self.success_count} success | Queue: {queue_size} | Processed: {processed_count}")
            
            # Clean old processed codes to prevent memory issues
            if processed_count > 1000:
                self.processed_codes = set(list(self.processed_codes)[-500:])
                print("🧹 Cleaned processed codes cache")
            
            time.sleep(3)  # Faster status updates
    
    def run(self):
        """Start the bot"""
        # Start queue processing workers
        for i in range(3):  # Multiple workers for parallel processing
            worker_thread = threading.Thread(
                target=self.process_code_queue, 
                daemon=True,
                name=f"QueueWorker-{i+1}"
            )
            worker_thread.start()
            print(f"🔧 Started queue worker {i+1}")
        
        # Start status thread
        status_thread = threading.Thread(target=self.show_status, daemon=True)
        status_thread.start()
        
        print("🔄 Starting Telegram monitor...")
        print("⚡ Ready to process codes instantly with queue system!")
        print("🚀 Multiple workers ready for parallel processing")
        print("Press Ctrl+C to stop\n")
        
        # Start Telegram monitoring
        try:
            asyncio.run(self.start_telegram_monitor())
        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user")
            print(f"📊 Final stats: {self.success_count} successful verifications")
        except Exception as e:
            print(f"\n❌ Bot error: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)
            self.run()  # Auto-restart on error

if __name__ == "__main__":
    bot = SoDEXAutoBot()
    bot.run()
