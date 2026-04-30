# OceanBase 论坛帖子分析 Agent

一个基于 LangChain 的智能 Agent，用于分析 OceanBase 论坛的帖子内容，自动判断帖子类型（水贴、求助帖、技术贴）。

## 功能特性

- 自动获取 OceanBase 论坛当天的新帖子
- 使用 LLM 智能分析帖子内容
- 自动分类帖子类型：
  - **水贴**：内容空洞、无实际意义、纯灌水
  - **求助帖**：提出具体问题、寻求帮助
  - **技术贴**：分享技术知识、经验总结、教程

## 技术栈

- **Python 3.10+**
- **LangChain** - Agent 框架
- **LangChain OpenAI** - OpenAI API 集成
- **httpx** - HTTP 客户端
- **uv** - 项目管理和包管理

## 项目结构

```
obceg/
├── src/
│   ├── agent.py          # Agent 主逻辑
│   └── fetch_posts.py    # 论坛数据获取工具
├── .env                  # 环境变量（不提交）
├── .env.example          # 环境变量模板
├── pyproject.toml        # 项目配置
└── uv.lock              # 依赖锁定
```

## 环境配置

1. **克隆项目**
```bash
git clone <your-repo-url>
cd obceg
```

2. **安装依赖**
```bash
uv sync
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

4. **配置 OpenAI API**

编辑 `.env` 文件：
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # 可选：使用的模型
OPENAI_TEMPERATURE=0.7       # 可选：温度参数
OPENAI_MAX_TOKENS=1024       # 可选：最大 token 数
```

## 使用方法

### 运行 Agent 分析帖子

```bash
uv run src/agent.py
```

Agent 会自动：
1. 获取当天 OceanBase 论坛的所有新帖子
2. 依次获取每个帖子的详细内容
3. 分析并判断每个帖子的类型
4. 输出分类结果

### 示例输出

```
正在分析今天的帖子...

分析结果:
帖子ID: 35644288
标题: 在OceanBase V3中，日志流的Leader副本如何分布?
类型: 求助帖
理由: 用户在询问具体的技术问题，关于日志流Leader副本的分布情况

帖子ID: 35644285
标题: SHOW PARAMETERS命令可以查询租户的所有配置项和变量的设置
类型: 技术贴
理由: 分享OceanBase数据库的配置项查询方法
```

## 开发相关

### 添加新的工具

在 `src/fetch_posts.py` 中定义新的工具函数，然后在 `src/agent.py` 中使用 `@tool` 装饰器包装。

### 修改 Agent 行为

编辑 `src/agent.py` 中的 `system_prompt` 变量来自定义 Agent 的行为和输出格式。

## License

MIT
