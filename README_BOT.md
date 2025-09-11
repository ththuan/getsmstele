# SoDEX Auto Bot

🚀 **Bot tự động verify referral codes từ Telegram**

## Tính năng
- ✅ Theo dõi Telegram group real-time
- ✅ Tự động phát hiện referral codes (8 ký tự)
- ✅ Verify với nhiều ví tự động
- ✅ Loại bỏ ví đã dùng thành công
- ✅ Chạy liên tục 24/7

## Cách chạy

### 1. Chạy bot chính (production)
```bash
python sodex_auto.py
```
- Nhập mã xác thực Telegram khi được yêu cầu
- Bot sẽ chạy liên tục và tự động xử lý codes

### 2. Test bot với codes demo
```bash
python test_bot.py
```

## Cấu hình
Bot đã được cấu hình sẵn với:
- ✅ Telegram API (21208198)
- ✅ Group ID (1002509849601) 
- ✅ 3 demo wallets
- ✅ API endpoint SoDEX

## Output Files
- `success.txt` - Log các code verify thành công
- `sodex_session.session` - Telegram session (tự tạo)

## Status
Bot hiển thị status mỗi 30 giây:
```
[22:55:43] 📊 Status: 3 available | 0 used | 0 success
```

**Để dừng bot:** Nhấn `Ctrl+C`
