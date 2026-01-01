"""配置加载模块

优先级：配置文件 > 环境变量
配置文件路径：~/.glm-codex-mcp/config.toml
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """配置错误"""
    pass


def get_config_path() -> Path:
    """获取配置文件路径"""
    return Path.home() / ".glm-codex-mcp" / "config.toml"


def load_config() -> dict[str, Any]:
    """加载配置，优先级：配置文件 > 环境变量

    Returns:
        配置字典，包含 glm 和 codex 配置

    Raises:
        ConfigError: 未找到有效配置时抛出
    """
    config_path = get_config_path()

    # 优先读取配置文件
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"配置文件格式错误：{e}")

    # 兜底：从环境变量读取
    if os.environ.get("GLM_API_TOKEN"):
        return {
            "glm": {
                "api_token": os.environ["GLM_API_TOKEN"],
                "base_url": os.environ.get(
                    "GLM_BASE_URL",
                    "https://open.bigmodel.cn/api/anthropic"
                ),
                "model": os.environ.get("GLM_MODEL", "glm-4.7"),
            }
        }

    # 生成配置引导信息
    config_example = '''# ~/.glm-codex-mcp/config.toml

[glm]
api_token = "your-glm-api-token"
base_url = "https://open.bigmodel.cn/api/anthropic"
model = "glm-4.7"

# 可选：额外环境变量
[glm.env]
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
'''

    raise ConfigError(
        f"未找到 GLM 配置！\n\n"
        f"请创建配置文件：{config_path}\n\n"
        f"配置文件示例：\n{config_example}\n"
        f"或设置环境变量 GLM_API_TOKEN"
    )


def build_glm_env(config: dict[str, Any]) -> dict[str, str]:
    """构建 GLM 调用所需的环境变量

    Args:
        config: 配置字典

    Returns:
        包含所有环境变量的字典
    """
    glm_config = config.get("glm", {})
    model = glm_config.get("model", "glm-4.7")

    env = os.environ.copy()

    # GLM API 认证
    env["ANTHROPIC_AUTH_TOKEN"] = glm_config.get("api_token", "")
    env["ANTHROPIC_BASE_URL"] = glm_config.get(
        "base_url",
        "https://open.bigmodel.cn/api/anthropic"
    )

    # 所有模型别名都映射到 GLM
    env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
    env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
    env["CLAUDE_CODE_SUBAGENT_MODEL"] = model

    # 用户自定义的额外环境变量
    for key, value in glm_config.get("env", {}).items():
        env[key] = str(value)

    return env


def validate_config(config: dict[str, Any]) -> None:
    """验证配置有效性

    Args:
        config: 配置字典

    Raises:
        ConfigError: 配置无效时抛出
    """
    glm_config = config.get("glm", {})

    if not glm_config.get("api_token"):
        raise ConfigError("GLM 配置缺少 api_token")

    if not glm_config.get("base_url"):
        raise ConfigError("GLM 配置缺少 base_url")


# 全局配置缓存
_config_cache: dict[str, Any] | None = None


def get_config() -> dict[str, Any]:
    """获取配置（带缓存）

    首次调用时加载配置并验证，后续调用直接返回缓存

    Returns:
        配置字典
    """
    global _config_cache

    if _config_cache is None:
        _config_cache = load_config()
        validate_config(_config_cache)

    return _config_cache


def reset_config_cache() -> None:
    """重置配置缓存（主要用于测试）"""
    global _config_cache
    _config_cache = None
