const axios = require('axios');

class SoDEXAPI {
    constructor(baseUrl, apiUrl) {
        this.baseUrl = baseUrl;
        this.apiUrl = apiUrl;
        this.authToken = null;
    }

    // Set auth token
    setAuthToken(token) {
        this.authToken = token;
    }

    // Lấy thông tin tài khoản
    async getAccountInfo() {
        try {
            const response = await axios.get(`${this.apiUrl}/user/profile`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            throw new Error(`Lỗi lấy thông tin tài khoản: ${error.response?.data?.message || error.message}`);
        }
    }

    // Lấy danh sách referral codes đã sử dụng
    async getUsedReferralCodes() {
        try {
            const response = await axios.get(`${this.apiUrl}/referral/history`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            throw new Error(`Lỗi lấy lịch sử referral: ${error.response?.data?.message || error.message}`);
        }
    }

    // Kiểm tra whitelist status
    async checkWhitelistStatus() {
        try {
            const response = await axios.get(`${this.apiUrl}/whitelist/status`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            throw new Error(`Lỗi kiểm tra whitelist: ${error.response?.data?.message || error.message}`);
        }
    }
}

module.exports = SoDEXAPI;
