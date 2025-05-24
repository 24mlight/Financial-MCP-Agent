# 金融分析 Agent 系统

```
 ╭─────────────────────────────────────────────────────────╮
 │  🏦 金融分析智能体系统 | Financial Analysis AI Agents   │
 │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
 │  📊 基本面 • 技术面 • 估值分析 • 智能总结               │
 ╰─────────────────────────────────────────────────────────╯
```

这是一个基于 LangGraph 的金融分析 Agent 系统，用于分析 A 股股票。系统包含四个 Agent：技术分析 Agent、价值分析 Agent、基本面分析 Agent 和总结 Agent。前三个 Agent 通过 MCP 工具获取 A 股相关数据并与大语言模型（LLM）交互；总结 Agent 综合上游数据，提供最终投资建议。

## 功能特点

- **多 Agent 协作**：技术分析、价值分析、基本面分析和总结四个 Agent 协同工作
- **MCP 工具集成**：通过`langchain-mcp-adapters`加载`a-share-mcp-v2`服务器上的多个工具
- **智能工具选择**：Agent 根据职能设计的 Prompt 智能选择工具，处理上游数据和 MCP 数据
- **数据流传递**：使用`AgentState`传递数据和元数据，确保信息流畅通
- **投资建议生成**：总结 Agent 综合上游数据，提供 A 股投资建议
- **Markdown 报告**：自动生成格式化的 Markdown 分析报告并保存到文件
- **🆕 自然语言查询**：支持任意自然语言查询，无需特定格式
- **🆕 交互式输入**：未提供命令参数时自动进入交互模式

## 系统架构

系统基于 LangGraph 框架，包含以下组件：

1. **AgentState**：自定义的 TypedDict，用于在 Agent 之间传递数据
2. **Agent**：四个专业 Agent，各司其职
3. **MCP 工具**：通过 MultiServerMCPClient 加载 a-share-mcp-v2 服务器上的多个工具
4. **LLM 交互**：每个 Agent 使用绑定的 ChatOpenAI 模型与 LLM 交互
5. **工作流**：使用 AsyncStateGraph 定义 Agent 执行顺序

## 使用方法

### 环境设置

1. 安装依赖：

   ```
   poetry install
   ```

2. 设置环境变量（.env 文件）：

   ```
   OPENAI_COMPATIBLE_API_KEY=your_api_key
   OPENAI_COMPATIBLE_BASE_URL=your_base_url
   OPENAI_COMPATIBLE_MODEL=your_model
   ```

3. 配置 MCP 服务器：

   编辑 `src/tools/mcp_config.py` 文件，修改 MCP 服务器路径：

   ```python
   SERVER_CONFIGS = {
       "a_share_mcp_v2": {  # 重命名以提高清晰度，原名为 "a-share-mcp-v2"
           "command": "uv",  # 假设'uv'在PATH中或使用完整路径
           "args": [
               "run",  # uv run命令
               "--directory",
               r"路径/到/a_share_mcp",  # 修改为您的MCP服务器项目路径
               "python",  # 在uv中运行的命令
               "mcp_server.py"  # MCP服务器脚本
           ],
           "transport": "stdio",
       }
   }
   ```

   系统通过此配置连接到 A 股 MCP 服务器获取实时金融数据。

### 运行分析

#### 方式一：命令行参数模式

通过命令行运行：

```
poetry run python -m src.main --command "分析股票名称"
```

例如：

```
poetry run python -m src.main --command "分析贵州茅台"
poetry run python -m src.main --command "帮我看看比亚迪这只股票怎么样"
poetry run python -m src.main --command "我想了解一下腾讯的投资价值"
```

#### 方式二：交互式模式 🆕

直接运行程序，系统将自动进入交互模式：

```
poetry run python -m src.main
```

系统会显示优美的欢迎界面和使用指南，然后等待您输入查询。

**支持的自然语言查询示例：**

- "分析嘉友国际"
- "帮我看看比亚迪这只股票怎么样"
- "我想了解一下腾讯的投资价值"
- "603871 这个股票值得买吗？"
- "给我分析一下宁德时代的财务状况"
- "中国平安现在的估值如何？"

> **注意**: 必须使用 `python -m src.main` 的模块导入方式运行，而不是直接运行 `python src/main.py`，这样可以确保正确的导入路径。

### 输出

系统将在终端显示分析结果，并将完整的 Markdown 格式报告保存到`reports`目录。

## 报告示例

报告包含以下部分：

- 执行摘要
- 基本面分析
- 技术分析
- 估值分析
- 交叉验证
- 投资建议

## 项目结构

```
financial_agent/
├── docs/             # 文档
├── reports/          # 生成的分析报告
├── src/
│   ├── agents/       # Agent实现
│   │   ├── fundamental_agent.py
│   │   ├── technical_agent.py
│   │   ├── value_agent.py
│   │   └── summary_agent.py
│   ├── tools/        # 工具实现
│   │   ├── mcp_client.py
│   │   ├── mcp_config.py
│   │   └── openrouter_config.py
│   ├── utils/        # 工具函数
│   │   ├── logging_config.py
│   │   └── state_definition.py
│   └── main.py       # 主程序
├── tests/            # 测试
├── tutorial/         # 教学文档
├── .env              # 环境变量
└── README.md         # 说明文档
```
## 关于terminal打印的信息
```bash
Exception ignored in: <function BaseSubprocessTransport.__del__ at 0x00000217922E20C0>
Traceback (most recent call last):
  File "D:\python3.11\Lib\asyncio\base_subprocess.py", line 126, in __del__
    self.close()
  File "D:\python3.11\Lib\asyncio\base_subprocess.py", line 104, in close
    proto.pipe.close()
  File "D:\python3.11\Lib\asyncio\proactor_events.py", line 109, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "D:\python3.11\Lib\asyncio\base_events.py", line 761, in call_soon
    self._check_closed()
  File "D:\python3.11\Lib\asyncio\base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
```
上述error可以忽略，这是由于异步执行未能正确关闭。不影响系统运行，可以忽视。