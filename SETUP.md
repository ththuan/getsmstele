# Hướng dẫn cài đặt và cấu hình Bot SoDEX Auto Referral

## Bước 1: Chuẩn bị môi trường

### Cài đặt Node.js
1. Tải Node.js từ: https://nodejs.org/
2. Chọn phiên bản LTS (Long Term Support)
3. Cài đặt và kiểm tra: `node --version`

## Bước 2: Tạo Telegram Bot

### 2.1 Tạo Bot với BotFather
1. Mở Telegram và tìm `@BotFather`
2. Gửi lệnh: `/start`
3. Gửi lệnh: `/newbot`
4. Đặt tên cho bot (ví dụ: "SoDEX Auto Referral Bot")
5. Đặt username cho bot (phải kết thúc bằng "bot", ví dụ: "sodex_auto_referral_bot")
6. Lưu TOKEN mà BotFather cung cấp

### 2.2 Lấy Group ID
1. Thêm bot vào nhóm Telegram mà bạn muốn theo dõi
2. Gửi tin nhắn bất kỳ trong nhóm
3. Chạy bot lần đầu (không cần cấu hình GROUP_ID), bot sẽ in ra Chat ID
4. Sao chép Chat ID và thêm vào file .env

## Bước 3: Cấu hình Private Key

### 3.1 Xuất Private Key từ ví
**MetaMask:**
1. Mở MetaMask
2. Click vào menu (3 chấm)
3. Chọn "Account details"
4. Click "Export Private Key"
5. Nhập password và sao chép key

**Trust Wallet:**
1. Mở Trust Wallet
2. Chọn ví cần xuất
3. Vào Settings > Wallets
4. Chọn ví và click "Show Recovery Phrase" hoặc "Private Key"

### 3.2 Lưu ý bảo mật
- ⚠️ KHÔNG BAO GIỜ chia sẻ private key
- 🔒 Chỉ sử dụng ví test hoặc ví có ít tiền
- 🛡️ Backup file .env an toàn

## Bước 4: Cấu hình file .env

Tạo file `.env` với nội dung:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_GROUP_ID=-1001234567890

# Wallet Private Key (không bao gồm 0x)
PRIVATE_KEY=your_private_key_here_without_0x

# SoDEX URLs
SODEX_BASE_URL=https://testnet.sodex.io
SODEX_API_URL=https://api.testnet.sodex.io

# Bot Settings
CHECK_DELAY=5000
NODE_ENV=production
```

## Bước 5: Cài đặt và chạy

### 5.1 Cài đặt dependencies
```bash
cd "e:\nodejs\get code"
npm install
```

### 5.2 Kiểm tra cấu hình
```bash
# Kiểm tra kết nối ví
node -e "
const { ethers } = require('ethers');
require('dotenv').config();
const wallet = new ethers.Wallet('0x' + process.env.PRIVATE_KEY);
console.log('Địa chỉ ví:', wallet.address);
"
```

### 5.3 Chạy bot
```bash
npm start
```

## Bước 6: Kiểm tra hoạt động

### 6.1 Kiểm tra log
Bot sẽ hiển thị:
- ✅ Ví đã được khởi tạo: 0x...
- ✅ Đăng nhập SoDEX thành công  
- ✅ Bot đã sẵn sàng. Đang theo dõi nhóm Telegram...

### 6.2 Test với mã referral
1. Gửi một tin nhắn có chứa mã 8 ký tự vào nhóm
2. Kiểm tra log bot có phát hiện và xử lý không

## Xử lý sự cố thường gặp

### Lỗi "Invalid private key"
- Kiểm tra private key không có 0x ở đầu
- Đảm bảo private key có đúng 64 ký tự hex

### Lỗi "Unauthorized" khi đăng nhập SoDEX
- Kiểm tra URL API có đúng không
- Thử các mainnet/testnet khác nhau

### Bot không phản hồi tin nhắn Telegram
- Kiểm tra TOKEN bot có đúng không
- Đảm bảo bot đã được thêm vào nhóm
- Kiểm tra GROUP_ID có chính xác không

### Lỗi "ECONNRESET" hoặc timeout
- Kiểm tra kết nối internet
- Thử tăng timeout trong code
- Kiểm tra firewall/proxy

## Tối ưu hóa

### Chạy như service trên Windows
Tạo file `run-bot.bat`:
```batch
@echo off
cd /d "e:\nodejs\get code"
:start
npm start
echo Bot stopped, restarting in 10 seconds...
timeout /t 10 /nobreak
goto start
```

### Chạy với PM2 (Process Manager)
```bash
npm install -g pm2
pm2 start index.js --name "sodex-auto-referral"
pm2 startup
pm2 save
```

## Monitoring và Logs

### Xem logs real-time
```bash
# Với PM2
pm2 logs sodex-auto-referral

# Hoặc chuyển output vào file
npm start > bot.log 2>&1
```

### Kiểm tra trạng thái
```bash
pm2 status
pm2 monit
```
