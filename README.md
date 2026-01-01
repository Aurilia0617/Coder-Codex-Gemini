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

### 0. 前置要求

请确保您已成功安装和配置 Claude Code 与 Codex 两个编程工具：

- [Claude Code 安装指南](https://code.claude.com/docs)
- [Codex CLI 安装指南](https://developers.openai.com/codex/quickstart)

> [!IMPORTANT]
> 请确保您的 Claude Code 版本在 **v2.0.56** 以上；Codex CLI 版本在 **v0.61.0** 以上！

请确保您已成功安装 [uv](https://docs.astral.sh/uv/) 工具：

**Windows** 在 PowerShell 中运行以下命令：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS** 使用 curl/wget 下载并安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # 使用 curl

wget -qO- https://astral.sh/uv/install.sh | sh   # 使用 wget
```

> [!NOTE]
> 我们极力推荐 Windows 用户在 WSL 中运行本项目！

此外，您还需要：

- **GLM API Token**（从 [智谱 AI](https://open.bigmodel.cn) 获取）

### 1. 配置 GLM

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

### 2. 安装 MCP

#### 2.1 安装 CodexMCP（Codex 工具依赖）

```bash
claude mcp add codex -s user --transport stdio -- uvx --from git+https://github.com/GuDaStudio/codexmcp.git codexmcp
```

#### 2.2 安装 GLM-CODEX-MCP

```bash
claude mcp add glm-codex -s user --transport stdio -- uvx --from git+https://github.com/FredericMN/GLM-CODEX-MCP.git glm-codex-mcp
```

#### 2.3 验证安装

在终端中运行：

```bash
claude mcp list
```

> [!IMPORTANT]
> 如果看到如下描述，说明安装成功！
> ```
> codex: uvx --from git+https://github.com/GuDaStudio/codexmcp.git codexmcp - ✓ Connected
> glm-codex: uvx --from git+https://github.com/FredericMN/GLM-CODEX-MCP.git glm-codex-mcp - ✓ Connected
> ```

### 3. 配置权限（可选）

在 `~/.claude/settings.json` 中添加自动允许，使 Claude Code 可以自动与工具交互：

```json
{
  "permissions": {
    "allow": [
      "mcp__codex__codex",
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
2. Claude 为子任务生成精确 Prompt（含边界管控）
    │
    ▼
3. 调用 GLM 工具执行代码任务  ◄───────────────┐
    │                                         │
    ▼                                         │
4. GLM 返回结果 → Claude 初审                  │
    │                                         │
    ├─ 有明显问题 → Claude 直接修改             │
    │                                         │
    ▼                                         │
5. 调用 Codex 工具深度 review                  │
    │                                         │
    ├── ✅ 通过 → 完成任务                     │
    │                                         │
    ├── ⚠️ 建议优化 → Claude 分析并修改         │
    │                                         │
    └── ❌ 需要修改 → Claude 分析根因 ──────────┤
                        │                     │
                        ├─ 简单问题 → 直接修改 ┘
                        │
                        └─ 复杂问题 → 优化 Prompt 重新调用 GLM
```

## 全局推荐提示词

<details>
<summary>点击展开全局提示词配置（推荐添加到 ~/.claude/CLAUDE.md）</summary>

```markdown
# GLM-CODEX-MCP 协作指南

GLM 是你的代码执行者，Codex 是你的代码审核者。**所有代码决策权归你（Claude）所有**。

**角色分工**：
- 你（Claude/Opus）：架构师 + 协调者 + 最终决策者
- GLM-4.7：代码执行者（量大管饱，执行力强）
- Codex：独立审核者（第三方视角，质量把关）

## 协作流程

**1. 编码前（可选）**

复杂任务可先调用 GLM 或 Codex 讨论思路，获取建议。但最终方案由你决定。

**2. 编码中**

- **简单任务**：你直接完成
- **批量/重复任务**：调用 GLM 执行，你负责给出清晰、精确的 Prompt
- **需求不明确**：先理解、拆解，再委托执行

**3. 编码后（推荐）**

完成代码改动后，**调用 Codex 进行 review**：
- 检查代码质量（可读性、可维护性、潜在 bug）
- 评估需求完成度
- 给出明确结论：✅ 通过 / ⚠️ 建议优化 / ❌ 需要修改

**4. 独立判断**

Codex 和 GLM 的意见**仅供参考**。你必须有自己的判断，批判性采纳建议，不盲从。

## 工具调用规范

### GLM 工具（代码执行）

**调用时机**：批量代码生成、重复性修改、明确定义的功能实现

**参数**：
- PROMPT (string, 必填): 任务指令
- cd (Path, 必填): 工作目录
- sandbox (string): 沙箱策略，默认 `workspace-write`
- SESSION_ID (string): 会话 ID，用于多轮对话，默认空字符串（开启新会话）
- return_all_messages (boolean): 返回完整消息，默认 False

**返回值**：
```json
// 成功时
{
  "success": true,
  "tool": "glm",
  "SESSION_ID": "uuid-string",  // ← 保存此值用于后续对话
  "result": "GLM回复的文本内容"
}

// 失败时
{
  "success": false,
  "tool": "glm",
  "error": "错误信息"
}
```

**Prompt 模板**：
```
请执行以下代码任务：

**任务类型**：[新增功能 / 修复 Bug / 重构 / 其他]
**目标文件**：[文件路径]

**具体要求**：
1. [要求1]
2. [要求2]

**约束条件**：
- [约束1，如：仅修改 X 函数，不要动其他部分]
- [约束2，如：保持 API 签名不变]

**验收标准**：
- [标准1，如：通过现有单元测试]
- [标准2，如：性能不劣化]

请严格按照上述范围修改代码，完成后说明改动内容。
```

**使用规范**：
- **必须保存** `SESSION_ID` 以便多轮对话
- 检查 `success` 字段判断执行是否成功
- 从 `result` 字段获取 GLM 的回复内容
- 调试时设置 `return_all_messages=True` 获取 `all_messages` 详细过程

### Codex 工具（代码审核）

**调用时机**：代码改动完成后，需要独立审核时

**参数**：
- PROMPT (string, 必填): 审核任务描述
- cd (Path, 必填): 工作目录
- sandbox (string): 沙箱策略，**必须** `read-only`（严禁修改代码）
- SESSION_ID (string): 会话 ID，用于多轮对话，默认空字符串（开启新会话）
- return_all_messages (boolean): 返回完整消息，默认 False
- skip_git_repo_check (boolean): 允许非 Git 仓库，默认 True
- image (List[Path]): 附加图片文件路径列表，默认空列表
- model (string): 指定模型，默认使用 Codex 自己的配置
- yolo (boolean): 无需审批运行所有命令，默认 False
- profile (string): 配置文件名称，默认使用默认配置

**返回值**：
```json
// 成功时
{
  "success": true,
  "tool": "codex",
  "SESSION_ID": "uuid-string",  // ← 保存此值用于后续对话
  "result": "Codex回复的文本内容"
}

// 失败时
{
  "success": false,
  "tool": "codex",
  "error": "错误信息"
}
```

**Prompt 模板**：
```
请 review 以下代码改动：

**改动文件**：[文件列表]
**改动目的**：[简要描述]

**请检查**：
1. 代码质量（可读性、可维护性）
2. 潜在 Bug 或边界情况
3. 需求完成度

**请给出明确结论**：
- ✅ 通过：代码质量良好，可以合入
- ⚠️ 建议优化：[具体建议]
- ❌ 需要修改：[具体问题]
```

**使用规范**：
- **严格边界**：必须使用 `sandbox="read-only"`，Codex 严禁修改代码
- **必须保存** `SESSION_ID` 以便多轮对话
- 检查 `success` 字段判断审核是否成功
- 从 `result` 字段获取 Codex 的审核结论
- 调试时设置 `return_all_messages=True` 获取 `all_messages` 详细过程

## 推荐用法

**Codex 工具**（审核）：
- 如需详细追踪推理过程，设置 `return_all_messages=True`
- 用于精准定位问题、debug、代码审核

**GLM 工具**（执行）：
- 如需详细追踪执行过程，设置 `return_all_messages=True`
- 用于批量代码生成、重复性修改、代码原型快速编写

## 注意事项

- **严格边界**：Codex 默认 `sandbox=read-only`，严禁修改代码，仅提供 diff 建议
- **GLM 可写**：GLM 默认 `sandbox=workspace-write`，允许修改代码
- **会话管理**：每次调用后保存 `SESSION_ID` 以便多轮对话
- **工作目录**：确保 `cd` 参数指向正确的项目目录
- **独立思考**：对工具的建议要有自己的判断，不盲从
- **工具识别**：通过 `tool` 字段区分是 `glm` 还是 `codex` 的返回
```

</details>

## 开发

```bash
# 克隆仓库
git clone https://github.com/FredericMN/GLM-CODEX-MCP.git
cd GLM-CODEX-MCP

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
