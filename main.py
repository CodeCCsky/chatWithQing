import deepseek_api
import tts

import yaml

class User :
    def __init__(self,
                 user_name : str,
                 user_sex : str,
                 favourite_food : str,
                 liked_style : str,
                 user_location : str) -> None:
        self.user_sex = user_sex
        self.user_name = user_name
        self.favourite_food = favourite_food
        self.liked_style = liked_style
        self.user_location = user_location

    def get_fulled_system_prompt(self, sys_prompt : str):
        return sys_prompt.format(user=self.user_name,
                                 user_sex=self.user_sex,
                                 favourite_food=self.favourite_food,
                                 liked_style=self.liked_style,
                                 user_location=self.user_location)

llm_api_key: str = None
system_prompt_main: str = None
system_prompt_action:str = None
user: User = None

def read_yaml(file : str)-> None:
    global llm_api_key, system_prompt_main, system_prompt_action, user
    with open(file, 'r', encoding='utf-8') as f:
        res = yaml.load(f.read(), Loader=yaml.FullLoader)
        llm_api_key = res['api_key']
        system_prompt_main = res['system_prompt_main_chat']
        system_prompt_action = res['system_prompt_action']
        user = User(user_name=res['user_name'],
                    user_sex=res['user_sex'],
                    favourite_food=res['favourite_food'],
                    liked_style=res['liked_style'],
                    user_location=res['user_location'])

try:
    read_yaml(r"private_setting.yaml")
except FileNotFoundError:
    read_yaml(r"private_setting")

system_prompt_main = user.get_fulled_system_prompt(system_prompt_main)
system_prompt_action = user.get_fulled_system_prompt(system_prompt_action)

tts_inference = tts.TTSAudio(cache_path=r'\cache')
llm_main_chat = deepseek_api.deepseek_model(api_key=llm_api_key, system_prompt=system_prompt_main)
llm_action = deepseek_api.deepseek_model(api_key=llm_api_key,system_prompt=system_prompt_action)
import threading
class DeepSeekThread(threading.Thread):
    def __init__(self, model: deepseek_api.deepseek_model):
        super().__init__()
        self.model = model
        self.response = None
        self.finish_reason = None

    def run(self):
        self.response, self.finish_reason, _ = self.model.send_message()

    def get_full_response(self):
        return self.response, self.finish_reason

    def get_response(self):
        return self.model.get_response()

import time
while True:
    usr_input = input("> ")
    if usr_input == '/history':
        print(llm_main_chat.get_history())
        continue
    llm_main_chat.add_msg(usr_input)
    thread = DeepSeekThread(llm_main_chat)
    thread.start()
    thread.join()
    print(thread.get_full_response()[0])
    #hist = llm_main_chat.get_history()[-6:]
    
    
