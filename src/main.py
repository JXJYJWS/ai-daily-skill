#!/usr/bin/env python3
"""
AI Daily 主入口
自动获取 AI 资讯并生成精美的 HTML 页面
"""
import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import (
    ZHIPU_API_KEY,
    OUTPUT_DIR,
    ENABLE_IMAGE_GENERATION
)
from src.tianapi_fetcher import TianapiFetcher
from src.simple_generator import generate_simple_html
from src.notifier import EmailNotifier


def print_banner():
    """打印程序横幅"""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║   AI Daily - AI 资讯日报自动生成器                          ║
║                                                              ║
║   自动获取 smol.ai 资讯 · Claude 智能分析                   ║
║   精美 HTML 页面 · 自动部署                                 ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_target_date(days_offset: int = 2) -> str:
    """
    获取目标日期（已废弃，保留用于兼容）

    Args:
        days_offset: 向前偏移的天数，默认2天

    Returns:
        格式化的日期字符串 (YYYY-MM-DD)
    """
    target_date = (datetime.now(timezone.utc) - timedelta(days=days_offset))
    return target_date.strftime("%Y-%m-%d")


def get_latest_available_date(fetcher, data) -> str:
    """
    获取最新可用日期

    Args:
        fetcher: TianapiFetcher 实例
        data: API 数据

    Returns:
        今天的日期字符串 (YYYY-MM-DD)
    """
    # 天行数据始终返回今天的日期
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main():
    """主函数"""
    print_banner()

    # 初始化组件
    notifier = EmailNotifier()
    email_enabled = notifier._is_configured()

    # 简化版步骤：获取资讯、生成HTML、发送邮件
    total_steps = 2
    if email_enabled:
        total_steps += 1

    try:
        # 1. 从天行数据获取资讯
        print(f"[步骤 1/{total_steps}] 获取 AI 资讯...")
        fetcher = TianapiFetcher()
        api_data = fetcher.fetch(num=10)

        print(f"   成功获取 {len(api_data)} 条资讯")
        print()

        # 2. 获取今天的日期并生成 HTML
        print(f"[步骤 2/{total_steps}] 生成 HTML 页面...")
        target_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        print(f"   目标日期: {target_date}")

        # 使用简化版生成器（跳过 AI 分析）
        html_path = generate_simple_html(api_data, target_date)

        print(f"   HTML 已生成: {html_path}")
        print(f"   资讯数量: {len(api_data)} 条")
        print()

        # 3. 发送邮件通知（可选）
        if email_enabled:
            print(f"[步骤 3/{total_steps}] 发送邮件通知...")
            try:
                notifier.send_success(target_date, len(api_data))
                print("   邮件已发送")
            except Exception as e:
                print(f"   邮件发送失败: {e}")
            print()
        else:
            print("   (邮件通知未配置，跳过)")
            print()

        # 完成
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                              ║")
        print("║   ✅ 任务完成!                                              ║")
        print("║                                                              ║")
        print(f"║   日期: {target_date}                                        ║")
        print(f"║   资讯数: {len(api_data)} 条                                         ║")
        print("║   数据来源: 天行数据                                         ║")
        print("║                                                              ║")
        print("╚════════════════════════════════════════════════════════════╝")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(130)

    except Exception as e:
        print(f"\n[错误] 执行过程出错: {e}")
        import traceback
        traceback.print_exc()

        # 发送错误通知（如果配置了邮件）
        if email_enabled:
            try:
                target_date = get_target_date(days_offset=2)
                notifier.send_error(target_date, str(e))
            except:
                pass

        sys.exit(1)


if __name__ == "__main__":
    main()
