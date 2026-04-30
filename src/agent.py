import os
import json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from fetch_posts import fetch_today_posts, fetch_post_content

load_dotenv()

@tool
def get_today_posts() -> str:
    """获取今天论坛上的帖子列表，返回帖子的基本信息包括id、标题、创建时间等。"""
    result = fetch_today_posts()
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool
def get_post_content(topic_id: int) -> str:
    """根据帖子ID获取帖子的详细内容，包括标题、内容、作者等信息。
    
    Args:
        topic_id: 帖子的topic_id
    """
    result = fetch_post_content(topic_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

tools = [get_today_posts, get_post_content]

system_prompt = """你是一个专业的oceanbase论坛维护人员，负责管理论坛环境，包括鉴别低质量话题和回复内容。

你的任务是分析论坛帖子，判断每个帖子的类型：
1. 水贴：内容空洞、无实际意义、纯灌水、刷积分的帖子
2. 求助帖：提出具体问题、寻求帮助的帖子
3. 技术贴：分享技术知识、经验总结、教程类帖子

请按照以下步骤工作：
1. 首先调用 get_today_posts 获取今天的帖子列表
2. 对于每个帖子，调用 get_post_content 获取详细内容
3. 分析帖子内容，判断帖子类型
4. 给出判断结果和理由

输出格式：
- 帖子ID: xxx
- 标题: xxx
- 类型: 水贴/求助帖/技术贴
- 理由: xxx
"""

llm = init_chat_model(
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.7)),
    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", 1024))
)

agent = create_agent(llm, tools, system_prompt=system_prompt)

if __name__ == "__main__":
    print("正在分析今天的帖子...")
    result = agent.invoke({"messages": [("user", "请分析今天的帖子，判断每个帖子是水贴、求助帖还是技术贴")]})
    print(f"\n分析结果:\n{result['messages'][-1].content}")
