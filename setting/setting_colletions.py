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

    def check(self) -> list:
        unfilled_list = []
        if not self.user_sex:
            unfilled_list.append('你的性别')
        if not self.user_name:
            unfilled_list.append('你的名字')
        if not self.favourite_food:
            unfilled_list.append('你喜欢的食物')
        if not self.user_location:
            unfilled_list.append('你的地址')
        return unfilled_list

class deepseek_api_setting:
    def __init__(self,
                 api_key: str,
                 temperature: float = 1.1,
                 frequency_penalty: float = 0.3,
                 presence_penalty: float = 0.3) -> None:
        self.api_key = api_key
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def use_setting(self, _deepseek_model: deepseek_model) -> None:
        _deepseek_model.set_api_key(self.api_key)
        _deepseek_model.set_temperature(self.temperature)
        _deepseek_model.set_frequency_penalty(self.frequency_penalty)
        _deepseek_model.set_presence_penalty(self.presence_penalty)

    def check(self) -> list:
        unfilled_list = []
        if not self.api_key:
            unfilled_list.append('api key')
        return unfilled_list

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

    def check(self) -> list:
        unfilled_list = []
        if not self.url:
            unfilled_list.append('tts网址')
        if not self.character_name:
            unfilled_list.append('tts角色名字')
        if not self.emotion:
            unfilled_list.append('角色情感')
        return unfilled_list

class show_setting:
    def __init__(self, text_show_gap: int) -> None:
        self.text_show_gap = text_show_gap

    def check(self) -> list:
        unfilled_list = []
        if not self.text_show_gap:
            unfilled_list.append('字符显示速度')
        return unfilled_list

class chat_summary_setting:
    def __init__(self,
                 add_same_day_summary: bool = True,
                 add_x_day_ago_summary: bool = False,
                 value_of_x_day_ago: int = 5) -> None:
        self.add_same_day_summary = add_same_day_summary
        self.add_x_day_ago_summary = add_x_day_ago_summary
        self.value_of_x_day_ago = value_of_x_day_ago

class recall_function_setting:
    def __init__(self, enable: bool = False) -> None:
        self.enable = enable

class settingManager:
    def __init__(self) -> None:
        self.user: user_setting = None
        self.deepseek_model: deepseek_api_setting = None
        self.show_setting: show_setting = None
        self.tts_setting: TTS_setting = None
        self.chat_summary_setting: chat_summary_setting = None
        self.recall_function_setting: recall_function_setting = None
        self.history_path =  None
        self.system_prompt_main = None
        self.load_path = "setting/private_setting.yaml"

    def load_from_parameter(self,
                            User: user_setting,
                            Deepseek_setting: deepseek_api_setting,
                            Show_setting: show_setting,
                            Tts_setting: TTS_setting,
                            Chat_summary_setting: chat_summary_setting,
                            Recall_function_setting: recall_function_setting) -> None:
        self.user = User
        self.deepseek_model = Deepseek_setting
        self.show_setting = Show_setting
        self.tts_setting = Tts_setting
        self.chat_summary_setting = Chat_summary_setting
        self.recall_function_setting = Recall_function_setting
        self.load_system_prompt_main()

    def load_from_file(self, path = "setting/private_setting.yaml") -> tuple:
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
            summary = res['summary']
            recall = res['recall']
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
            self.chat_summary_setting = chat_summary_setting(add_same_day_summary=summary['add_same_day_summary'],
                                                             add_x_day_ago_summary=summary['add_x_day_ago_summary'],
                                                             value_of_x_day_ago=summary['value_of_x_day_ago'])
            self.recall_function_setting = recall_function_setting(enable=recall['enable'])
            self.load_system_prompt_main()

    def write_yaml(self) -> bool:
        if not self.check() == []:
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
                'summary': {
                    'add_same_day_summary' : self.chat_summary_setting.add_same_day_summary,
                    'add_x_day_ago_summary' : self.chat_summary_setting.add_x_day_ago_summary,
                    'value_of_x_day_ago' : self.chat_summary_setting.value_of_x_day_ago,
                },
                'recall' : {
                    'enable' : self.recall_function_setting.enable
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
        return self.user.check() + self.deepseek_model.check() + self.show_setting.check() + self.tts_setting.check()