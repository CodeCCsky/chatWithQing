import copy
import logging
import time
import random
from typing import Union

from openai import OpenAI, APIError

from third_party.deepseek_api.deepseek_tools import ds_tool

logger = logging.getLogger(__name__)


# 不记录历史，每次需要传入history_manager处理后的history
class deepseek_model:
    """deepseek api接口. 每次发送前需要调用 load_history 加载历史."""

    def __init__(
        self,
        api_key: str,
        system_prompt: str,
        tools: ds_tool = ds_tool(),
        temperature: float = 1.5,
        frequency_penalty: float = 0.8,
        presence_penalty: float = 0.8,
        output_json: bool = False,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> None:
        """deepseek api接口. 每次发送前需要调用load_history加载历史.

        Args:
            api_key (str): 你的 deepseek api key.
            system_prompt (str): 系统提示词.
            tools (ds_tool, optional): 可用工具, 传入ds_tool实例 (这个功能还没开始做). Defaults to ds_tool().
            temperature (float, optional): 模型温度 (0 ~ 2), 越高的温度输出越随机. Defaults to 1.5.
            frequency_penalty (float, optional): 频率惩罚 (-2 ~ 2), 0 以上时越高的频率惩罚会使模型输出相同内容的可能越小. Defaults to 0.8.
            presence_penalty (float, optional): 存在惩罚 (-2 ~ 2), 0 以上时越高的存在惩罚会使模型谈论新话题的可能性越大. Defaults to 0.8.
            output_json (bool, optional): 要求大模型严格使用json格式回复. 该项不建议设置为True, 经测试会有不给出回复的问题. Defaults to False.
            max_retries (int, optional): 请求出错时重试次数. Defaults to 3.
            retry_delay (int, optional): 请求出错时重试等待时间. Defaults to 5.
        """
        self.history = []
        self.api_key = api_key
        self.tools = tools
        self.current_response = None
        self.finish_reason = None
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.output_json = output_json
        self.system_prompt = system_prompt
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        if self.system_prompt is not None:
            self.history.append({"role": "system", "content": self.system_prompt})

        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def set_temperature(self, temperature: float) -> None:
        self.temperature = temperature

    def get_temperature(self) -> float:
        return self.temperature

    def set_frequency_penalty(self, frequency_penalty: float) -> None:
        self.frequency_penalty = frequency_penalty

    def get_frequency_penalty(self) -> float:
        return self.frequency_penalty

    def set_presence_penalty(self, presence_penalty: float) -> None:
        self.presence_penalty = presence_penalty

    def get_presence_penalty(self) -> float:
        return self.presence_penalty

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def get_api_key(self) -> str:
        return self.api_key

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def load_history(self, history: list[dict]) -> None:
        if not isinstance(history, list):
            raise ValueError("History must be a list of dictionaries")
        if history[0]["role"] == "system":
            self.history = copy.deepcopy(history[1:])
        else:
            self.history = copy.deepcopy(history)
        self.history.insert(0, {"role": "system", "content": self.system_prompt})

    def send_message(self, history: list[dict] = None, is_prefix: bool = False) -> tuple[str, str, dict]:
        if history is not None:
            self.load_history(history)
        if is_prefix:
            self.history[-1]["prefix"] = True
        for _ in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=self.history,
                    # tools=self.tools,  # TODO Implement tools functionality
                    # max_tokens=2048,
                    temperature=self.temperature,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stream=True,
                )
                self.current_response = ""
                token_usage = None
                self.finish_reason = None
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        self.current_response += chunk.choices[0].delta.content
                    if chunk.choices[0].finish_reason:
                        self.finish_reason = chunk.choices[0].finish_reason
                    if chunk.usage:
                        token_usage = {
                            "completion_tokens": chunk.usage.completion_tokens,
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        }
                self.history.clear()
                return self.current_response, self.finish_reason, token_usage
            except APIError as e:
                logger.error(f"api错误，将等待一段时间后重试 occured error content:{e} ; status code:{e.code}")
                delay = self.retry_delay + random.uniform(0, 5)  # 增加随机延迟
                time.sleep(delay)
            except Exception as e:
                logger.error(f"获取回复时出现意料之外的错误，将等待一段时间后重试 {e}")
                delay = self.retry_delay + random.uniform(0, 5)
                time.sleep(delay)
        self.history.clear()
        return "", "error", {}

    def get_response(self) -> str:
        return self.current_response

    def is_done(self) -> Union[str, None]:
        return self.finish_reason
