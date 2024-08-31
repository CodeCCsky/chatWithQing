# -*- coding: utf-8 -*-
import deepseek_api
import tts
import json
import yaml
from setting import settingManager

setting = settingManager()

system_prompt_main = setting.get_system_prompt()

tts_inference = tts.TTSAudio(cache_path=r'\cache')
llm_main_chat = deepseek_api.deepseek_model(api_key=setting.get_api_key(), system_prompt=system_prompt_main)
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

import copy
import json
history = deepseek_api.historyManager(setting.get_user_name())
while True:
    sys_input = ''
    usr_input = input("user> ")
    history.add_user_message(usr_input)
    llm_main_chat.load_history(history.get_history())
    print(history.get_history())
    thread = DeepSeekThread(llm_main_chat)
    thread.start()
    #while thread.is_alive() :
        #print(thread.get_response())
    thread.join()
    response,_ = thread.get_full_response()
    print(_)
    try:
        content = json.loads(response)
        thought = content['role_thoughts']
        resp = content['role_response']
        print("thought:\n",thought,"\nresonse:\n",resp)
    except Exception as e:
        print("JSONDecodeError, origin str:\n",response,'\nerror:')
    history.add_assistant_message(response)