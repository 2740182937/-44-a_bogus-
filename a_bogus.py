#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
a_bogus 签名算法 Python 实现
抖音/百应平台反爬虫核心算法
"""

import time
import base64
from Crypto.Cipher import ARC4
from gmssl import sm3


class ABogusGenerator:
    """a_bogus 签名生成器"""
    
    # 自定义Base64编码表1 (用于UA编码)
    BASE64_VARIATION1 = "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe"
    
    # 自定义Base64编码表2 (用于最终输出)
    BASE64_VARIATION2 = "Dkdpgh2ZmsQB80/MfvV36XI1R45-WUAlEixNLwoqYTOPuzKFjJnry79HbGcaStCe"
    
    # RC4加密密钥
    RC4_KEY1 = bytes([0, 1, 4])    # 用于UA加密
    RC4_KEY2 = bytes([131])        # 用于数据加密
    
    # 空body的SM3哈希值 (预计算)
    EMPTY_BODY_SM3 = bytes([
        83, 69, 109, 82, 24, 153, 247, 200, 198, 128, 168, 162,
        244, 70, 5, 146, 100, 77, 138, 136, 44, 216, 207, 115,
        118, 120, 152, 238, 238, 224, 239, 43
    ])
    
    # 字节重排索引 (关键混淆步骤)
    RIGHT_INDEX = [
        0, 1, 5, 9, 13, 17, 19, 21, 2, 6, 10, 14, 18, 20, 22,
        3, 7, 11, 15, 4, 8, 12, 16, 23, 24, 25, 26, 27, 28
    ]
    
    def __init__(self):
        """初始化"""
        # 创建自定义Base64编码器
        self.base64_encoder1 = self._create_base64_encoder(self.BASE64_VARIATION1)
        self.base64_encoder2 = self._create_base64_encoder(self.BASE64_VARIATION2)
    
    def _create_base64_encoder(self, alphabet):
        """创建自定义Base64编码器"""
        class CustomBase64:
            def __init__(self, alphabet):
                self.alphabet = alphabet
                self.standard = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
                self.trans_table = str.maketrans(self.standard, alphabet)
            
            def encode(self, data):
                """编码"""
                standard_b64 = base64.b64encode(data).decode('utf-8')
                return standard_b64.translate(self.trans_table)
        
        return CustomBase64(alphabet)
    
    def _sm3_hash(self, data):
        """SM3哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return bytes.fromhex(sm3.sm3_hash(list(data)))
    
    def _rc4_encrypt(self, key, data):
        """RC4加密"""
        cipher = ARC4.new(key)
        return cipher.encrypt(data)
    
    def _put_int64(self, value):
        """将int64转为4字节大端序"""
        return bytes([
            (value >> 24) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF
        ])
    
    def _put_ts3(self, ts):
        """特殊的时间戳编码 (位运算混淆)"""
        return bytes([
            ((ts & 255 & 170) | 1) & 0xFF,
            ((ts & 255 & 85) | 2) & 0xFF,
            (((ts >> 8) & 255 & 170) | 64) & 0xFF,
            (((ts >> 8) & 255 & 85) | 2) & 0xFF
        ])
    
    def _xor_sum(self, arr):
        """计算异或校验和"""
        result = arr[0]
        for i in range(1, len(arr)):
            result ^= arr[i]
        return result
    
    def sign(self, query, body="", user_agent=""):
        """
        生成a_bogus签名
        
        Args:
            query: URL查询参数 (不包含a_bogus)
            body: POST请求体 (GET请求为空字符串)
            user_agent: 浏览器UA
        
        Returns:
            a_bogus签名字符串
        """
        # ========== 步骤1: 生成时间戳1 ==========
        ts1 = int(time.time() * 1000)
        
        # ========== 步骤2: 对body进行SM3双重哈希 ==========
        if len(body) == 0:
            body_sm3 = self.EMPTY_BODY_SM3
        else:
            body_sm3 = self._sm3_hash(self._sm3_hash((body + "bds").encode('utf-8')))
        
        # ========== 步骤3: 对query进行SM3双重哈希 ==========
        query_sm3 = self._sm3_hash(self._sm3_hash((query + "bds").encode('utf-8')))
        
        # ========== 步骤4: 对UserAgent进行RC4加密+Base64+SM3 ==========
        ua_encrypted = self._rc4_encrypt(self.RC4_KEY1, user_agent.encode('utf-8'))
        ua_base64 = self.base64_encoder1.encode(ua_encrypted)
        ua_sm3 = self._sm3_hash(ua_base64.encode('utf-8'))
        
        # ========== 步骤5: 生成时间戳2 ==========
        ts2 = int(time.time() * 1000) + 103
        
        # ========== 步骤6: 构造29字节签名数据 ==========
        to_sign = bytearray(29)
        to_sign[0] = 65                                    # 固定标识
        to_sign[1:5] = self._put_int64(ts2)                # 时间戳2
        to_sign[10] = 1                                    # 固定值
        to_sign[16] = self.RC4_KEY1[2]                     # RC4密钥片段 (值为4)
        to_sign[17:19] = query_sm3[21:23]                  # query哈希片段
        to_sign[19:21] = body_sm3[21:23]                   # body哈希片段
        to_sign[21:23] = ua_sm3[23:25]                     # UA哈希片段
        to_sign[23:27] = self._put_int64(ts1)              # 时间戳1
        to_sign[27] = 3                                    # 固定值
        to_sign[28] = self._xor_sum(to_sign[0:28])         # 校验和
        
        # ========== 步骤7: 字节重排 (关键混淆) ==========
        data = bytearray(29)
        for i in range(29):
            data[i] = to_sign[self.RIGHT_INDEX[i]]
        
        # ========== 步骤8: 生成时间戳3 ==========
        ts3 = int(time.time() * 1000) + 103
        
        # ========== 步骤9: RC4二次加密 ==========
        data = bytearray(self._rc4_encrypt(self.RC4_KEY2, bytes(data)))
        
        # ========== 步骤10: 添加时间戳前缀 ==========
        final = bytearray(len(data) + 4)
        final[0:4] = self._put_ts3(ts3)
        final[4:] = data
        
        # ========== 步骤11: 自定义Base64编码输出 ==========
        return self.base64_encoder2.encode(bytes(final))


def generate_a_bogus(query, body="", user_agent=""):
    """
    便捷函数: 生成a_bogus签名
    
    Args:
        query: URL查询参数
        body: POST请求体
        user_agent: 浏览器UA
    
    Returns:
        a_bogus签名字符串
    
    Example:
        >>> query = "device_platform=webapp&aid=6383&channel=channel_pc_web"
        >>> ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        >>> a_bogus = generate_a_bogus(query, "", ua)
        >>> print(a_bogus)
    """
    generator = ABogusGenerator()
    return generator.sign(query, body, user_agent)


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("a_bogus 签名算法测试")
    print("=" * 60)
    
    # 测试参数
    test_query = "device_platform=webapp&aid=6383&channel=channel_pc_web&version_code=170400"
    test_body = ""
    test_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    
    # 生成签名
    print(f"\n输入参数:")
    print(f"Query: {test_query[:50]}...")
    print(f"Body: {test_body if test_body else '(空)'}")
    print(f"UA: {test_ua[:50]}...")
    
    # 生成多次验证一致性
    print(f"\n生成签名 (测试5次):")
    for i in range(5):
        a_bogus = generate_a_bogus(test_query, test_body, test_ua)
        print(f"第{i+1}次: {a_bogus}")
        time.sleep(0.1)  # 等待时间戳变化
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
