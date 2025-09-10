# SoDEX Auto Referral Bot

Bot tự động theo dõi Telegram và verify referral code cho SoDEX.

## 🚀 Tính năng
- ✅ **Multi-wallet support**: Hỗ trợ 90+ private keys
- ✅ **Real-time monitoring**: Theo dõi Telegram group real-time
- ✅ **Auto verification**: Tự động verify codes 8 ký tự
- ✅ **Smart rotation**: Tự động đổi wallet sau verify thành công
- ✅ **Error handling**: Xử lý lỗi và retry tự động

## 📋 Yêu cầu
- Python 3.7+
- Telegram API credentials
- Private keys của wallets

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd sodex-auto-referral-bot
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình
1. Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Chỉnh sửa file `.env` với thông tin của bạn:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_GROUP_ID=-1002509849601
PRIVATE_KEY=key1,key2,key3...
```

### 4. Lấy Telegram API credentials
1. Truy cập https://my.telegram.org/apps
2. Tạo ứng dụng mới
3. Copy `api_id` và `api_hash` vào file `.env`

## 🎮 Sử dụng
```bash
python sodex_auto.py
```

Bot sẽ:
1. Load tất cả private keys từ `.env`
2. Kết nối Telegram và theo dõi group
3. Tự động detect và verify referral codes
4. Rotation wallets sau mỗi lần verify thành công

## 📁 Cấu trúc files
```
├── sodex_auto.py          # Bot chính
├── .env                   # Cấu hình (không commit)
├── .env.example          # Template cấu hình
├── requirements.txt       # Dependencies
├── .gitignore            # Git ignore rules
└── README.md             # Hướng dẫn này
```

## ⚠️ Lưu ý
- File `.env` chứa thông tin nhạy cảm, không được commit lên git
- Telegram session sẽ được tạo tự động khi chạy lần đầu
- Bot cần kết nối internet để hoạt động

## 🔧 Troubleshooting
- Nếu lỗi encoding: Đảm bảo file `.env` được save với UTF-8
- Nếu không connect được Telegram: Kiểm tra API credentials
- Nếu không detect code: Kiểm tra group ID và permissions

## 📊 Status
- ✅ **Stable**: Bot đã test và hoạt động ổn định
- ✅ **Multi-wallet**: Hỗ trợ 90+ wallets đồng thời  
- ✅ **Real-time**: Detect codes ngay lập tức từ Telegram
