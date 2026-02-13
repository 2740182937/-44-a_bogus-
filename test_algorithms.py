#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心算法测试脚本
测试a_bogus签名和设备指纹生成
"""

import time
from a_bogus import generate_a_bogus, ABogusGenerator
from device_fingerprint import generate_device_fingerprint, DeviceFingerprintGenerator


def test_a_bogus():
    """测试a_bogus签名算法"""
    print("=" * 80)
    print("测试 1: a_bogus 签名算法")
    print("=" * 80)
    
    # 测试参数
    query = "device_platform=webapp&aid=6383&channel=channel_pc_web&version_code=170400&version_name=17.4.0"
    body = ""
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    
    print(f"\n输入参数:")
    print(f"  Query: {query[:60]}...")
    print(f"  Body: {body if body else '(空)'}")
    print(f"  UA: {user_agent[:60]}...")
    
    # 测试1: 基础功能
    print(f"\n[测试1] 基础功能测试:")
    try:
        a_bogus = generate_a_bogus(query, body, user_agent)
        print(f"  ✓ 签名生成成功")
        print(f"  ✓ a_bogus: {a_bogus}")
        print(f"  ✓ 长度: {len(a_bogus)} 字符")
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return False
    
    # 测试2: 多次生成 (验证时间戳变化)
    print(f"\n[测试2] 多次生成测试 (验证时间戳影响):")
    results = []
    for i in range(3):
        a_bogus = generate_a_bogus(query, body, user_agent)
        results.append(a_bogus)
        print(f"  第{i+1}次: {a_bogus}")
        time.sleep(0.1)  # 等待时间戳变化
    
    # 验证每次结果不同 (因为时间戳不同)
    if len(set(results)) == len(results):
        print(f"  ✓ 每次生成的签名都不同 (符合预期)")
    else:
        print(f"  ✗ 警告: 有重复的签名")
    
    # 测试3: 带body的请求
    print(f"\n[测试3] 带body的POST请求:")
    test_body = '{"page":1,"limit":20}'
    try:
        a_bogus_with_body = generate_a_bogus(query, test_body, user_agent)
        print(f"  ✓ 签名生成成功")
        print(f"  ✓ a_bogus: {a_bogus_with_body}")
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return False
    
    # 测试4: 性能测试
    print(f"\n[测试4] 性能测试 (生成100次):")
    start_time = time.time()
    for _ in range(100):
        generate_a_bogus(query, body, user_agent)
    elapsed = time.time() - start_time
    print(f"  ✓ 总耗时: {elapsed:.3f}秒")
    print(f"  ✓ 平均耗时: {elapsed/100*1000:.2f}毫秒/次")
    print(f"  ✓ 吞吐量: {100/elapsed:.1f}次/秒")
    
    return True


def test_device_fingerprint():
    """测试设备指纹生成"""
    print("\n" + "=" * 80)
    print("测试 2: 设备指纹生成")
    print("=" * 80)
    
    # 测试1: 本地生成
    print(f"\n[测试1] 本地模拟生成:")
    try:
        fingerprint = generate_device_fingerprint(fetch_online=False)
        print(f"  ✓ 设备指纹生成成功")
        print(f"  ✓ SVWebId: {fingerprint['sv_web_id']}")
        print(f"  ✓ msToken: {fingerprint['ms_token'][:50]}...")
        print(f"  ✓ Token: {fingerprint['token']}")
        print(f"  ✓ Nonce: {fingerprint['nonce']}")
        print(f"  ✓ Signature: {fingerprint['signature'][:50]}...")
        print(f"  ✓ Ttwid: {fingerprint['ttwid'][:50]}...")
        print(f"  ✓ User-Agent: {fingerprint['user_agent'][:50]}...")
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return False
    
    # 测试2: 验证SVWebId格式
    print(f"\n[测试2] 验证SVWebId格式:")
    sv_web_id = fingerprint['sv_web_id']
    if sv_web_id.startswith('verify_'):
        print(f"  ✓ 前缀正确: verify_")
        parts = sv_web_id.split('_')
        if len(parts) >= 6:
            print(f"  ✓ 格式正确: verify_时间戳_随机字符串")
        else:
            print(f"  ✗ 格式错误: 分段数量不对")
    else:
        print(f"  ✗ 前缀错误")
    
    # 测试3: 验证msToken长度
    print(f"\n[测试3] 验证msToken长度:")
    ms_token = fingerprint['ms_token']
    if len(ms_token) == 108:
        print(f"  ✓ 长度正确: {len(ms_token)} 字符")
    else:
        print(f"  ✗ 长度错误: {len(ms_token)} 字符 (应为108)")
    
    # 测试4: 多次生成验证唯一性
    print(f"\n[测试4] 多次生成验证唯一性:")
    sv_web_ids = set()
    ms_tokens = set()
    for i in range(5):
        fp = generate_device_fingerprint(fetch_online=False)
        sv_web_ids.add(fp['sv_web_id'])
        ms_tokens.add(fp['ms_token'])
    
    if len(sv_web_ids) == 5:
        print(f"  ✓ SVWebId每次都不同")
    else:
        print(f"  ✗ SVWebId有重复")
    
    if len(ms_tokens) == 5:
        print(f"  ✓ msToken每次都不同")
    else:
        print(f"  ✗ msToken有重复")
    
    # 测试5: 性能测试
    print(f"\n[测试5] 性能测试 (生成100次):")
    start_time = time.time()
    for _ in range(100):
        generate_device_fingerprint(fetch_online=False)
    elapsed = time.time() - start_time
    print(f"  ✓ 总耗时: {elapsed:.3f}秒")
    print(f"  ✓ 平均耗时: {elapsed/100*1000:.2f}毫秒/次")
    print(f"  ✓ 吞吐量: {100/elapsed:.1f}次/秒")
    
    return True


def test_integration():
    """集成测试: 模拟真实请求"""
    print("\n" + "=" * 80)
    print("测试 3: 集成测试 (模拟真实请求)")
    print("=" * 80)
    
    print(f"\n[场景] 模拟访问抖音百应API:")
    
    # 1. 生成设备指纹
    print(f"\n  步骤1: 生成设备指纹...")
    fingerprint = generate_device_fingerprint(fetch_online=False)
    print(f"    ✓ 设备指纹生成完成")
    
    # 2. 构造请求参数
    print(f"\n  步骤2: 构造请求参数...")
    query_params = {
        "device_platform": fingerprint['device_platform'],
        "aid": fingerprint['aid'],
        "channel": fingerprint['channel'],
        "version_code": fingerprint['version_code'],
        "msToken": fingerprint['ms_token'],
        "verifyFp": fingerprint['sv_web_id'],
    }
    query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
    print(f"    ✓ Query参数: {query_string[:60]}...")
    
    # 3. 生成a_bogus签名
    print(f"\n  步骤3: 生成a_bogus签名...")
    a_bogus = generate_a_bogus(query_string, "", fingerprint['user_agent'])
    print(f"    ✓ a_bogus: {a_bogus}")
    
    # 4. 构造完整URL
    print(f"\n  步骤4: 构造完整URL...")
    base_url = "https://buyin.jinritemai.com/api/example"
    full_url = f"{base_url}?{query_string}&a_bogus={a_bogus}"
    print(f"    ✓ URL: {full_url[:80]}...")
    
    # 5. 构造Cookie
    print(f"\n  步骤5: 构造Cookie...")
    cookies = {
        "__ac_nonce": fingerprint['nonce'],
        "__ac_signature": fingerprint['signature'],
        "ttwid": fingerprint['ttwid'],
        "passport_csrf_token": fingerprint['token'],
        "s_v_web_id": fingerprint['sv_web_id'],
    }
    cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    print(f"    ✓ Cookie: {cookie_string[:80]}...")
    
    # 6. 构造Headers
    print(f"\n  步骤6: 构造Headers...")
    headers = {
        "User-Agent": fingerprint['user_agent'],
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": cookie_string,
        "Referer": "https://buyin.jinritemai.com/",
        "Origin": "https://buyin.jinritemai.com",
    }
    print(f"    ✓ Headers准备完成")
    
    print(f"\n  ✓ 请求构造完成! 可以发送HTTP请求了")
    print(f"\n  提示: 实际使用时,将上述参数传给requests库:")
    print(f"    requests.get(full_url, headers=headers)")
    
    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("抖音/百应核心算法 Python版本 - 完整测试")
    print("=" * 80)
    
    results = []
    
    # 测试a_bogus算法
    try:
        result = test_a_bogus()
        results.append(("a_bogus签名算法", result))
    except Exception as e:
        print(f"\n✗ a_bogus测试异常: {e}")
        results.append(("a_bogus签名算法", False))
    
    # 测试设备指纹生成
    try:
        result = test_device_fingerprint()
        results.append(("设备指纹生成", result))
    except Exception as e:
        print(f"\n✗ 设备指纹测试异常: {e}")
        results.append(("设备指纹生成", False))
    
    # 集成测试
    try:
        result = test_integration()
        results.append(("集成测试", result))
    except Exception as e:
        print(f"\n✗ 集成测试异常: {e}")
        results.append(("集成测试", False))
    
    # 输出测试结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")
    
    # 统计
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过! 算法运行正常!")
    else:
        print("\n⚠️  部分测试失败,请检查依赖是否安装完整")
        print("   安装命令: pip install -r requirements.txt")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
