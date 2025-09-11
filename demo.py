"""
Chạy tool demo không cần input
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import SodexAutoVerify

def demo():
    print("="*60)
    print("🎯 SODEX AUTO VERIFY TOOL - DEMO MODE")
    print("="*60)
    
    bot = SodexAutoVerify()
    
    print("🔄 Demo với 10 random codes...")
    codes = bot.generate_random_codes(10)
    
    print(f"📝 Generated codes: {codes}")
    
    # Test từng code một để xem kết quả
    for code in codes[:3]:  # Chỉ test 3 codes đầu
        print(f"\n🔍 Testing: {code}")
        bot.verify_code(code)
        
    print("\n✅ Demo hoàn thành!")

if __name__ == "__main__":
    demo()
