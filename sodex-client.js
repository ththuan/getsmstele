const axios = require('axios');
const { ethers } = require('ethers');

class SodexClient {
    constructor(baseUrl, apiUrl, privateKey) {
        this.baseUrl = baseUrl;
        this.apiUrl = apiUrl;
        this.privateKey = privateKey;
        this.wallet = null;
        this.accessToken = null;
        this.cookies = null;
    }

    async initialize() {
        try {
            // Kiểm tra private key
            if (!this.privateKey || this.privateKey === 'your_private_key_here') {
                console.error('❌ Private key chưa được cấu hình trong file .env');
                return false;
            }

            // Xử lý private key (thêm 0x nếu chưa có)
            let formattedKey = this.privateKey;
            if (!formattedKey.startsWith('0x')) {
                formattedKey = '0x' + formattedKey;
            }

            // Kiểm tra độ dài private key (64 ký tự hex + 0x)
            if (formattedKey.length !== 66) {
                console.error('❌ Private key không hợp lệ (phải có 64 ký tự hex)');
                return false;
            }

            // Tạo wallet từ private key
            this.wallet = new ethers.Wallet(formattedKey);
            console.log(`🔐 Wallet address: ${this.wallet.address}`);
            return true;
        } catch (error) {
            console.error('❌ Lỗi khởi tạo wallet:', error.message);
            return false;
        }
    }

    async login() {
        try {
            console.log('🔄 Đang đăng nhập vào SoDEX...');

            // Bước 1: Lấy thông tin session
            const sessionResponse = await axios.get(`${this.baseUrl}/faucet`, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            });

            // Lưu cookies
            this.cookies = sessionResponse.headers['set-cookie']?.join('; ') || '';

            // Bước 2: Tạo signature để đăng nhập
            const message = `Login to SoDEX at ${Date.now()}`;
            const signature = await this.wallet.signMessage(message);

            // Bước 3: Gọi API đăng nhập
            const loginData = {
                address: this.wallet.address,
                message: message,
                signature: signature
            };

            const loginResponse = await axios.post(`${this.apiUrl}/auth/wallet-login`, loginData, {
                headers: {
                    'Content-Type': 'application/json',
                    'Cookie': this.cookies,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            });

            if (loginResponse.data && loginResponse.data.accessToken) {
                this.accessToken = loginResponse.data.accessToken;
                console.log('✅ Đăng nhập thành công!');
                return true;
            } else {
                console.error('❌ Đăng nhập thất bại: Không nhận được access token');
                return false;
            }

        } catch (error) {
            console.error('❌ Lỗi đăng nhập:', error.response?.data || error.message);
            return false;
        }
    }

    async verifyReferralCode(code) {
        try {
            console.log(`🔄 Đang verify referral code: ${code}`);

            if (!this.accessToken) {
                console.log('⚠️ Chưa đăng nhập, đang thực hiện đăng nhập...');
                const loginSuccess = await this.login();
                if (!loginSuccess) {
                    return false;
                }
            }

            // Gọi API verify referral code
            const verifyData = {
                referralCode: code
            };

            const response = await axios.post(`${this.apiUrl}/referral/verify`, verifyData, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Cookie': this.cookies,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            });

            if (response.data && response.data.success) {
                console.log(`✅ Verify thành công code: ${code}`);
                return true;
            } else {
                console.log(`❌ Verify thất bại code: ${code} - ${response.data?.message || 'Không rõ lý do'}`);
                return false;
            }

        } catch (error) {
            if (error.response?.status === 401) {
                console.log('🔄 Token hết hạn, đang đăng nhập lại...');
                this.accessToken = null;
                return await this.verifyReferralCode(code);
            }
            
            console.error(`❌ Lỗi verify code ${code}:`, error.response?.data || error.message);
            return false;
        }
    }

    async getWhitelistStatus() {
        try {
            if (!this.accessToken) {
                await this.login();
            }

            const response = await axios.get(`${this.apiUrl}/user/whitelist-status`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Cookie': this.cookies,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            });

            return response.data;
        } catch (error) {
            console.error('❌ Lỗi lấy whitelist status:', error.response?.data || error.message);
            return null;
        }
    }
}

module.exports = SodexClient;
