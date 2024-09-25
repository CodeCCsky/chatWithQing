# -*- coding: utf-8 -*-
import copy
import os
import sys

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from app.GUI.Ui.Ui_setting import Ui_MainWindow
from app.GUI.src.image_preview import image_preview
from third_party.setting_manager import *


# from Ui_initialization import Ui_MainWindow

# 其实就是从设置界面copy了一份，改了改逻辑而已..


class initialzationWidget(QMainWindow, Ui_MainWindow):
    changeSetting = pyqtSignal(settingManager)

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("初始化设置")
        self.initValue()
        self.initConnect()

    def initValue(self):
        self.setting_manager = settingManager()
        self.setting_manager.load_from_parameter(
            user_setting(None, "男", None, None),
            deepseek_api_setting(None),
            show_setting(),
            TTS_setting(),
            chat_summary_setting(),
            extension_func_setting(),
            emo_setting()
        )
        self.setting_manager_backup = copy.deepcopy(self.setting_manager)

        # user
        self.yourSexComboBox.setCurrentIndex(0)
        self.yourSexEdit.setEnabled(False)

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
        print(self.setting_manager.extension_func_setting)
        self.enableRecallCheckBox.setChecked(self.setting_manager.extension_func_setting.recall)

    def initConnect(self):
        # user
        self.listWidget.itemClicked.connect(self.sideListWidgetClicked)
        self.yourNameEdit.textChanged.connect(lambda p: setattr(self.setting_manager.user, "user_name", p))
        self.yourFavouriteFood.textChanged.connect(lambda p: setattr(self.setting_manager.user, "favourite_food", p))
        self.yourAddressEdit.textChanged.connect(lambda p: setattr(self.setting_manager.user, "user_location", p))
        self.yourSexComboBox.currentIndexChanged.connect(self.progress_user_sex)

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
            lambda p: setattr(self.setting_manager.show_setting, "img_show_zoom", float(p)/100.0)
        )
        self.imageShowSlider.valueChanged.connect(lambda p:self.image_preview_widget.resize_(float(p)/100.0))
        self.imageShowPreviewCheckBox.toggled.connect(self.progress_image_preview)
        self.image_preview_widget.closeSignal.connect(lambda : self.imageShowPreviewCheckBox.setChecked(False))

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
        self.addXDayAgoHisSummaryCheckBox.toggled.connect(
            lambda p: setattr(self.setting_manager.chat_summary_setting, "add_x_day_ago_summary", p)
        )
        self.addSameDayHisSummaryCheckBox.toggled.connect(self.addXDayAgoHisSummaryCheckBox.setCheckable)
        self.addXDayAgoHisSummarySpinBox.valueChanged.connect(
            lambda p: setattr(self.setting_manager.chat_summary_setting, "value_of_x_day_ago", p)
        )

        # extension_func
        self.enableRecallCheckBox.toggled.connect(
            lambda p: setattr(self.setting_manager.extension_func_setting, "recall", p)
        )

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

    def progress_image_preview(self, is_show: bool):
        if is_show:
            self.image_preview_widget.show()
        else:
            self.image_preview_widget.hide()

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

    def save_setting(self):
        check = self.setting_manager.check()
        if check == []:
            self.setting_manager_backup = copy.deepcopy(self.setting_manager)
            self.changeSetting.emit(self.setting_manager)
            QMessageBox.information(self, "已保存", "已保存当前设置。关闭当前窗口以启动主程序。")
        else:
            QMessageBox.warning(self, "出错", f'保存失败。存在尚未填入的值：{"，".join(check)}')

    def cancel_save(self):
        # self.setting_manager = copy.deepcopy(self.setting_manager_backup)
        self.close()

    def sideListWidgetClicked(self, item):
        index = self.listWidget.indexFromItem(item)
        self.stackedWidget.setCurrentIndex(index.row())

    def closeEvent(self, a0: QCloseEvent):
        reply = QMessageBox.warning(
            self,
            "退出",
            "确认要直接退出程序吗？若已经保存过，则按保存的设置启动主程序；若未保存，则会直接退出程序。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            a0.accept()
        else:
            a0.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    v0 = initialzationWidget()
    v0.show()
    app.exec_()
