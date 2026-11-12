#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大鹏官网 · API 地址自动生成器（支持 IPv4/IPv6 双栈）
运行：python generate_api.py
"""

import socket
import os
import json
import sys


# ==================== 获取 IPv4 地址 ====================
def get_local_ipv4():
    """获取本机局域网 IPv4 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    return None


# ==================== 获取 IPv6 地址 ====================
def get_local_ipv6():
    """获取本机局域网 IPv6 地址"""
    try:
        # 方法1：连接外部 IPv6 地址
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(('2001:4860:4860::8888', 80))  # Google IPv6 DNS
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith('::1') and not ip.startswith('fe80'):
            return ip
    except Exception:
        pass

    try:
        # 方法2：通过 getaddrinfo 获取
        hostname = socket.gethostname()
        results = socket.getaddrinfo(hostname, None, socket.AF_INET6)
        for result in results:
            ip = result[4][0]
            if ip and not ip.startswith('::1') and not ip.startswith('fe80'):
                # 去掉 IPv6 地址的 scope id（如 %eth0）
                if '%' in ip:
                    ip = ip.split('%')[0]
                return ip
    except Exception:
        pass

    return None


# ==================== 测试 IPv4 是否可连 ====================
def test_ipv4_connection(ip, port='3000', timeout=2):
    """测试 IPv4 地址是否可以连接"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, int(port)))
        s.close()
        return result == 0
    except Exception:
        return False


# ==================== 测试 IPv6 是否可连 ====================
def test_ipv6_connection(ip, port='3000', timeout=2):
    """测试 IPv6 地址是否可以连接"""
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, int(port)))
        s.close()
        return result == 0
    except Exception:
        return False


# ==================== 选择可用的 IP ====================
def choose_ip(port='3000'):
    """优先 IPv4，连不上时切换 IPv6"""
    ipv4 = get_local_ipv4()
    ipv6 = get_local_ipv6()

    print(f'🔍 检测到 IPv4: {ipv4 or "无"}')
    print(f'🔍 检测到 IPv6: {ipv6 or "无"}')

    # 优先测试 IPv4
    if ipv4:
        print(f'⏳ 测试 IPv4 连接 ({ipv4}:{port})...')
        if test_ipv4_connection(ipv4, port):
            print(f'✅ IPv4 可连接，使用 IPv4')
            return ipv4, 'ipv4'
        else:
            print(f'⚠️ IPv4 连接失败，尝试 IPv6')

    # IPv4 不行，测试 IPv6
    if ipv6:
        print(f'⏳ 测试 IPv6 连接 ([{ipv6}]:{port})...')
        if test_ipv6_connection(ipv6, port):
            print(f'✅ IPv6 可连接，使用 IPv6')
            return ipv6, 'ipv6'
        else:
            print(f'⚠️ IPv6 连接也失败，使用 IPv6（默认）')
            return ipv6, 'ipv6'

    # 都没检测到，兜底
    print(f'⚠️ 未检测到可用的 IPv4/IPv6，使用 127.0.0.1')
    return '127.0.0.1', 'ipv4'


# ==================== 生成配置 ====================
def generate_config():
    """生成 API 配置文件"""
    port = sys.argv[1] if len(sys.argv) > 1 else '3000'

    # 选择 IP
    ip, ip_type = choose_ip(port)

    # 构建 API 地址（IPv6 需要加中括号）
    if ip_type == 'ipv6':
        api_base = f'http://[{ip}]:{port}/'
        ollama_host = f'http://[{ip}]:11434/v1'
    else:
        api_base = f'http://{ip}:{port}/'
        ollama_host = f'http://{ip}:11434/v1'

    # 生成 JS 配置文件
    from datetime import datetime
    js_content = f'''// ============================================================
// 大鹏官网 · API 配置（自动生成）
// 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 本机 IP：{ip} ({ip_type.upper()})
// ============================================================

const API_CONFIG = {{
    baseURL: '{api_base}',
    ip: '{ip}',
    ipType: '{ip_type}',
    port: '{port}',
    ollamaHost: '{ollama_host}',
    status: 'ok'
}};

// 兼容旧代码
const API_BASE = API_CONFIG.baseURL;
const API_READY = true;

console.log('📍 大鹏 API 地址:', API_BASE);
console.log('📍 Ollama 地址:', API_CONFIG.ollamaHost);
console.log('📍 IP 类型:', API_CONFIG.ipType.toUpperCase());
'''

    # 写入配置文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'api_config.js')

    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

    # 同时生成 JSON 格式（备用）
    json_config = {
        'ip': ip,
        'ipType': ip_type,
        'port': port,
        'baseURL': api_base,
        'ollamaHost': ollama_host
    }
    json_path = os.path.join(script_dir, 'api_config.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_config, f, indent=4, ensure_ascii=False)

    # 输出结果
    print('')
    print('=' * 60)
    print('✅ API 配置生成成功！')
    print('=' * 60)
    print(f'📍 IP 类型: {ip_type.upper()}')
    print(f'📍 本机 IP: {ip}')
    print(f'📍 API 地址: {api_base}')
    print(f'📍 Ollama 地址: {ollama_host}')
    print(f'📄 配置文件: {config_path}')
    print(f'📄 JSON 配置: {json_path}')
    print('=' * 60)
    print('👉 现在打开大鹏官网即可使用')
    print('👉 如果 IP 变化，重新运行此脚本即可')
    print('')


if __name__ == '__main__':
    generate_config()