import yaml
import re
import random
import enum


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
        self.read_yaml()

    def read_yaml(self) -> None:
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

    def process_string(self, input_string: str) -> dict:
        extracted_emotion = {}
        normal_result_string = input_string
        forced_result_string = input_string
        now_unconfirmed = []
        offset = 0
        offset_forced = 0

        pattern = r"[\(（](.*?)[\)）]"
        # 好恐怖的正则表达式...(ai生成的)
        force_pattern = re.compile(
            r"[^\u0020-\u007E\uFF00-\uFFEF\u00A0-\u00FF\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF\u0021-\u002F\u003A-\u0040\u005B-\u0060\u007B-\u007E\u3000-\u303F]"
        )
        matches = re.finditer(pattern, input_string)
        forced_result_string = re.sub(force_pattern, ",", forced_result_string)

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
                normal_result_string = (
                    normal_result_string[: start - offset] + "," + normal_result_string[end - offset :]
                )
                forced_result_string = (
                    forced_result_string[: start - offset_forced] + "," + forced_result_string[end - offset_forced :]
                )
                offset += end - start - 1
                offset_forced += end - start - 1
            else:
                extracted_emotion[start - offset] = -1
                if substring not in self.unconfirmed_emoji:
                    self.unconfirmed_emoji.append(substring)
                forced_result_string = (
                    forced_result_string[: start - offset_forced] + "," + forced_result_string[end - offset_forced :]
                )
                offset_forced += end - start - 1

        return {
            "normal_result_string": normal_result_string,
            "forced_result_string": forced_result_string,
            "extracted_emotion": extracted_emotion,
            "now_unconfirmed": now_unconfirmed,
        }
