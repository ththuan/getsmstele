const { ethers } = require('ethers');
const { Telegraf } = require('telegraf');
require('dotenv').config();

console.log('🔍 Kiểm tra cấu hình bot...\n');

// Kiểm tra biến môi trường
const requiredVars = ['TELEGRAM_BOT_TOKEN', 'PRIVATE_KEY', 'SODEX_BASE_URL', 'SODEX_API_URL'];
let configValid = true;

console.log('📋 Kiểm tra biến môi trường:');
for (const varName of requiredVars) {
    if (process.env[varName]) {
        console.log(`  ✅ ${varName}: ${varName === 'PRIVATE_KEY' ? '[HIDDEN]' : process.env[varName]}`);
    } else {
        console.log(`  ❌ ${varName}: THIẾU`);
        configValid = false;
    }
}

if (!configValid) {
    console.log('\n❌ Vui lòng cấu hình đầy đủ file .env');
    process.exit(1);
}

// Kiểm tra private key và ví
console.log('\n🔐 Kiểm tra ví:');
try {
    let privateKey = process.env.PRIVATE_KEY;
    if (!privateKey.startsWith('0x')) {
        privateKey = '0x' + privateKey;
    }
    
    const wallet = new ethers.Wallet(privateKey);
    console.log(`  ✅ Private key hợp lệ`);
    console.log(`  ✅ Địa chỉ ví: ${wallet.address}`);
} catch (error) {
    console.log(`  ❌ Private key không hợp lệ: ${error.message}`);
    process.exit(1);
}

// Kiểm tra Telegram bot token
console.log('\n🤖 Kiểm tra Telegram bot:');
try {
    const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
    
    // Test connection
    bot.telegram.getMe()
        .then(botInfo => {
            console.log(`  ✅ Bot token hợp lệ`);
            console.log(`  ✅ Bot name: @${botInfo.username}`);
            console.log(`  ✅ Bot ID: ${botInfo.id}`);
            
            if (process.env.TELEGRAM_GROUP_ID) {
                console.log(`  ℹ️  Sẽ theo dõi group: ${process.env.TELEGRAM_GROUP_ID}`);
            } else {
                console.log(`  ⚠️  Sẽ theo dõi tất cả chat (thiếu TELEGRAM_GROUP_ID)`);
            }
            
            console.log('\n✅ Tất cả cấu hình đều hợp lệ! Bot sẵn sàng chạy.');
            console.log('\n🚀 Để chạy bot, sử dụng lệnh: npm start');
            process.exit(0);
        })
        .catch(error => {
            console.log(`  ❌ Bot token không hợp lệ: ${error.message}`);
            process.exit(1);
        });
        
} catch (error) {
    console.log(`  ❌ Lỗi khởi tạo bot: ${error.message}`);
    process.exit(1);
}
