#!/usr/bin/env python3
"""
Test script to simulate Telegram codes for testing
"""
import time
import threading
from sodex_auto import SoDEXAutoBot

def test_codes():
    """Test with demo codes"""
    bot = SoDEXAutoBot()
    
    # Demo codes for testing
    test_codes = [
        "ABC12345",  # Valid format
        "XYZ98765",  # Valid format  
        "TEST1234",  # Valid format
        "12345678",  # Invalid (all numbers)
        "ABCDEFGH",  # Invalid (all letters)
        "SHORT12",   # Invalid (too short)
    ]
    
    print("🧪 Testing bot with demo codes...")
    
    for code in test_codes:
        print(f"\n🔍 Testing code: {code}")
        
        if bot.is_valid_code(code):
            print("✅ Code format valid - sending to verify")
            result = bot.verify_code(code)
            if result:
                print(f"🎉 SUCCESS: {code}")
            else:
                print(f"❌ FAILED: {code}")
        else:
            print("❌ Invalid code format - skipped")
        
        time.sleep(2)  # Wait between tests

if __name__ == "__main__":
    test_codes()
