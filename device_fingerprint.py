#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备指纹生成 Python 实现
抖音/百应平台设备伪造核心算法
"""

import time
import random
import string
import hashlib
import requests
from typing import Optional


class DeviceFingerprintGenerator:
    """设备指纹生成器"""
    
    # 浏览器UA池
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]
    
    def __init__(self):
        """初始化设备参数"""
        self.device_platform = "webapp"
        self.aid = "6383"
        self.channel = "channel_pc_web"
        self.version_code = "170400"
        self.version_name = "17.4.0"
        self.screen_width = "1920"
        self.screen_height = "1080"
        self.browser_language = "zh-CN"
        self.browser_platform = "MacIntel"
        self.browser_name = "Chrome"
        self.browser_version = "119.0.0.0"
        self.browser_online = "true"
        self.engine_name = "Blink"
        self.engine_version = "119.0.0.0"
        self.os_name = "Mac OS"
        self.os_version = "10.15.7"
        self.cpu_core_num = "8"
        self.device_memory = "8"
        self.platform = "PC"
        self.downlink = "10"
        self.effective_type = "4g"
        self.round_trip_time = "50"
        
        # 关键Cookie参数
        self.user_agent = random.choice(self.USER_AGENTS)
        self.nonce = ""
        self.ttwid = ""
        self.signature = ""
        self.sv_web_id = ""
        self.token = ""
        self.webid = ""
    
    def generate_sv_web_id(self) -> str:
        """
        生成s_v_web_id (verify_开头的36位字符串)
        
        Returns:
            verify_开头的字符串
        
        Example:
            verify_m04njd8y_ecYFX88p_LJSF_45ED_AYYO_L9cpMPlDEAJD
        """
        # 字符集
        chars = string.digits + string.ascii_letters
        
        # 生成时间戳部分 (base36编码)
        timestamp = int(time.time() * 1000) - 100000
        time_part = self._base36_encode(timestamp).lower()
        
        # 生成36位随机字符串 (带下划线分隔)
        parts = []
        for i in range(36):
            if i in [8, 13, 18, 23]:
                parts.append('_')
            elif i == 19:
                # 第19位特殊处理
                parts.append(random.choice(chars[8:16]))
            else:
                parts.append(random.choice(chars))
        
        # 拼接: verify_ + 时间戳 + _ + 随机字符串
        return f"verify_{time_part}_{''.join(parts)}"
    
    def generate_ms_token(self, length: int = 108) -> str:
        """
        生成msToken (108位随机字符串)
        
        Args:
            length: 长度 (默认108)
        
        Returns:
            随机字符串
        
        Example:
            oEUzc-rN48GV5vmSHPF8n5CazUHaNa8_k6DjlK_SiBM...
        """
        chars = string.digits + string.ascii_letters + "_-="
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_token(self, length: int = 32) -> str:
        """
        生成passport_csrf_token (32位随机字符串)
        
        Args:
            length: 长度 (默认32)
        
        Returns:
            随机字符串
        """
        chars = string.hexdigits.lower()
        return ''.join(random.choice(chars) for _ in range(length))
    
    def calculate_signature(self, nonce: str) -> str:
        """
        计算__ac_signature签名 (简化版)
        
        Args:
            nonce: __ac_nonce值
        
        Returns:
            签名字符串
        
        Note:
            这是简化版实现,完整版需要复杂的位运算
            实际使用建议直接从浏览器抓取
        """
        # 简化实现: 使用时间戳+nonce+ua生成签名
        timestamp = int(time.time())
        data = f"{timestamp}{nonce}{self.user_agent}"
        hash_obj = hashlib.md5(data.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # 添加固定前缀
        return f"_02B4Z6wo00f01{hash_hex[:40]}"
    
    def get_ttwid(self, session: Optional[requests.Session] = None) -> Optional[str]:
        """
        从字节跳动服务器获取ttwid
        
        Args:
            session: requests会话对象
        
        Returns:
            ttwid字符串或None
        """
        if session is None:
            session = requests.Session()
        
        try:
            url = "https://ttwid.bytedance.com/ttwid/union/register/"
            headers = {
                "User-Agent": self.user_agent,
                "Content-Type": "application/json"
            }
            data = {
                "region": "cn",
                "aid": 1768,
                "needFid": False,
                "service": "www.ixigua.com",
                "migrate_info": {"ticket": "", "source": "node"},
                "cbUrlProtocol": "https",
                "union": True
            }
            
            response = session.post(url, json=data, headers=headers, timeout=10)
            
            # 从Cookie中提取ttwid
            if 'ttwid' in response.cookies:
                return response.cookies['ttwid']
            
            return None
        except Exception as e:
            print(f"获取ttwid失败: {e}")
            return None
    
    def get_nonce(self, session: Optional[requests.Session] = None) -> Optional[str]:
        """
        从抖音首页获取__ac_nonce
        
        Args:
            session: requests会话对象
        
        Returns:
            __ac_nonce字符串或None
        """
        if session is None:
            session = requests.Session()
        
        try:
            url = "https://www.douyin.com/"
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            
            response = session.get(url, headers=headers, timeout=10)
            
            # 从Cookie中提取__ac_nonce
            if '__ac_nonce' in response.cookies:
                return response.cookies['__ac_nonce']
            
            return None
        except Exception as e:
            print(f"获取__ac_nonce失败: {e}")
            return None
    
    def generate(self, fetch_online: bool = False) -> dict:
        """
        生成完整的设备指纹
        
        Args:
            fetch_online: 是否从线上获取真实Cookie (需要网络)
        
        Returns:
            设备指纹字典
        """
        # 生成本地参数
        self.sv_web_id = self.generate_sv_web_id()
        self.token = self.generate_token()
        ms_token = self.generate_ms_token()
        
        # 如果需要,从线上获取真实Cookie
        if fetch_online:
            session = requests.Session()
            
            # 获取__ac_nonce
            nonce = self.get_nonce(session)
            if nonce:
                self.nonce = nonce
                self.signature = self.calculate_signature(nonce)
            
            # 获取ttwid
            ttwid = self.get_ttwid(session)
            if ttwid:
                self.ttwid = ttwid
        else:
            # 生成模拟值
            self.nonce = self.generate_token(21)
            self.signature = self.calculate_signature(self.nonce)
            self.ttwid = f"1%7C{self.generate_token(48)}%7C0"
        
        # 返回完整设备指纹
        return {
            # 浏览器参数
            "device_platform": self.device_platform,
            "aid": self.aid,
            "channel": self.channel,
            "version_code": self.version_code,
            "version_name": self.version_name,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "browser_language": self.browser_language,
            "browser_platform": self.browser_platform,
            "browser_name": self.browser_name,
            "browser_version": self.browser_version,
            "browser_online": self.browser_online,
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            
            # 系统参数
            "os_name": self.os_name,
            "os_version": self.os_version,
            "cpu_core_num": self.cpu_core_num,
            "device_memory": self.device_memory,
            "platform": self.platform,
            
            # 网络参数
            "downlink": self.downlink,
            "effective_type": self.effective_type,
            "round_trip_time": self.round_trip_time,
            
            # 关键Cookie
            "user_agent": self.user_agent,
            "nonce": self.nonce,
            "ttwid": self.ttwid,
            "signature": self.signature,
            "sv_web_id": self.sv_web_id,
            "token": self.token,
            "ms_token": ms_token,
        }
    
    def _base36_encode(self, number: int) -> str:
        """Base36编码"""
        if number == 0:
            return '0'
        
        chars = string.digits + string.ascii_lowercase
        result = []
        
        while number:
            number, remainder = divmod(number, 36)
            result.append(chars[remainder])
        
        return ''.join(reversed(result))


def generate_device_fingerprint(fetch_online: bool = False) -> dict:
    """
    便捷函数: 生成设备指纹
    
    Args:
        fetch_online: 是否从线上获取真实Cookie
    
    Returns:
        设备指纹字典
    
    Example:
        >>> fingerprint = generate_device_fingerprint()
        >>> print(fingerprint['sv_web_id'])
        >>> print(fingerprint['ms_token'])
    """
    generator = DeviceFingerprintGenerator()
    return generator.generate(fetch_online)


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("设备指纹生成测试")
    print("=" * 60)
    
    # 生成设备指纹 (本地模拟)
    print("\n1. 本地模拟生成:")
    print("-" * 60)
    fingerprint = generate_device_fingerprint(fetch_online=False)
    
    print(f"User-Agent: {fingerprint['user_agent'][:50]}...")
    print(f"SVWebId: {fingerprint['sv_web_id']}")
    print(f"msToken: {fingerprint['ms_token'][:50]}...")
    print(f"Token: {fingerprint['token']}")
    print(f"Nonce: {fingerprint['nonce']}")
    print(f"Signature: {fingerprint['signature'][:50]}...")
    print(f"Ttwid: {fingerprint['ttwid'][:50]}...")
    
    # 生成设备指纹 (从线上获取)
    print("\n2. 从线上获取真实Cookie:")
    print("-" * 60)
    print("提示: 需要网络连接,可能需要代理")
    
    try:
        fingerprint_online = generate_device_fingerprint(fetch_online=True)
        print(f"✓ Nonce (真实): {fingerprint_online['nonce']}")
        print(f"✓ Ttwid (真实): {fingerprint_online['ttwid'][:50]}...")
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        print("  (可能需要配置代理或网络不可达)")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
