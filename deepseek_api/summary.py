import datetime
import logging
import random
import time

from openai import APIError, OpenAI

logger = logging.getLogger(__name__)

chat_summary_prompt = """请你根据以下对话，提取关键信息，给出总结。应使用简洁的语言，尽量包含较准确的内容，输出不能多于100字。如果某一条对话为json格式，你需要视json中的\"role_response\"项的内容为这条对话的内容。"""

day_summary_prompt = """请根据以下多条包含时间的对话总结，提取关键信息，生成一份简洁的总对话总结。总结中应使用较粗略的时间词描述对话发生的时间段，使用简洁干练的语言，避免冗长描述。
例如以下输入：
2024-09-07 08:53:25到2024-09-07 09:04:53 总结：{user}正在分享最近的生活经历，想要与晴讨论{user}最近看的电影。晴表现出对{user}生活的兴趣，并对{user}所提及的电影感兴趣。
2024-09-07 10:45:23到2024-09-07 10:53:21 总结：{user}在编程中遇到问题，需要写一条大语言模型的提示词来总结对话。晴主动提供帮助，建议提示词为：「请总结以下对话的主要内容,提取关键信息,并概括对话双方的立场和观点。」晴表现出对{user}的关注和支持。

你应该给出如下总结：
上午9点左右，{user}分享了最近的生活经历和观看的电影，晴表现出兴趣并参与讨论。在上午11点左右，{user}在编程中遇到问题，晴主动提供帮助，建议了有效的提示词，并表现出对{user}的关注和支持。"""


class deepseek_summary:
    def __init__(
        self,
        api_key: str,
        user_name: str,
        temperature: float = 0.7,
        frequency_penalty: float = 0.3,
        presence_penalty: float = 0,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> None:
        self.api_key = api_key
        self.current_response = ""
        self.finish_reason = ""
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.user_name = user_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.chat_summary_prompt = chat_summary_prompt.format(user=self.user_name)
        self.day_summary_prompt = day_summary_prompt.format(user=self.user_name)
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def get_chat_summary(self, chat_history: list):
        processed_history_list = []
        for item in chat_history:
            if item["role"] == "user":
                # try:
                processed_history_list.append(f"{self.user_name}:{item['content'][self.user_name]}")
            elif item["role"] == "assistant":
                try:
                    processed_history_list.append(f"晴:{item['content']['role_response']}")
                except (KeyError, ValueError):
                    processed_history_list.append(f"{self.user_name}:{item['content']}")
        if processed_history_list == []:
            return None, None, {}
        messages = [
            {"role": "system", "content": self.chat_summary_prompt},
            {"role": "user", "content": "\n".join(processed_history_list)},
        ]
        return self._send(messages)

    def get_day_summary(self, day_data: dict):
        day_historys = day_data["historys"]
        processed_historys_list = []
        for item in day_historys:
            crt_time = datetime.datetime.strptime(item["create_time"], "%Y-%m-%d %H:%M:%S")
            upd_time = datetime.datetime.strptime(item["update_time"], "%Y-%m-%d %H:%M:%S")
            processed_historys_list.append(
                f"{crt_time.hour}:{crt_time.minute}到{upd_time.hour}:{upd_time.minute} 总结: {item['summary']}"
            )
        if processed_historys_list == []:
            return None, None, {}
        messages = [
            {"role": "system", "content": self.day_summary_prompt},
            {"role": "user", "content": "\n".join(processed_historys_list)},
        ]
        return self._send(messages)

    def _send(self, messages: list):
        for _ in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    max_tokens=1024,
                    temperature=self.temperature,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stream=True,
                )
                self.current_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        self.current_response += chunk.choices[0].delta.content
                    if chunk.choices[0].finish_reason:
                        self.finish_reason = chunk.choices[0].finish_reason
                    if chunk.usage:
                        token_usage = {
                            "completion_tokens": chunk.usage.completion_tokens,
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        }
                # print("\n-------\n",messages,"\n---\n",self.current_response,"\n---------\n\n")##################################
                return self.current_response, self.finish_reason, token_usage
            except APIError as e:
                logger.warning(f"api错误，将等待一段时间后重试 status code:{e.code}")
                delay = self.retry_delay + random.uniform(0, 5)  # 增加随机延迟
                time.sleep(delay)
            except Exception as e:
                logger.error(f"获取总结时出现意料之外的错误，将等待一段时间后重试 {e}")
                delay = self.retry_delay + random.uniform(0, 5)
