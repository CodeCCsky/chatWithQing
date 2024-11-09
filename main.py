# -*- coding: utf-8 -*-
import datetime
import logging
import logging.handlers
import os
import sys
import time

now_dir = os.getcwd()
sys.path.insert(0, now_dir)

from PyQt5.QtWidgets import QApplication, QMessageBox

# TODO 代理支持

from app.GUI import initialzationWidget
from third_party.setting_manager import settingManager

file_handler = logging.handlers.TimedRotatingFileHandler("log/app.log", when="midnight", backupCount=3, encoding="utf8")
stream_hanlder = logging.StreamHandler()
logging.basicConfig(
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[file_handler, stream_hanlder],
)

logger = logging.getLogger(__name__)

import main_window


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, Exception):
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception


def main():
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y%m%d")
    logger.info("设置加载完成，启动主程序中")
    pet = main_window.mainWidget(history_path=os.path.join(main_window.default_history_path, f"{current_time}.json"))
    sys.exit(main_app.exec_())


def set_setting(__setting: settingManager):
    __setting.load_system_prompt_main()
    state = __setting.write_yaml()
    logger.info(f"设置写入状态：{state}")


def initize():
    init = initialzationWidget()
    init.changeSetting.connect(set_setting)
    init.show()
    main_app.exec_()
    time.sleep(1)  # 保证设置写入成功
    init_setting = settingManager()
    state = init_setting.load_from_file()
    if state[0] == 0:
        logger.info("成功加载设置")
        reply = QMessageBox.information(
            None,
            "测试版提示",
            "当前版本为测试版。由于作者实力不足，可能会有许多未知的bug，欢迎向作者反馈(反馈方式见'请先读我.pdf')\ntips: 现在这个ai晴小姐没有关于爱之巢游戏本体内容的记忆...以后会想办法解决的",
        )
        main()
    else:
        logger.error(f"设置加载失败", exc_info=state)
        sys.exit()


if __name__ == "__main__":
    logger.info("程序启动")
    main_app = QApplication(sys.argv)
    _setting = settingManager()
    state_num = _setting.load_from_file()
    if state_num[0] == 0:
        logger.info("成功加载设置")
        main()
    else:
        logger.warning(f"err: {state_num[1]}。启动初始化。")
        initize()
