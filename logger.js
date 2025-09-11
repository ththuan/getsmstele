class Logger {
    static info(message, data = null) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ℹ️  ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }

    static success(message, data = null) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ✅ ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }

    static error(message, error = null) {
        const timestamp = new Date().toISOString();
        console.error(`[${timestamp}] ❌ ${message}`, error ? error.stack || error : '');
    }

    static warning(message, data = null) {
        const timestamp = new Date().toISOString();
        console.warn(`[${timestamp}] ⚠️  ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }

    static debug(message, data = null) {
        const timestamp = new Date().toISOString();
        if (process.env.NODE_ENV === 'development') {
            console.log(`[${timestamp}] 🐛 ${message}`, data ? JSON.stringify(data, null, 2) : '');
        }
    }
}

module.exports = Logger;
