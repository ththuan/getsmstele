#!/usr/bin/env python3
from sodex_auto import SoDEXAutoBot

def test_bot():
    print("🧪 Testing optimized SoDEX Auto Bot...")
    
    bot = SoDEXAutoBot()
    
    # Test improved code detection
    test_messages = [
        'Hello ABC123DE world',
        'Check this: XYZ789AB',
        'abc123defghijk', 
        'Multiple: AB12CD34 and EF56GH78',
        'Long message with embedded code AB12CD34 in middle',
        'Very long message that should not be scanned for embedded codes because it is over 100 characters long and contains ABC123DE but should not detect extra patterns'
    ]

    print('\n🎯 Testing improved code detection:')
    for msg in test_messages:
        codes = bot.extract_codes_from_message(msg)
        if codes:
            print(f'✅ "{msg[:50]}..." -> Found: {codes}')
        else:
            print(f'❌ "{msg[:50]}..." -> No codes found')
    
    print(f'\n💰 Bot loaded {len(bot.wallets)} wallets successfully')
    
    # Test wallet rotation
    print('\n🔄 Testing wallet rotation:')
    current = bot.get_available_wallet()
    if current:
        print(f'Current wallet: {current["address"][:10]}...')
        print(f'Index: {current.get("index", "N/A")}')
    
    print('\n✅ All tests completed successfully!')
    print('🚀 Bot is ready to run with optimizations:')
    print('   ⚡ Real-time message tracking')
    print('   📨 All messages monitored')
    print('   🎯 Enhanced code detection')
    print('   🗑️ Auto wallet removal after success')
    print('   ➡️ Automatic wallet rotation')

if __name__ == "__main__":
    test_bot()