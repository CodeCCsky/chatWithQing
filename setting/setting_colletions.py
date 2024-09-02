from deepseek_api.model import deepseek_model
from tts import TTSAudio
import yaml

SYS_PROMPT_MAIN_PATH = r"system_prompt\system_prompt_main.txt"

class user_setting:
    def __init__(self,
                 user_name: str,
                 user_sex: str,
                 favourite_food: str,
                 user_location: str) -> None:
        self.user_sex = user_sex
        self.user_name = user_name
        self.favourite_food = favourite_food
        self.user_location = user_location

    def get_full_system_prompt(self, sys_prompt: str):
        return sys_prompt.format(user=self.user_name,
                                 user_sex=self.user_sex,
                                 favourite_food=self.favourite_food,
                                 user_location=self.user_location)

    def check(self) -> bool:
        return bool(self.user_sex and self.user_name and self.favourite_food and self.user_location)

class deepseek_api_setting:
    def __init__(self,
                 api_key: str,
                 temperature: float = 1.1,
                 frequency_penalty: float = 0,
                 presence_penalty: float = 0.1) -> None:
        self.api_key = api_key
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def use_setting(self, _deepseek_model: deepseek_model) -> None:
        _deepseek_model.set_api_key(self.api_key)
        _deepseek_model.set_temperature(self.temperature)
        _deepseek_model.set_frequency_penalty(self.frequency_penalty)
        _deepseek_model.set_presence_penalty(self.presence_penalty)

    def check(self) -> bool:
        return bool(self.api_key and self.temperature and self.frequency_penalty and self.presence_penalty)

class TTS_setting:
    def __init__(self,
                 use_tts: bool = False,
                 url: str = 'http://127.0.0.1:5000/tts',
                 character_name: str = '晴',
                 emotion: str = 'default') -> None:
        self.use_tts = use_tts
        self.url = url
        self.character_name = character_name
        self.emotion = emotion

    def use_setting(self, _TTSAudio: TTSAudio):
        _TTSAudio.set_tts_character(self.character_name)
        _TTSAudio.set_emotion(self.emotion)
        _TTSAudio.set_request_url(self.url)

    def check(self) -> bool:
        return bool(self.url and self.character_name and self.emotion)

class show_setting:
    def __init__(self, text_show_gap: int) -> None:
        self.text_show_gap = text_show_gap

    def check(self) -> bool:
        return bool(self.text_show_gap)

class settingManager:
    def __init__(self) -> None:
        self.user: user_setting = None
        self.deepseek_model: deepseek_api_setting = None
        self.show_setting: show_setting = None
        self.tts_setting: TTS_setting = None
        self.histoy_path =  None
        self.system_prompt_main = None
        self.load_path = "setting/private_setting.yaml"

    def load_from_parameter(self,
                            User: user_setting,
                            Deepseek_setting: deepseek_api_setting,
                            Show_setting: show_setting,
                            Tts_setting: TTS_setting) -> None:
        self.user = User
        self.deepseek_model = Deepseek_setting
        self.show_setting = Show_setting
        self.tts_setting = Tts_setting
        self.load_system_prompt_main()

    def load_from_file(self, path = "setting/private_setting.yaml") -> None:
        self.load_path = path
        self._read_yaml()

    def load_system_prompt_main(self) -> None:
        with open(SYS_PROMPT_MAIN_PATH, 'r', encoding='utf-8') as f:
            prompt = f.read()
            self.system_prompt_main = self.user.get_full_system_prompt(prompt)

    def _read_yaml(self) -> None:
        with open(self.load_path, 'r', encoding='utf-8') as f:
            res = yaml.load(f.read(), Loader=yaml.FullLoader)
            user = res['user']
            deepseek = res['deepseek']
            tts = res['TTS']
            show_s = res['show']
            self.user = user_setting(user_name=user['name'],
                             user_sex=user['sex'],
                             favourite_food=user['favourite_food'],
                             user_location=user['location'])
            self.deepseek_model = deepseek_api_setting(api_key=deepseek['api_key'],
                                                       temperature=deepseek['temperature'],
                                                       frequency_penalty=deepseek['frequency_penalty'],
                                                       presence_penalty=deepseek['presence_penalty'])
            self.tts_setting = TTS_setting(use_tts=tts['use_tts'],
                                           url=tts['url'],
                                           character_name=tts['character'],
                                           emotion=tts['emotion'])
            self.show_setting = show_setting(show_s['text_show_gap'])
            self.load_system_prompt_main()

    def write_yaml(self) -> bool:
        if not self.check():
            return False
        with open(self.load_path, 'w', encoding='utf-8') as f:
            write_dict = {
                'user' : {
                    'name' : self.user.user_name,
                    'sex' : self.user.user_sex,
                    'favourite_food' : self.user.favourite_food,
                    'location' : self.user.user_location,
                },
                'deepseek' : {
                    'api_key' : self.deepseek_model.api_key,
                    'temperature' : self.deepseek_model.temperature,
                    'frequency_penalty' : self.deepseek_model.frequency_penalty,
                    'presence_penalty' : self.deepseek_model.presence_penalty,
                },
                'TTS' : {
                    'use_tts' : self.tts_setting.use_tts,
                    'url' : self.tts_setting.url,
                    'character' : self.tts_setting.character_name,
                    'emotion' : self.tts_setting.emotion,
                },
                'show' : {
                    'text_show_gap' : self.show_setting.text_show_gap,
                },
                'system_prompt_main' : self.system_prompt_main,
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
        return bool(self.user.check() and
                    self.deepseek_model.check() and
                    self.show_setting.check() and
                    self.tts_setting.check() and
                    self.histoy_path and
                    self.system_prompt_main and
                    self.load_path)