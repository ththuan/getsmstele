#!/usr/bin/env python3
"""
Debug wallet loading
"""

def debug_load_wallets():
    print("🔍 Debug Wallet Loading")
    print("=" * 30)
    
    # Try to read from .env first
    all_keys = []
    
    try:
        with open('.env', 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print(f"📄 File content length: {len(content)} chars")
            
            for line_num, line in enumerate(content.split('\n'), 1):
                print(f"Line {line_num}: {line}")
                line = line.strip()
                if 'PRIVATE_KEY=' in line and not line.startswith('#'):
                    key_value = line.split('=', 1)[1]
                    print(f"🔑 Found PRIVATE_KEY value: {key_value}")
                    
                    # Split by comma if multiple keys
                    keys = [k.strip() for k in key_value.split(',') if k.strip()]
                    print(f"📝 Split into {len(keys)} keys:")
                    for i, key in enumerate(keys, 1):
                        print(f"  Key {i}: {key[:10]}...{key[-10:]}")
                    all_keys.extend(keys)
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
    
    print(f"\n💰 Total keys found: {len(all_keys)}")
    
    if not all_keys:
        print("⚠️ No keys found, using demo keys")
        all_keys = [
            "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            "59c6995e998f97436c6005777ac073d908686e16b2c46f8c38e2ac58c50f8ea9", 
            "5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
        ]
    
    # Test wallet creation
    from eth_account import Account
    wallets = []
    for i, key in enumerate(all_keys, 1):
        try:
            account = Account.from_key(key)
            wallets.append({
                'key': key,
                'address': account.address,
                'used': False
            })
            print(f"✅ Wallet {i}: {account.address}")
        except Exception as e:
            print(f"❌ Invalid key {i}: {key[:10]}... - {e}")
    
    print(f"\n🎯 Successfully loaded {len(wallets)} wallets")

if __name__ == "__main__":
    debug_load_wallets()
