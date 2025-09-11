const { Telegraf } = require('telegraf');
const EventEmitter = require('events');

class TelegramMonitor extends EventEmitter {
    constructor(botToken, groupId) {
        super();
        this.bot = new Telegraf(botToken);
        this.groupId = groupId;
        this.isMonitoring = false;
    }

    async start() {
        if (this.isMonitoring) return;

        console.log('🤖 Bắt đầu theo dõi Telegram...');

        // Lắng nghe tin nhắn trong group
        this.bot.on('text', (ctx) => {
            try {
                const message = ctx.message;
                const chatId = message.chat.id.toString();
                
                // Kiểm tra xem tin nhắn có từ group được chỉ định không
                if (chatId === this.groupId || message.chat.username) {
                    const text = message.text;
                    console.log(`📱 Nhận tin nhắn: ${text}`);
                    
                    // Tìm referral code 8 ký tự (có thể là chữ và số)
                    const referralCodes = this.extractReferralCodes(text);
                    
                    if (referralCodes.length > 0) {
                        referralCodes.forEach(code => {
                            console.log(`🎯 Tìm thấy referral code: ${code}`);
                            this.emit('referralCodeFound', code);
                        });
                    }
                }
            } catch (error) {
                console.error('❌ Lỗi xử lý tin nhắn Telegram:', error);
            }
        });

        // Bắt đầu bot
        await this.bot.launch();
        this.isMonitoring = true;
        
        console.log('✅ Telegram monitor đã khởi động');
    }

    extractReferralCodes(text) {
        const codes = [];
        
        // Pattern 1: Tìm code 8 ký tự được đề cập cụ thể
        const patterns = [
            /referral[:\s]*([A-Za-z0-9]{8})/gi,
            /ref[:\s]*([A-Za-z0-9]{8})/gi,
            /code[:\s]*([A-Za-z0-9]{8})/gi,
            /\b([A-Za-z0-9]{8})\b/g  // Bất kỳ chuỗi 8 ký tự nào đứng một mình
        ];

        patterns.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const code = match[1];
                // Kiểm tra xem code có hợp lệ không (không phải toàn số hoặc toàn chữ)
                if (this.isValidReferralCode(code)) {
                    codes.push(code);
                }
            }
        });

        // Loại bỏ duplicate
        return [...new Set(codes)];
    }

    isValidReferralCode(code) {
        // Kiểm tra độ dài
        if (code.length !== 8) return false;
        
        // Kiểm tra có cả số và chữ
        const hasNumber = /\d/.test(code);
        const hasLetter = /[A-Za-z]/.test(code);
        
        // Phải có cả số và chữ (không được toàn số hoặc toàn chữ)
        return hasNumber && hasLetter;
    }

    stop() {
        if (this.bot) {
            this.bot.stop();
            this.isMonitoring = false;
            console.log('🛑 Dừng theo dõi Telegram');
        }
    }
}

module.exports = TelegramMonitor;
