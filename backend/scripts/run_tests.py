#!/usr/bin/env python3
"""
测试运行脚本
Test Runner Script
"""

import subprocess
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests(test_type="all", coverage=True, verbose=True):
    """运行测试
    
    Args:
        test_type: 测试类型 ("all", "unit", "integration", "api")
        coverage: 是否生成覆盖率报告
        verbose: 是否详细输出
    """
    
    # 基础pytest命令
    cmd = ["python", "-m", "pytest"]
    
    # 添加测试路径
    if test_type == "unit":
        cmd.extend(["tests/test_*_service.py", "-m", "not integration"])
    elif test_type == "integration":
        cmd.extend(["tests/test_api_endpoints.py", "-m", "integration"])
    elif test_type == "api":
        cmd.extend(["tests/test_api_endpoints.py"])
    else:  # all
        cmd.append("tests/")
    
    # 添加选项
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # 其他选项
    cmd.extend([
        "--tb=short",
        "--disable-warnings"
    ])
    
    print(f"运行命令: {' '.join(cmd)}")
    print("-" * 50)
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # 运行测试
    try:
        result = subprocess.run(cmd, cwd=project_root, env=env)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return False
    except Exception as e:
        print(f"运行测试时发生错误: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="运行电力预测系统测试")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "api"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="不生成覆盖率报告"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式"
    )
    
    args = parser.parse_args()
    
    print("🧪 电力需求预测系统 - 测试运行器")
    print("=" * 50)
    
    success = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet
    )
    
    if success:
        print("\n✅ 所有测试通过!")
        if not args.no_coverage:
            print("📊 覆盖率报告已生成到 htmlcov/ 目录")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
