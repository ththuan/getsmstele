#!/usr/bin/env python3
"""
Test manual code verification
"""
import requests
import json
from eth_account import Account
from datetime import datetime

def test_manual_verify():
    """Test verify with manual input"""
    url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Demo wallet
    private_key = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    account = Account.from_key(private_key)
    
    print("🧪 Manual Code Verification Test")
    print("=" * 40)
    print(f"💰 Using wallet: {account.address}")
    print()
    
    while True:
        code = input("Enter referral code to test (or 'quit'): ").strip()
        
        if code.lower() == 'quit':
            break
            
        if len(code) != 8:
            print("❌ Code must be 8 characters!")
            continue
        
        payload = {
            "referralCode": code,
            "walletAddress": account.address
        }
        
        try:
            print(f"🔍 Testing code: {code}...")
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10,
                verify=False
            )
            result = response.json()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if result.get("code") == 20003:
                print(f"[{timestamp}] ❌ USED - Code already used")
            elif result.get("code") == 20002:
                print(f"[{timestamp}] ❌ INVALID - Code not found")
            else:
                print(f"[{timestamp}] ✅ SUCCESS!")
                print(f"🎉 Response: {result}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_manual_verify()
