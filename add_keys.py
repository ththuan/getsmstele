#!/usr/bin/env python3
"""
Add Private Keys to .env file safely
"""

import os
from eth_account import Account

def add_private_keys():
    """Interactive script to add private keys"""
    print("🔐 ADD PRIVATE KEYS TO BOT")
    print("=" * 40)
    print("⚠️  QUAN TRỌNG: Private keys sẽ được lưu trong file .env")
    print("⚠️  Đảm bảo file .env an toàn và không share cho ai!")
    print()
    
    keys = []
    
    while True:
        print(f"\n📝 Nhập private key #{len(keys) + 1} (hoặc 'done' để hoàn thành):")
        key = input("Private Key (không có 0x): ").strip()
        
        if key.lower() == 'done':
            break
            
        if len(key) == 0:
            continue
            
        # Remove 0x prefix if present
        if key.startswith('0x'):
            key = key[2:]
            
        # Validate private key
        try:
            account = Account.from_key(key)
            keys.append(key)
            print(f"✅ Valid key #{len(keys)} - Address: {account.address}")
            
            if len(keys) >= 12:
                print(f"\n🎉 Đã nhập đủ {len(keys)} private keys!")
                break
                
        except Exception as e:
            print(f"❌ Invalid private key: {e}")
    
    if len(keys) == 0:
        print("❌ Không có private key nào được thêm!")
        return
    
    # Save to .env file
    print(f"\n💾 Saving {len(keys)} keys to .env...")
    
    env_content = f"""# Multiple Private Keys (without 0x prefix) - YOUR REAL KEYS
PRIVATE_KEY={','.join(keys)}

# Real Telegram API Configuration  
TELEGRAM_API_ID=21208198
TELEGRAM_API_HASH=788973d196fc50bc1653732c1b9a6089
TELEGRAM_PHONE=+84944300848
TELEGRAM_GROUP_ID=1002509849601

# Delay between checks (milliseconds)
CHECK_DELAY=100"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Đã lưu {len(keys)} private keys vào .env")
    print("\n🚀 Bây giờ bạn có thể chạy bot:")
    print("python sodex_auto.py")
    
    # Show addresses for verification
    print(f"\n💰 Addresses đã thêm:")
    for i, key in enumerate(keys, 1):
        account = Account.from_key(key)
        print(f"  {i}. {account.address}")

if __name__ == "__main__":
    add_private_keys()
