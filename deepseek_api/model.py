import copy
from typing import Union, List, Dict
from openai import OpenAI
from deepseek_api.deepseek_tools import ds_tool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 不记录历史，每次需要传入history_manager处理后的history

class deepseek_model:
    def __init__(self, api_key: str, system_prompt: str, tools: ds_tool = ds_tool(), temperature: float = 1.0, presence_penalty: float = 0.4, output_json: bool = True) -> None:
        self.history = []
        self.api_key = api_key
        self.tools = tools
        self.current_response = None
        self.finish_reason = None
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.output_json = output_json
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.history.append({"role": "system", "content": self.system_prompt})

        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def load_history(self, history: List[Dict]) -> None:
        if not isinstance(history, list):
            raise ValueError("History must be a list of dictionaries")
        if history[0]['role'] == 'system':
            self.history = copy.deepcopy(history[1:])
        else :
            self.history = copy.deepcopy(history)
        self.history.insert(0,{'role': 'system', 'content': self.system_prompt})

    def send_message(self, is_prefix: bool = False) -> tuple[str, str, dict]:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.history,
                #tools=self.tools,  # TODO Implement tools functionality
                max_tokens=1024,
                temperature=self.temperature,
                presence_penalty=self.presence_penalty,
                stream=True
            )
            if is_prefix:
                self.history[-1]['prefix'] = True
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
                        'completion_tokens': chunk.usage.completion_tokens,
                        'prompt_tokens': chunk.usage.prompt_tokens,
                        'total_tokens': chunk.usage.total_tokens
                    }
            return self.current_response, self.finish_reason, token_usage
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return "", "error", {}
        self.history.clear()

    def get_response(self) -> str:
        return self.current_response

    def is_done(self) -> Union[str, None]:
        return self.finish_reason
