"""
analysis 模块 —— 文献摘要分析工具集。

提供基于 DeepSeek 和 Gemini 的文献分析功能。
"""

from importlib import import_module as _im

# analysis-ds.py 中的函数（文件名含连字符，需用 importlib 导入）
_ds = _im("src.analysis.analysis-ds")
analyze_with_deepseek = _ds.analyze_with_deepseek
PROMPT_DEFAULT = _ds.PROMPT_DEFAULT

# analasis copy.py 中的函数（文件名含空格，需用 importlib 导入）
_gemini = _im("src.analysis.analasis copy")
analyze_context = _gemini.analyze_context
ANALYSIS_SCHEMA = _gemini.ANALYSIS_SCHEMA

__all__ = [
    "analyze_with_deepseek",
    "PROMPT_DEFAULT",
    "analyze_context",
    "ANALYSIS_SCHEMA",
]
