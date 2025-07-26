# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Tools module for Trae Agent."""

from typing import Type

from .base import Tool, ToolCall, ToolExecutor, ToolResult
from .bash_tool import BashTool
from .ckg_tool import CKGTool
from .context7_tool import Context7Tool
from .edit_tool import TextEditorTool
from .json_edit_tool import JSONEditTool
from .selenium_tool import SeleniumTool
from .sequential_thinking_tool import SequentialThinkingTool
from .task_done_tool import TaskDoneTool

__all__ = [
    "Tool",
    "ToolResult",
    "ToolCall",
    "ToolExecutor",
    "BashTool",
    "TextEditorTool",
    "JSONEditTool",
    "SeleniumTool",
    "SequentialThinkingTool",
    "TaskDoneTool",
    "CKGTool",
    "Context7Tool",
]

tools_registry: dict[str, Type[Tool]] = {
    "bash": BashTool,
    "str_replace_based_edit_tool": TextEditorTool,
    "json_edit_tool": JSONEditTool,
    "selenium": SeleniumTool,
    "sequentialthinking": SequentialThinkingTool,
    "task_done": TaskDoneTool,
    "ckg": CKGTool,
    "context7": Context7Tool,
}
