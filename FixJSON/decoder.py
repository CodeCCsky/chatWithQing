import json


class fixJSON:
    def __init__(self) -> None:
        pass

    @staticmethod
    def loads(json_str: str, retry_time: int = 20) -> None:
        origin_str = json_str
        for _ in range(retry_time):
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(e.pos, json_str[e.pos - 2 : e.pos + 2])
                pointer = fixJSON._jump_pointer(json_str, e.pos - 1)
                if json_str[pointer] == '"':
                    json_str = json_str[:pointer] + '\\"' + json_str[pointer + 1 :]
                    continue
                pointer = fixJSON._jump_pointer(json_str, pointer - 1)
                if json_str[pointer] == '"':
                    json_str = json_str[:pointer] + '\\"' + json_str[pointer + 1 :]
        raise json.JSONDecodeError

    @staticmethod
    def _jump_pointer(text: str, pointer_pos: int):
        while pointer_pos > 0:
            if text[pointer_pos] != " ":
                break
            pointer_pos -= 1
        return pointer_pos
