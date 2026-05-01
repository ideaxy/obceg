import os
import json
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from fetch_posts import fetch_today_posts, fetch_post_content

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.7)),
    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", 8192))
)

def build_multimodal_messages(title: str, text_content: str, image_urls: list, url: str) -> list:
    """构建包含文本和图片的多模态消息"""
    text_content = re.sub(r'<[^>]+>', '', text_content)
    text_content = text_content.strip()

    content_parts = []
    content_parts.append(f"请分析以下帖子，判断它是水贴、求助帖还是技术贴：\n\n")
    content_parts.append(f"标题：{title}\n")
    content_parts.append(f"链接：{url}\n")

    if text_content:
        content_parts.append(f"文字内容：{text_content}\n")

    if image_urls:
        content_parts.append(f"\n【此帖包含 {len(image_urls)} 张图片】\n")

    content_parts.append("\n判断标准：")
    content_parts.append("\n1. 水贴：内容空洞、无实际意义、纯灌水、刷积分的帖子")
    content_parts.append("\n2. 求助帖：提出具体技术问题、寻求帮助解决实际遇到的难题（如报错、性能问题、配置问题等）")
    content_parts.append("\n3. 技术贴：分享技术知识、经验总结、教程类、配置说明、原理分析等")
    content_parts.append("\n重要：如果帖子既提了问题又分享了解决方案，优先归类为求助帖")

    content_parts.append("\n\n请给出判断结果和理由，格式如下：")
    content_parts.append("\n- 类型：水贴/求助帖/技术贴")
    content_parts.append("\n- 理由：xxx")

    text_prompt = "".join(content_parts)

    if image_urls:
        content = []
        for img_url in image_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": img_url
                }
            })
        content.append({"type": "text", "text": text_prompt})
        return [HumanMessage(content=content)]
    else:
        return [HumanMessage(content=text_prompt)]

def analyze_posts():
    print("正在检查今天的帖子...\n")
    today_posts = fetch_today_posts()

    if today_posts.get("today_posts_count", 0) == 0:
        print("今天论坛上没有新发布的帖子")
        return

    print(f"发现 {today_posts['today_posts_count']} 个新帖子，正在分析...\n")

    posts = today_posts.get("posts", [])

    for post in posts:
        topic_id = post.get("topic_id")
        post_detail = fetch_post_content(topic_id)

        title = post.get("topic_title", "")
        url = post.get("url", "")
        text_content = post_detail.get("content", "")
        image_urls = post_detail.get("image_urls", [])

        messages = build_multimodal_messages(title, text_content, image_urls, url)

        response = llm.invoke(messages)
        print(f"标题: {title}")
        print(f"链接: {url}")
        print(f"分析结果:\n{response.content}\n")
        print("-" * 50)

if __name__ == "__main__":
    analyze_posts()