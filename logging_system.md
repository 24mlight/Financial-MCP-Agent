# 执行日志系统

## 概述

执行日志系统为每次运行创建独立的日志文件夹，详细记录所有 agent 与 LLM 的交互信息，包括输入、输出、执行时间、工具使用等。这个系统可以帮助你：

- 调试 agent 执行过程中的问题
- 分析性能瓶颈
- 追踪 LLM 交互的详细信息
- 监控工具使用情况
- 生成执行报告

## 日志目录结构

每次执行都会在 `logs/` 目录下创建一个独立的子文件夹，结构如下：

```
logs/
└── 20241220_143052_a1b2c3d4/          # 执行ID (时间戳_唯一标识)
    ├── execution_info.json            # 执行基本信息
    ├── EXECUTION_SUMMARY.md           # 可读的执行摘要
    ├── agents/                        # Agent执行记录
    │   ├── fundamental_agent_execution.json
    │   ├── technical_agent_execution.json
    │   ├── value_agent_execution.json
    │   └── summary_agent_execution.json
    ├── llm_interactions/              # LLM交互详情
    │   ├── fundamental_agent_react_agent_12345678.json
    │   ├── fundamental_agent_react_agent_12345678.txt
    │   ├── summary_agent_summary_generation_87654321.json
    │   └── summary_agent_summary_generation_87654321.txt
    ├── tools/                         # 工具使用记录
    │   ├── fundamental_agent_tools.jsonl
    │   ├── technical_agent_tools.jsonl
    │   └── value_agent_tools.jsonl
    └── reports/                       # 报告相关
        ├── final_report_info.json
        └── final_report_copy.md
```

## 日志文件说明

### 1. execution_info.json

记录整个执行过程的基本信息：

- 执行 ID 和时间戳
- 环境配置信息
- 总执行时间
- 成功/失败状态
- 执行统计摘要

### 2. agents/目录

每个 agent 的执行记录，包含：

- 开始和结束时间
- 输入数据
- 输出数据预览
- 执行时间
- 成功/失败状态
- 错误信息（如有）

### 3. llm_interactions/目录

详细的 LLM 交互记录，包含：

- JSON 格式的结构化数据
- TXT 格式的可读文本
- 输入消息和输出内容
- 模型配置参数
- 执行时间和性能数据

### 4. tools/目录

工具使用记录（JSONL 格式），包含：

- 工具名称和参数
- 执行结果
- 执行时间
- 成功/失败状态

### 5. reports/目录

最终报告相关信息：

- 报告元数据
- 报告内容副本

## 使用日志查看器

系统提供了一个专门的日志查看器工具，可以方便地查看和分析执行日志。

### 基本用法

```bash
# 查看最近5次执行记录
python -m src.utils.log_viewer

# 查看最近10次执行记录
python -m src.utils.log_viewer --list --limit 10

# 查看特定执行的详细信息
python -m src.utils.log_viewer --show 20241220_143052_a1b2c3d4

# 只查看摘要，不显示详细信息
python -m src.utils.log_viewer --show 20241220_143052_a1b2c3d4 --summary-only

# 指定日志目录
python -m src.utils.log_viewer --log-dir /path/to/logs
```

### 命令行参数

- `--list, -l`: 列出最近的执行记录
- `--show, -s`: 显示特定执行 ID 的详细信息
- `--limit`: 列出记录的数量限制（默认 5）
- `--summary-only`: 只显示摘要，不显示详细信息
- `--log-dir`: 指定日志目录路径（默认"logs"）

## 日志系统集成

日志系统已经完全集成到主程序中，无需额外配置。每次运行 `python -m src.main` 时，系统会自动：

1. 初始化执行日志记录器
2. 记录每个 agent 的执行过程
3. 记录所有 LLM 交互详情
4. 记录工具使用情况
5. 生成最终的执行摘要

## 性能影响

日志系统设计为轻量级，对程序性能的影响很小：

- 异步写入，不阻塞主程序执行
- 智能缓存，避免重复操作
- 压缩存储，节省磁盘空间

## 日志管理

### 自动清理

系统不会自动删除旧日志，你可以根据需要手动清理：

```bash
# 删除30天前的日志
find logs/ -type d -mtime +30 -exec rm -rf {} \;
```

### 日志分析

你可以使用各种工具分析日志数据：

- 使用 `jq` 处理 JSON 文件
- 使用 `grep` 搜索特定内容
- 编写自定义脚本进行数据分析

## 故障排除

### 常见问题

1. **日志目录权限问题**

   - 确保程序有写入 `logs/` 目录的权限

2. **磁盘空间不足**

   - 定期清理旧日志文件
   - 监控磁盘使用情况

3. **日志文件损坏**
   - 检查磁盘错误
   - 验证 JSON 文件格式

### 调试技巧

1. **查看最新执行的错误**

   ```bash
   python -m src.utils.log_viewer --list --limit 1
   ```

2. **搜索特定错误**

   ```bash
   grep -r "Error" logs/
   ```

3. **分析性能问题**
   ```bash
   # 查看执行时间最长的LLM交互
   find logs/ -name "*.json" -path "*/llm_interactions/*" -exec jq '.performance.execution_time_seconds' {} \; | sort -nr | head -10
   ```

## 扩展功能

日志系统设计为可扩展的，你可以：

1. **添加自定义日志记录**

   ```python
   from src.utils.execution_logger import get_execution_logger

   logger = get_execution_logger()
   logger.log_custom_event("my_event", {"data": "value"})
   ```

2. **创建自定义分析工具**

   ```python
   from src.utils.log_viewer import LogViewer

   viewer = LogViewer()
   executions = viewer.list_executions(100)
   # 进行自定义分析
   ```

3. **集成监控系统**
   - 将日志数据发送到监控平台
   - 设置告警规则
   - 生成性能报告

## 最佳实践

1. **定期检查日志**

   - 每周查看执行摘要
   - 关注错误和性能问题

2. **保留重要日志**

   - 备份成功的执行日志
   - 保存问题诊断相关的日志

3. **监控资源使用**

   - 定期检查磁盘使用情况
   - 监控日志文件大小

4. **使用日志进行优化**
   - 分析 LLM 交互时间
   - 优化工具使用效率
   - 改进 agent 提示词
