import json


class fixJSON:
    def __init__(self) -> None:
        pass

    @staticmethod
    def loads(json_str: str, retry_time: int = 20) -> None:
        for _ in range(retry_time):
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                pointer = fixJSON._jump_pointer(json_str, e.pos - 1)
                if json_str[pointer] == '"':
                    json_str = json_str[:pointer] + '\\"' + json_str[pointer + 1 :]
                    continue
                pointer = fixJSON._jump_pointer(json_str, pointer - 1)
                if json_str[pointer] == '"':
                    json_str = json_str[:pointer] + '\\"' + json_str[pointer + 1 :]
        raise ValueError

    @staticmethod
    def _jump_pointer(text: str, pointer_pos: int):
        while pointer_pos > 0:
            if text[pointer_pos] != " ":
                break
            pointer_pos -= 1
        return pointer_pos


prompt = """请接受一个格式错误的JSON输入，并输出一个格式正确的JSON。输出的JSON必须包含"role_thoughts"和"role_response"项，并且不能更改原始JSON中存储的数据。请确保输出的JSON格式正确且易于解析。
示例1:
输入: 修复以下JSON: "{\"role_thoughts\": \"……好喜欢♥\"}\n{\"role_response\": \"(沉醉)**……最喜欢你的手了♥**\"}"
输出: "{\"role_thoughts\": \"……好喜欢♥\",\"role_response\": \"(沉醉)**……最喜欢你的手了♥**\"}"
"""


#from third_party.deepseek_api import deepseek_model
from openai import OpenAI
class fixJSONwithLLM:
    def __init__(self) -> None:
        pass

    @staticmethod
    def loads(json_str: str, api_key: str):
        # 调用deepseek_model会造成循环引用...我恨循环引用...
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        sys_prompt = ""
        try:
            with open(r"system_prompt\FixJSON\prompt.txt", "r", encoding="utf-8") as f:
                sys_prompt = f.read()
        except OSError:
            sys_prompt = prompt
        finally:
            
            request_data = [{"role" :"system","content":sys_prompt},{"role": "user", "content": json_str}]
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=request_data,
                response_format={
                    'type': 'json_object'
                },
                stream=False
            )
        return response.choices[0].message.content
