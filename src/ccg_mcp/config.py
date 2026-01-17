"""配置加载模块

配置文件路径：~/.ccg-mcp/config.toml
配置文件可选，用于自定义各角色的默认模型。
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """配置错误"""
    pass


def get_config_path() -> Path:
    """获取配置文件路径"""
    return Path.home() / ".ccg-mcp" / "config.toml"


def load_config() -> dict[str, Any]:
    """加载配置文件

    Returns:
        配置字典，如果配置文件不存在则返回空字典
    """
    config_path = get_config_path()

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"配置文件格式错误：{e}")

    return {}


# 全局配置缓存
_config_cache: dict[str, Any] | None = None


def get_config() -> dict[str, Any]:
    """获取配置（带缓存）

    首次调用时加载配置，后续调用直接返回缓存

    Returns:
        配置字典
    """
    global _config_cache

    if _config_cache is None:
        _config_cache = load_config()

    return _config_cache


def reset_config_cache() -> None:
    """重置配置缓存（主要用于测试）"""
    global _config_cache
    _config_cache = None


def get_coder_model() -> str:
    """获取 Coder 默认模型

    优先级：配置文件 coder.model > 默认值 "gpt-5.2-codex"

    Returns:
        模型名称
    """
    try:
        config = get_config()
        return config.get("coder", {}).get("model", "gpt-5.2-codex")
    except ConfigError:
        return "gpt-5.2-codex"


def get_codex_model() -> str:
    """获取 Codex 默认模型

    优先级：配置文件 codex.model > 默认值 "gpt-5.2-codex"

    Returns:
        模型名称
    """
    try:
        config = get_config()
        return config.get("codex", {}).get("model", "gpt-5.2-codex")
    except ConfigError:
        return "gpt-5.2-codex"


def get_gemini_model() -> str:
    """获取 Gemini 默认模型

    优先级：配置文件 gemini.model > 默认值 "gemini-3-pro-preview"

    Returns:
        模型名称
    """
    try:
        config = get_config()
        return config.get("gemini", {}).get("model", "gemini-3-pro-preview")
    except ConfigError:
        return "gemini-3-pro-preview"
