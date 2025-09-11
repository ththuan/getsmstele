# 🚀 SODEX Multi-Wallet Auto Verify Bot

Bot tự động verify referral codes cho SoDEX với nhiều ví, check liên tục, loại bỏ ví đã dùng.

## ✨ Tính năng chính

- ✅ **Multi-Wallet**: Hỗ trợ nhiều ví cùng lúc
- ✅ **Auto Remove**: Tự động loại bỏ ví đã verify thành công  
- ✅ **Real-time**: Theo dõi Telegram real-time không miss code
- ✅ **High Speed**: Xử lý cực nhanh với multiple workers
- ✅ **Smart Queue**: Hàng đợi thông minh, không duplicate
- ✅ **Full Logging**: Ghi log đầy đủ success/used/invalid

## 🛠️ Cài đặt

### 1. Clone repo và cài dependencies
```bash
cd "E:\nodejs\get code"
pip install requests python-dotenv eth_account telethon
```

### 2. Setup Telegram API
1. Truy cập https://my.telegram.org/auth
2. Đăng nhập và vào "API Development tools"
3. Tạo app mới và lấy `API ID` và `API Hash`
4. Lấy `Group Chat ID` của nhóm Telegram cần theo dõi

### 3. Cấu hình .env file
```env
# Telegram API (BẮT BUỘC)
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here  
TELEGRAM_PHONE=+your_phone_number
TELEGRAM_GROUP_ID=-group_chat_id_here

# Speed settings
CHECK_DELAY=100
```

## 🚀 Sử dụng

### Bước 1: Thêm wallets
```bash
python sodex_real_bot.py
# Chọn 2 - Add Wallets
# Nhập từng private key (không có 0x)
```

### Bước 2: Chạy bot
```bash
python sodex_real_bot.py  
# Chọn 1 - Start Real-Time Bot
```

## 📊 Output Files

- `success.txt` - Codes verify thành công
- `used.txt` - Codes đã được sử dụng
- `invalid.txt` - Codes không hợp lệ
- `wallets.json` - Quản lý trạng thái wallets

## ⚡ Workflow

1. **Telegram Monitor**: Theo dõi group real-time cho codes 8 ký tự
2. **Smart Filter**: Chỉ lấy codes hợp lệ (mix chữ + số)
3. **Queue System**: Xếp hàng codes để xử lý
4. **Multi Workers**: 3 workers xử lý song song
5. **Wallet Management**: Tự động reserve/release/mark used wallets
6. **Instant Processing**: Xử lý ngay khi có code mới

## 📱 Code Format

Bot chỉ nhận codes:
- ✅ Đúng 8 ký tự
- ✅ Mix chữ và số (ví dụ: `ABC12345`)
- ❌ Loại bỏ toàn số (`12345678`)
- ❌ Loại bỏ toàn chữ (`ABCDEFGH`)

## ⚙️ Advanced Features

### Multiple Wallets
```bash
# Thêm nhiều ví cùng lúc
python sodex_real_bot.py
# Option 2 - Add Wallets
# Nhập từng private key, Enter để kết thúc
```

### Speed Configuration
- `CHECK_DELAY=100`: Check mỗi 0.1 giây
- `CHECK_DELAY=50`: Check mỗi 0.05 giây (cực nhanh)

### Reset Wallets
```bash
python sodex_real_bot.py
# Option 5 - Reset Used Wallets (chuyển used → available)
```

## 🐛 Troubleshooting

### Lỗi Telegram
- Kiểm tra API ID/Hash đúng
- Đảm bảo phone number format `+84xxxxxxxxx`
- Bot phải được add vào group cần theo dõi

### Lỗi Wallet
- Private key không có `0x` prefix
- Kiểm tra format đúng 64 ký tự hex

### Lỗi API
- Kiểm tra network connection
- API URL có thể thay đổi

## 📈 Performance

- **Speed**: Xử lý < 1 giây mỗi code
- **Capacity**: Hỗ trợ unlimited wallets
- **Reliability**: Auto retry, error handling
- **Efficiency**: Smart queue, no duplicate processing

## ⚠️ Lưu ý

1. **Bảo mật**: Giữ private keys an toàn
2. **Rate Limit**: Không spam API quá nhanh
3. **Backup**: Backup file `wallets.json`
4. **Monitor**: Theo dõi log files để debug

## 🔥 Quick Start

```bash
# 1. Add wallets
python sodex_real_bot.py → 2

# 2. Setup .env với Telegram config

# 3. Start bot  
python sodex_real_bot.py → 1

# 4. Bot sẽ tự động:
#    - Connect Telegram
#    - Monitor codes real-time  
#    - Process với multi-wallets
#    - Auto remove used wallets
#    - Log tất cả kết quả
```

🎯 **Mục tiêu**: Không bao giờ miss code, verify nhanh nhất có thể!
