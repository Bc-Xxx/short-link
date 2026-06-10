# ============================================================
# AI 安全分析工具
# 作用：调用通义千问大模型，分析链接的安全性
# ============================================================

import json
import re
import requests as req
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


def fetch_page_title(url: str) -> str:
    """
    抓取网页标题
    用 requests 访问目标 URL，从 HTML 中提取 <title> 标签的内容
    """
    try:
        resp = req.get(
            url,
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()[:200]
    except Exception:
        pass
    return ""


def analyze_url_safety(url: str, title: str = "") -> dict:
    """
    调用通义千问分析 URL 的安全性

    参数：
        url: 要分析的链接
        title: 网页标题（可选，帮助AI判断）

    返回：
        {"score": 8, "level": "安全", "reason": "分析理由..."}
    """
    if not settings.DASHSCOPE_API_KEY:
        return {
            "score": None,
            "level": "未配置API",
            "reason": "未配置 DASHSCOPE_API_KEY，无法进行AI分析"
        }

    client = OpenAI(
        api_key=settings.DASHSCOPE_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    prompt = f"""你是一个网络安全分析助手。请分析以下 URL 的安全性：

URL：{url}
网页标题：{title}

请从以下角度分析：
1. 域名是否可信（是否是知名网站）
2. URL 结构是否异常（是否有钓鱼特征）
3. 内容是否涉及诈骗、赌博、色情等违规内容

请直接返回 JSON 格式，不要有其他文字：
{{"score": 安全评分1到10的整数, "level": "安全或警告或危险", "reason": "一句话分析理由"}}"""

    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "score": result.get("score", 5),
            "level": result.get("level", "未知"),
            "reason": result.get("reason", "分析失败")
        }
    except Exception as e:
        return {
            "score": None,
            "level": "分析失败",
            "reason": f"AI分析出错: {str(e)}"
        }
