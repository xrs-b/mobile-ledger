#!/usr/bin/env python3
"""
综合测试脚本
"""
import os
import sys
import json
import time
import subprocess

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_USER = "testadmin"
TEST_PASS = "test123"

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_result(name: str, passed: bool, message: str = ""):
    """打印测试结果"""
    status = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")


def get_token() -> str:
    """获取测试token"""
    result = subprocess.run(
        ["python", "-c", f"""
from app.auth.token import create_access_token
token = create_access_token({{'sub': 1, 'username': '{TEST_USER}', 'is_admin': True}})
print(token)
"""],
        cwd="/root/.openclaw/workspace/mobile-ledger/backend",
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def main():
    """主测试函数"""
    print(f"{Colors.BLUE}================================{Colors.END}")
    print(f"{Colors.BLUE}  移动账本 API 综合测试{Colors.END}")
    print(f"{Colors.BLUE}================================{Colors.END}\n")
    
    passed = 0
    failed = 0
    
    # 获取token
    print(f"{Colors.YELLOW}获取认证Token...{Colors.END}")
    token = get_token()
    if token:
        print_result("获取Token", True)
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print_result("获取Token", False, "无法获取Token")
        return
    
    # 1. 健康检查
    print(f"\n{Colors.YELLOW}1. 健康检查{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/health"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get("status") == "ok":
            print_result("健康检查", True)
            passed += 1
        else:
            print_result("健康检查", False)
            failed += 1
    else:
        print_result("健康检查", False)
        failed += 1
    
    # 2. 详细健康检查
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/health/detailed"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get("status") == "ok":
            print_result("详细健康检查", True)
            passed += 1
        else:
            print_result("详细健康检查", False)
            failed += 1
    else:
        print_result("详细健康检查", False)
        failed += 1
    
    # 3. 用户信息
    print(f"\n{Colors.YELLOW}3. 认证接口{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/api/v1/auth/profile"],
        capture_output=True,
        text=True,
        env={**os.environ, "HTTP_AUTHORIZATION": f"Bearer {token}"}
    )
    # 使用正确的方式传递header
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/auth/profile"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get("username") == TEST_USER:
            print_result("获取用户信息", True)
            passed += 1
        else:
            print_result("获取用户信息", False, result.stdout[:100])
            failed += 1
    else:
        print_result("获取用户信息", False)
        failed += 1
    
    # 4. 分类列表
    print(f"\n{Colors.YELLOW}4. 分类接口{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/categories"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if isinstance(data, list):
            print_result("获取分类列表", True, f"共 {len(data)} 个分类")
            passed += 1
        else:
            print_result("获取分类列表", False)
            failed += 1
    else:
        print_result("获取分类列表", False)
        failed += 1
    
    # 5. 分类树
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/categories/tree"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if isinstance(data, list):
            print_result("获取分类树", True, f"共 {len(data)} 个一级分类")
            passed += 1
        else:
            print_result("获取分类树", False)
            failed += 1
    else:
        print_result("获取分类树", False)
        failed += 1
    
    # 6. 统计概览
    print(f"\n{Colors.YELLOW}5. 统计接口{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/statistics/overview"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "today_income" in data:
            print_result("统计概览", True)
            print(f"   今日收入: {data.get('today_income', 0)}")
            print(f"   今日支出: {data.get('today_expense', 0)}")
            passed += 1
        else:
            print_result("统计概览", False)
            failed += 1
    else:
        print_result("统计概览", False)
        failed += 1
    
    # 7. 每日统计
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/statistics/daily?year=2026&month=2"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "stats" in data:
            print_result("每日统计", True)
            passed += 1
        else:
            print_result("每日统计", False)
            failed += 1
    else:
        print_result("每日统计", False)
        failed += 1
    
    # 8. 月度统计
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/statistics/monthly?year=2026"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "stats" in data:
            print_result("月度统计", True)
            passed += 1
        else:
            print_result("月度统计", False)
            failed += 1
    else:
        print_result("月度统计", False)
        failed += 1
    
    # 9. 分类统计
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/statistics/category?type=expense"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "categories" in data:
            print_result("分类统计", True, f"共 {len(data.get('categories', []))} 个分类")
            passed += 1
        else:
            print_result("分类统计", False)
            failed += 1
    else:
        print_result("分类统计", False)
        failed += 1
    
    # 10. 记账列表
    print(f"\n{Colors.YELLOW}6. 记账接口{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/records"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "records" in data:
            print_result("记账列表", True, f"共 {data.get('total', 0)} 条记录")
            passed += 1
        else:
            print_result("记账列表", False)
            failed += 1
    else:
        print_result("记账列表", False)
        failed += 1
    
    # 11. 项目列表
    print(f"\n{Colors.YELLOW}7. 项目接口{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/projects"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "projects" in data:
            print_result("项目列表", True, f"共 {data.get('total', 0)} 个项目")
            passed += 1
        else:
            print_result("项目列表", False)
            failed += 1
    else:
        print_result("项目列表", False)
        failed += 1
    
    # 12. 预算列表
    print(f"\n{Colors.YELLOW}8. 预算接口{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/budgets"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "budgets" in data:
            print_result("预算列表", True, f"共 {data.get('total', 0)} 个预算")
            passed += 1
        else:
            print_result("预算列表", False)
            failed += 1
    else:
        print_result("预算列表", False)
        failed += 1
    
    # 13. 预算摘要
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/budgets/summary/current"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "total_budget" in data:
            print_result("预算摘要", True)
            passed += 1
        else:
            print_result("预算摘要", False)
            failed += 1
    else:
        print_result("预算摘要", False)
        failed += 1
    
    # 14. 年度统计
    print(f"\n{Colors.YELLOW}9. 年度统计{Colors.END}")
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/statistics/yearly?year=2026"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "year" in data:
            print_result("年度统计", True)
            passed += 1
        else:
            print_result("年度统计", False)
            failed += 1
    else:
        print_result("年度统计", False)
        failed += 1
    
    # 15. 仪表盘
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
         f"{BASE_URL}/api/v1/statistics/dashboard?days=7"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if "overview" in data:
            print_result("仪表盘", True)
            passed += 1
        else:
            print_result("仪表盘", False)
            failed += 1
    else:
        print_result("仪表盘", False)
        failed += 1
    
    # 总结
    print(f"\n{Colors.BLUE}================================{Colors.END}")
    print(f"{Colors.BLUE}  测试结果{Colors.END}")
    print(f"{Colors.BLUE}================================{Colors.END}")
    print(f"{Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"{Colors.RED}失败: {failed}{Colors.END}")
    print(f"{Colors.BLUE}总计: {passed + failed}{Colors.END}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
