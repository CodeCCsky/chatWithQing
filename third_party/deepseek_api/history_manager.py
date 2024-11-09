import copy
import datetime
import json
from third_party.FixJSON import fixJSON
from pydantic import BaseModel, model_validator
import logging
import os
from typing import Union
from functools import singledispatchmethod

DEFAULT_PATH = r"./history/"
logger = logging.getLogger(__name__)


class AssistantContentModel(BaseModel):
    role_thoughts: str
    role_response: str


class HistoryItemModel(BaseModel):
    role: str
    content: Union[str, AssistantContentModel, dict]

    @model_validator(mode="before")
    @classmethod
    def check_content(cls, values):
        role = values.get("role")
        content = values.get("content")
        if role == "assistant" and not isinstance(content, (AssistantContentModel, str)):
            raise ValueError(f"content must be AssistantContentModel or str when role is 'assistant'， {content}")
        return values


class chatManager:  # TODO test
    def __init__(self, history_data: dict, user_name: str) -> None:
        self.create_time: str = history_data["create_time"]
        self.update_time: str = history_data["update_time"]
        self.summary: str = history_data["summary"]
        self.origin_history = []
        for item in history_data["origin_history"]:
            if isinstance(item["content"], dict) and item["role"] == "assistant":
                item_content = AssistantContentModel(**item["content"])
            else:
                item_content = item["content"]
            self.origin_history.append(HistoryItemModel(role=item["role"], content=item_content))
        # sself.origin_history: list[HistoryItemModel] = [
        #    HistoryItemModel(**item) for item in history_data["origin_history"]
        # ]
        self.progressed_history: list = history_data["progressed_history"]
        self.user_name: str = user_name
        self.summaried_history: str = None
        if os.path.exists(DEFAULT_PATH) is False:
            os.makedirs(DEFAULT_PATH)

    def set_summaried_history(self, summaried_history: str):
        self.summaried_history = summaried_history

    def add_user_message(self, user_input: str, sys_input: str = None, **kwargs) -> None:
        new_content = {self.user_name: user_input} if user_input else {}

        # self.origin_history.append({"role": "user", "content": {}})
        # if user_input:
        #    self.origin_history[-1]["content"][self.user_name] = user_input
        if sys_input:
            new_content["sys"] = sys_input
        for key, value in kwargs.items():
            new_content[key] = value
        self.origin_history.append(HistoryItemModel(role="user", content=new_content))
        self.update_update_time()

    @singledispatchmethod
    def add_assistant_message(self, value) -> None:
        raise NotImplementedError(f"不支持的参数类型", type(value), value)

    @add_assistant_message.register(str)
    def add_ast_msg(self, assistant_response: str) -> None:
        # print("str:\n", assistant_response)

        try:
            content = fixJSON.loads(assistant_response)
            self.origin_history.append(HistoryItemModel(role="assistant", content=AssistantContentModel(**content)))
        except ValueError:
            logger.error("模型返回格式有误，历史对话文件将直接存储原始字符串")
            self.origin_history.append(HistoryItemModel(role="assistant", content=assistant_response))
        self.update_update_time()

    @add_assistant_message.register(dict)
    def add_ast_msg(self, assistant_response: dict) -> None:
        self.origin_history.append(
            HistoryItemModel(role="assistant", content=AssistantContentModel(**assistant_response))
        )

    def add_tool_message(self, tool_msg: str) -> None:
        self.update_update_time()
        # TODO

    def readd_wait_to_del_msg(self, wait_to_del_msg: list) -> None:
        self.origin_history.extend(wait_to_del_msg[::-1])

    def change_name(self, new_name: str):
        origin_history_copy = copy.deepcopy(self.origin_history)
        for index, item in enumerate(self.origin_history):
            if isinstance(item["content"], dict) and self.user_name in item["content"]:
                for key, value in item["content"].items():
                    if key == self.user_name:
                        origin_history_copy[index]["content"][new_name] = origin_history_copy[index]["content"].pop(
                            self.user_name
                        )
        self.origin_history = origin_history_copy

        progressed_history_copy = copy.deepcopy(self.progressed_history)
        for index, item in enumerate(self.progressed_history):
            if isinstance(item["content"], dict) and self.user_name in item["content"]:
                for key, value in item["content"].items():
                    if key == self.user_name:
                        progressed_history_copy[index]["content"][new_name] = progressed_history_copy[index][
                            "content"
                        ].pop(self.user_name)

        self.user_name = new_name

    def get_current_history(self) -> list:
        processed_historys = []
        for item in self.origin_history:
            processed_item = {"role": item.role}
            if isinstance(item.content, AssistantContentModel):
                processed_item["content"] = item.content.model_dump_json()
            elif isinstance(item.content, dict):
                processed_item["content"] = json.dumps(item.content, ensure_ascii=False)
            elif isinstance(item.content, str):
                processed_item["content"] = item.content
            processed_historys.append(processed_item)
        return processed_historys

    def get_current_history_dict(self) -> list:
        processed_historys = []
        for item in self.origin_history:
            processed_item = {"role": item.role}
            if isinstance(item.content, AssistantContentModel):
                processed_item["content"] = item.content.model_dump()
            elif isinstance(item.content, (dict, str)):
                processed_item["content"] = item.content
            processed_historys.append(processed_item)

        return processed_historys

    def get_full_fomatted_data(self) -> dict:
        return {
            "create_time": self.create_time,
            "update_time": self.update_time,
            "summary": self.summary,
            "origin_history": self.get_current_history_dict(),
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

    def pop(self) -> HistoryItemModel:
        return self.origin_history.pop()  # TODO 同时处理pregressed_history

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
        self.wait_to_del_msgs = []
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
        # except Exception as e:
        # logger.error(f"发生了意料之外的错误。Error:{e}")
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

    def change_user_name(self, name: str):
        self.user_name = name
        for history in self.historys:
            history.change_name(self.user_name)

    def add_user_message(self, user_input: str, sys_input: str = None, **kwargs) -> None:
        self.historys[self.current_history_index].add_user_message(user_input, sys_input, **kwargs)
        # self.save_history()

    @staticmethod
    def get_user_message_template(user_name: str, user_input: str, sys_input: str = None, **kwargs) -> str:
        msg = {}
        if user_input:
            msg[user_name] = user_input
        if sys_input:
            msg["sys"] = sys_input
        for key, value in kwargs.items():
            msg[key] = value
        return json.dumps(msg)

    def add_assistant_message(self, assistant_response: Union[str, dict]) -> None:
        self.historys[self.current_history_index].add_assistant_message(assistant_response)

    def add_tool_message(self, tool_msg: str) -> None:
        self.historys[self.current_history_index].add_tool_message(tool_msg)

    def pop_to_wait_to_del_msgs(self) -> HistoryItemModel:
        self.wait_to_del_msgs.append(self.historys[self.current_history_index].pop())
        return self.wait_to_del_msgs[-1]

    def get_wait_to_del_msgs(self) -> list:
        return self.wait_to_del_msgs

    def re_add_wait_to_del_msgs(self) -> None:
        self.historys[self.current_history_index].readd_wait_to_del_msg(self.wait_to_del_msgs)
        self.clear_wait_to_del_msgs()

    def clear_wait_to_del_msgs(self) -> None:
        self.wait_to_del_msgs.clear()

    def get_create_time_by_index(self, index: int) -> str:
        return self.historys[index].create_time

    def get_update_time_by_index(self, index: int) -> str:
        return self.historys[index].update_time

    def get_current_history(self) -> list:
        return self.historys[self.current_history_index].get_current_history()

    def get_history_list_by_index(self, index: int) -> list:
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
            json.dump(
                {"summary": self.summary, "historys": historys},
                f,
                indent=4,
                ensure_ascii=False,
            )
