import requests
import json
from eth_account import Account
import warnings

# Tắt warning SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def test_single_code():
    """Test với một code cụ thể"""
    
    # Private key demo (KHÔNG SỬ DỤNG CHO TÀI KHOẢN THẬT)
    private_key = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    
    # Tạo wallet từ private key
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    print(f"🔍 Testing với wallet: {wallet_address}")
    
    # URL verify
    url = "https://test-vex-v1.sodex.dev/biz/task/referral/join"
    
    # Headers
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Content-Type': 'application/json',
        'Origin': 'https://testnet.sodex.dev',
        'Referer': 'https://testnet.sodex.dev/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    
    # Test code
    test_code = "TEST1234"
    
    payload = {
        "referralCode": test_code,
        "walletAddress": wallet_address
    }
    
    print(f"🚀 Gửi request với code: {test_code}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=10,
            verify=False
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 20003:
                print("✅ Code đã được sử dụng (response 20003)")
            elif result.get("code") == 20002:
                print("❌ Code không tồn tại (response 20002)")
            else:
                print(f"🎯 Code hợp lệ! Response: {result}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    test_single_code()
