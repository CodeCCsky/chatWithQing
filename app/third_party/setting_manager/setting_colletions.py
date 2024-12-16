from app.third_party.deepseek_api.model import deepseek_model
from app.third_party.tts import TTSAudio
import yaml

SYS_PROMPT_MAIN_PATH = r"system_prompt\main\system_prompt_main.txt"


class user_setting:
    def __init__(
        self,
        user_name: str,
        user_sex: str,
        favourite_food: str,
        user_location: str,
        user_birthday: str,
    ) -> None:
        self.user_sex = user_sex
        self.user_name = user_name
        self.favourite_food = favourite_food
        self.user_location = user_location
        self.user_birthday = user_birthday

    def get_full_system_prompt(self, sys_prompt: str):
        return sys_prompt.format(
            user=self.user_name,
            user_sex=self.user_sex,
            favourite_food=self.favourite_food,
            user_location=self.user_location,
            user_birthday=self.user_birthday,
        )

    def check(self) -> list:
        unfilled_list = []
        if not self.user_sex:
            unfilled_list.append("你的性别")
        if not self.user_name:
            unfilled_list.append("你的名字")
        if not self.favourite_food:
            unfilled_list.append("你喜欢的食物")
        if not self.user_location:
            unfilled_list.append("你的地址")
        if not self.user_birthday:
            unfilled_list.append("你的生日")
        return unfilled_list

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, user_setting):
            return NotImplemented
        return (
            self.user_name == other.user_name
            and self.user_sex == other.user_sex
            and self.favourite_food == other.favourite_food
            and self.user_location == other.user_location
            and self.user_birthday == other.user_birthday
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(
            user_name=data_dict["name"],
            user_sex=data_dict["sex"],
            favourite_food=data_dict["favourite_food"],
            user_location=data_dict["location"],
            user_birthday=data_dict["birthday"],
        )

    def get_dict(self) -> dict:
        return {
            "name": self.user_name,
            "sex": self.user_sex,
            "favourite_food": self.favourite_food,
            "location": self.user_location,
            "birthday": self.user_birthday,
        }


class deepseek_api_setting:
    def __init__(
        self,
        api_key: str,
        temperature: float = 1.5,
        frequency_penalty: float = 0.8,
        presence_penalty: float = 0.8,
    ) -> None:
        self.api_key = api_key
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def use_setting(self, _deepseek_model: deepseek_model, sys_prompt: str) -> None:
        _deepseek_model.set_api_key(self.api_key)
        _deepseek_model.set_temperature(self.temperature)
        _deepseek_model.set_frequency_penalty(self.frequency_penalty)
        _deepseek_model.set_presence_penalty(self.presence_penalty)
        _deepseek_model.system_prompt = sys_prompt

    def check(self) -> list:
        unfilled_list = []
        if not self.api_key:
            unfilled_list.append("api key")
        return unfilled_list

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(
            api_key=data_dict["api_key"],
            temperature=data_dict.get("temperature", 1.5),
            frequency_penalty=data_dict.get("frequency_penalty", 0.8),
            presence_penalty=data_dict.get("presence_penalty", 0.8),
        )

    def get_dict(self) -> dict:
        return {
            "api_key": self.api_key,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }


class TTS_setting:
    def __init__(
        self,
        use_tts: bool = False,
        url: str = "http://127.0.0.1:5000/tts",
        character_name: str = "晴",
        emotion: str = "default",
    ) -> None:
        self.use_tts = use_tts
        self.url = url
        self.character_name = character_name
        self.emotion = emotion

    def use_setting(self, _TTSAudio: TTSAudio):
        _TTSAudio.set_tts_character(self.character_name)
        _TTSAudio.set_emotion(self.emotion)
        _TTSAudio.set_request_url(self.url)

    def check(self) -> list:
        unfilled_list = []
        if not self.url:
            unfilled_list.append("tts网址")
        if not self.character_name:
            unfilled_list.append("tts角色名字")
        if not self.emotion:
            unfilled_list.append("角色情感")
        return unfilled_list

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(
            use_tts=data_dict.get("use_tts", False),
            url=data_dict.get("url", "http://127.0.0.1:5000/tts"),
            character_name=data_dict.get("character", "晴"),
            emotion=data_dict.get("emotion", "default"),
        )

    def get_dict(self) -> dict:
        return {
            "use_tts": self.use_tts,
            "url": self.url,
            "character": self.character_name,
            "emotion": self.emotion,
        }


class show_setting:
    def __init__(self, text_show_gap: int = 200, img_show_zoom: bool = 1) -> None:
        self.text_show_gap = text_show_gap
        self.img_show_zoom = img_show_zoom

    def check(self) -> list:
        unfilled_list = []
        if not self.text_show_gap:
            unfilled_list.append("字符显示速度")
        if not self.img_show_zoom:
            unfilled_list.append("图片大小缩放")
        return unfilled_list

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(text_show_gap=data_dict.get("text_show_gap", 200), img_show_zoom=data_dict.get("img_show_zoom", 1.0))

    def get_dict(self) -> dict:
        return {
            "text_show_gap": self.text_show_gap,
            "img_show_zoom": self.img_show_zoom,
        }


class chatting_setting:
    def __init__(
        self,
        add_same_day_summary: bool = True,
        add_x_day_ago_summary: bool = False,
        value_of_x_day_ago: int = 5,
        enable_self_activation: bool = True,
    ) -> None:
        self.add_same_day_summary = add_same_day_summary
        self.add_x_day_ago_summary = add_x_day_ago_summary
        self.value_of_x_day_ago = value_of_x_day_ago
        self.enable_self_activation: bool = enable_self_activation

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(
            add_same_day_summary=data_dict.get("add_same_day_summary", True),
            add_x_day_ago_summary=data_dict.get("add_x_day_ago_summary", False),
            value_of_x_day_ago=data_dict.get("value_of_x_day_ago", 5),
            enable_self_activation=data_dict.get("enable_self_activation", True),
        )

    def get_dict(self) -> dict:
        return {
            "add_same_day_summary": self.add_same_day_summary,
            "add_x_day_ago_summary": self.add_x_day_ago_summary,
            "value_of_x_day_ago": self.value_of_x_day_ago,
            "enable_self_activation": self.enable_self_activation,
        }


class extension_func_setting:
    def __init__(self, recall: bool = False) -> None:
        self.recall = recall

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(recall=data_dict.get("recall", False))

    def get_dict(self) -> dict:
        return {"recall": self.recall}


class emo_setting:
    def __init__(self, show_in_text: bool = False) -> None:
        self.show_in_text = show_in_text

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(show_in_text=data_dict.get("show_in_text", False))

    def get_dict(self) -> dict:
        return {"show_in_text": self.show_in_text}


class settingManager:
    def __init__(self) -> None:
        self.user: user_setting = None
        self.deepseek_model: deepseek_api_setting = None
        self.show_setting: show_setting = None
        self.tts_setting: TTS_setting = None
        self.chatting_setting: chatting_setting = None
        self.extension_func_setting: extension_func_setting = None
        self.emo_setting: emo_setting = None
        self.history_path = None
        self.system_prompt_main = None
        self.load_path = r"setting/private_setting.yaml"

    def load_from_parameter(
        self,
        User: user_setting,
        Deepseek_setting: deepseek_api_setting,
        Show_setting: show_setting,
        Tts_setting: TTS_setting,
        chatting_setting: chatting_setting,
        extension_func_setting_: extension_func_setting,
        emo_setting_: emo_setting,
    ) -> None:
        self.user = User
        self.deepseek_model = Deepseek_setting
        self.show_setting = Show_setting
        self.tts_setting = Tts_setting
        self.chatting_setting = chatting_setting
        self.extension_func_setting = extension_func_setting_
        self.emo_setting = emo_setting_
        self.load_system_prompt_main()

    def load_from_file(self, path=r"setting/private_setting.yaml") -> tuple:
        self.load_path = path
        try:
            self._read_yaml()
            return 0, None
        except IOError as fe:
            return 1, fe
        except yaml.YAMLError as ye:
            return 2, ye
        except KeyError as ke:
            return 2, ke

    def load_system_prompt_main(self) -> None:
        with open(SYS_PROMPT_MAIN_PATH, "r", encoding="utf-8") as f:
            prompt = f.read()
            self.system_prompt_main = self.user.get_full_system_prompt(prompt)

    def _read_yaml(self) -> None:
        with open(self.load_path, "r", encoding="utf-8") as f:
            res: dict = yaml.load(f.read(), Loader=yaml.FullLoader)

            self.user = user_setting.from_dict(res["user"])
            self.deepseek_model = deepseek_api_setting.from_dict(res["deepseek"])
            self.tts_setting = TTS_setting.from_dict(res["TTS"])
            self.show_setting = show_setting.from_dict(res["show"])
            if isinstance(res.get("chatting", None), dict):
                chatting: dict = res["chatting"]
            else:
                chatting: dict = res["summary"]
            self.chatting_setting = chatting_setting.from_dict(chatting)
            self.extension_func_setting = extension_func_setting.from_dict(res.get("extension_func", {}))
            self.emo_setting = emo_setting.from_dict(res.get("emo", {}))

            self.load_system_prompt_main()

    def write_yaml(self) -> bool:
        if not self.check() == []:
            return False
        with open(self.load_path, "w", encoding="utf-8") as f:
            write_dict = {
                "user": self.user.get_dict(),
                "deepseek": self.deepseek_model.get_dict(),
                "TTS": self.tts_setting.get_dict(),
                "show": self.show_setting.get_dict(),
                "chatting": self.chatting_setting.get_dict(),
                "extension_func": self.extension_func_setting.get_dict(),
                "emo": self.emo_setting.get_dict(),
                "system_prompt_main": self.system_prompt_main,
            }
            yaml.dump(data=write_dict, stream=f, allow_unicode=True)
        return True

    def get_system_prompt(self) -> str:
        return self.system_prompt_main

    def get_user_name(self) -> str:
        return self.user.user_name

    def get_api_key(self) -> str:
        return self.deepseek_model.api_key

    def check(self) -> bool:
        return self.user.check() + self.deepseek_model.check() + self.show_setting.check() + self.tts_setting.check()


import threading


class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class globalSettingManager(Singleton, settingManager):
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            super().__init__()
