import copy
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
)
from PyQt5.QtCore import pyqtSignal, QSize

from app.GUI.Ui.Ui_retry_message_show_dialog import Ui_Dialog
from app.third_party.deepseek_api import historyManager


class SubWidget(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        layout = QVBoxLayout()

        role_label = QLabel(data["role"])
        layout.addWidget(role_label)

        self.data = data
        self.value_edits = []

        for key, value in self.data["content"].items():
            # 创建不可更改的key标签
            key_label = QLabel(key)
            layout.addWidget(key_label)

            # 创建可更改的value输入框
            value_edit = QLineEdit(value)
            layout.addWidget(value_edit)
            self.value_edits.append(value_edit)

        self.setLayout(layout)

    def get_edited_data(self) -> dict:
        edited_data = copy.deepcopy(self.data)
        for key, value_edit in zip(self.data["content"].keys(), self.value_edits):
            edited_data["content"][key] = value_edit.text()
        return edited_data


class RetryMessageDialog(QDialog, Ui_Dialog):
    _instance = None
    continueRetry = pyqtSignal(list)
    ignoreRetry = pyqtSignal()

    def __init__(self, history_manager: historyManager):
        super().__init__()
        self.history_manager = history_manager
        self.setupUi(self)
        self.setWindowTitle("未成功发送的信息")

        self.OKButton.clicked.connect(self.on_ok_clicked)
        self.cancelButton.clicked.connect(self.on_cancel_clicked)
        self.populate_list_widget()

    def populate_list_widget(self):
        # print(self.history_manager.get_full_data())
        messages = self.history_manager.get_wait_to_del_msgs()
        # print(messages)
        for msg in messages:
            sub_widget = SubWidget(msg)
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(QSize(sub_widget.sizeHint().width(), sub_widget.sizeHint().height()))
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, sub_widget)

    def get_edited_data(self) -> list:
        edited_data_list = []
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            sub_widget = sub_widget = self.listWidget.itemWidget(item)
            edited_data_list.append(sub_widget.get_edited_data())
        return edited_data_list

    def on_ok_clicked(self):
        self.continueRetry.emit(self.get_edited_data())
        self.hide()

    def on_cancel_clicked(self):
        self.ignoreRetry.emit()
        self.hide()

    def closeEvent(self, event):
        self.on_cancel_clicked()
        super().closeEvent(event)
