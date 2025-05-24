# 金融分析 Agent 系统

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,15,20,24&height=200&section=header&text=金融分析智能体系统&fontSize=80&fontAlignY=35&desc=A股股票全方位分析平台&descAlignY=60&animation=fadeIn" />

[![License](https://img.shields.io/badge/License-GPLv3-lightgrey.svg?style=flat-square&logo=gnu)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.56-green?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![MCP Tools](https://img.shields.io/badge/MCP-Tools-E6162D?style=flat-square)](https://github.com/24mlight/a-share-mcp-is-just-i-need)

<img src="https://img.shields.io/badge/智能分析-基本面/技术面/估值-E6162D?style=for-the-badge">

</div>

**⚠️ 免责声明：本项目仅用于教育目的，不构成任何投资建议。投资有风险，交易需谨慎。**

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 🔍 项目概述

这是一个基于 LangGraph 的金融分析 Agent 系统，用于分析 A 股股票。系统包含四个 Agent：技术分析 Agent、价值分析 Agent、基本面分析 Agent 和总结 Agent。前三个 Agent 通过 MCP 工具获取 A 股相关数据并与大语言模型（LLM）交互；总结 Agent 综合上游数据，提供最终投资建议。

<div align="center">
<table>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/stocks-growth.png" width="30px"/><br><b>多维度分析</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/line-chart.png" width="30px"/><br><b>数据驱动</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/economic-improvement.png" width="30px"/><br><b>智能决策</b></td>
  </tr>
  <tr>
    <td>系统同时从基本面、技术面和估值三个维度进行分析</td>
    <td>利用实时A股数据，提供数据支持的决策建议</td>
    <td>AI智能汇总分析结果，提供清晰的投资建议</td>
  </tr>
</table>
</div>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## ✨ 功能特点

<div align="center">
<table>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/group-of-projects.png" width="30px"/><br><b>多 Agent 协作</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/tools.png" width="30px"/><br><b>MCP 工具集成</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/artificial-intelligence.png" width="30px"/><br><b>智能工具选择</b></td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/data-flow.png" width="30px"/><br><b>数据流传递</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/financial-growth-analysis.png" width="30px"/><br><b>投资建议生成</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/markdown.png" width="30px"/><br><b>Markdown 报告</b></td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/query.png" width="30px"/><br><b>自然语言查询</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/chat.png" width="30px"/><br><b>交互式输入</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/update.png" width="30px"/><br><b>实时数据更新</b></td>
  </tr>
</table>
</div>

- **多 Agent 协作**：技术分析、价值分析、基本面分析和总结四个 Agent 协同工作
- **MCP 工具集成**：通过`langchain-mcp-adapters`加载`a-share-mcp-v2`服务器上的多个工具
- **智能工具选择**：Agent 根据职能设计的 Prompt 智能选择工具，处理上游数据和 MCP 数据
- **数据流传递**：使用`AgentState`传递数据和元数据，确保信息流畅通
- **投资建议生成**：总结 Agent 综合上游数据，提供 A 股投资建议
- **Markdown 报告**：自动生成格式化的 Markdown 分析报告并保存到文件
- **🆕 自然语言查询**：支持任意自然语言查询，无需特定格式
- **🆕 交互式输入**：未提供命令参数时自动进入交互模式

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 🏗️ 系统架构

系统基于 LangGraph 框架，包含以下组件：

<div align="center">
<table>
  <tr>
    <th>组件</th>
    <th>描述</th>
  </tr>
  <tr>
    <td><b>AgentState</b></td>
    <td>自定义的 TypedDict，用于在 Agent 之间传递数据</td>
  </tr>
  <tr>
    <td><b>Agent</b></td>
    <td>四个专业 Agent，各司其职</td>
  </tr>
  <tr>
    <td><b>MCP 工具</b></td>
    <td>通过 MultiServerMCPClient 加载 a-share-mcp-v2 服务器上的多个工具</td>
  </tr>
  <tr>
    <td><b>LLM 交互</b></td>
    <td>每个 Agent 使用绑定的 ChatOpenAI 模型与 LLM 交互</td>
  </tr>
  <tr>
    <td><b>工作流</b></td>
    <td>使用 StateGraph 定义 Agent 执行顺序</td>
  </tr>
</table>
</div>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 🚀 使用方法

### 环境设置

<div align="center">
<table>
  <tr>
    <th>步骤</th>
    <th>命令/操作</th>
  </tr>
  <tr>
    <td><b>1. 安装依赖</b></td>
    <td>
      
```bash
poetry install
```

```bash
cp .env.example .env
```

    </td>

  </tr>
  <tr>
    <td><b>2. 配置环境变量</b></td>
    <td>
      
```
OPENAI_COMPATIBLE_API_KEY=your_api_key
OPENAI_COMPATIBLE_BASE_URL=your_base_url
OPENAI_COMPATIBLE_MODEL=your_model
```
    </td>
  </tr>
  <tr>
    <td><b>3. 配置 MCP 服务器</b></td>
    <td>编辑 <code>src/tools/mcp_config.py</code> 文件</td>
  </tr>
</table>
</div>

1. 安装依赖：

   ```bash
   poetry install
   ```

   ```bash
   cp .env.example .env
   ```

或者手动将 `.env.example` 文件改名为 `.env`

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
               r"a_share_mcp项目的绝对路径",  # 修改为您已部署好的MCP服务器项目路径，如未部署好，请git clone https://github.com/24mlight/a-share-mcp-is-just-i-need.git， 然后部署
               "python",  # 在uv中运行的命令
               "mcp_server.py"  # MCP服务器脚本
           ],
           "transport": "stdio",
       }
   }
   ```

   系统通过此配置连接到 A 股 MCP 服务器获取实时金融数据。

### 运行分析

<div align="center">
<table>
  <tr>
    <th colspan="2"><b>运行方式</b></th>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/console.png" width="30px"/><br><b>命令行参数模式</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/chat.png" width="30px"/><br><b>交互式模式</b></td>
  </tr>
</table>
</div>

#### 方式一：命令行参数模式

通过命令行运行：

```bash
poetry run python -m src.main --command "分析股票名称"
```

例如：

```bash
poetry run python -m src.main --command "分析贵州茅台"
poetry run python -m src.main --command "帮我看看比亚迪这只股票怎么样"
poetry run python -m src.main --command "我想了解一下腾讯的投资价值"
```

#### 方式二：交互式模式 🆕

直接运行程序，系统将自动进入交互模式：

```bash
poetry run python -m src.main
```

系统会显示的欢迎界面和使用指南，然后等待您输入查询。

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

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 📝 报告示例

<div align="center">
<table>
  <tr>
    <th>报告章节</th>
    <th>内容描述</th>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/resume.png" width="25px"/> <b>执行摘要</b></td>
    <td>对分析结果的整体概述和关键结论</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/company.png" width="25px"/> <b>基本面分析</b></td>
    <td>公司财务状况、经营情况和行业地位分析</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/stocks-growth.png" width="25px"/> <b>技术分析</b></td>
    <td>股价走势、交易量和技术指标分析</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/money-bag.png" width="25px"/> <b>估值分析</b></td>
    <td>市盈率、市净率等估值指标分析</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/check-all.png" width="25px"/> <b>交叉验证</b></td>
    <td>不同分析方法的对比验证</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/idea.png" width="25px"/> <b>投资建议</b></td>
    <td>基于综合分析的投资决策建议</td>
  </tr>
</table>
</div>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 📁 项目结构

```
Financial-MCP-Agent/
├── .venv/            # 虚拟环境
├── logs/             # 执行日志
├── reports/          # 生成的分析报告
├── src/
│   ├── agents/       # Agent实现
│   │   ├── fundamental_agent.py  # 基本面分析智能体
│   │   ├── technical_agent.py    # 技术面分析智能体
│   │   ├── value_agent.py        # 估值分析智能体
│   │   └── summary_agent.py      # 总结智能体
│   ├── tools/        # 工具实现
│   │   ├── mcp_client.py        # MCP客户端实现
│   │   ├── mcp_config.py        # MCP服务器配置
│   │   └── openrouter_config.py # OpenRouter配置
│   ├── utils/        # 工具函数
│   │   ├── execution_logger.py  # 执行日志系统
│   │   ├── log_viewer.py        # 日志查看器
│   │   ├── logging_config.py    # 日志配置
│   │   ├── llm_clients.py       # LLM客户端
│   │   └── state_definition.py  # 状态定义
│   └── main.py       # 主程序
├── tests/            # 测试
├── .env              # 环境变量
├── .env.example      # 环境变量示例
├── .gitignore        # Git忽略文件
├── logging_system.md # 日志系统说明
├── poetry.lock       # Poetry依赖锁定
├── pyproject.toml    # 项目配置
├── README.md         # 项目说明
└── test_agent_with_real_tools.py # 测试脚本
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## ⚠️ 关于 terminal 打印的信息

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

上述 error 可以忽略，这是由于异步执行未能正确关闭。不影响系统运行，可以忽视。

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,15,20,24&section=footer&height=100&animation=fadeIn" />
</div>
