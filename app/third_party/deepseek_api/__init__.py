# from app.third_party.deepseek_api.deepseek_tools import tool_template
from app.third_party.deepseek_api.model import deepseek_model
from app.third_party.deepseek_api.history_manager import historyManager, HistoryItemModel
from app.third_party.deepseek_api.summary import deepseek_summary
from app.third_party.deepseek_api.deepseek_request_thread import (
    PyQt_deepseek_request_thread,
    PyQt_deepseek_request_prefix_thread,
)