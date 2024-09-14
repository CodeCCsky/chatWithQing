# -*- coding: utf-8 -*-
# import numpy as np
import random
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QFontMetrics, QPainter, QPen, QPainterPath, QTextCursor
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMenu, QWidget

import app.asset.res_rc
from app.GUI.opacity_controller import opacity_controller

#from opacity_controller import opacity_controller

TEXT_UPDATE_TIME = 200  # 毫秒


# 忘记做分离了 :(
class talkBubble(opacity_controller):
    HIDE_OPACITY = 0
    AWAIT_OPACITY = 0.3
    SHOW_OPACITY = 0.99

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.name_size = 24
        self.text_size = 16
        self.row_spacing = 2
        self.name_str = "晴"
        self.text_str = ""

        self.setup_opacity_controller()
        self.initUI()
        self.init_rand()

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
        self.horizontalLayout.setStretch(3, 25)
        self.horizontalLayout.setStretch(4, 8)
        self.verticalLayout.addWidget(self.widget)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)
        self.verticalLayout.setStretch(0, 5)
        self.verticalLayout.setStretch(1, 7)
        self.verticalLayout.setStretch(2, 4)
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

    """def init_window_opacity_control(self):
        self.keep_opacity_time = 100
        self.target_opacity = 0
        self.keep_opacity = False
        self.keep_opacity_timer = QTimer()
        self.keep_opacity_timer.timeout.connect(self.reset_keep_opacity)
        self.keep_opacity_timer.start(self.keep_opacity_time)
        self.window_opacity_timer = QTimer()
        self.window_opacity_timer.timeout.connect(self.window_opacity_control)
        self.window_opacity_timer.start(25)  # 25 毫秒更新一次窗口透明度"""

    def init_rand(self) -> None:
        self.update_rand()
        self.rand_timer = QTimer()
        self.rand_timer.timeout.connect(self.update_rand)
        self.rand_timer.start(500)

    def update_rand(self) -> None:
        self.border_round = 5
        self.points_of_path = []
        self.points_of_path.append(get_square_with_noise(self.width(), self.height(), 2, 0.01, 0.85))
        self.points_of_path.append(get_square_with_noise(self.width(), self.height(), self.border_round, 0.03, 0.87))
        self.update()

    def update_text(self, text, is_thinking: bool = False):
        self.set_opacity_mode(mode="normal")
        self._setTextLabel("晴", text, is_thinking)

    def clear_text(self):
        self._setTextLabel("晴", "")

    def _setTextLabel(self, name: str, text: str, is_thinking: bool = False) -> None:
        if len(text) >= 120:
            size = max(16 - int((len(text) - 120) / 50), 12)
            self.change_text_size(size)
            self.text_area.setFont(self.text_font)
        else:
            self.change_text_size(16)
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
        # 保持显示最后一行
        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_area.setTextCursor(cursor)
        self.text_area.ensureCursorVisible()
        self.adjustSize()

    def adjustSize(self) -> None:
        document = self.text_area.document()
        document.setTextWidth(self.text_area.width())
        document_height = document.size().height()
        window_width = self.width()
        self.text_area.setFixedHeight(min(int(document_height), 400))
        window_height = max(200, int(self.text_area.height() * 4 / 3))
        self.setFixedSize(window_width, window_height)
        self.update()

    def hide_window(self):
        self.set_opacity_mode(
            mode="hide", clear_keep_opacity_status=True, is_keep_opacity=True, lock_when_change=True, is_enforce=True
        )

    def show_window(self):
        self.set_opacity_mode(mode="normal", clear_keep_opacity_status=True, lock_when_change=True, is_enforce=True)

    def enterEvent(self, event):
        self.set_opacity_mode(mode="normal", clear_keep_opacity_status=True, is_keep_opacity=True)

    def leaveEvent(self, event):
        self.set_opacity_mode(mode="await", clear_keep_opacity_status=True, delay=3000)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景和边框
        # 背景
        bg_path = QPainterPath()
        bg_path.moveTo(
            self.points_of_path[0][1][0],
            self.points_of_path[0][1][1],
        )
        for i in range(0, 12, 3):
            p1 = self.points_of_path[0][i]
            p2 = self.points_of_path[0][i + 1]
            p3 = self.points_of_path[0][i + 2]
            bg_path.cubicTo(
                p1[0],
                p1[1],
                p2[0],
                p2[1],
                p3[0],
                p3[1],
            )
        bg_path.quadTo(
            self.points_of_path[0][0][0],
            self.points_of_path[0][0][1],
            self.points_of_path[0][1][0],
            self.points_of_path[0][1][1],
        )
        bg_path.closeSubpath()

        # 背景边缘线
        border_path = QPainterPath()
        border_path.moveTo(
            (self.points_of_path[1][1][0] + self.points_of_path[1][2][0]) / 2,
            (self.points_of_path[1][1][1] + self.points_of_path[1][2][1]) / 2,
        )
        for i in range(0, 12 * self.border_round, 3):
            p1 = self.points_of_path[1][i]
            p2 = self.points_of_path[1][i + 1]
            p3 = self.points_of_path[1][i + 2]
            border_path.cubicTo(
                p1[0],
                p1[1],
                p2[0],
                p2[1],
                p3[0],
                p3[1],
            )
        border_path.quadTo(
            self.points_of_path[1][0][0],
            self.points_of_path[1][0][1],
            self.points_of_path[1][1][0],
            self.points_of_path[1][1][1],
        )
        border_path.closeSubpath()

        # 绘画背景和边框
        painter.setPen(QPen(QColor(0, 0, 0, 220), 8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        # painter.setBrush(QBrush(QColor(0, 0, 0), Qt.SolidPattern))
        painter.fillPath(bg_path, QColor(0, 0, 0))
        # painter.setBrush(QBrush())
        painter.setPen(QPen(QColor(252, 58, 170, 255), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(border_path)

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


def get_square_with_noise(a: int, b: int, _round: int, noise_level: float, zoom_factor: float):
    points = []
    corner = [(a / 2, b / 2), (-a / 2, b / 2), (-a / 2, -b / 2), (a / 2, -b / 2)]
    start_num = random.randint(0, 3)
    for _ in range(_round):
        for cr in range(4):
            current_cr = (cr + start_num) % 4
            next_cr = (current_cr + 1) % 4
            for i in range(0, 3):
                noise_x = 1 + (random.random() * 2 - 1) * noise_level
                noise_y = 1 + (random.random() * 2 - 1) * noise_level
                x = (corner[current_cr][0] * (3 - i) / 3 + corner[next_cr][0] * i / 3) * noise_x * zoom_factor
                x = x + a / 2
                y = (corner[current_cr][1] * (3 - i) / 3 + corner[next_cr][1] * i / 3) * noise_y * zoom_factor
                y = y + b / 2
                points.append((x, y))
    return points


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = talkBubble()
    atimer = QTimer()
    atimer.singleShot(10 * 1000, lambda: ex.hide_window())
    ex.show()
    sys.exit(app.exec_())
