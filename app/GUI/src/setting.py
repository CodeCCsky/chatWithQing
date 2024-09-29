# -*- coding: utf-8 -*-
import copy
import os
import sys

from PyQt5.QtCore import QTimer, pyqtSignal, QDate
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox


from app.GUI.Ui.Ui_setting import Ui_MainWindow
from app.GUI.src.image_preview import image_preview
from app.GUI.src.emotion_manager import emotionManagerWidget
from third_party.setting_manager import settingManager
from third_party.emo_manager import emo_manager

# from Ui_setting import Ui_MainWindow


class SettingWidget(QMainWindow, Ui_MainWindow):
    date_format = "yyyy-MM-dd"
    changeSetting = pyqtSignal(settingManager)
    changeEmoSetting = pyqtSignal(emo_manager)

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.initValue()
        self.initConnect()

    def initValue(self):
        self.setting_manager = settingManager()
        result = self.setting_manager.load_from_file()
        if result[0] != 0:
            raise ValueError(f"设置错误. error: {result}")
        self.setting_manager_backup = copy.deepcopy(self.setting_manager)
        self.emotion_manager = emo_manager()

        # user
        self.yourNameEdit.setText(self.setting_manager.user.user_name)
        self.yourAddressEdit.setText(self.setting_manager.user.user_location)
        self.yourFavouriteFood.setText(self.setting_manager.user.favourite_food)
        self.birthdayDateEdit.setDate(QDate.fromString(self.setting_manager.user.user_birthday, self.date_format))
        if self.setting_manager.user.user_sex == "男":
            self.yourSexComboBox.setCurrentIndex(0)
            self.yourSexEdit.setEnabled(False)
        elif self.setting_manager.user.user_sex == "女":
            self.yourSexComboBox.setCurrentIndex(1)
            self.yourSexEdit.setEnabled(False)
        else:
            self.yourSexComboBox.setCurrentIndex(2)
            self.yourSexEdit.setEnabled(True)
            self.yourSexEdit.setText(self.setting_manager.user.user_sex)

        # deepseek
        self.lAPIEdit.setText(self.setting_manager.deepseek_model.api_key)
        self.temperatureSlider.setValue(self.setting_manager.deepseek_model.temperature * 10)
        self.temperatureShowLabel.setText(str(self.setting_manager.deepseek_model.temperature))
        self.frequencyPenaltySlider.setValue(self.setting_manager.deepseek_model.frequency_penalty * 10)
        self.frequencyPenaltyShowLabel.setText(str(self.setting_manager.deepseek_model.frequency_penalty))
        self.presencePenaltylSlider.setValue(self.setting_manager.deepseek_model.presence_penalty * 10)
        self.presencePenaltyShowLabel.setText(str(self.setting_manager.deepseek_model.presence_penalty))

        # TTS
        self.EnableTTScheckBox.setChecked(self.setting_manager.tts_setting.use_tts)
        self.TTSUrlEdit.setText(self.setting_manager.tts_setting.url)
        self.TTSCharacterEdit.setText(self.setting_manager.tts_setting.character_name)
        self.lTTSEmotionEdit.setText(self.setting_manager.tts_setting.emotion)

        # show
        self.textShowSpeedSpinBox.setMaximum(1000)
        self.textShowSpeedSpinBox.setValue(self.setting_manager.show_setting.text_show_gap)
        self.show_gap_timer = QTimer()
        self.show_gap_timer.timeout.connect(self.progress_example)
        self.example_text = "这个显示速度还可以吗？"
        self.example_pointer = 0
        self.progress_text_gap(self.setting_manager.show_setting.text_show_gap)
        self.imageShowSlider.setValue(int(self.setting_manager.show_setting.img_show_zoom * 100))
        self.imageShowPreviewCheckBox.setChecked(False)

        # history
        # self.scan_history_file()

        # summary
        self.addSameDayHisSummaryCheckBox.setChecked(self.setting_manager.chat_summary_setting.add_same_day_summary)
        self.addXDayAgoHisSummaryCheckBox.setChecked(self.setting_manager.chat_summary_setting.add_x_day_ago_summary)
        self.addXDayAgoHisSummarySpinBox.setValue(self.setting_manager.chat_summary_setting.value_of_x_day_ago)

        # extension_func
        self.enableRecallCheckBox.setChecked(self.setting_manager.extension_func_setting.recall)

        # emo
        self.showEmoInTextCheckBox.setChecked(self.setting_manager.emo_setting.show_in_text)
        self.emo_manager_widget = emotionManagerWidget(self.emotion_manager)
        self.emo_manager_widget.setVisible(False)

    def initConnect(self):
        # user
        self.listWidget.itemClicked.connect(self.sideListWidgetClicked)
        self.yourNameEdit.textChanged.connect(lambda p: setattr(self.setting_manager.user, "user_name", p))
        self.yourFavouriteFood.textChanged.connect(lambda p: setattr(self.setting_manager.user, "favourite_food", p))
        self.yourAddressEdit.textChanged.connect(lambda p: setattr(self.setting_manager.user, "user_location", p))
        self.yourSexComboBox.currentIndexChanged.connect(self.progress_user_sex)
        self.birthdayDateEdit.dateChanged.connect(
            lambda p: setattr(self.setting_manager.user, "user_birthday", p.toString(self.date_format))
        )

        # deepseek
        self.lAPIEdit.textChanged.connect(lambda p: setattr(self.setting_manager.deepseek_model, "api_key", p))
        self.temperatureSlider.valueChanged.connect(
            lambda p: setattr(self.setting_manager.deepseek_model, "temperature", float(p) / 10)
        )
        self.temperatureSlider.valueChanged.connect(
            lambda p: self.temperatureShowLabel.setText(str(round(float(p) / 10, 1)))
        )
        self.frequencyPenaltySlider.valueChanged.connect(
            lambda p: setattr(self.setting_manager.deepseek_model, "frequency_penalty", float(p) / 10)
        )
        self.frequencyPenaltySlider.valueChanged.connect(
            lambda p: self.frequencyPenaltyShowLabel.setText(str(round(float(p) / 10, 1)))
        )
        self.presencePenaltylSlider.valueChanged.connect(
            lambda p: setattr(self.setting_manager.deepseek_model, "presence_penalty", float(p) / 10)
        )
        self.presencePenaltylSlider.valueChanged.connect(
            lambda p: self.presencePenaltyShowLabel.setText(str(round(float(p) / 10, 1)))
        )

        # TTS
        self.EnableTTScheckBox.toggled.connect(lambda p: setattr(self.setting_manager.tts_setting, "use_tts", p))
        self.TTSUrlEdit.textChanged.connect(lambda p: setattr(self.setting_manager.tts_setting, "url", p))
        self.TTSCharacterEdit.textChanged.connect(lambda p: setattr(self.setting_manager.tts_setting, "character", p))
        self.lTTSEmotionEdit.textChanged.connect(lambda p: setattr(self.setting_manager.tts_setting, "emotion", p))

        # show
        self.image_preview_widget = image_preview(zoom_factor=self.setting_manager.show_setting.img_show_zoom)
        self.textShowSpeedSpinBox.valueChanged.connect(self.progress_text_gap)
        self.imageShowSlider.valueChanged.connect(lambda p: self.imageShowZoomPercentLabel.setText(str(p) + "%"))
        self.imageShowSlider.valueChanged.connect(
            lambda p: setattr(self.setting_manager.show_setting, "img_show_zoom", float(p) / 100.0)
        )
        self.imageShowSlider.valueChanged.connect(lambda p: self.image_preview_widget.resize_(float(p) / 100.0))
        self.imageShowPreviewCheckBox.toggled.connect(self.progress_image_preview)
        self.image_preview_widget.closeSignal.connect(lambda: self.imageShowPreviewCheckBox.setChecked(False))

        # history
        # self.chooseHistoryComboBox.currentTextChanged.connect(lambda p:setattr(self.setting_manager,'history_path',os.path.join('./history',p)))
        # self.scanHistoryFileButton.clicked.connect(self.scan_history_file)

        # ensure
        self.SaveButtonBox.accepted.connect(self.save_setting)
        self.SaveButtonBox.rejected.connect(self.cancel_save)

        # summary
        self.addSameDayHisSummaryCheckBox.toggled.connect(
            lambda p: setattr(self.setting_manager.chat_summary_setting, "add_same_day_summary", p)
        )
        self.addSameDayHisSummaryCheckBox.toggled.connect(self.addXDayAgoHisSummaryCheckBox.setCheckable)
        self.addXDayAgoHisSummaryCheckBox.toggled.connect(
            lambda p: setattr(self.setting_manager.chat_summary_setting, "add_x_day_ago_summary", p)
        )
        self.addXDayAgoHisSummarySpinBox.valueChanged.connect(
            lambda p: setattr(self.setting_manager.chat_summary_setting, "value_of_x_day_ago", p)
        )

        # extension_func
        self.enableRecallCheckBox.toggled.connect(
            lambda p: setattr(self.setting_manager.extension_func_setting, "recall", p)
        )

        self.showEmoInTextCheckBox.toggled.connect(
            lambda p: setattr(self.setting_manager.emo_setting, "show_in_text", p)
        )
        self.EmotionManagePushButton.clicked.connect(lambda: self.emo_manager_widget.setVisible(True))
        self.emo_manager_widget.changeEmotionSetting.connect(self.changeEmoSetting.emit)

    def scan_history_file(self):
        file_lists = os.listdir("history/")
        self.chooseHistoryComboBox.clear()
        self.chooseHistoryComboBox.addItems(file_lists)
        self.chooseHistoryComboBox.setCurrentIndex(self.chooseHistoryComboBox.count() - 1)
        if self.setting_manager.history_path is None:
            self.setting_manager.history_path = os.path.join(
                "./history", self.chooseHistoryComboBox.itemText(self.chooseHistoryComboBox.count() - 1)
            )

    def progress_text_gap(self, gap: int):
        self.show_gap_timer.start(gap)
        self.setting_manager.show_setting.text_show_gap = gap

    def progress_example(self):
        self.textShowSpeedExampleLabel.setText(self.example_text[: self.example_pointer])
        self.example_pointer = (self.example_pointer + 1) % (len(self.example_text) + 1)

    def progress_user_sex(self, index: int):
        if index == 0:
            self.yourSexEdit.setEnabled(False)
            self.setting_manager.user.user_sex = "男"
        elif index == 1:
            self.yourSexEdit.setEnabled(False)
            self.setting_manager.user.user_sex = "女"
        else:
            self.yourSexEdit.setEnabled(True)
            sex = self.yourSexEdit.text()
            if not sex:
                sex = "其他"
            self.setting_manager.user.user_sex = sex

    def progress_image_preview(self, is_show: bool):
        if is_show:
            self.image_preview_widget.show()
        else:
            self.image_preview_widget.hide()

    def save_setting(self):
        if self.setting_manager.get_user_name() == "晴" or self.setting_manager.get_user_name() == "晴小姐" or self.setting_manager.get_user_name() == "sys":
            reply = QMessageBox.warning(
                self,
                "非法起名",
                f"不能使用{self.setting_manager.get_user_name()}作为用户名，这会导致不可预知的错误。\n请重新输入。",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
            return
        if self.setting_manager.user != self.setting_manager_backup.user:  # TODO 自动修改
            reply = QMessageBox.warning(
                self,
                "警告",
                "你似乎更改了认知设置的某些项。\n建议手动关闭程序后前往历史记录目录下(history/)修改相应的项后再次启动程序。\n否则可能会出现不可预知的结果。",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
            # test = historyComparisonDialog(self.setting_manager,self)
            # test.exec_()
        self.setting_manager_backup = copy.deepcopy(self.setting_manager)
        self.changeSetting.emit(self.setting_manager)
        self.closeEvent(QCloseEvent())

    def cancel_save(self):
        self.setting_manager = copy.deepcopy(self.setting_manager_backup)
        self.closeEvent(QCloseEvent())

    def sideListWidgetClicked(self, item):
        index = self.listWidget.indexFromItem(item)
        self.stackedWidget.setCurrentIndex(index.row())

    def closeEvent(self, a0: QCloseEvent):
        self.setting_manager = copy.deepcopy(self.setting_manager_backup)
        self.setVisible(False)
        self.image_preview_widget.hide()
        self.imageShowPreviewCheckBox.setChecked(False)
        a0.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    v0 = SettingWidget()
    v0.show()
    sys.exit(app.exec_())


"""# 历史修改 废案 也许哪天要正式写历史修改功能的时候改改还能用？
class historyComparisonDialog(QDialog, Ui_Dialog):
    default_history_path = r"history/"

    def __init__(self, setting_manager: settingManager, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setting_manager = setting_manager
        self.list_of_history = []
        self.load_history = {}
        self.changed_history = {}
        self.highlight_timer = QTimer()
        self.highlight_timer.timeout.connect(self.highlight_changes)
        self.init_connect()
        self.init_history_list()

    def init_history_list(self):
        files = os.listdir(self.default_history_path)
        for file in files:
            if not file.endswith(".json"):
                continue
            self.list_of_history.append(os.path.join(self.default_history_path, os.path.basename(file)))
            self.listWidget.addItem(os.path.basename(file))
        self.now_index = len(self.list_of_history) - 1
        print(self.list_of_history)

    def init_connect(self):
        self.listWidget.itemClicked.connect(self.progress_listWidget_click)
        self.replaceWithLLMButton
        self.forceReplaceButton
        self.delHistoryButton
        self.confirmButtonBox
        self.originTextEdit
        self.replacedTextEdit.textChanged.connect(self.schedule_highlight_changes)
        self.cancelButton.clicked.connect(self.progress_cancel)

    def progress_listWidget_click(self, item):
        self.now_index = self.listWidget.indexFromItem(item).row()
        if self.now_index not in self.load_history:
            self.load_history[self.now_index] = historyManager(
                user_name=self.setting_manager.get_user_name(),
                history_path=self.list_of_history[self.now_index],
                current_history_index=0,
            ).get_full_data()
            self.changed_history[self.now_index] = copy.deepcopy(self.load_history)
        self.replacedTextEdit.setText(json.dumps(self.changed_history[self.now_index], ensure_ascii=False, indent=2))
        self.originTextEdit.setText(json.dumps(self.load_history[self.now_index], ensure_ascii=False, indent=2))
        self.highlight_changes()

    def progress_cancel(self):
        pass

    def schedule_highlight_changes(self):
        # 停止之前的定时器
        self.highlight_timer.stop()
        # 启动新的定时器，延迟 500 毫秒后执行 highlight_changes
        self.highlight_timer.start(500)

    def highlight_changes(self):
        # 避免递归调用
        if self.replacedTextEdit.blockSignals(True):
            original_text = self.originTextEdit.toPlainText()
            modified_text = self.replacedTextEdit.toPlainText()

            dmp = diff_match_patch()
            diffs = dmp.diff_main(original_text, modified_text)
            dmp.diff_cleanupSemantic(diffs)

            # 清空高亮
            self.clear_highlights(self.originTextEdit)
            self.clear_highlights(self.replacedTextEdit)

            # 高亮显示差异
            cursor_original = self.originTextEdit.textCursor()
            cursor_modified = self.replacedTextEdit.textCursor()

            cursor_origined_cnt = 0
            cursor_modified_cnt = 0

            for (op, data) in diffs:
                if op == 0:  # 未修改
                    cursor_origined_cnt += len(data)
                    cursor_modified_cnt += len(data)
                elif op == -1:  # 删除
                    cursor_original.setPosition(cursor_origined_cnt)
                    cursor_original.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(data))
                    cursor_original.mergeCharFormat(self.create_highlight_format(QColor(255, 100, 100)))
                    cursor_origined_cnt += len(data)
                elif op == 1:  # 添加
                    cursor_modified.setPosition(cursor_modified_cnt)
                    cursor_modified.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(data))
                    cursor_modified.mergeCharFormat(self.create_highlight_format(QColor(100, 255, 100)))
                    cursor_modified_cnt += len(data)

            self.replacedTextEdit.blockSignals(False)

    def clear_highlights(self, text_edit):
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        format.setBackground(QColor(Qt.white))
        cursor.mergeCharFormat(format)
        #text_edit.setTextCursor(cursor)

    def create_highlight_format(self, color):
        format = QTextCharFormat()
        format.setBackground(color)
        return format
"""
