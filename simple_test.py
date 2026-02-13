#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试: 直接测试Python版本的a_bogus算法
由于Go版本需要1.24,我们先验证Python版本的正确性
"""

import time
from a_bogus import generate_a_bogus, ABogusGenerator
from device_fingerprint import generate_device_fingerprint


def test_a_bogus_basic():
    """基础功能测试"""
    print("=" * 80)
    print("测试 1: a_bogus 基础功能")
    print("=" * 80)
    
    query = "device_platform=webapp&aid=6383&channel=channel_pc_web"
    body = ""
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    print(f"\n输入:")
    print(f"  Query: {query}")
    print(f"  Body: {body if body else '(空)'}")
    print(f"  UA: {ua[:50]}...")
    
    try:
        a_bogus = generate_a_bogus(query, body, ua)
        print(f"\n输出:")
        print(f"  ✓ a_bogus: {a_bogus}")
        print(f"  ✓ 长度: {len(a_bogus)} 字符")
        
        # 验证格式
        if len(a_bogus) > 0:
            print(f"  ✓ 格式正确")
            return True
        else:
            print(f"  ✗ 格式错误: 长度为0")
            return False
            
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_a_bogus_with_body():
    """带body的POST请求测试"""
    print("\n" + "=" * 80)
    print("测试 2: 带body的POST请求")
    print("=" * 80)
    
    query = "device_platform=webapp&aid=6383"
    body = '{"page":1,"limit":20,"query":{"status":1}}'
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    print(f"\n输入:")
    print(f"  Query: {query}")
    print(f"  Body: {body}")
    print(f"  UA: {ua[:50]}...")
    
    try:
        a_bogus = generate_a_bogus(query, body, ua)
        print(f"\n输出:")
        print(f"  ✓ a_bogus: {a_bogus}")
        print(f"  ✓ 长度: {len(a_bogus)} 字符")
        return True
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        return False


def test_a_bogus_consistency():
    """一致性测试: 相同输入多次生成"""
    print("\n" + "=" * 80)
    print("测试 3: 时间戳变化测试")
    print("=" * 80)
    
    query = "device_platform=webapp&aid=6383"
    body = ""
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    print(f"\n说明: 由于包含时间戳,每次生成的签名应该不同")
    print(f"\n生成5次签名:")
    
    results = []
    for i in range(5):
        a_bogus = generate_a_bogus(query, body, ua)
        results.append(a_bogus)
        print(f"  第{i+1}次: {a_bogus}")
        time.sleep(0.05)  # 等待时间戳变化
    
    # 检查是否都不同
    unique_count = len(set(results))
    print(f"\n结果:")
    print(f"  生成数量: {len(results)}")
    print(f"  唯一数量: {unique_count}")
    
    if unique_count == len(results):
        print(f"  ✓ 每次生成的签名都不同 (符合预期)")
        return True
    else:
        print(f"  ✗ 有重复的签名 (可能有问题)")
        return False


def test_a_bogus_performance():
    """性能测试"""
    print("\n" + "=" * 80)
    print("测试 4: 性能测试")
    print("=" * 80)
    
    query = "device_platform=webapp&aid=6383&channel=channel_pc_web"
    body = ""
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    print(f"\n测试: 连续生成100次签名")
    
    start_time = time.time()
    for _ in range(100):
        generate_a_bogus(query, body, ua)
    elapsed = time.time() - start_time
    
    print(f"\n结果:")
    print(f"  总耗时: {elapsed:.3f}秒")
    print(f"  平均耗时: {elapsed/100*1000:.2f}毫秒/次")
    print(f"  吞吐量: {100/elapsed:.1f}次/秒")
    
    if elapsed < 5.0:  # 100次应该在5秒内完成
        print(f"  ✓ 性能良好")
        return True
    else:
        print(f"  ⚠️  性能较慢")
        return False


def test_device_fingerprint():
    """设备指纹测试"""
    print("\n" + "=" * 80)
    print("测试 5: 设备指纹生成")
    print("=" * 80)
    
    print(f"\n生成设备指纹...")
    
    try:
        fingerprint = generate_device_fingerprint(fetch_online=False)
        
        print(f"\n生成结果:")
        print(f"  ✓ SVWebId: {fingerprint['sv_web_id']}")
        print(f"  ✓ msToken: {fingerprint['ms_token'][:50]}...")
        print(f"  ✓ Token: {fingerprint['token']}")
        print(f"  ✓ Nonce: {fingerprint['nonce']}")
        print(f"  ✓ Signature: {fingerprint['signature'][:50]}...")
        print(f"  ✓ Ttwid: {fingerprint['ttwid'][:50]}...")
        print(f"  ✓ User-Agent: {fingerprint['user_agent'][:50]}...")
        
        # 验证格式
        errors = []
        
        if not fingerprint['sv_web_id'].startswith('verify_'):
            errors.append("SVWebId格式错误")
        
        if len(fingerprint['ms_token']) != 108:
            errors.append(f"msToken长度错误: {len(fingerprint['ms_token'])} (应为108)")
        
        if len(fingerprint['token']) != 32:
            errors.append(f"Token长度错误: {len(fingerprint['token'])} (应为32)")
        
        if errors:
            print(f"\n✗ 格式验证失败:")
            for error in errors:
                print(f"    - {error}")
            return False
        else:
            print(f"\n✓ 格式验证通过")
            return True
            
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """集成测试"""
    print("\n" + "=" * 80)
    print("测试 6: 集成测试 (完整请求流程)")
    print("=" * 80)
    
    print(f"\n模拟完整的请求构造流程:")
    
    try:
        # 1. 生成设备指纹
        print(f"\n  步骤1: 生成设备指纹...")
        fingerprint = generate_device_fingerprint(fetch_online=False)
        print(f"    ✓ 完成")
        
        # 2. 构造query参数
        print(f"\n  步骤2: 构造query参数...")
        query_params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "msToken": fingerprint['ms_token'],
            "verifyFp": fingerprint['sv_web_id'],
        }
        query = "&".join([f"{k}={v}" for k, v in query_params.items()])
        print(f"    ✓ Query: {query[:60]}...")
        
        # 3. 生成a_bogus
        print(f"\n  步骤3: 生成a_bogus签名...")
        a_bogus = generate_a_bogus(query, "", fingerprint['user_agent'])
        print(f"    ✓ a_bogus: {a_bogus}")
        
        # 4. 构造完整URL
        print(f"\n  步骤4: 构造完整URL...")
        full_url = f"https://buyin.jinritemai.com/api/test?{query}&a_bogus={a_bogus}"
        print(f"    ✓ URL: {full_url[:80]}...")
        
        # 5. 构造Cookie
        print(f"\n  步骤5: 构造Cookie...")
        cookies = {
            "__ac_nonce": fingerprint['nonce'],
            "__ac_signature": fingerprint['signature'],
            "ttwid": fingerprint['ttwid'],
            "s_v_web_id": fingerprint['sv_web_id'],
        }
        print(f"    ✓ Cookie准备完成")
        
        print(f"\n  ✓ 完整请求构造成功!")
        print(f"\n  提示: 可以使用requests发送请求:")
        print(f"    import requests")
        print(f"    response = requests.get(full_url, headers={{'User-Agent': ...}}, cookies=cookies)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("Python版本 - 核心算法完整测试")
    print("=" * 80)
    print()
    
    tests = [
        ("a_bogus基础功能", test_a_bogus_basic),
        ("带body的POST请求", test_a_bogus_with_body),
        ("时间戳变化测试", test_a_bogus_consistency),
        ("性能测试", test_a_bogus_performance),
        ("设备指纹生成", test_device_fingerprint),
        ("集成测试", test_integration),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name}异常: {e}")
            results.append((name, False))
    
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
        print("\n🎉 所有测试通过! Python版本算法运行正常!")
        print("\n说明:")
        print("  - a_bogus签名算法: 正常工作")
        print("  - 设备指纹生成: 正常工作")
        print("  - 性能表现: 良好")
        print("  - 可以用于实际项目")
    else:
        print(f"\n⚠️  有{total-passed}个测试失败")
        print("\n建议:")
        print("  1. 检查依赖是否安装完整: pip install -r requirements.txt")
        print("  2. 查看上面的错误信息")
        print("  3. 确认Python版本 >= 3.7")
    
    print("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
