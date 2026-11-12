// ============================================================
// 大鹏官网 · API 配置（自动生成）
// 生成时间：2026-10-26 23:28:52
// 本机 IP：127.0.0.1 (IPV4)
// ============================================================

const API_CONFIG = {
    baseURL: 'http://127.0.0.1:3000/',
    ip: '127.0.0.1',
    ipType: 'ipv4',
    port: '3000',
    ollamaHost: 'http://127.0.0.1:11434/v1',
    status: 'ok'
};

// 兼容旧代码
const API_BASE = API_CONFIG.baseURL;
const API_READY = true;

console.log('📍 大鹏 API 地址:', API_BASE);
console.log('📍 Ollama 地址:', API_CONFIG.ollamaHost);
console.log('📍 IP 类型:', API_CONFIG.ipType.toUpperCase());
