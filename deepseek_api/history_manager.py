import os
import json
import copy
import datetime
import logging

DEFAULT_PATH = r"./history/"
logger = logging.getLogger("history_manager")

class historyManager:
    def __init__(self, user_name: str,history_path : str = None) -> None:
        self.history = []
        self.history_path = history_path
        self.user_name = user_name
        self.error_index = []
        self.summary = None
        self.create_time = None
        if history_path:
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    self.history = content['history']
                    #self.error_index = content['error_index']
                    self.summary = content['summary']
                    self.create_time = content['create_time']
            except FileNotFoundError as fe:
                logger.error(f"指定的对话历史文件未找到创建新的对话。Error:{fe}")
                self.create_new_history_file()
            except PermissionError as pe:
                logger.error(f"指定的对话历史文件拒绝访问，请检查文件读取权限和是否被占用。Error:{pe}")
                self.create_new_history_file()
            except Exception as e:
                logger.error(f"发生了意料之外的错误。Error:{e}")
                self.create_new_history_file()
        else:
            self.create_new_history_file()

    def create_new_history_file(self) -> None:
        if os.path.exists(DEFAULT_PATH) is False:
            os.makedirs(DEFAULT_PATH)
        current_time = datetime.datetime.now()
        self.create_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"history_{self.create_time}.txt"
        self.history_path = os.path.join(DEFAULT_PATH,filename)
        self.save_history()
        logger.info(f"创建了新的历史对话文件在{self.history_path}")

    def add_user_message(self, user_input: str, sys_input: str = None) -> None:
        self.history.append({"role":"user", "content":{self.user_name:user_input}})
        if sys_input:
            self.history[-1]['content']['sys'] = sys_input
        self.save_history()

    @staticmethod
    def get_user_message_template(user_name: str, user_input: str, sys_input: str = None) -> str:
        msg = {user_name : user_input}
        if sys_input:
            msg['sys'] = sys_input
        return json.dumps(msg)

    def add_assistant_message(self, assistant_response: str) -> None:
        try:
            content = json.loads(assistant_response)
            self.history.append({"role":"assistant","content":content})
        except ValueError as ve:
            logger.error(f"模型返回格式有误，历史对话文件将直接存储原始字符串")
            self.error_index.append(len(self.history))
            self.history.append({"role":"assistant","content":assistant_response})
        finally:
            self.save_history()

    def add_tool_message(self) -> None:
        pass

    def get_history(self) -> str:
        processed_history = copy.deepcopy(self.history)
        for i in range(len(processed_history)):
            if isinstance(processed_history[i]['content'],dict):
                processed_history[i]['content'] = json.dumps(self.history[i]['content'],ensure_ascii=False)
        return processed_history

    def set_summary(self, summary: str) -> None:
        self.summary = summary
        self.save_history()

    def save_history(self) -> None:
        with open(self.history_path,'w',encoding='utf-8') as f:
            json.dump({"create_time":self.create_time,"summary":self.summary,'history':self.history}, f, indent=4, ensure_ascii=False)
