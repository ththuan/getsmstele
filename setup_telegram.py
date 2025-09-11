#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Setup - Create session file
"""
import asyncio
from telethon import TelegramClient

def load_env_file():
    """Load .env file manually"""
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("❌ .env file not found!")
        exit(1)
    return env_vars

async def setup_telegram():
    """Setup Telegram session"""
    env_vars = load_env_file()
    
    api_id = env_vars.get("TELEGRAM_API_ID", "21208198")
    api_hash = env_vars.get("TELEGRAM_API_HASH", "788973d196fc50bc1653732c1b9a6089")
    phone = env_vars.get("TELEGRAM_PHONE", "+84944300848")
    
    print(f"📱 Setting up Telegram with phone: {phone}")
    
    client = TelegramClient('sodex_session', api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        print("✅ Telegram setup successful!")
        print("📄 Session file 'sodex_session.session' created")
        
        # Test connection
        me = await client.get_me()
        print(f"👤 Logged in as: {me.first_name} {me.last_name or ''}")
        
        # Try to get group info
        try:
            group_id = int(env_vars.get("TELEGRAM_GROUP_ID", "1002509849601"))
            entity = await client.get_entity(group_id)
            print(f"📢 Group found: {entity.title}")
        except Exception as e:
            print(f"⚠️ Could not access group: {e}")
        
        await client.disconnect()
        print("🎉 Setup complete! You can now run sodex_auto.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_telegram())
