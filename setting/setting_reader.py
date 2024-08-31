from deepseek_api.history_manager import historyManager
from deepseek_api.model import deepseek_model
import yaml

class User :
    def __init__(self,
                 user_name: str,
                 user_sex: str,
                 favourite_food: str,
                 user_location: str) -> None:
        self.user_sex = user_sex
        self.user_name = user_name
        self.favourite_food = favourite_food
        self.user_location = user_location

    def get_fulled_system_prompt(self, sys_prompt: str):
        return sys_prompt.format(user=self.user_name,
                                 user_sex=self.user_sex,
                                 favourite_food=self.favourite_food,
                                 user_location=self.user_location)

class deepseel_api_setting:
    def __init__(self,
                 api_key: str,
                 temperature: float,
                 frequency_penalty: float,
                 presence_penalty: float,
                 history_path: str) -> None:
        self.api_key = api_key
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.history = history_path

    def use_setting_on_model(self, _deepseek_model: deepseek_model):
        _deepseek_model.set_api_key(self.api_key)
        _deepseek_model.set_temperature(self.temperature)
        _deepseek_model.set_frequency_penalty(self.frequency_penalty)
        _deepseek_model.set_presence_penalty(self.presence_penalty)

    def load_history(self, _history_manager: historyManager):
        pass

class settingManager:
    def __init__(self, path = "private_setting.yaml") -> None:
        self.llm_api_key: str = None
        self.user: User = None
        self.system_prompt_main = None
        self._read_yaml('private_setting.yaml')

    def _read_yaml(self, file: str)-> None:
        with open(file, 'r', encoding='utf-8') as f:
            res = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.llm_api_key = res['api_key']
            self.system_prompt_main = res['system_prompt_main']
            self.user = User(user_name=res['user_name'],
                             user_sex=res['user_sex'],
                             favourite_food=res['favourite_food'],
                             user_location=res['user_location'])
            self.system_prompt_main = self.user.get_fulled_system_prompt(self.system_prompt_main)

    def get_system_prompt(self):
        return self.system_prompt_main

    def get_user_name(self):
        return self.user.user_name

    def get_api_key(self):
        return self.llm_api_key