#!/usr/bin/env python3
"""
Counselor项目测试运行脚本
支持运行CounselorApp和CounselorAdmin的API测试
"""

import os
import sys
import argparse
import subprocess
import pytest

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Counselor.settings')

import django
django.setup()


def run_counselorapp_tests(verbose=False, coverage=False):
    """运行CounselorApp测试"""
    print("🚀 开始运行CounselorApp测试...")
    
    test_args = [
        'tests/counselorapp/test_api.py',
        '-v' if verbose else '',
        '--cov=CounselorApp' if coverage else '',
        '--cov-report=term-missing' if coverage else ''
    ]
    
    # 过滤空参数
    test_args = [arg for arg in test_args if arg]
    
    result = pytest.main(test_args)
    
    if result == 0:
        print("✅ CounselorApp测试全部通过！")
    else:
        print("❌ CounselorApp测试有失败用例")
    
    return result


def run_counseloradmin_tests(verbose=False, coverage=False):
    """运行CounselorAdmin测试"""
    print("🚀 开始运行CounselorAdmin测试...")
    
    test_args = [
        'tests/counseloradmin/test_api.py',
        '-v' if verbose else '',
        '--cov=CounselorAdmin' if coverage else '',
        '--cov-report=term-missing' if coverage else ''
    ]
    
    # 过滤空参数
    test_args = [arg for arg in test_args if arg]
    
    result = pytest.main(test_args)
    
    if result == 0:
        print("✅ CounselorAdmin测试全部通过！")
    else:
        print("❌ CounselorAdmin测试有失败用例")
    
    return result


def run_all_tests(verbose=False, coverage=False):
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    
    test_args = [
        'tests/',
        '-v' if verbose else '',
        '--cov=CounselorApp,CounselorAdmin' if coverage else '',
        '--cov-report=term-missing' if coverage else '',
        '--cov-report=html' if coverage else ''
    ]
    
    # 过滤空参数
    test_args = [arg for arg in test_args if arg]
    
    result = pytest.main(test_args)
    
    if result == 0:
        print("🎉 所有测试全部通过！")
    else:
        print("💥 部分测试失败")
    
    return result


def run_specific_test(test_path, verbose=False):
    """运行特定测试文件或测试用例"""
    print(f"🚀 开始运行特定测试: {test_path}")
    
    test_args = [
        test_path,
        '-v' if verbose else ''
    ]
    
    # 过滤空参数
    test_args = [arg for arg in test_args if arg]
    
    result = pytest.main(test_args)
    return result


def generate_test_report():
    """生成测试报告"""
    print("📊 生成测试报告中...")
    
    # 使用pytest-html生成HTML报告
    result = pytest.main([
        'tests/',
        '--html=test_reports/report.html',
        '--self-contained-html'
    ])
    
    if result == 0:
        print("✅ 测试报告已生成: test_reports/report.html")
    else:
        print("❌ 测试报告生成失败")
    
    return result


def setup_test_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 创建测试报告目录
    os.makedirs('test_reports', exist_ok=True)
    
    # 检查Django设置
    try:
        from django.conf import settings
        print(f"✅ Django设置已加载: {settings.SETTINGS_MODULE}")
    except Exception as e:
        print(f"❌ Django设置加载失败: {e}")
        return False
    
    # 检查数据库连接
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Counselor项目测试运行器')
    parser.add_argument('--app', choices=['counselorapp', 'counseloradmin', 'all'], 
                       default='all', help='选择要测试的应用')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='详细输出')
    parser.add_argument('--coverage', '-c', action='store_true', 
                       help='生成代码覆盖率报告')
    parser.add_argument('--report', '-r', action='store_true', 
                       help='生成HTML测试报告')
    parser.add_argument('--test', '-t', type=str,
                       help='运行特定测试文件或测试用例')
    
    args = parser.parse_args()
    
    # 设置测试环境
    if not setup_test_environment():
        print("❌ 测试环境设置失败，退出")
        sys.exit(1)
    
    # 运行测试
    if args.test:
        result = run_specific_test(args.test, args.verbose)
    elif args.app == 'counselorapp':
        result = run_counselorapp_tests(args.verbose, args.coverage)
    elif args.app == 'counseloradmin':
        result = run_counseloradmin_tests(args.verbose, args.coverage)
    else:
        result = run_all_tests(args.verbose, args.coverage)
    
    # 生成报告
    if args.report:
        generate_test_report()
    
    # 退出代码
    sys.exit(result)


if __name__ == '__main__':
    main()