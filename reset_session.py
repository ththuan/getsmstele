#!/usr/bin/env python3
"""
Session Reset Tool for SoDEX Auto Bot
Helps reset Telegram session when locked
"""
import os
import sys

def reset_session():
    """Reset Telegram session and optionally update phone number"""
    
    print("🔧 SoDEX Bot Session Reset Tool")
    print("=" * 40)
    
    # Check for existing session files
    session_files = [f for f in os.listdir('.') if f.startswith('sodex_session')]
    
    if session_files:
        print(f"📁 Found session files: {session_files}")
        confirm = input("🗑️ Delete existing session files? (y/n): ").lower().strip()
        
        if confirm == 'y':
            for file in session_files:
                try:
                    os.remove(file)
                    print(f"✅ Deleted: {file}")
                except Exception as e:
                    print(f"❌ Error deleting {file}: {e}")
        else:
            print("⏭️ Skipping session file deletion")
    else:
        print("✅ No existing session files found")
    
    # Option to update phone number
    print("\n📱 Telegram Phone Number Configuration")
    update_phone = input("📞 Do you want to update phone number? (y/n): ").lower().strip()
    
    if update_phone == 'y':
        new_phone = input("📱 Enter new phone number (with country code, e.g., +84123456789): ").strip()
        
        if new_phone:
            # Update .env file
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update or add phone number
                lines = content.split('\n')
                phone_updated = False
                
                for i, line in enumerate(lines):
                    if line.startswith('TELEGRAM_PHONE='):
                        lines[i] = f'TELEGRAM_PHONE={new_phone}'
                        phone_updated = True
                        break
                
                if not phone_updated:
                    lines.append(f'TELEGRAM_PHONE={new_phone}')
                
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Updated phone number to: {new_phone}")
                
            except Exception as e:
                print(f"❌ Error updating .env file: {e}")
        else:
            print("⏭️ No phone number provided")
    
    print("\n🚀 Session reset complete!")
    print("💡 Next steps:")
    print("   1. Run the bot: python sodex_auto.py")
    print("   2. Enter verification code when prompted")
    print("   3. Bot will create new session automatically")
    
    # Option to run bot immediately
    run_now = input("\n▶️ Run bot now? (y/n): ").lower().strip()
    if run_now == 'y':
        print("🚀 Starting SoDEX Auto Bot...")
        os.system('python sodex_auto.py')

if __name__ == "__main__":
    reset_session()