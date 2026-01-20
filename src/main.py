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
from src.claude_analyzer import ClaudeAnalyzer
from src.html_generator import HTMLGenerator
from src.notifier import EmailNotifier
from src.image_generator import ImageGenerator
from src.xiaohongshu_generator import XiaohongshuGenerator


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

    # 检查环境变量
    if not ZHIPU_API_KEY:
        print("❌ 错误: ZHIPU_API_KEY 环境变量未设置")
        print("   请设置智谱 AI 的 API Key")
        sys.exit(1)

    # 初始化组件
    notifier = EmailNotifier()
    email_enabled = notifier._is_configured()
    image_enabled = ENABLE_IMAGE_GENERATION
    # 基础步骤: 下载RSS, 获取日期, 查找资讯, 分析, 生成HTML = 5步
    # 可选步骤: 生成图片, 发送邮件
    total_steps = 5  # 基础步骤
    if image_enabled:
        total_steps += 1  # 图片生成
    if email_enabled:
        total_steps += 1  # 邮件通知

    try:
        # 1. 从天行数据获取资讯
        print(f"[步骤 1/{total_steps}] 获取 AI 资讯...")
        fetcher = TianapiFetcher()
        api_data = fetcher.fetch(num=10)

        print(f"   成功获取 {len(api_data)} 条资讯")
        print()

        # 2. 获取今天的日期
        print(f"[步骤 2/{total_steps}] 获取日期...")
        target_date = get_latest_available_date(fetcher, api_data)
        print(f"   目标日期: {target_date}")
        print(f"   (北京时间: {datetime.now(timezone.utc) + timedelta(hours=8)})")
        print()

        # 3. 格式化内容
        print(f"[步骤 3/{total_steps}] 格式化资讯内容...")
        content = fetcher.get_content(num=10)

        print(f"   标题: {content.get('title', '')}")
        print()

        # 4. 调用 Claude 分析
        print(f"[步骤 4/{total_steps}] 调用 Claude 进行智能分析...")
        analyzer = ClaudeAnalyzer()
        result = analyzer.analyze(content, target_date)

        # 检查分析状态
        if result.get("status") == "empty":
            print("   分析结果为空")
            if email_enabled:
                notifier.send_empty(target_date, result.get("reason", "内容分析为空"))
            return

        print()

        # 5. 生成 HTML
        print(f"[步骤 5/{total_steps}] 生成 HTML 页面...")
        generator = HTMLGenerator()
        generator.generate_css()

        # 生成日报页面
        html_path = generator.generate_daily(result)
        print(f"   文件路径: {html_path}")
        print()

        # 计算总资讯数
        total_items = sum(
            len(cat.get('items', []))
            for cat in result.get('categories', [])
        )

        # 6. 生成分享图片（可选）
        image_path = None
        xhs_path = None
        if image_enabled:
            print(f"[步骤 6/{total_steps}] 生成分享卡片图片...")
            image_gen = ImageGenerator()
            image_path = image_gen.generate_from_analysis_result(
                result,
                output_path=str(Path(OUTPUT_DIR) / "images" / f"{target_date}.png")
            )
            if image_path:
                print(f"   图片已保存: {image_path}")
            else:
                print("   图片生成失败或跳过")

            # 生成小红书封面
            print(f"   生成小红书封面...")
            xhs_gen = XiaohongshuGenerator()
            xhs_path = xhs_gen.generate(result)
            print(f"   小红书封面: {xhs_path}")
            print()
        else:
            print("   (图片生成未启用，跳过)")
            print()

        # 7. 发送成功通知（可选）
        if email_enabled:
            step_num = 7 if image_enabled else 6
            print(f"[步骤 {step_num}/{total_steps}] 发送邮件通知...")
            notifier.send_success(target_date, total_items)
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
        print(f"║   资讯数: {total_items} 条                                          ║")
        print(f"║   主题: {result.get('theme', 'blue')}                                                ║")
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
