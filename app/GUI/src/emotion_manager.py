from PyQt5.QtWidgets import (
    QMainWindow,
    QListWidgetItem,
    QListWidget,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent

from app.GUI.Ui.Ui_emotion_setting import Ui_MainWindow
from third_party.emo_manager import emo_manager
import copy


class ListSelectionDialog(QDialog):
    def __init__(self, title, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        for item in items:
            self.list_widget.addItem(item)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def selected_items(self):
        return [
            self.list_widget.indexFromItem(self.list_widget.item(i)).row()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).isSelected()
        ]


class emotionManagerWidget(QMainWindow, Ui_MainWindow):
    changeEmotionSetting = pyqtSignal(emo_manager)

    def __init__(self, emo_manager_: emo_manager, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.emotion_manager_copy = copy.deepcopy(emo_manager_)
        self.emotion_manager = copy.deepcopy(emo_manager_)
        self.setupUi(self)
        self.init_connect()
        self.strShowListWidget.setSelectionMode(QListWidget.NoSelection)

    def init_connect(self):
        self.categoryMenuListWidget.itemClicked.connect(self.on_item_clicked)
        self.categoryMenuListWidget.setCurrentRow(0)
        self.on_item_clicked(self.categoryMenuListWidget.item(0))
        self.strShowListWidget.itemClicked.connect(self.on_sub_item_clicked)
        self.moveButton.clicked.connect(self.progress_move)
        self.copyButton.clicked.connect(self.progress_copy)
        self.delButton.clicked.connect(self.progress_del)
        self.addItemButton.clicked.connect(self.progress_add)
        self.ensureButtonBox.accepted.connect(self.progress_OK)
        self.ensureButtonBox.rejected.connect(self.progress_cancel)

    def on_item_clicked(self, item):
        self.selected_class_i = self.categoryMenuListWidget.indexFromItem(item).row()
        self.strShowListWidget.clear()
        select_all_item = QListWidgetItem("全选")
        select_all_item.setFlags(select_all_item.flags() | Qt.ItemIsUserCheckable)
        select_all_item.setCheckState(Qt.Unchecked)
        self.strShowListWidget.addItem(select_all_item)
        if self.selected_class_i == 0:
            for sub_item in self.emotion_manager.unconfirmed_emoji:
                list_item = QListWidgetItem(sub_item)
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Unchecked)
                self.strShowListWidget.addItem(list_item)
            self.graphicsView.unlock_facial_expr()
            self.graphicsView.change_emo(0)
        elif self.selected_class_i == len(self.emotion_manager.confirmed_emoji) + 1:
            for sub_item in self.emotion_manager.ignored_str:
                list_item = QListWidgetItem(sub_item)
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Unchecked)
                self.strShowListWidget.addItem(list_item)
            self.graphicsView.unlock_facial_expr()
            self.graphicsView.change_emo(0)
        else:
            for sub_item in self.emotion_manager.confirmed_emoji[self.selected_class_i - 1]:
                list_item = QListWidgetItem(sub_item)
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Unchecked)
                self.strShowListWidget.addItem(list_item)
            self.graphicsView.unlock_facial_expr()
            self.graphicsView.change_emo(self.selected_class_i - 1, self.selected_class_i != 1)

    # BUG 勾选框可点击无反应

    def on_sub_item_clicked(self, item):
        if item.text() == "全选" and self.strShowListWidget.indexFromItem(item).row() == 0:
            # 处理 "全选" 项的文字部分点击事件
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
        else:
            # 处理其他项的文字部分点击事件
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

        # 处理 "全选" 项的勾选状态变化
        if item.text() == "全选" and self.strShowListWidget.indexFromItem(item).row() == 0:
            if item.checkState() == Qt.Checked:
                for i in range(1, self.strShowListWidget.count()):
                    self.strShowListWidget.item(i).setCheckState(Qt.Checked)
            else:
                for i in range(1, self.strShowListWidget.count()):
                    self.strShowListWidget.item(i).setCheckState(Qt.Unchecked)

    def progress_move(self):
        selected_items = [
            self.strShowListWidget.item(i).text()
            for i in range(self.strShowListWidget.count())
            if self.strShowListWidget.item(i).checkState() == Qt.Checked
        ]
        if selected_items == [] or selected_items == ["全选"]:
            QMessageBox.warning(self, "警告", "没有选中任何项")
            return
        target_list = [self.categoryMenuListWidget.item(i).text() for i in range(self.categoryMenuListWidget.count())]
        dialog = ListSelectionDialog("移动到...", target_list)
        if dialog.exec_() == QDialog.Accepted:
            selected_targets = dialog.selected_items()
            self.del_str_in_manager(self.selected_class_i, selected_items)
            for target in selected_targets:
                self.add_str_in_manager(target, selected_items)
        # 刷新
        self.on_item_clicked(self.categoryMenuListWidget.item(self.selected_class_i))

    def progress_copy(self):
        selected_items = [
            self.strShowListWidget.item(i).text()
            for i in range(self.strShowListWidget.count())
            if self.strShowListWidget.item(i).checkState() == Qt.Checked
        ]
        if selected_items == [] or selected_items == ["全选"]:
            QMessageBox.warning(self, "警告", "没有选中任何项")
            return
        target_list = [self.categoryMenuListWidget.item(i).text() for i in range(self.categoryMenuListWidget.count())]
        dialog = ListSelectionDialog("复制到...", target_list)
        if dialog.exec_() == QDialog.Accepted:
            selected_targets = dialog.selected_items()
            for target in selected_targets:
                self.add_str_in_manager(target, selected_items)
        # 刷新
        self.on_item_clicked(self.categoryMenuListWidget.item(self.selected_class_i))

    def progress_del(self):
        selected_items = [
            self.strShowListWidget.item(i).text()
            for i in range(self.strShowListWidget.count())
            if self.strShowListWidget.item(i).checkState() == Qt.Checked
        ]
        if selected_items == [] or selected_items == ["全选"]:
            QMessageBox.warning(self, "警告", "没有选中任何项")
            return
        reply = QMessageBox.question(self, "确认删除", "确定要删除选中的项吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.del_str_in_manager(self.selected_class_i, selected_items)
        # 刷新
        self.on_item_clicked(self.categoryMenuListWidget.item(self.selected_class_i))

    def progress_add(self):
        texts = [
            self.lineEdit.text(),
        ]
        self.lineEdit.clear()
        self.add_str_in_manager(self.selected_class_i, texts)

    def progress_OK(self):
        self.emotion_manager_copy = copy.deepcopy(self.emotion_manager)
        self.changeEmotionSetting.emit(self.emotion_manager)
        self.closeEvent(QCloseEvent())

    def progress_cancel(self):
        self.emotion_manager = copy.deepcopy(self.emotion_manager_copy)
        self.closeEvent(QCloseEvent())

    def closeEvent(self, a0: QCloseEvent):
        self.setVisible(False)
        self.emotion_manager = copy.deepcopy(self.emotion_manager_copy)
        a0.ignore()

    def del_str_in_manager(self, index: int, strs: list):
        if "全选" in strs:
            strs.remove("全选")
        if index == 0:
            for i in strs:
                try:
                    self.emotion_manager.unconfirmed_emoji.remove(i)
                except ValueError:
                    continue
        elif index == len(self.emotion_manager.confirmed_emoji) + 1:
            for i in strs:
                try:
                    self.emotion_manager.ignored_str.remove(i)
                except ValueError:
                    continue
        else:
            for i in strs:
                try:
                    self.emotion_manager.confirmed_emoji[index - 1].remove(i)
                except ValueError:
                    continue

    def add_str_in_manager(self, index: int, strs: list):
        if "全选" in strs:
            strs.remove("全选")
        if index == 0:
            self.emotion_manager.unconfirmed_emoji.extend(strs)
        elif index == len(self.emotion_manager.confirmed_emoji) + 1:
            self.emotion_manager.ignored_str.extend(strs)
        else:
            self.emotion_manager.confirmed_emoji[index - 1].extend(strs)
