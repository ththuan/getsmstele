# 🤖 SODEX Auto Verify Bot - Python

Công cụ tự động verify referral code cho SoDEX với tích hợp Telegram monitoring.

## ✨ Tính năng

- 🤖 **Auto Mode**: Theo dõi Telegram group tự động lấy codes
- 🎯 **Manual Mode**: Brute force thủ công với nhiều tùy chọn
- 👛 **Wallet Integration**: Tự động đăng nhập bằng private key
- ⚡ **Multi-threading**: Test nhanh với nhiều threads
- 🎲 **Smart Generation**: Tạo codes thông minh (mix chữ + số)
- 📝 **Pattern Support**: Brute force theo pattern cụ thể
- 🔄 **Auto Stop**: Tự động dừng khi tìm thấy code hợp lệ

## 🛠️ Cài đặt

1. **Cài đặt Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Cấu hình file `.env`:**
```env
# Private Key của ví (REQUIRED)
PRIVATE_KEY=your_private_key_here

# Telegram Config (OPTIONAL - chỉ cần nếu dùng Auto Mode)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_group_id
```

## 🚀 Cách sử dụng

### Chạy Bot chính (Khuyến nghị):
```bash
python bot.py
```

### Các mode khác:
```bash
# Manual mode cơ bản
python main.py

# Test API
python test_api.py

# Demo nhanh
python demo.py
```

## 🔧 Các chế độ hoạt động

### 1. 🤖 Auto Mode (Telegram)
- Theo dõi Telegram group liên tục
- Tự động extract codes 8 ký tự từ tin nhắn
- Verify ngay khi tìm thấy code mới
- Lưu codes đã xử lý để tránh duplicate

### 2. 🎯 Manual Mode
**Load codes từ file:**
- Đọc codes từ file text (mỗi dòng 1 code)
- Multi-threading verify

**Generate random codes:**
- Tự động tạo codes ngẫu nhiên
- Đảm bảo mix chữ + số (không phải toàn chữ/số)

**Pattern brute force:**
- `ABCD****`: 4 ký tự đầu cố định
- `****1234`: 4 ký tự cuối cố định  
- `AB**CD**`: Mix cố định và random

**Test code cụ thể:**
- Test một code nhất định

## 📁 Files output

- `valid.txt`: Codes hợp lệ tìm được
- `used.txt`: Codes đã sử dụng/không hợp lệ  
- `processed.txt`: Codes từ Telegram đã xử lý
- `codes.txt`: File input mẫu

## ⚙️ Cấu hình

- **Threads**: Mặc định 50 (có thể điều chỉnh)
- **Timeout**: 10 giây
- **Delay**: 0.1 giây giữa requests
- **Pattern**: Hỗ trợ 8 ký tự với wildcard `*`

## 🔒 Bảo mật

- ⚠️ **KHÔNG BAO GIỜ** chia sẻ private key
- 🔒 File `.env` được gitignore tự động
- 🎭 Demo key có sẵn chỉ để test

## 📋 API Response Codes

- `20002`: Code không tồn tại
- `20003`: Code đã được sử dụng
- `success`: Code hợp lệ (Tool sẽ dừng ngay)

## 🚨 Lưu ý

- Tool tự động **DỪNG** ngay khi tìm thấy code hợp lệ đầu tiên
- Telegram mode cần bot token và chat ID
- Private key phải là Ethereum private key hợp lệ
- Không spam quá nhanh để tránh bị block IP
