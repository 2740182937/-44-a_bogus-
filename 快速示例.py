#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速示例: 如何使用 a_bogus算法 和 设备指纹生成
"""

from a_bogus import generate_a_bogus
from device_fingerprint import generate_device_fingerprint


def example1_basic():
    """示例1: 基础使用 - 生成a_bogus签名"""
    print("=" * 60)
    print("示例1: 生成a_bogus签名")
    print("=" * 60)
    
    # 准备参数
    query = "device_platform=webapp&aid=6383&channel=channel_pc_web"
    body = ""  # GET请求为空
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # 生成签名
    a_bogus = generate_a_bogus(query, body, user_agent)
    
    print(f"\n输入:")
    print(f"  Query: {query}")
    print(f"  Body: {body if body else '(空)'}")
    print(f"  UA: {user_agent[:50]}...")
    
    print(f"\n输出:")
    print(f"  a_bogus: {a_bogus}")
    
    print(f"\n使用:")
    print(f"  完整URL: https://api.example.com?{query}&a_bogus={a_bogus}")
    print()


def example2_device():
    """示例2: 生成设备指纹"""
    print("=" * 60)
    print("示例2: 生成设备指纹")
    print("=" * 60)
    
    # 生成设备指纹
    fp = generate_device_fingerprint()
    
    print(f"\n生成的设备指纹:")
    print(f"  SVWebId: {fp['sv_web_id']}")
    print(f"  msToken: {fp['ms_token'][:50]}...")
    print(f"  Token: {fp['token']}")
    print(f"  Nonce: {fp['nonce']}")
    print(f"  User-Agent: {fp['user_agent'][:50]}...")
    
    print(f"\n使用:")
    print(f"  可以用于构造Cookie和URL参数")
    print()


def example3_post_request():
    """示例3: POST请求 (带body)"""
    print("=" * 60)
    print("示例3: POST请求 (带body)")
    print("=" * 60)
    
    # 准备参数
    query = "device_platform=webapp&aid=6383"
    body = '{"page":1,"limit":20,"query":{"status":1}}'  # POST请求体
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # 生成签名
    a_bogus = generate_a_bogus(query, body, user_agent)
    
    print(f"\n输入:")
    print(f"  Query: {query}")
    print(f"  Body: {body}")
    print(f"  UA: {user_agent[:50]}...")
    
    print(f"\n输出:")
    print(f"  a_bogus: {a_bogus}")
    
    print(f"\n使用:")
    print(f"  URL: https://api.example.com?{query}&a_bogus={a_bogus}")
    print(f"  Method: POST")
    print(f"  Body: {body}")
    print()


def example4_complete():
    """示例4: 完整的请求流程"""
    print("=" * 60)
    print("示例4: 完整的请求流程")
    print("=" * 60)
    
    # 步骤1: 生成设备指纹
    print("\n步骤1: 生成设备指纹")
    fp = generate_device_fingerprint()
    print(f"  ✓ 完成")
    
    # 步骤2: 构造query参数
    print("\n步骤2: 构造query参数")
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "msToken": fp['ms_token'],
        "verifyFp": fp['sv_web_id'],
    }
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    print(f"  ✓ Query: {query[:60]}...")
    
    # 步骤3: 生成a_bogus签名
    print("\n步骤3: 生成a_bogus签名")
    a_bogus = generate_a_bogus(query, "", fp['user_agent'])
    print(f"  ✓ a_bogus: {a_bogus}")
    
    # 步骤4: 构造完整URL
    print("\n步骤4: 构造完整URL")
    url = f"https://buyin.jinritemai.com/api/example?{query}&a_bogus={a_bogus}"
    print(f"  ✓ URL: {url[:80]}...")
    
    # 步骤5: 构造Headers
    print("\n步骤5: 构造Headers")
    headers = {
        "User-Agent": fp['user_agent'],
        "Accept": "application/json",
        "Referer": "https://buyin.jinritemai.com/",
    }
    print(f"  ✓ Headers准备完成")
    
    # 步骤6: 构造Cookies
    print("\n步骤6: 构造Cookies")
    cookies = {
        "__ac_nonce": fp['nonce'],
        "__ac_signature": fp['signature'],
        "ttwid": fp['ttwid'],
        "s_v_web_id": fp['sv_web_id'],
    }
    print(f"  ✓ Cookies准备完成")
    
    # 步骤7: 发送请求 (示例代码)
    print("\n步骤7: 发送请求")
    print(f"  代码示例:")
    print(f"    import requests")
    print(f"    response = requests.get(url, headers=headers, cookies=cookies)")
    print(f"    print(response.json())")
    
    print(f"\n✓ 完整流程演示完成!")
    print()


def example5_batch():
    """示例5: 批量生成 (高性能)"""
    print("=" * 60)
    print("示例5: 批量生成 (高性能)")
    print("=" * 60)
    
    import time
    
    # 生成一次设备指纹,可以重复使用
    print("\n生成设备指纹 (只需要一次):")
    fp = generate_device_fingerprint()
    print(f"  ✓ 完成")
    
    # 批量生成a_bogus签名
    print("\n批量生成10个a_bogus签名:")
    start_time = time.time()
    
    for i in range(10):
        query = f"device_platform=webapp&aid=6383&page={i+1}"
        a_bogus = generate_a_bogus(query, "", fp['user_agent'])
        print(f"  第{i+1}个: {a_bogus}")
    
    elapsed = time.time() - start_time
    print(f"\n性能:")
    print(f"  总耗时: {elapsed:.3f}秒")
    print(f"  平均: {elapsed/10*1000:.2f}毫秒/次")
    print()


if __name__ == "__main__":
    # 运行所有示例
    example1_basic()
    example2_device()
    example3_post_request()
    example4_complete()
    example5_batch()
    
    print("=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)
    print()
    print("提示:")
    print("  - 可以直接复制上面的代码使用")
    print("  - 查看 README.md 了解更多")
    print("  - 运行 simple_test.py 进行完整测试")
    print()
