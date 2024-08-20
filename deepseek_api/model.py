import copy
from typing import Union, List, Dict
from openai import OpenAI
from deepseek_api.deepseek_tools import ds_tool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class deepseek_model:
    def __init__(self, api_key: str, system_prompt: str, tools: ds_tool = ds_tool(), record_history: bool = True) -> None:
        self.history = []
        self.api_key = api_key
        self.tools = tools
        self.record_history = record_history
        self.current_response = None
        self.finish_reason = None
        if system_prompt is not None:
            self.history.append({"role": "system", "content": system_prompt})

        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def load_history(self, history: List[Dict]) -> None:
        if not isinstance(history, list):
            raise ValueError("History must be a list of dictionaries")
        self.history = copy.deepcopy(history)

    def get_history(self) -> List[Dict]:
        return copy.deepcopy(self.history)

    def add_msg(self, text: str) -> None:
        if not isinstance(text, str):
            raise ValueError("Message text must be a string")
        self.history.append({"role": "user", "content": text})

    def send_message(self) -> tuple[str, str, dict]:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.history,
                #tools=self.tools,  # TODO: Implement tools functionality
                max_tokens=1024,
                temperature=1.1,
                presence_penalty=0.4,
                stream=True
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
                        'completion_tokens': chunk.usage.completion_tokens,
                        'prompt_tokens': chunk.usage.prompt_tokens,
                        'total_tokens': chunk.usage.total_tokens
                    }
            self.history.append({"role": "assistant", "content": self.current_response})
            if not self.record_history:
                self.history = [self.history[0]]
            return self.current_response, self.finish_reason, token_usage
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return "", "error", {}

    def get_response(self) -> str:
        return self.current_response

    def is_done(self) -> Union[str, None]:
        return self.finish_reason