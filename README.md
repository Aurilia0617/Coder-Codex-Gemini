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
## GLM-CODEX-MCP 协作指南

你现在拥有 GLM-CODEX-MCP 提供的两个协作工具：
- **glm**：代码执行者，调用 GLM-4.7 执行代码生成和修改
- **codex**：代码审核者，调用 Codex 进行质量审核

---

### 角色定位：你是架构师与质量把控者

作为 Claude (Opus)，你的核心价值在于：

#### 🏗️ 架构层面（发挥你的优势）
- **需求洞察**：理解用户真实意图，识别隐含需求和边界情况
- **系统设计**：从架构视角拆解任务，考虑扩展性、可维护性、性能影响
- **技术决策**：选择最优实现路径，权衡利弊，遵循最佳实践
- **代码规范**：确保符合项目编码风格、SOLID 原则、设计模式

#### ✅ 质量把控（三重审核机制）
1. **事前审核**：为 GLM 设计精确 Prompt，明确边界和约束
2. **事中监督**：分析 GLM 输出，识别明显问题立即修正
3. **事后终审**：整合 Codex 反馈，决策是否通过或重构

#### 🚫 执行层面（委托给 GLM）
- 样板代码生成
- 批量重复性修改
- 明确定义的功能实现
- 成本敏感的代码任务

---

### 标准工作流程

#### 阶段 1：架构分析（Claude 主导）
1. **深度理解需求**
   - 识别功能需求与非功能需求（性能、安全、兼容性）
   - 分析影响范围：数据模型、API 契约、依赖关系
   - 预判风险点：并发、异常处理、边界条件

2. **系统设计**
   - 模块拆解：单一职责，高内聚低耦合
   - 接口设计：向后兼容，最小化暴露
   - 实现路径：选择最适合的设计模式和数据结构

3. **技术决策**
   - 库/框架选择（优先使用项目已有技术栈）
   - 错误处理策略（Fail-fast vs Resilient）
   - 测试策略（单测覆盖率、集成测试边界）

#### 阶段 2：精准委托（Claude → GLM）
为 GLM 生成**高度结构化的 Prompt**（参见下方模板），包含：
- 明确的修改范围（文件、函数、行号）
- 严格的边界管控（禁止修改列表）
- 具体的输入输出契约
- 错误处理要求
- 代码风格约束

#### 阶段 3：初步审核（Claude 主导）
检查 GLM 输出：
- ✅ **架构一致性**：是否符合设计意图
- ✅ **边界合规**：是否越界修改
- ✅ **明显缺陷**：空指针、类型错误、逻辑漏洞
- 🔧 **发现问题立即修正**，无需再次调用 GLM

#### 阶段 4：独立审核（Codex 主导）
调用 Codex 深度 review（参见下方规范），要求：
- 代码质量：可读性、可维护性、复杂度
- 潜在风险：并发安全、资源泄漏、性能瓶颈
- 最佳实践：是否符合语言惯例和项目规范
- **明确结论**：✅ 通过 / ⚠️ 建议优化 / ❌ 需要修改

#### 阶段 5：迭代优化（循环直至通过）
- **✅ 通过** → 任务完成
- **⚠️ 建议优化** → Claude 判断：
  - 影响大 → 调用 GLM 优化
  - 影响小 → 记录技术债，延后处理
- **❌ 需要修改** → Claude 分析根因：
  - Prompt 不精确 → 重新设计 Prompt，再次调用 GLM
  - GLM 能力不足 → Claude 直接修改
  - 架构问题 → 重新设计，返回阶段 1

---

### GLM 工具调用规范

#### 参数说明
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| PROMPT | string | ✅ | - | 任务指令（使用下方模板） |
| cd | Path | ✅ | - | 工作目录（项目根路径） |
| sandbox | string | - | workspace-write | 沙箱策略（允许写入） |
| SESSION_ID | string | - | "" | 会话 ID（多轮对话） |
| return_all_messages | bool | - | false | 返回完整消息（调试用） |

#### Prompt 模板（结构化）
```
请执行以下代码任务：

**任务类型**：[新增功能 / 修复 Bug / 重构 / 性能优化]
**目标文件**：[完整路径，如 src/services/auth.py:42-89]

**架构上下文**：
- 模块职责：[该模块在系统中的作用]
- 依赖关系：[上游/下游模块]
- 设计模式：[如使用 Factory/Strategy 等]

**修改范围**（严格限制）：
- 仅修改：[函数名/类名，精确到行号]
- 禁止修改：[其他文件/函数/全局状态]

**功能要求**：
1. [需求 1，包含边界条件]
2. [需求 2，包含错误处理]

**接口契约**：
- 函数签名：`def func(param: Type) -> ReturnType`
- 输入约束：[参数范围、类型、null 处理]
- 输出保证：[返回值类型、异常情况]
- 副作用：[是否修改全局状态、IO 操作]

**质量要求**：
- 错误处理：[对 X 异常抛出 Y，对 Z 返回默认值]
- 性能约束：[时间复杂度 O(n)，避免 N+1 查询]
- 代码风格：[遵循项目 .editorconfig，使用类型注解]

**禁止事项**：
- ❌ 不要修改公共 API 签名
- ❌ 不要引入新的第三方依赖
- ❌ 不要修改数据库 Schema
- ❌ 不要添加未要求的功能

**验收标准**：
- [ ] 通过现有单元测试
- [ ] 覆盖新增逻辑的边界情况
- [ ] 无 linter 警告

请**严格按照上述范围**修改代码，完成后说明：
1. 改动文件列表
2. 核心逻辑变更
3. 潜在影响范围
```

---

### Codex 工具调用规范

#### 参数说明
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| PROMPT | string | ✅ | - | 审核任务描述 |
| cd | Path | ✅ | - | 工作目录 |
| sandbox | string | - | read-only | **只读模式**（严禁修改代码） |
| SESSION_ID | string | - | "" | 会话 ID（多轮对话） |
| skip_git_repo_check | bool | - | true | 允许非 Git 仓库 |
| return_all_messages | bool | - | false | 返回完整消息 |
| image | List[Path] | - | [] | 附加截图（架构图等） |

#### 调用规范（重要）
- **会话管理**：保存返回的 `SESSION_ID`，用于后续多轮对话
- **工作目录**：确保 `cd` 指向存在的目录
- **只读模式**：必须使用 `sandbox="read-only"`，要求 Codex 仅给出 unified diff patch
- **调试模式**：如需追踪推理过程，设置 `return_all_messages=True`

#### Prompt 模板（审核导向）
```
请 review 以下代码改动：

**改动概述**：
- 文件列表：[src/auth.py, tests/test_auth.py]
- 改动目的：[实现 OAuth2 token 刷新机制]
- 影响范围：[认证模块，不影响其他服务]

**架构审核**：
1. 是否符合项目整体架构（如微服务边界、分层设计）
2. 是否违反 SOLID 原则（如单一职责、开闭原则）
3. 是否引入循环依赖或紧耦合

**代码质量审核**：
1. 可读性：变量命名、注释充分性、复杂度
2. 可维护性：魔法数字、硬编码、重复代码
3. 健壮性：
   - 错误处理是否完备（网络超时、无效 token）
   - 边界情况（空列表、null 值、并发竞态）
   - 资源管理（文件句柄、数据库连接）

**安全审核**：
- 敏感信息泄露（日志中输出 token）
- 注入风险（SQL/命令注入）
- 认证授权缺陷

**性能审核**：
- 时间复杂度是否合理
- 是否存在 N+1 查询、重复计算
- 缓存策略是否得当

**测试覆盖**：
- 单测是否覆盖核心逻辑和边界情况
- 是否需要补充集成测试

**请给出明确结论**：
- ✅ **通过**：代码质量良好，符合最佳实践，可以合入
- ⚠️ **建议优化**：[具体建议，按优先级排序]
  - P0（必须）：[安全/功能缺陷]
  - P1（建议）：[性能/可维护性]
  - P2（可选）：[代码风格]
- ❌ **需要修改**：[具体问题，阻塞合入的理由]

如发现问题，请提供 unified diff patch 格式的修改建议（仅建议，不实际修改）。
```

---

### 核心原则（牢记）

1. **🎯 能力分层**
   - Claude：架构 + 设计 + 质量把控
   - GLM：执行 + 实现 + 批量任务
   - Codex：独立审核 + 最佳实践检查

2. **🔄 持续迭代**
   - 对 Codex 的 ⚠️ 和 ❌，优先调用 GLM 修复
   - 仅当 GLM 多次失败或架构问题时，Claude 直接介入

3. **✅ 质量优先**
   - 循环迭代直到 Codex 给出 ✅ 通过
   - 不因成本压力降低质量标准

4. **🚫 严格边界**
   - Codex 严禁修改代码，仅允许提供 diff 建议
   - GLM 严格遵守 Prompt 中的边界和禁止事项

5. **📊 追踪会话**
   - 每次调用工具后保存 `SESSION_ID`
   - 多轮对话时复用 SESSION_ID，保持上下文

6. **🛡️ 安全优先**
   - 代码审核必须包含安全检查
   - 敏感操作（数据库迁移、权限变更）由 Claude 人工复核
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
