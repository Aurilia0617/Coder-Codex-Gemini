# GLM-CODEX-MCP

> Claude + GLM + Codex 三方协作 MCP 服务器

让 Claude (Opus) 作为架构师调度 GLM 执行代码任务、Codex 审核代码质量，形成自动化的三方协作闭环。

## 核心价值

| 维度 | 价值 |
|------|------|
| **成本优化** | Opus 负责思考（贵但强），GLM 负责执行（量大管饱） |
| **能力互补** | Opus 补足 GLM 创造力短板，Codex 提供独立审核视角 |
| **质量保障** | 双重审核机制（Claude 初审 + Codex 终审） |
| **全自动闭环** | 拆解 → 执行 → 审核 → 重试，无需人工干预 |

## 角色分工

```
Claude (Opus)     →  架构师 + 初审官 + 终审官 + 协调者
GLM-4.7           →  代码执行者（生成、修改、批量任务）
Codex (OpenAI)    →  独立代码审核者（质量把关）
```

## 快速开始

### 1. 前置要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器
- Claude Code CLI（已安装并登录）
- Codex CLI（已安装并登录）
- GLM API Token（从[智谱 AI](https://open.bigmodel.cn) 获取）

### 2. 配置 GLM

**方式一：配置文件（推荐）**

```bash
# Windows
mkdir %USERPROFILE%\.glm-codex-mcp

# macOS/Linux
mkdir -p ~/.glm-codex-mcp
```

创建配置文件 `~/.glm-codex-mcp/config.toml`：

```toml
[glm]
api_token = "your-glm-api-token"
base_url = "https://open.bigmodel.cn/api/anthropic"
model = "glm-4.7"

[glm.env]
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
```

**方式二：环境变量**

```bash
# Windows PowerShell
$env:GLM_API_TOKEN = "your-glm-api-token"
$env:GLM_BASE_URL = "https://open.bigmodel.cn/api/anthropic"
$env:GLM_MODEL = "glm-4.7"

# macOS/Linux
export GLM_API_TOKEN="your-glm-api-token"
export GLM_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export GLM_MODEL="glm-4.7"
```

### 3. 安装 MCP

```bash
# 从 GitHub 安装
claude mcp add glm-codex -s user -- uvx --from git+https://github.com/your-username/glm-codex-mcp.git glm-codex-mcp

# 或从本地安装（开发模式）
claude mcp add glm-codex -s user -- uv run --directory /path/to/glm-codex-mcp glm-codex-mcp

# 验证安装
claude mcp list
```

### 4. 配置权限（可选）

在 `~/.claude/settings.json` 中添加自动允许：

```json
{
  "permissions": {
    "allow": [
      "mcp__glm-codex__glm",
      "mcp__glm-codex__codex"
    ]
  }
}
```

## MCP 工具

### glm

调用 GLM-4.7 执行代码生成或修改任务。

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| PROMPT | string | ✅ | - | 任务指令 |
| cd | Path | ✅ | - | 工作目录 |
| sandbox | string | - | workspace-write | 沙箱策略 |
| SESSION_ID | string | - | "" | 会话 ID |
| return_all_messages | bool | - | false | 返回完整消息 |
| image | List[Path] | - | [] | 附加图片 |

### codex

调用 Codex 进行代码审核。

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| PROMPT | string | ✅ | - | 审核任务描述 |
| cd | Path | ✅ | - | 工作目录 |
| sandbox | string | - | read-only | 沙箱策略 |
| SESSION_ID | string | - | "" | 会话 ID |
| skip_git_repo_check | bool | - | true | 允许非 Git 仓库 |
| return_all_messages | bool | - | false | 返回完整消息 |
| image | List[Path] | - | [] | 附加图片 |
| model | string | - | "" | 指定模型 |
| yolo | bool | - | false | 跳过沙箱 |
| profile | string | - | "" | 配置文件名称 |

## 协作流程

```
用户需求
    │
    ▼
1. Claude 分析需求，拆解为子任务
    │
    ▼
2. Claude 为子任务生成精确 Prompt
    │
    ▼
3. 调用 GLM 工具执行代码任务  ◄───────┐
    │                                 │
    ▼                                 │
4. GLM 返回结果 → Claude 初审          │
    │                                 │
    ▼                                 │
5. 调用 Codex 工具 review              │
    │                                 │
    ├── ✅ 通过 → 完成任务             │
    │                                 │
    └── ❌ 不通过 → 分析原因 → 优化 ───┘
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/your-username/glm-codex-mcp.git
cd glm-codex-mcp

# 安装依赖
uv sync

# 运行测试
uv run pytest

# 本地运行
uv run glm-codex-mcp
```

## 参考资源

- [CodexMCP](https://github.com/GuDaStudio/codexmcp) - 核心参考实现
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 框架
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- [Codex CLI](https://developers.openai.com/codex/quickstart)
- [智谱 AI](https://open.bigmodel.cn) - GLM API

## License

MIT
