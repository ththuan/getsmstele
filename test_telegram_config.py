#!/usr/bin/env python3
"""
Test Telegram API credentials
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_telegram_config():
    print("🔍 KIỂM TRA CẤU HÌNH TELEGRAM")
    print("=" * 40)
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash}")
    print(f"Phone: {phone}")
    print()
    
    # Validate API ID
    if not api_id or api_id == 'your_api_id_here':
        print("❌ API ID chưa được cấu hình!")
        return False
    
    try:
        api_id_int = int(api_id)
        print(f"✅ API ID hợp lệ: {api_id_int}")
    except ValueError:
        print(f"❌ API ID phải là số, không phải: {api_id}")
        return False
    
    # Validate API Hash
    if not api_hash or api_hash == 'your_api_hash_here':
        print("❌ API Hash chưa được cấu hình!")
        return False
    
    if len(api_hash) != 32:
        print(f"❌ API Hash phải có 32 ký tự, hiện tại có: {len(api_hash)}")
        return False
    
    print(f"✅ API Hash hợp lệ: {api_hash[:8]}...{api_hash[-8:]}")
    
    # Validate Phone
    if not phone or not phone.startswith('+'):
        print(f"❌ Số điện thoại không hợp lệ: {phone}")
        return False
    
    print(f"✅ Số điện thoại hợp lệ: {phone}")
    
    print("\n✅ TẤT CẢ CẤU HÌNH TELEGRAM HỢP LỆ!")
    return True

if __name__ == "__main__":
    if test_telegram_config():
        print("\n🚀 Bạn có thể chạy bot ngay bây giờ!")
        print("Chạy lệnh: python sodex_real_bot.py")
    else:
        print("\n🔧 Vui lòng cập nhật file .env với thông tin chính xác")
        print("Xem hướng dẫn: python get_telegram_api.py")
