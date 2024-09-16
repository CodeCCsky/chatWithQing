from PyQt5.QtCore import QThread, pyqtSignal
from third_party.deepseek_api import historyManager, deepseek_model
from third_party.setting import settingManager
import logging

PROMPT = """# 任务:判断当前对话话题是否结束

你现在需要分析给定的对话片段,判断对话双方是否已经结束他们最新讨论的话题，且没有开启新的话题。

## 输出格式

- 如果对话双方仍在讨论最新话题，或已开启新话题，请返回: False
- 如果对话双方已经结束最新话题，且没有开启新话题，请返回: True

请只返回True或False,不要包含任何其他解释或评论。

## 示例

### 示例1:
A: 你觉得今天的天气怎么样?
B: 今天天气很好,阳光明媚。
A: 是啊,很适合出去散步。
B: 确实如此。

输出: True

### 示例2:
A: 你最近在看什么电视剧?
B: 我在追《星际迷航:皮卡德》,真的很精彩!
A: 哦,我听说过这部剧。讲的是什么内容呢?

输出: False

### 示例3:
A: 周末有什么计划吗?
B: 我打算去看个电影,你呢?
A: 我还没想好。话说回来,你上周提到的那个项目进展如何?

输出: False

### 示例4:
A: 你觉得这份报告怎么样?
B: 整体来说不错，但是有几处数据需要更新。
A: 明白了，我会修改的。
B: 好的，改好后发给我看看。
A: 没问题。

输出: True"""

logger = logging.getLogger(__name__)


class topic_check_thread(QThread):
    result = pyqtSignal(bool)

    def __init__(self, history_manager: historyManager, setting_manager: settingManager, parent=None) -> None:
        super().__init__(parent)
        self.history_manager = history_manager
        self.setting_manager = setting_manager
        self.prompt = get_prompt()
        self.inference = deepseek_model(
            api_key=self.setting_manager.get_api_key(), system_prompt=self.prompt, temperature=1
        )

    def run(self):
        logger.info("判断话题结束线程启动")
        processed_history_list = []
        chat_history = self.history_manager.get_history_dict_by_index(-1)
        for item in chat_history:
            if item["role"] == "user":
                # try:
                processed_history_list.append(
                    f"{self.setting_manager.get_user_name()}:{item['content'][self.setting_manager.get_user_name()]}"
                )
            elif item["role"] == "assistant":
                try:
                    processed_history_list.append(f"晴:{item['content']['role_response']}")
                except (KeyError, ValueError, TypeError):
                    processed_history_list.append(f"{self.setting_manager.get_user_name()}:{item['content']}")
        if processed_history_list == []:
            logger.info("判断话题结束线程 - 无历史记录，默认返回结束")
            self.result.emit(True)
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": "\n".join(processed_history_list)},
        ]
        self.inference.load_history(messages)
        response = self.inference.send_message()[0]

        try:
            if "FALSE" in response.upper():
                logger.info(f"判断话题结束线程 - 返回:话题未结束 - 返回值:{response}")
                self.result.emit(False)
            elif "TRUE" in response.upper():
                logger.info(f"判断话题结束线程 - 返回:话题结束 - 返回值:{response}")
                self.result.emit(True)
            else:
                logger.warning(f"判断话题结束线程 - 返回出错, 格式不正确. 默认为话题结束 - 返回值:{response}")
                self.result.emit(True)
        except Exception:
            logger.warning(f"判断话题结束线程 - 返回出错, 格式不正确. 默认为话题结束 - 返回值:{response}")
            self.result.emit(True)


def get_prompt() -> str:
    prompt = PROMPT
    try:
        with open(r"system_prompt\chat_acitvity_manager\topic_complete_check_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
    except OSError:
        pass
    finally:
        return prompt
