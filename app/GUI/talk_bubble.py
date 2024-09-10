# -*- coding: utf-8 -*-
# import numpy as np
import random
import math
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QPainter,
    QPen,
)
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMenu, QWidget

import app.asset.res_rc

# import res_rc

TEXT_UPDATE_TIME = 200  # 毫秒


# 忘记做分离了 :(
class talkBubble(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.name_size = 24
        self.text_size = 16
        self.row_spacing = 2
        self.name_str = "晴"
        self.text_str = ""
        self.keep_opacity_time = 5000

        self.initUI()
        self.init_rand()
        self.init_window_opacity_control()

    def initUI(self) -> None:
        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(":/font/荆南波波黑.ttf")
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(int(screen.width() * 0.5 - 800 / 2), int(screen.height() * 0.7), 800, 200)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setStyleSheet("background:transparent; border: none;")
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground)

        self.name_font = QFont("荆南波波黑", self.name_size, QFont.Bold)
        self.text_font = QFont("荆南波波黑", self.text_size)
        self.text_fm = QFontMetrics(self.text_font)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 16, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(53, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.widget_2 = QtWidgets.QWidget(self.widget)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.name_area = QtWidgets.QLabel(self.widget_2)
        self.name_area.setAlignment(QtCore.Qt.AlignCenter)
        self.name_area.setObjectName("name_area")
        self.verticalLayout_3.addWidget(self.name_area)
        spacerItem3 = QtWidgets.QSpacerItem(20, 47, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(2, 3)
        self.horizontalLayout.addWidget(self.widget_2)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.text_area = QtWidgets.QTextEdit(self.widget)
        self.text_area.setObjectName("text_area")
        self.text_area.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.text_area.setFixedWidth(int(self.width() * 27 / 42))
        self.horizontalLayout.addWidget(self.text_area)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.horizontalLayout.setStretch(0, 4)
        self.horizontalLayout.setStretch(1, 4)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 27)
        self.horizontalLayout.setStretch(4, 5)
        self.verticalLayout.addWidget(self.widget)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 6)
        self.verticalLayout.setStretch(2, 1)
        self.name_area.setFont(self.name_font)
        self.name_area.setStyleSheet("color: white;")
        self.text_area.setFont(self.text_font)
        self.text_area.setStyleSheet("background: transparent; border: none;")
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_area.setTextInteractionFlags(Qt.NoTextInteraction)
        self.text_area.setReadOnly(True)
        self.text_area.mousePressEvent = self.mousePressEvent
        self.text_area.mouseMoveEvent = self.mouseMoveEvent
        self.text_area.contextMenuEvent = self.contextMenuEvent
        self.text_area.textChanged.connect(self.adjustSize)
        self.name_area.setText("晴")
        self.is_hide = False

    def init_window_opacity_control(self):
        self.keep_opacity = False
        self.keep_opacity_timer = QTimer()
        self.keep_opacity_timer.timeout.connect(self.reset_keep_opacity)
        self.is_mouse_over = True
        self.window_opacity_timer = QTimer()
        self.window_opacity_timer.timeout.connect(self.window_opacity_control)
        self.window_opacity_timer.start(25)  # 25 毫秒更新一次窗口透明度
        self.set_mouse_over_timer = QTimer()  # 鼠标离开/进入窗口后多久更新 is_mouse_over

    def init_rand(self) -> None:
        self.update_rand()
        self.rand_timer = QTimer()
        self.rand_timer.timeout.connect(self.update_rand)
        self.rand_timer.start(500)

    def update_rand(self) -> None:
        # np.random.seed(self.randnum)
        self.points_num = int((self.width() + self.height()) * 1.6 / 50)
        self.points_of_path = []
        # self.points_of_path.append(get_required_point_coordinates(self.points_num, 0.03))
        # self.points_of_path.append(get_required_point_coordinates(self.points_num, 0.015))
        # self.points_of_path.append(get_required_point_coordinates(self.points_num, 0.01))
        # self.path_start_index = int((np.random.rand())*2*self.points_num) % self.points_num
        self.update()

    def update_text(self, text, is_thinking: bool = False):
        self.set_keep_opacity()
        self._setTextLabel("晴", text, is_thinking)

    def clear_text(self):
        self._setTextLabel("晴", "")

    def set_keep_opacity_time(self, keep_time: int):
        self.keep_opacity_time = keep_time

    def set_keep_opacity(self):
        self.keep_opacity = True
        self.keep_opacity_timer.start(self.keep_opacity_time)

    def reset_keep_opacity(self):
        self.keep_opacity = False
        self.keep_opacity_timer.stop()

    def _setTextLabel(self, name: str, text: str, is_thinking: bool = False) -> None:
        default_start = '<p style="color: white;">'
        default_end = "</p>"
        grey_start = '<p style="color: grey;">'
        purple_start = '<p style="color: #ff0084;"'
        processed_text = ""
        emph_flag = False  # TODO 标记强调
        grey_flag = is_thinking
        skip_char_num = 0
        if text.startswith("**"):
            emph_flag = True
            processed_text = purple_start
        elif grey_flag:
            processed_text = grey_start
        else:
            processed_text = default_start
        for i in range(0, len(text)):
            if skip_char_num > 0:
                skip_char_num = skip_char_num - 1
                continue
            if text[i : i + 1] == "**":
                emph_flag = not emph_flag
                skip_char_num = 1
                if emph_flag:
                    processed_text = processed_text + default_end + purple_start
                elif grey_flag:
                    processed_text = processed_text + default_end + grey_start
                else:
                    processed_text = processed_text + default_end + default_start
            elif text[i] == "\n":
                if emph_flag:
                    processed_text = processed_text + default_end + purple_start
                elif grey_flag:
                    processed_text = processed_text + default_end + grey_start
                else:
                    processed_text = processed_text + default_end + default_start
            else:
                processed_text += text[i]
        processed_text += "</p>"
        self.name_str = name
        self.text_str = processed_text
        self.text_area.setHtml(self.text_str)
        self.adjustSize()

    def adjustSize(self) -> None:
        document = self.text_area.document()
        document.setTextWidth(self.text_area.width())
        document_height = document.size().height()
        window_width = self.width()
        self.text_area.setFixedHeight(document_height)
        window_height = max(200, int(document_height * 4 / 3))
        self.setFixedSize(window_width, window_height)
        self.update()

    def hide_window(self):
        self.is_hide = True
        self.setWindowOpacity(0)

    def show_window(self):
        self.is_hide = False
        self.setWindowOpacity(0.99)

    def set_mouse_over(self, status: bool):
        self.set_mouse_over_timer.stop()
        self.is_mouse_over = status

    def window_opacity_control(self):
        if self.is_hide is False and self.keep_opacity is False:
            if self.is_mouse_over:
                opacity_value = min(0.99, self.windowOpacity() + 0.1)
                self.setWindowOpacity(opacity_value)
            else:
                opacity_value = max(0.3, self.windowOpacity() - 0.1)
                self.setWindowOpacity(opacity_value)
        elif self.is_hide:
            self.setWindowOpacity(0)
        elif self.keep_opacity:
            self.setWindowOpacity(0.99)

    def enterEvent(self, event):
        self.set_mouse_over_timer.stop()
        self.set_mouse_over_timer.timeout.connect(lambda p=True: self.set_mouse_over(p))
        self.set_mouse_over_timer.start(10)

    def leaveEvent(self, event):
        self.set_mouse_over_timer.stop()
        self.set_mouse_over_timer.timeout.connect(lambda p=False: self.set_mouse_over(p))
        self.set_mouse_over_timer.start(1000)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景和边框
        window_width = self.width()
        window_height = self.height()

        # 背景
        #        bg_polygon_zoom_factor = 0.83
        #        bg_polygon = QPolygon([QPoint(int(x*window_width*bg_polygon_zoom_factor + window_width/2), int(y*window_height*bg_polygon_zoom_factor + window_height/2)) for x, y in self.points_of_path[0]])

        # 背景边缘线
        #        border_path = QPainterPath()
        #        border_zoom_factor = 0.87
        #        border_path.moveTo(self.points_of_path[1][self.path_start_index][0]*window_width*border_zoom_factor + window_width/2,
        #                           self.points_of_path[1][self.path_start_index][1]*window_height*border_zoom_factor + window_height/2)

        # 边框
        #        for i in range(self.path_start_index, self.points_num + self.path_start_index - 1, 3):
        #            p1 = self.points_of_path[1][i%self.points_num]
        #            p2 = self.points_of_path[1][(i + 1)%self.points_num]
        #            p3 = self.points_of_path[1][(i + 2)%self.points_num]
        #            border_path.cubicTo(p1[0]*window_width*border_zoom_factor + window_width/2,
        #                                p1[1]*window_height*border_zoom_factor + window_height/2,
        #                                p2[0]*window_width*border_zoom_factor + window_width/2,
        #                                p2[1]*window_height*border_zoom_factor + window_height/2,
        #                                p3[0]*window_width*border_zoom_factor + window_width/2,
        #                                p3[1]*window_height*border_zoom_factor + window_height/2)
        #        border_zoom_factor = 0.9
        #        for i in range(self.path_start_index, self.points_num + self.path_start_index - 1, 3):
        #            p1 = self.points_of_path[2][i%self.points_num]
        #            p2 = self.points_of_path[2][(i + 1)%self.points_num]
        #            p3 = self.points_of_path[2][(i + 2)%self.points_num]
        #            border_path.cubicTo(p1[0]*window_width*border_zoom_factor + window_width/2,
        #                                p1[1]*window_height*border_zoom_factor + window_height/2,
        #                                p2[0]*window_width*border_zoom_factor + window_width/2,
        #                                p2[1]*window_height*border_zoom_factor + window_height/2,
        #                                p3[0]*window_width*border_zoom_factor + window_width/2,
        #                                p3[1]*window_height*border_zoom_factor + window_height/2)
        # 绘画背景和边框
        painter.setPen(QPen(QColor(0, 0, 0, 210), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QBrush(QColor(0, 0, 0), Qt.SolidPattern))
        #        painter.drawPolygon(bg_polygon)
        painter.setBrush(QBrush())
        painter.setPen(QPen(QColor(252, 58, 170, 255), 8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    #        painter.drawPath(border_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = self.window_pos + (event.globalPos() - self.mouse_press_pos)
            self.move(new_pos)
            event.accept()

    def change_name_size(self, size: int) -> None:
        self.name_size = size
        self.name_font = QFont("荆南波波黑", self.name_size, QFont.Bold)

    def change_text_size(self, size: int) -> None:
        self.text_size = size
        self.text_font = QFont("荆南波波黑", self.text_size)
        self.text_fm = QFontMetrics(self.text_font)

    def change_row_spacing(self, height: int) -> None:
        self.row_spacing = height

    def contextMenuEvent(self, event):
        """右键菜单"""
        talk_bubble_menu = QMenu()
        talk_bubble_menu.setStyleSheet(
            """
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid #ff0084;
            }
            QMenu::item:selected {
                background-color: gray;
            }
        """
        )
        hide = talk_bubble_menu.addAction("隐藏")
        action = talk_bubble_menu.exec_(self.mapToGlobal(event.pos()))
        if action == hide:
            self.hide_window()


def font_size_in_pixels(font_size_pt: int) -> int:

    dpi = app.primaryScreen().logicalDotsPerInch()  # 获取屏幕 DPI
    font_size_px = font_size_pt * (dpi / 72)  # 转换
    return font_size_px


# def get_required_point_coordinates(points_num: int, noise_level: float):
#    # 生成背景和边界QPainterPath所需路径
#    points = []
#    a, b = 0.5, 0.5
#    pi_2 = np.pi / 2
#    pi_3_2 = 3 * np.pi / 2
#    for i in range(points_num):
#        theta = (np.pi * 2.0 * i / points_num)
#        sin_theta = np.sin(theta)
#        cos_theta = np.cos(theta)
#        _len = (a * b) / np.power(np.power(a * sin_theta, 4) + np.power(b * cos_theta, 4), 0.25)
#        x = _len * cos_theta
#        y = _len * sin_theta
#        noise_x = 1 + (np.random.rand() * 2 - 1) * noise_level
#        noise_y = 1 + (np.random.rand() * 2 - 1) * noise_level
#        x *= noise_x
#        y *= noise_y
#        points.append((x, y))
#    if not points:
#        print("Warning: points list is empty")
#        return None
#    return points


def get_square_with_noise(round: int, noise_level: float):
    pi = 3.14159265
    points = []
    start_num = random.randint(1, 4)
    for _ in range(round):
        for i in range(12):
            current_angle = float(i + start_num * 3 - 2) % 12 * 2 * pi
            math.tan(current_angle)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = talkBubble()
    ex.show()
    sys.exit(app.exec_())
