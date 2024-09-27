import copy
import datetime
import json
from third_party.FixJSON import fixJSON
import logging
import os

DEFAULT_PATH = r"./history/"
logger = logging.getLogger(__name__)


class chatManager:
    def __init__(self, history_data: dict, user_name: str) -> None:
        self.create_time: str = history_data["create_time"]
        self.update_time: str = history_data["update_time"]
        self.summary: str = history_data["summary"]
        self.origin_history: list = history_data["origin_history"]
        self.progressed_history: list = history_data["progressed_history"]
        self.user_name: str = user_name
        self.summaried_history: str = None

    def set_summaried_history(self, summaried_history: str):
        self.summaried_history = summaried_history

    def add_user_message(self, user_input: str, sys_input: str = None) -> None:
        self.origin_history.append({"role": "user", "content": {self.user_name: user_input}})
        if sys_input:
            self.origin_history[-1]["content"]["sys"] = sys_input
        self.update_update_time()

    def add_assistant_message(self, assistant_response: str) -> None:
        try:
            content = fixJSON.loads(assistant_response)
            self.origin_history.append({"role": "assistant", "content": content})
        except ValueError:
            logger.error("模型返回格式有误，历史对话文件将直接存储原始字符串")
            self.origin_history.append({"role": "assistant", "content": assistant_response})
        self.update_update_time()

    def add_tool_message(self, tool_msg: str) -> None:
        self.update_update_time()
        # TODO

    def get_current_history(self) -> list:
        processed_history = copy.deepcopy(self.origin_history)  # TODO
        for i in range(len(processed_history)):
            if isinstance(processed_history[i]["content"], dict):
                processed_history[i]["content"] = json.dumps(self.origin_history[i]["content"], ensure_ascii=False)
        if self.summaried_history:
            processed_history.insert(
                0,
                {
                    "role": "user",
                    "content": json.dumps({self.user_name: "", "sys": self.summaried_history}, ensure_ascii=False),
                },
            )
        # print(processed_history)
        return processed_history

    def get_current_history_dict(self) -> list:
        return copy.deepcopy(self.origin_history)

    def get_full_fomatted_data(self) -> dict:
        return {
            "create_time": self.create_time,
            "update_time": self.update_time,
            "summary": self.summary,
            "origin_history": self.origin_history,
            "progressed_history": self.progressed_history,
        }

    def is_empty(self) -> bool:
        if self.progressed_history == [] and len(self.origin_history) < 2:
            return True
        else:
            return False

    def init_create_time(self):
        current_time = datetime.datetime.now()
        now_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.create_time = now_time
        self.update_update_time()

    def update_update_time(self):
        current_time = datetime.datetime.now()
        now_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.update_time = now_time

    @staticmethod
    def get_template_dict(
        create_time: str = None,
        update_time: str = None,
        summary: str = None,
        origin_history: list = [],
        progressed_history: list = [],
    ):
        return {
            "create_time": create_time,
            "update_time": update_time,
            "summary": summary,
            "origin_history": origin_history,
            "progressed_history": progressed_history,
        }


class historyManager:
    def __init__(self, user_name: str = None, history_path: str = None) -> None:
        self.historys: list[chatManager] = []
        self.history_path = ""
        self.user_name = ""
        self.current_history_index = 0
        self.summary = None
        if user_name:
            self.set_user_name(user_name)
        if history_path:
            self.load_from_file(history_path)

    def set_user_name(self, name: str):
        self.user_name = name

    def load_from_file(self, path: str):
        self.history_path = path
        logger.debug(f"尝试加载位于{self.history_path}的历史记录文件中...")
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                self.summary = content["summary"]
                historys = content["historys"]
                for _slice in historys:
                    self.historys.append(chatManager(_slice, self.user_name))
                    if self.historys[-1].is_empty():
                        logger.debug(f"检测到创建时间为{self.historys[-1].create_time}的空对话记录，已自动删除。")
                        self.historys.pop()
        except FileNotFoundError as fe:
            logger.warning(f"指定的对话历史文件未找到。Error:{fe}")
            # self.create_new_history_file()
        except PermissionError as pe:
            logger.error(f"指定的对话历史文件拒绝访问，请检查文件读取权限和是否被占用。Error:{pe}")
            # self.create_new_history_file()
        except Exception as e:
            logger.error(f"发生了意料之外的错误。Error:{e}")
            # self.create_new_history_file()

    def set_current_index(self, index: int):
        self.current_history_index = index

    def create_new_chat(self) -> int:
        self.historys.append(chatManager(chatManager.get_template_dict(), self.user_name))
        self.current_history_index = len(self.historys) - 1
        self.historys[self.current_history_index].init_create_time()
        return self.current_history_index

    def create_new_history_file(self) -> None:
        if os.path.exists(DEFAULT_PATH) is False:
            os.makedirs(DEFAULT_PATH)
        current_time = datetime.datetime.now()
        now_time = current_time.strftime("%Y%m%d")
        filename = f"{now_time}.json"
        self.history_path = os.path.join(DEFAULT_PATH, filename)
        self.create_new_chat()
        self.save_history()
        logger.debug(f"创建了新的历史对话文件在{self.history_path}")

    def get_last_index(self) -> int:
        return len(self.historys) - 1

    def add_user_message(self, user_input: str, sys_input: str = None) -> None:
        self.historys[self.current_history_index].add_user_message(user_input, sys_input)
        # self.save_history()

    @staticmethod
    def get_user_message_template(user_name: str, user_input: str, sys_input: str = None) -> str:
        msg = {user_name: user_input}
        if sys_input:
            msg["sys"] = sys_input
        return json.dumps(msg)

    def add_assistant_message(self, assistant_response: str) -> None:
        self.historys[self.current_history_index].add_assistant_message(assistant_response)

    def add_tool_message(self, tool_msg: str) -> None:
        self.historys[self.current_history_index].add_tool_message(tool_msg)

    def get_create_time_by_index(self, index: int) -> str:
        return self.historys[index].create_time

    def get_update_time_by_index(self, index: int) -> str:
        return self.historys[index].update_time

    def get_current_history(self) -> str:
        return self.historys[self.current_history_index].get_current_history()

    def get_history_dict_by_index(self, index: int) -> str:
        return self.historys[index].get_current_history_dict()

    def get_summary_by_index(self, index: int) -> str:
        return self.historys[index].summary

    def get_overall_summary(self) -> str:
        return self.summary

    def set_current_summaried_history(self, summaried_history: str) -> None:
        self.historys[self.current_history_index].set_summaried_history(summaried_history)

    def set_summary_by_index(self, index: int, summary: str) -> None:
        self.historys[index].summary = summary

    def set_current_summary(self, summary: str) -> None:
        self.historys[self.current_history_index].summary = summary

    def set_overall_summary(self, summary: str) -> None:
        self.summary = summary

    def get_full_data(self) -> dict:
        historys = []
        for _slice in self.historys:
            historys.append(_slice.get_full_fomatted_data())
        return {"summary": self.summary, "historys": historys}

    def save_history(self) -> None:
        with open(self.history_path, "w", encoding="utf-8") as f:
            historys = []
            for _slice in self.historys:
                historys.append(_slice.get_full_fomatted_data())
            json.dump({"summary": self.summary, "historys": historys}, f, indent=4, ensure_ascii=False)
