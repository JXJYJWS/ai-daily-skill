"""
天行数据 API 获取器
使用天行数据的 AI 资讯 API 获取最新的 AI 行业新闻
"""
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, List
import os

class TianapiFetcher:
    """天行数据 API 获取器"""

    API_URL = "https://apis.tianapi.com/ai/index"

    def __init__(self, api_key: str = None):
        # ⚡️ 核心修改：这里强制只读环境变量！如果没有环境变量，直接让它报错，绝不妥协用旧 Key
        self.api_key = api_key or os.getenv("TIANAPI_API_KEY")
        
        if not self.api_key:
            print("❌ [严重错误] 未检测到 API Key！程序将无法获取数据。")
        else:
            # 只打印前4位用于调试，保护隐私
            print(f"✅ API Key 已加载: {self.api_key[:4]}******")

        self.timeout = 30

    def fetch(self, num: int = 10) -> List[Dict]:
        """获取 AI 资讯"""
        print(f"[INFO] 正在调用天行数据 AI 资讯 API...")

        try:
            params = {
                "key": self.api_key,
                "num": num,
                "rand": 1
            }

            response = requests.get(
                self.API_URL,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                # 打印详细错误码，方便排查
                raise Exception(f"API 接口报错: {data.get('msg')} (代码: {data.get('code')})")

            news_list = data.get("result", {}).get("newslist", [])
            print(f"[OK] 成功获取 {len(news_list)} 条 AI 资讯")
            return news_list

        except Exception as e:
            raise Exception(f"获取资讯失败: {e}")

    def get_content(self, num: int = 10) -> Dict:
        """获取并格式化资讯内容"""
        news_list = self.fetch(num)

        return {
            "title": f"AI 行业资讯 · {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "content": self._format_to_html(news_list),
            "news_list": news_list,
            "pubDate": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        }

    def _format_to_html(self, news_list: List[Dict]) -> str:
        """格式化为 HTML"""
        html = "<h2>最新 AI 资讯</h2><ul>"
        for news in news_list:
            html += f'<li><strong>{news.get("title", "无标题")}</strong><br>'
            html += f'{news.get("description", "")}<br>'
            html += f'<small>来源: {news.get("source", "")} | {news.get("ctime", "")}</small></li>'
        html += "</ul>"
        return html
