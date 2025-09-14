#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to recreate Telegram session when expired
"""
import asyncio
from telethon import TelegramClient

async def recreate_session():
    """Recreate Telegram session"""
    # API credentials (same as bot)
    api_id = "21208198"
    api_hash = "788973d196fc50bc1653732c1b9a6089"
    phone = "+84944300848"
    
    print("🔄 Recreating Telegram session...")
    print(f"📱 Phone: {phone}")
    print("💡 You'll need to enter verification code and password")
    
    # Create new client
    client = TelegramClient('sodex_session', api_id, api_hash)
    
    try:
        print("\n📡 Connecting to Telegram...")
        await client.start(phone=phone)
        
        print("✅ Successfully connected and created new session!")
        
        # Get user info to verify
        me = await client.get_me()
        print(f"👤 Logged in as: {me.first_name} (@{me.username if me.username else 'No username'})")
        
        # Test group access
        try:
            group_id = 1002509849601
            entity = await client.get_entity(group_id)
            print(f"🎯 Successfully accessed group: {entity.title}")
        except Exception as e:
            print(f"⚠️ Warning: Could not access group: {e}")
        
        print("\n🎉 Session recreated successfully!")
        print("🚀 You can now run: python sodex_auto.py")
        
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        if "phone number" in str(e).lower():
            print("💡 Make sure the phone number is correct: +84944300848")
        elif "password" in str(e).lower():
            print("💡 Make sure to enter the correct 2FA password")
        elif "code" in str(e).lower():
            print("💡 Make sure to enter the verification code correctly")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("🔧 Telegram Session Recreator")
    print("=" * 40)
    asyncio.run(recreate_session())