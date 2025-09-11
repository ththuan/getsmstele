const { Telegraf } = require('telegraf');
const axios = require('axios');
const { ethers } = require('ethers');
const SoDEXAPI = require('./sodex-api');
const Logger = require('./logger');
require('dotenv').config();

class SoDEXAutoReferral {
    constructor() {
        this.bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
        this.wallet = null;
        this.authToken = null;
        this.processedCodes = new Set(); // Lưu trữ các code đã xử lý
        this.sodexAPI = new SoDEXAPI(process.env.SODEX_BASE_URL, process.env.SODEX_API_URL);
        this.lastLoginTime = null;
        this.loginInterval = 3600000; // 1 giờ
        
        this.validateConfig();
        this.initializeWallet();
        this.setupTelegramBot();
    }

    // Kiểm tra cấu hình
    validateConfig() {
        const required = ['TELEGRAM_BOT_TOKEN', 'PRIVATE_KEY', 'SODEX_BASE_URL', 'SODEX_API_URL'];
        for (const key of required) {
            if (!process.env[key]) {
                Logger.error(`Thiếu cấu hình: ${key}`);
                process.exit(1);
            }
        }
        Logger.success('Cấu hình hợp lệ');
    }

    // Khởi tạo ví từ private key
    initializeWallet() {
        try {
            // Thêm 0x nếu chưa có
            let privateKey = process.env.PRIVATE_KEY;
            if (!privateKey.startsWith('0x')) {
                privateKey = '0x' + privateKey;
            }
            
            this.wallet = new ethers.Wallet(privateKey);
            Logger.success(`Ví đã được khởi tạo: ${this.wallet.address}`);
        } catch (error) {
            Logger.error('Lỗi khởi tạo ví:', error);
            process.exit(1);
        }
    }

    // Thiết lập Telegram bot để lắng nghe tin nhắn
    setupTelegramBot() {
        // Lắng nghe tất cả tin nhắn văn bản
        this.bot.on('text', async (ctx) => {
            const message = ctx.message.text;
            const chatId = ctx.chat.id;
            
            // Log thông tin chat để debug
            if (!process.env.TELEGRAM_GROUP_ID) {
                Logger.info(`Chat ID: ${chatId} (Thêm vào .env nếu đây là nhóm đích)`);
            }
            
            // Kiểm tra xem có phải nhóm được cấu hình không
            if (process.env.TELEGRAM_GROUP_ID && chatId.toString() !== process.env.TELEGRAM_GROUP_ID) {
                return;
            }

            Logger.info(`Nhận tin nhắn từ ${ctx.from.username || ctx.from.first_name}: ${message.substring(0, 100)}...`);
            
            // Tìm mã referral 8 ký tự
            const referralCodes = this.extractReferralCodes(message);
            
            if (referralCodes.length > 0) {
                Logger.info(`Tìm thấy ${referralCodes.length} mã potencial: ${referralCodes.join(', ')}`);
            }
            
            for (const code of referralCodes) {
                if (!this.processedCodes.has(code)) {
                    Logger.info(`Phát hiện mã referral mới: ${code}`);
                    await this.processReferralCode(code);
                    this.processedCodes.add(code);
                } else {
                    Logger.debug(`Mã ${code} đã được xử lý trước đó`);
                }
            }
        });

        // Xử lý lỗi bot
        this.bot.catch((err, ctx) => {
            Logger.error('Lỗi Telegram bot:', err);
        });

        this.bot.launch();
        Logger.success('Telegram bot đã được khởi động');
    }

    // Trích xuất mã referral 8 ký tự từ tin nhắn
    extractReferralCodes(text) {
        // Tìm các chuỗi 8 ký tự (chữ và số)
        const regex = /\b[A-Za-z0-9]{8}\b/g;
        const matches = text.match(regex) || [];
        
        // Lọc bỏ các chuỗi có vẻ không phải mã referral
        return matches.filter(code => {
            // Loại bỏ các chuỗi toàn số hoặc toàn chữ
            const hasNumber = /\d/.test(code);
            const hasLetter = /[A-Za-z]/.test(code);
            return hasNumber && hasLetter;
        });
    }

    // Đăng nhập vào SoDEX bằng wallet
    async loginToSoDEX() {
        try {
            Logger.info('Đang đăng nhập vào SoDEX...');
            
            // Kiểm tra xem có cần đăng nhập lại không
            if (this.authToken && this.lastLoginTime && 
                (Date.now() - this.lastLoginTime) < this.loginInterval) {
                Logger.debug('Token vẫn còn hợp lệ, bỏ qua đăng nhập');
                return true;
            }
            
            // Tạo message để ký
            const timestamp = Date.now();
            const message = `SoDEX Login ${timestamp}`;
            
            // Ký message
            const signature = await this.wallet.signMessage(message);
            
            // Thử các endpoint khác nhau
            const loginEndpoints = [
                '/auth/wallet-login',
                '/auth/login',
                '/api/auth/wallet-login',
                '/api/v1/auth/wallet-login'
            ];

            for (const endpoint of loginEndpoints) {
                try {
                    Logger.debug(`Thử endpoint: ${endpoint}`);
                    
                    const loginResponse = await axios.post(`${process.env.SODEX_API_URL}${endpoint}`, {
                        address: this.wallet.address,
                        signature: signature,
                        message: message,
                        timestamp: timestamp
                    }, {
                        timeout: 10000,
                        headers: {
                            'Content-Type': 'application/json',
                            'User-Agent': 'SoDEX-Auto-Bot/1.0'
                        }
                    });

                    if (loginResponse.data && (loginResponse.data.success || loginResponse.data.token)) {
                        this.authToken = loginResponse.data.token || loginResponse.data.data?.token;
                        this.lastLoginTime = Date.now();
                        this.sodexAPI.setAuthToken(this.authToken);
                        Logger.success('Đăng nhập SoDEX thành công');
                        return true;
                    }
                } catch (endpointError) {
                    Logger.debug(`Endpoint ${endpoint} thất bại: ${endpointError.message}`);
                    continue;
                }
            }
            
            Logger.error('Tất cả endpoint đăng nhập đều thất bại');
            return false;
            
        } catch (error) {
            Logger.error('Lỗi đăng nhập SoDEX:', error);
            return false;
        }
    }

    // Verify mã referral
    async verifyReferralCode(code) {
        const verifyEndpoints = [
            '/referral/verify',
            '/api/referral/verify',
            '/api/v1/referral/verify',
            '/whitelist/verify',
            '/api/whitelist/verify'
        ];

        for (const endpoint of verifyEndpoints) {
            try {
                Logger.debug(`Thử verify endpoint: ${endpoint}`);
                
                const response = await axios.post(
                    `${process.env.SODEX_API_URL}${endpoint}`,
                    { 
                        referralCode: code,
                        code: code,
                        inviteCode: code
                    },
                    {
                        headers: {
                            'Authorization': `Bearer ${this.authToken}`,
                            'Content-Type': 'application/json',
                            'User-Agent': 'SoDEX-Auto-Bot/1.0'
                        },
                        timeout: 10000
                    }
                );

                if (response.data && (response.data.success || response.status === 200)) {
                    Logger.success(`Verify thành công mã: ${code} qua ${endpoint}`);
                    return true;
                }
            } catch (error) {
                Logger.debug(`Endpoint ${endpoint} thất bại: ${error.response?.data?.message || error.message}`);
                
                // Nếu lỗi là mã đã được sử dụng hoặc không hợp lệ, không cần thử endpoint khác
                const errorMsg = error.response?.data?.message || error.message;
                if (errorMsg.includes('already') || errorMsg.includes('invalid') || errorMsg.includes('expired')) {
                    Logger.warning(`Mã ${code} không hợp lệ hoặc đã được sử dụng: ${errorMsg}`);
                    return false;
                }
                continue;
            }
        }
        
        Logger.error(`Tất cả endpoint verify đều thất bại cho mã: ${code}`);
        return false;
    }

    // Xử lý mã referral
    async processReferralCode(code) {
        try {
            Logger.info(`Bắt đầu xử lý mã referral: ${code}`);
            
            // Đăng nhập nếu chưa có token hoặc token hết hạn
            if (!this.authToken || !this.lastLoginTime || 
                (Date.now() - this.lastLoginTime) > this.loginInterval) {
                Logger.info('Cần đăng nhập lại...');
                const loginSuccess = await this.loginToSoDEX();
                if (!loginSuccess) {
                    Logger.error(`Không thể đăng nhập, bỏ qua mã: ${code}`);
                    return false;
                }
            }

            // Verify mã referral
            const success = await this.verifyReferralCode(code);
            
            if (success) {
                Logger.success(`✨ Đã verify thành công mã: ${code}`);
                
                // Kiểm tra trạng thái tài khoản sau khi verify
                try {
                    const accountInfo = await this.sodexAPI.getAccountInfo();
                    Logger.info('Thông tin tài khoản:', accountInfo);
                } catch (error) {
                    Logger.debug('Không thể lấy thông tin tài khoản:', error.message);
                }
            } else {
                Logger.warning(`Không thể verify mã: ${code}`);
            }
            
            // Delay để tránh spam
            await this.delay(parseInt(process.env.CHECK_DELAY) || 5000);
            return success;
            
        } catch (error) {
            Logger.error('Lỗi xử lý mã referral:', error);
            return false;
        }
    }

    // Helper function để delay
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Bắt đầu bot
    async start() {
        Logger.info('🚀 Khởi động SoDEX Auto Referral Bot...');
        Logger.info(`📱 Địa chỉ ví: ${this.wallet.address}`);
        
        // Thử đăng nhập lần đầu
        const loginSuccess = await this.loginToSoDEX();
        if (loginSuccess) {
            Logger.success('Đăng nhập thành công, bot sẵn sàng hoạt động');
        } else {
            Logger.warning('Không thể đăng nhập lần đầu, sẽ thử lại khi có mã referral');
        }
        
        // Thiết lập auto-login định kỳ
        setInterval(async () => {
            Logger.debug('Kiểm tra và làm mới token...');
            await this.loginToSoDEX();
        }, this.loginInterval);
        
        Logger.success('✅ Bot đã sẵn sàng. Đang theo dõi nhóm Telegram...');
        if (process.env.TELEGRAM_GROUP_ID) {
            Logger.info(`🎯 Theo dõi nhóm: ${process.env.TELEGRAM_GROUP_ID}`);
        } else {
            Logger.warning('⚠️  TELEGRAM_GROUP_ID chưa được cấu hình, bot sẽ theo dõi tất cả chat');
        }
        
        // Graceful shutdown
        process.once('SIGINT', () => {
            Logger.info('Đang tắt bot...');
            this.bot.stop('SIGINT');
        });
        process.once('SIGTERM', () => {
            Logger.info('Đang tắt bot...');
            this.bot.stop('SIGTERM');
        });
    }
}

// Khởi động bot
const bot = new SoDEXAutoReferral();
bot.start().catch(console.error);
