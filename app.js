require('dotenv').config();
const TelegramMonitor = require('./telegram-monitor');
const SodexClient = require('./sodex-client');

class SodexAutoReferral {
    constructor() {
        this.telegramMonitor = null;
        this.sodexClient = null;
        this.processedCodes = new Set(); // Tránh xử lý trùng lặp
    }

    async initialize() {
        console.log('🚀 Khởi động ứng dụng SoDEX Auto Referral...');
        
        // Kiểm tra cấu hình
        const missingConfig = [];
        if (!process.env.TELEGRAM_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN === 'your_telegram_bot_token_here') {
            missingConfig.push('TELEGRAM_BOT_TOKEN');
        }
        if (!process.env.TELEGRAM_GROUP_ID || process.env.TELEGRAM_GROUP_ID === 'your_telegram_group_id_here') {
            missingConfig.push('TELEGRAM_GROUP_ID');
        }
        if (!process.env.PRIVATE_KEY || process.env.PRIVATE_KEY === 'your_private_key_here') {
            missingConfig.push('PRIVATE_KEY');
        }

        if (missingConfig.length > 0) {
            console.error('❌ Thiếu cấu hình trong file .env:');
            missingConfig.forEach(key => console.log(`   - ${key}`));
            console.log('\n📖 Xem file SETUP_GUIDE.md để biết cách cấu hình chi tiết');
            return false;
        }

        // Khởi tạo SoDEX client
        this.sodexClient = new SodexClient(
            process.env.SODEX_BASE_URL || 'https://testnet.sodex.com',
            process.env.SODEX_API_URL || 'https://api.testnet.sodex.io',
            process.env.PRIVATE_KEY
        );

        const initSuccess = await this.sodexClient.initialize();
        if (!initSuccess) {
            console.error('❌ Không thể khởi tạo SoDEX client');
            return false;
        }

        // Đăng nhập vào SoDEX
        const loginSuccess = await this.sodexClient.login();
        if (!loginSuccess) {
            console.error('❌ Không thể đăng nhập vào SoDEX');
            return false;
        }

        // Khởi tạo Telegram monitor
        this.telegramMonitor = new TelegramMonitor(
            process.env.TELEGRAM_BOT_TOKEN,
            process.env.TELEGRAM_GROUP_ID
        );

        // Lắng nghe sự kiện tìm thấy referral code
        this.telegramMonitor.on('referralCodeFound', (code) => {
            this.handleReferralCode(code);
        });

        return true;
    }

    async handleReferralCode(code) {
        // Kiểm tra xem code đã được xử lý chưa
        if (this.processedCodes.has(code)) {
            console.log(`⏭️ Code ${code} đã được xử lý trước đó, bỏ qua`);
            return;
        }

        console.log(`🎯 Xử lý referral code: ${code}`);
        
        // Đánh dấu code đã được xử lý
        this.processedCodes.add(code);

        // Thử verify code
        const success = await this.sodexClient.verifyReferralCode(code);
        
        if (success) {
            console.log(`🎉 Thành công! Code ${code} đã được verify`);
            
            // Kiểm tra trạng thái whitelist
            const status = await this.sodexClient.getWhitelistStatus();
            if (status) {
                console.log('📊 Trạng thái whitelist:', status);
            }
        } else {
            console.log(`😞 Thất bại! Không thể verify code ${code}`);
        }

        // Delay trước khi xử lý code tiếp theo
        await this.delay(parseInt(process.env.CHECK_DELAY) || 5000);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async start() {
        const initSuccess = await this.initialize();
        if (!initSuccess) {
            process.exit(1);
        }

        console.log('✅ Ứng dụng đã sẵn sàng!');
        console.log('👂 Đang theo dõi Telegram để tìm referral code...');
        console.log(`📧 Wallet address: ${this.sodexClient.wallet.address}`);
        
        await this.telegramMonitor.start();

        // Xử lý thoát ứng dụng
        process.on('SIGINT', () => {
            console.log('\n🛑 Đang dừng ứng dụng...');
            this.telegramMonitor.stop();
            process.exit(0);
        });

        // Hiển thị hướng dẫn
        console.log('\n📋 HƯỚNG DẪN SỬ DỤNG:');
        console.log('1. Đảm bảo bot Telegram đã được thêm vào group');
        console.log('2. Bot sẽ tự động theo dõi các tin nhắn chứa referral code 8 ký tự');
        console.log('3. Khi tìm thấy code, bot sẽ tự động verify trên SoDEX');
        console.log('4. Nhấn Ctrl+C để dừng ứng dụng\n');
    }
}

// Khởi chạy ứng dụng
const app = new SodexAutoReferral();
app.start().catch(console.error);
