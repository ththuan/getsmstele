#!/usr/bin/env python3
"""
Fix .env encoding and count private keys
"""
import os

def fix_env_encoding():
    print("🔧 Fixing .env encoding...")
    
    # Try different encodings to read the file
    encodings = ['utf-16', 'utf-8-sig', 'cp1252', 'latin1']
    
    for encoding in encodings:
        try:
            with open('.env', 'r', encoding=encoding) as f:
                content = f.read()
            
            print(f"✅ Successfully read .env with encoding: {encoding}")
            
            # Count private keys
            private_key_line = None
            for line in content.split('\n'):
                line = line.strip()
                if 'PRIVATE_KEY=' in line and not line.startswith('#'):
                    private_key_line = line
                    break
            
            if private_key_line:
                key_value = private_key_line.split('=', 1)[1]
                keys = [k.strip() for k in key_value.split(',') if k.strip() and len(k.strip()) == 64]
                print(f"🔑 Found {len(keys)} private keys")
                
                # Show first few keys for verification
                for i, key in enumerate(keys[:5], 1):
                    print(f"  Key {i}: {key[:10]}...{key[-10:]}")
                
                if len(keys) > 5:
                    print(f"  ... and {len(keys) - 5} more keys")
            
            # Write clean UTF-8 version
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Converted .env to clean UTF-8")
            return True
            
        except Exception as e:
            continue
    
    print("❌ Could not read .env file with any encoding")
    return False

if __name__ == "__main__":
    fix_env_encoding()
