import yaml

class User :
    def __init__(self,
                 user_name : str,
                 user_sex : str,
                 favourite_food : str,
                 user_location : str) -> None:
        self.user_sex = user_sex
        self.user_name = user_name
        self.favourite_food = favourite_food
        self.user_location = user_location

    def get_fulled_system_prompt(self, sys_prompt : str):
        return sys_prompt.format(user=self.user_name,
                                 user_sex=self.user_sex,
                                 favourite_food=self.favourite_food,
                                 user_location=self.user_location)

class settingReader:
    def __init__(self, path = "private_setting.yaml") -> None:
        self.llm_api_key: str = None
        self.user: User = None
        self.system_prompt_main = None
        self._read_yaml('private_setting.yaml')

    def _read_yaml(self, file : str)-> None:
        #global llm_api_key, system_prompt_main, user
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