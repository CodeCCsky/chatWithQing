import yaml
import re
import random


class emo_manager:
    EYE_NORMAL = 0
    EYE_INTENSE = 1
    EYE_SURPRISE = 2
    EYE_HALF_CLOSED = 3
    EYE_CLOSE_NORMAL = 4
    EYE_CLOSE_DEPRESSED = 5
    EYE_CLOSE_SMILE = 6

    def __init__(self) -> None:
        self.load_path = r"setting\emo_manager_setting.yaml"
        self.load_path = r"D:\workspace\CGMO\chatWIthQing\setting\emo_manager_setting.yaml"
        self.confirmed_emoji = {
            self.EYE_NORMAL: [],
            self.EYE_INTENSE: [],
            self.EYE_SURPRISE: [],
            self.EYE_HALF_CLOSED: [],
            self.EYE_CLOSE_NORMAL: [],
            self.EYE_CLOSE_DEPRESSED: [],
            self.EYE_CLOSE_SMILE: [],
        }
        self.unconfirmed_emoji = []
        self.ignored_str = []

    def _read_yaml(self) -> None:
        with open(self.load_path, "r", encoding="utf-8") as f:
            res: dict = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.confirmed_emoji = res.get("confirmed", self.confirmed_emoji)
            self.unconfirmed_emoji = res.get("unconfirmed", self.unconfirmed_emoji)
            self.ignored_str = res.get("ignored", self.ignored_str)

    def write_yaml(self) -> None:
        with open(self.load_path, "w", encoding="utf-8") as f:
            data = {
                "confirmed": self.confirmed_emoji,
                "unconfirmed": self.unconfirmed_emoji,
                "ignored": self.ignored_str,
            }
            yaml.dump(data=data, stream=f, allow_unicode=True)

    def process_string(self, input_string):
        extracted_emotion = {}
        result_string = input_string
        now_unconfirmed = []
        offset = 0

        pattern = r"[\(（](.*?)[\)）]"
        matches = re.finditer(pattern, input_string)

        for match in matches:
            start, end = match.span()
            substring = match.group(1)
            
            if substring in self.ignored_str:
                continue
            
            matching_keys = []
            for key, value_list in self.confirmed_emoji.items():
                if substring in value_list:
                    matching_keys.append(key)
            
            if matching_keys:
                chosen_key = random.choice(matching_keys)
                extracted_emotion[start - offset] = chosen_key
                result_string = result_string[:start - offset] + result_string[end - offset:]
                offset += end - start
            else:
                extracted_emotion[start - offset] = -1
                self.unconfirmed_emoji.append(substring)

        return result_string, extracted_emotion, now_unconfirmed
