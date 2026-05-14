import os
from typing import Optional
from openai import OpenAI


class Analyzer:
    """DeepSeek 文献分析器，封装 API 客户端与分析逻辑。"""

    # 默认模型
    DEFAULT_MODEL: str = "deepseek-v4-pro"

    # 预设系统提示词
    SYSTEM_PROMPT: str = (
        "你是一个科研助理，能够准确理解用户的需求并提供文献摘要的分析结果。"
        "请根据以下内容进行分析，并提供详细的分析结果和建议："
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化分析器。

        Args:
            api_key:      DeepSeek API 密钥，默认从环境变量 DEEPSEEK_API_KEY 读取。
            base_url:     API 基础地址。
            model:        使用的模型名称，默认为 deepseek-v4-pro。
            system_prompt: 系统级提示词，默认使用类内置的 SYSTEM_PROMPT。
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.model = model or self.DEFAULT_MODEL
        self.system_prompt = system_prompt or self.SYSTEM_PROMPT

        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    def analyze(self, content: str, prompt: Optional[str] = None) -> str:
        """
        向 DeepSeek 发送分析请求。

        Args:
            content: 待分析的文本内容。
            prompt:  可选的系统提示词，为 None 时使用实例的 system_prompt。

        Returns:
            模型返回的分析结果字符串。
        """
        system_msg = prompt or self.system_prompt

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": content},
            ],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )
        return response.choices[0].message.content

    # ------------------------------------------------------------------
    # 魔术方法
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Analyzer(model={self.model!r}, base_url={self.base_url!r})"


# ======================================================================
# 便捷函数 —— 保持向后兼容，内部委托给类实例
# ======================================================================

_DEFAULT_ANALYZER = Analyzer()


def analyze_with_deepseek(
    content: str,
    prompt: Optional[str] = None,
    model: str = "deepseek-v4-pro",
) -> str:
    """
    向 DeepSeek 发送分析请求（兼容旧接口）。

    Args:
        content: 分析内容。
        prompt:  提示词。
        model:   使用的模型，默认为 deepseek-v4-pro。

    Returns:
        分析结果。
    """
    analyzer = Analyzer(model=model)
    return analyzer.analyze(content, prompt=prompt)


