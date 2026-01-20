"""
简化版 HTML 生成器
直接从天行数据生成 HTML，跳过 AI 分析
"""
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from src.config import (
    OUTPUT_DIR,
    THEMES,
    SITE_META
)


def generate_simple_html(news_list: List[Dict], target_date: str) -> str:
    """
    直接从天行数据生成 HTML 页面

    Args:
        news_list: 天行数据返回的新闻列表
        target_date: 目标日期

    Returns:
        HTML 文件路径
    """
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建 CSS 目录
    css_dir = output_dir / "css"
    css_dir.mkdir(parents=True, exist_ok=True)

    # 生成 CSS
    generate_css(css_dir / "styles.css")

    # 构建页面标题
    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][date_obj.weekday()]
    date_str = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日 {weekday}"

    # 提取关键词（从标题中）
    keywords = extract_keywords(news_list)

    # 生成 HTML
    html_content = build_html(news_list, target_date, date_str, keywords)

    # 写入文件
    filename = f"{target_date}.html"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 生成 index.html
    update_index(output_dir, target_date, date_str)

    return str(filepath)


def extract_keywords(news_list: List[Dict]) -> List[str]:
    """从新闻标题中提取关键词"""
    keywords = set()
    for news in news_list[:10]:  # 只从前10条提取
        title = news.get("title", "")
        # 简单提取：提取包含AI、科技等关键词
        for keyword in ["AI", "人工智能", "机器学习", "深度学习", "大模型", "科技", "算法"]:
            if keyword in title:
                keywords.add(keyword)
    return list(keywords)[:10]


def build_html(news_list: List[Dict], target_date: str, date_str: str, keywords: List[str]) -> str:
    """构建完整的 HTML 页面"""

    # 生成核心摘要（前5条）
    summary_html = generate_summary(news_list[:5])

    # 生成新闻卡片
    news_cards_html = generate_news_cards(news_list)

    # 关键词字符串
    keywords_str = ", ".join(keywords) if keywords else "AI, 人工智能, 科技"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Daily · {date_str}</title>
    <meta name="description" content="{SITE_META['description']}">
    <meta name="keywords" content="{keywords_str}">
    <link rel="stylesheet" href="css/styles.css">
</head>
<body data-theme="blue">
    <div class="background-glow"></div>
    <div class="geometric-lines"></div>

    <div class="container">
        <header class="header">
            <div class="logo-icon">🤖</div>
            <h1>AI Daily</h1>
            <div class="date-badge">{date_str}</div>
        </header>

        <main class="main-content">
            {summary_html}

            <section class="category-section">
                <div class="category-header">
                    <span class="category-icon">📰</span>
                    <h2 class="category-title">今日资讯</h2>
                    <span class="category-count">{len(news_list)}</span>
                </div>
                <div class="news-grid">
                    {news_cards_html}
                </div>
            </section>

            <section class="footer-section">
                <div class="keywords">
                    <strong>关键词：</strong>
                    {" ".join([f"#{kw}" for kw in keywords])}
                </div>
                <div class="source-info">
                    <p>数据来源：天行数据 AI 资讯 API</p>
                    <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </section>
        </main>
    </div>

    <script>
        // 添加平滑滚动效果
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>"""

    return html


def generate_summary(news_list: List[Dict]) -> str:
    """生成核心摘要部分"""
    if not news_list:
        return ""

    summary_items = ""
    for news in news_list:
        title = news.get("title", "无标题")
        description = news.get("description", "")
        # 简化描述
        if len(description) > 100:
            description = description[:100] + "..."
        summary_items += f'                <li class="summary-item">{title} - {description}</li>\n'

    return f"""            <section class="summary-card">
                <h2 class="section-title">📌 今日核心摘要</h2>
                <ul class="summary-list">
{summary_items}                </ul>
            </section>

"""


def generate_news_cards(news_list: List[Dict]) -> str:
    """生成新闻卡片"""
    cards_html = ""

    for news in news_list:
        title = news.get("title", "无标题")
        description = news.get("description", "")
        url = news.get("url", "#")
        source = news.get("source", "未知来源")
        ctime = news.get("ctime", "")

        # 从标题提取简单的标签
        tags = extract_tags_from_title(title)

        card_html = f"""                <article class="news-card">
                    <div class="news-card-header">
                        <h3 class="news-title">{title}</h3>
                        <a href="{url}" class="item-link" target="_blank" rel="noopener">详情</a>
                    </div>
                    <p class="news-summary">{description}</p>
                    <div class="item-meta">
                        <span class="source">来源: {source}</span>
                        <span class="time">{ctime}</span>
                    </div>
                    <div class="item-tags">{" ".join([f'<span class="tag">#{tag}</span>' for tag in tags])}</div>
                </article>
"""
        cards_html += card_html

    return cards_html


def extract_tags_from_title(title: str) -> List[str]:
    """从标题中提取标签"""
    tags = []

    # 常见AI公司和技术的关键词
    keywords = {
        "OpenAI": "OpenAI",
        "ChatGPT": "ChatGPT",
        "GPT": "GPT",
        "Google": "Google",
        "Gemini": "Gemini",
        "Anthropic": "Anthropic",
        "Claude": "Claude",
        "Microsoft": "Microsoft",
        "Meta": "Meta",
        "LLaMA": "LLaMA",
        "DeepSeek": "DeepSeek",
        "百度": "百度",
        "阿里": "阿里",
        "腾讯": "腾讯",
        "字节": "字节",
        "AI": "AI",
        "大模型": "大模型",
        "机器人": "机器人",
        "自动驾驶": "自动驾驶",
        "芯片": "芯片",
        "算法": "算法",
        "模型": "模型",
    }

    for keyword, tag in keywords.items():
        if keyword in title:
            tags.append(tag)
            if len(tags) >= 4:  # 最多4个标签
                break

    if not tags:
        tags.append("AI")

    return tags


def generate_css(css_path):
    """生成 CSS 文件"""
    css_content = """
/* AI Daily Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
    background: #000000;
    color: #E3F2FD;
    line-height: 1.6;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

.background-glow {
    position: fixed;
    top: 0;
    right: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(ellipse at bottom right, rgba(26, 58, 82, 0.4) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    position: relative;
    z-index: 1;
}

.header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
}

.logo-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.header h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #42A5F5 0%, #64B5F6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.date-badge {
    display: inline-block;
    padding: 0.5rem 1.5rem;
    background: rgba(66, 165, 245, 0.2);
    border: 1px solid rgba(66, 165, 245, 0.3);
    border-radius: 20px;
    font-size: 0.9rem;
    color: #42A5F5;
}

.summary-card {
    background: rgba(10, 25, 41, 0.6);
    border: 1px solid rgba(66, 165, 245, 0.2);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 3rem;
    backdrop-filter: blur(10px);
}

.section-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    color: #42A5F5;
}

.summary-list {
    list-style: none;
}

.summary-item {
    padding: 0.75rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.summary-item::before {
    content: "▸";
    position: absolute;
    left: 0;
    color: #42A5F5;
    font-weight: bold;
}

.category-section {
    margin-bottom: 3rem;
}

.category-header {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(66, 165, 245, 0.3);
}

.category-icon {
    font-size: 2rem;
    margin-right: 1rem;
}

.category-title {
    font-size: 1.8rem;
    flex: 1;
}

.category-count {
    padding: 0.25rem 0.75rem;
    background: rgba(66, 165, 245, 0.2);
    border-radius: 12px;
    font-size: 0.9rem;
}

.news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.news-card {
    background: rgba(10, 25, 41, 0.6);
    border: 1px solid rgba(66, 165, 245, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    transition: transform 0.3s, box-shadow 0.3s;
}

.news-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(66, 165, 245, 0.2);
}

.news-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.news-title {
    font-size: 1.2rem;
    font-weight: 600;
    flex: 1;
    padding-right: 1rem;
}

.item-link {
    color: #42A5F5;
    text-decoration: none;
    padding: 0.25rem 0.75rem;
    border: 1px solid rgba(66, 165, 245, 0.3);
    border-radius: 6px;
    font-size: 0.85rem;
    white-space: nowrap;
    transition: all 0.3s;
}

.item-link:hover {
    background: rgba(66, 165, 245, 0.2);
}

.news-summary {
    color: #B0BEC5;
    margin-bottom: 1rem;
    line-height: 1.6;
}

.item-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #B0BEC5;
    margin-bottom: 0.75rem;
}

.item-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tag {
    padding: 0.25rem 0.75rem;
    background: rgba(66, 165, 245, 0.15);
    border-radius: 6px;
    font-size: 0.8rem;
    color: #42A5F5;
}

.footer-section {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(66, 165, 245, 0.2);
}

.keywords {
    margin-bottom: 1rem;
    color: #42A5F5;
}

.source-info {
    color: #B0BEC5;
    font-size: 0.9rem;
}

.source-info p {
    margin: 0.25rem 0;
}

@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }

    .header h1 {
        font-size: 2rem;
    }

    .news-grid {
        grid-template-columns: 1fr;
    }
}
"""

    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)


def update_index(output_dir: Path, target_date: str, date_str: str):
    """更新索引页"""
    index_path = output_dir / "index.html"

    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Daily - AI 资讯日报</title>
    <meta name="description" content="{SITE_META['description']}">
    <meta http-equiv="refresh" content="0;url={target_date}.html">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #000000;
            color: #E3F2FD;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        p {{
            color: #B0BEC5;
        }}
        a {{
            color: #42A5F5;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Daily</h1>
        <p>正在跳转到最新资讯...</p>
        <p><a href="{target_date}.html">如果没有自动跳转，请点击这里</a></p>
    </div>
</body>
</html>"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
