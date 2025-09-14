# 🔄 Session Renewal Guide

## Khi nào cần tạo lại session?

- ✅ Bot báo lỗi authentication 
- ✅ Không kết nối được Telegram
- ✅ Session expired error
- ✅ Đăng nhập từ thiết bị khác

## 🚀 Cách tạo lại session nhanh:

### 1. Dừng bot hiện tại
```bash
# Nhấn Ctrl+C để dừng bot
# Hoặc dùng lệnh
taskkill /f /im python3.11.exe
```

### 2. Xóa session cũ
```bash
del sodex_session.session
del sodex_session.session-journal  # nếu có
```

### 3. Tạo script tạm để recreate
```python
# recreate_session.py
import asyncio
from telethon import TelegramClient

async def recreate():
    client = TelegramClient('sodex_session', '21208198', '788973d196fc50bc1653732c1b9a6089')
    await client.start(phone='+84944300848')
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name}")
    await client.disconnect()

asyncio.run(recreate())
```

### 4. Chạy và nhập code
```bash
python recreate_session.py
# Nhập verification code từ Telegram
# Nhập 2FA password nếu có
```

### 5. Chạy lại bot
```bash
python sodex_auto.py
```

## 💡 Tips:
- Giữ session files an toàn
- Không đăng nhập từ nhiều thiết bị cùng lúc
- Backup session files định kỳ
- Session thường hết hạn sau vài tuần không sử dụng

## 🔧 Troubleshooting:
- **"Phone number invalid"**: Kiểm tra format +84944300848
- **"Password incorrect"**: Đảm bảo 2FA password đúng
- **"Code expired"**: Yêu cầu code mới từ Telegram
- **"Flood wait"**: Đợi vài phút rồi thử lại