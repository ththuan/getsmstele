require('dotenv').config();
const SodexClient = require('./sodex-client');

async function testSodexClient() {
    console.log('🧪 Test SoDEX Client...\n');

    // Test 1: Khởi tạo với private key giả
    console.log('Test 1: Private key validation');
    const badClient = new SodexClient(
        'https://testnet.sodex.com',
        'https://api.testnet.sodex.io', 
        'your_private_key_here'
    );
    
    const badResult = await badClient.initialize();
    console.log(`Kết quả với private key giả: ${badResult ? '✅' : '❌'}\n`);

    // Test 2: Khởi tạo với private key thật (nếu có)
    if (process.env.PRIVATE_KEY && process.env.PRIVATE_KEY !== 'your_private_key_here') {
        console.log('Test 2: Private key thật');
        const goodClient = new SodexClient(
            process.env.SODEX_BASE_URL || 'https://testnet.sodex.com',
            process.env.SODEX_API_URL || 'https://api.testnet.sodex.io',
            process.env.PRIVATE_KEY
        );
        
        const goodResult = await goodClient.initialize();
        console.log(`Kết quả với private key thật: ${goodResult ? '✅' : '❌'}`);
        
        if (goodResult) {
            console.log(`Wallet address: ${goodClient.wallet.address}`);
            
            // Test đăng nhập
            console.log('\nTest 3: Đăng nhập SoDEX');
            const loginResult = await goodClient.login();
            console.log(`Kết quả đăng nhập: ${loginResult ? '✅' : '❌'}`);
        }
    } else {
        console.log('Test 2: Bỏ qua (chưa cấu hình private key thật)');
    }

    console.log('\n🏁 Test hoàn thành!');
}

testSodexClient().catch(console.error);
