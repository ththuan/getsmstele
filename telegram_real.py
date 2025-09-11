"""
Telegram Integration for Real-time Code Monitoring
Tích hợp Telegram API thật để theo dõi codes
"""
import re
import time
import asyncio
from telethon import TelegramClient
from telethon.events import NewMessage
import threading
from queue import Queue

class TelegramRealMonitor:
    def __init__(self, api_id, api_hash, phone, group_chat_id):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.group_chat_id = group_chat_id
        self.client = None
        self.code_queue = Queue()
        self.running = False
        
        # Regex pattern để tìm codes 8 ký tự (mix chữ và số)
        self.code_pattern = re.compile(r'\b[A-Za-z0-9]{8}\b')
        
    async def start_monitoring(self):
        """Start monitoring Telegram group"""
        self.client = TelegramClient('session', self.api_id, self.api_hash)
        
        try:
            await self.client.start(phone=self.phone)
            print("✅ Connected to Telegram successfully!")
            
            # Add event handler for new messages
            @self.client.on(NewMessage(chats=[self.group_chat_id]))
            async def handler(event):
                message = event.message.message
                print(f"📱 New message: {message}")
                
                # Tìm codes trong message
                codes = self.extract_codes(message)
                for code in codes:
                    self.code_queue.put(code)
                    print(f"🆕 Found code: {code}")
            
            self.running = True
            print(f"📱 Monitoring group {self.group_chat_id} for codes...")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
        finally:
            if self.client:
                await self.client.disconnect()
    
    def extract_codes(self, message):
        """Extract 8-character codes from message"""
        codes = []
        matches = self.code_pattern.findall(message)
        
        for match in matches:
            # Validate: must contain both letters and numbers
            if (any(c.isalpha() for c in match) and 
                any(c.isdigit() for c in match) and
                not match.isalpha() and 
                not match.isdigit()):
                codes.append(match.upper())
        
        return codes
    
    def get_new_codes(self):
        """Get new codes from queue"""
        codes = []
        while not self.code_queue.empty():
            try:
                code = self.code_queue.get_nowait()
                codes.append(code)
            except:
                break
        return codes
    
    def stop(self):
        """Stop monitoring"""
        self.running = False

def run_telegram_monitor(monitor):
    """Run Telegram monitor in asyncio loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor.start_monitoring())

# Test function
if __name__ == "__main__":
    print("=== TELEGRAM MONITOR TEST ===")
    
    # Test code extraction
    monitor = TelegramRealMonitor("", "", "", "")
    
    test_messages = [
        "Hey everyone! Just a quick reminder about how we share referral codes ABC12345",
        "can u give me code DEF67890 please",
        "New code: GHI13579",
        "12345678",  # All numbers - should be rejected
        "ABCDEFGH",  # All letters - should be rejected
        "Valid: JKL24680"
    ]
    
    print("Testing code extraction:")
    for msg in test_messages:
        codes = monitor.extract_codes(msg)
        print(f"Message: {msg}")
        print(f"Codes found: {codes}")
        print()
