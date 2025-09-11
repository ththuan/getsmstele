require('dotenv').config();
const TelegramMonitor = require('./telegram-monitor');

class TelegramDemo {
    constructor() {
        this.monitor = null;
    }

    async start() {
        console.log('🤖 Demo Telegram Monitor\n');

        // Kiểm tra config Telegram
        if (!process.env.TELEGRAM_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN === 'your_telegram_bot_token_here') {
            console.log('❌ TELEGRAM_BOT_TOKEN chưa được cấu hình');
            console.log('📝 Để test, hãy:');
            console.log('1. Tạo bot với @BotFather');
            console.log('2. Cập nhật TELEGRAM_BOT_TOKEN trong file .env');
            console.log('3. Chạy lại: node demo-telegram.js\n');
            return;
        }

        this.monitor = new TelegramMonitor(
            process.env.TELEGRAM_BOT_TOKEN,
            process.env.TELEGRAM_GROUP_ID || 'demo'
        );

        // Lắng nghe sự kiện tìm thấy code
        this.monitor.on('referralCodeFound', (code) => {
            console.log(`🎯 DEMO: Tìm thấy code ${code} - sẽ verify trên SoDEX`);
        });

        console.log('✅ Telegram monitor đang khởi động...');
        console.log('📱 Hãy gửi tin nhắn chứa code 8 ký tự vào group/chat với bot');
        console.log('📋 Ví dụ: "Code mới: ABC12345" hoặc "ref: XYZ98765"');
        console.log('🛑 Nhấn Ctrl+C để dừng\n');

        await this.monitor.start();

        // Xử lý thoát
        process.on('SIGINT', () => {
            console.log('\n🛑 Dừng demo...');
            this.monitor.stop();
            process.exit(0);
        });
    }
}

// Test các pattern matching
function testPatterns() {
    console.log('🧪 Test Pattern Matching:\n');
    
    const testMessages = [
        'Code mới: ABC12345',
        'ref: XYZ98765', 
        'referral code: QWE45678',
        'Mã giới thiệu RTY56789',
        'ABC12345 là code mới',
        'Hôm nay có code ZXC09876',
        'Code không hợp lệ: 12345678', // toàn số
        'Code không hợp lệ: ABCDEFGH'  // toàn chữ
    ];

    // Tạo instance monitor để test
    const monitor = new TelegramMonitor('demo', 'demo');
    
    testMessages.forEach(msg => {
        const codes = monitor.extractReferralCodes(msg);
        console.log(`"${msg}"`);
        console.log(`  → Codes tìm thấy: ${codes.length > 0 ? codes.join(', ') : 'Không có'}\n`);
    });
}

// Chạy demo
if (process.argv.includes('--test-patterns')) {
    testPatterns();
} else {
    const demo = new TelegramDemo();
    demo.start().catch(console.error);
}
