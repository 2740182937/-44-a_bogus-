#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比测试: Python版本 vs Go版本
确保两个版本生成的a_bogus签名一致
"""

import json
import subprocess
import sys
from a_bogus import generate_a_bogus


def run_go_test():
    """运行Go测试并获取结果"""
    try:
        # 编译Go程序
        print("正在编译Go测试程序...")
        compile_result = subprocess.run(
            ["go", "build", "-o", "compare_test_go", "compare_test.go"],
            cwd="/Users/cds-dn-141/Downloads/my_golang/cx-spider",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if compile_result.returncode != 0:
            print(f"Go编译失败: {compile_result.stderr}")
            return None
        
        print("✓ Go程序编译成功")
        
        # 运行Go程序
        print("正在运行Go测试...")
        result = subprocess.run(
            ["./compare_test_go"],
            cwd="/Users/cds-dn-141/Downloads/my_golang/cx-spider",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"Go运行失败: {result.stderr}")
            return None
        
        # 解析输出
        output = result.stdout
        
        # 提取JSON部分
        json_start = output.find("=== JSON输出")
        if json_start == -1:
            print("未找到JSON输出")
            return None
        
        json_text = output[json_start:].split("\n", 1)[1]
        
        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"JSON文本: {json_text[:200]}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Go程序运行超时")
        return None
    except Exception as e:
        print(f"运行Go测试失败: {e}")
        return None


def test_python_version(test_cases):
    """测试Python版本"""
    print("\n=== Python版本 a_bogus 生成测试 ===\n")
    
    results = []
    
    for i, tc in enumerate(test_cases):
        print(f"测试用例 {i+1}:")
        print(f"  Query: {tc['query']}")
        print(f"  Body: {tc['body']}")
        print(f"  UA: {tc['user_agent'][:50]}...")
        
        # 生成a_bogus
        a_bogus = generate_a_bogus(tc['query'], tc['body'], tc['user_agent'])
        
        print(f"  a_bogus: {a_bogus}")
        print()
        
        results.append({
            'a_bogus': a_bogus,
            'timestamp': tc['timestamp']
        })
    
    return results


def compare_results(go_results, python_results):
    """对比Go和Python的结果"""
    print("\n" + "=" * 80)
    print("对比结果")
    print("=" * 80 + "\n")
    
    if len(go_results) != len(python_results):
        print(f"✗ 结果数量不一致: Go={len(go_results)}, Python={len(python_results)}")
        return False
    
    all_match = True
    
    for i, (go_res, py_res) in enumerate(zip(go_results, python_results)):
        print(f"测试用例 {i+1}:")
        print(f"  Go版本:     {go_res['a_bogus']}")
        print(f"  Python版本: {py_res['a_bogus']}")
        
        if go_res['a_bogus'] == py_res['a_bogus']:
            print(f"  结果: ✓ 一致")
        else:
            print(f"  结果: ✗ 不一致")
            all_match = False
            
            # 详细对比
            go_bogus = go_res['a_bogus']
            py_bogus = py_res['a_bogus']
            
            print(f"\n  详细对比:")
            print(f"    长度: Go={len(go_bogus)}, Python={len(py_bogus)}")
            
            if len(go_bogus) == len(py_bogus):
                # 找出不同的位置
                diff_positions = []
                for j, (c1, c2) in enumerate(zip(go_bogus, py_bogus)):
                    if c1 != c2:
                        diff_positions.append(j)
                
                if diff_positions:
                    print(f"    不同位置: {diff_positions[:10]}...")  # 只显示前10个
                    for pos in diff_positions[:3]:  # 详细显示前3个
                        print(f"      位置{pos}: Go='{go_bogus[pos]}' vs Python='{py_bogus[pos]}'")
        
        print()
    
    return all_match


def main():
    """主测试函数"""
    print("=" * 80)
    print("a_bogus算法对比测试: Python版本 vs Go版本")
    print("=" * 80)
    print()
    
    # 1. 运行Go测试
    print("步骤1: 运行Go版本测试")
    print("-" * 80)
    
    go_data = run_go_test()
    
    if go_data is None:
        print("\n✗ Go测试失败,无法继续对比")
        print("\n可能的原因:")
        print("  1. Go环境未配置")
        print("  2. 缺少依赖包")
        print("  3. 编译错误")
        print("\n请先确保Go版本可以正常运行:")
        print("  cd /Users/cds-dn-141/Downloads/my_golang/cx-spider")
        print("  go run compare_test.go")
        return False
    
    test_cases = go_data['test_cases']
    go_results = go_data['results']
    
    print(f"✓ Go测试完成,共 {len(go_results)} 个测试用例")
    
    # 2. 运行Python测试
    print("\n步骤2: 运行Python版本测试")
    print("-" * 80)
    
    try:
        python_results = test_python_version(test_cases)
        print(f"✓ Python测试完成,共 {len(python_results)} 个测试用例")
    except Exception as e:
        print(f"\n✗ Python测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 对比结果
    print("\n步骤3: 对比两个版本的结果")
    print("-" * 80)
    
    all_match = compare_results(go_results, python_results)
    
    # 4. 输出总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if all_match:
        print("\n🎉 测试通过! Python版本和Go版本生成的a_bogus完全一致!")
        print("\n两个版本的算法实现正确,可以互相替换使用。")
        return True
    else:
        print("\n⚠️  测试失败! Python版本和Go版本生成的结果不一致!")
        print("\n可能的原因:")
        print("  1. 时间戳处理方式不同")
        print("  2. 字节序列处理差异")
        print("  3. 加密库实现差异")
        print("  4. 字符编码问题")
        print("\n需要检查Python实现是否完全匹配Go版本的逻辑。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
