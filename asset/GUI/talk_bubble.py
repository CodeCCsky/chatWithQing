import sys
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMenu
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QFontMetrics, QFontDatabase, QPolygon, QBrush
from PyQt5.QtCore import Qt, QPoint, QTimer
import numpy as np
import asset.GUI.res_rc
#import res_rc

TEXT_UPDATE_TIME = 100 # 毫秒

class talkBubble(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.name_size = 24
        self.text_size = 16
        self.row_spacing = 2
        self.name_str = '晴'
        self.text_str = ''

        self.initUI()
        self.init_rand()

    def initUI(self) -> None:
        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(':/font/荆南波波黑.ttf')
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(int(screen.width()*0.5-800/2),int(screen.height()*0.7),800,200)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setStyleSheet("background:transparent; border: none;")
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground)

        self.name_font = QFont("荆南波波黑",self.name_size, QFont.Bold)
        self.text_font = QFont("荆南波波黑",self.text_size)
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
        self.text_area.setFixedWidth(int(self.width()*27/42))
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

    def init_rand(self) -> None:
        self.update_rand()
        self.rand_timer = QTimer()
        self.rand_timer.timeout.connect(self.update_rand)
        self.rand_timer.start(500)

    def update_rand(self) -> None:
        #np.random.seed(self.randnum)
        self.points_num = int((self.width()+self.height())*1.6/50)
        self.points_of_path = []
        self.points_of_path.append(get_required_point_coordinates(self.points_num, 0.03))
        self.points_of_path.append(get_required_point_coordinates(self.points_num, 0.015))
        self.points_of_path.append(get_required_point_coordinates(self.points_num, 0.01))
        self.path_start_index = int((np.random.rand())*2*self.points_num) % self.points_num
        self.update()

    def update_text(self, text):
        self._setTextLabel('晴', text)

    def clear_text(self):
        self._setTextLabel('晴', '')

    def _setTextLabel(self, name, text) -> None:
        processed_text = '<p style=\"color: white;\">'
        #emph_flag = False # TODO 标记强调
        for char in text:
            if char == '\n':
                processed_text += '</p><p style=\"color: white;\">'
            else:
                processed_text += char
        processed_text += "</p>"
        self.name_str = name
        self.text_str = processed_text
        self.text_area.setHtml(self.text_str)
        self.adjustSize()

    def adjustSize(self) -> None:
        document = self.text_area.document()
        document_height = document.size().height()
        window_width = self.width()
        window_height = max(200,int(document_height*3/2))# TODO 自动调整高度
        self.setFixedSize(window_width, window_height)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景和边框
        window_width = self.width()
        window_height= self.height()
        # 背景
        bg_polygon_zoom_factor = 0.83
        bg_polygon = QPolygon([QPoint(int(x*window_width*bg_polygon_zoom_factor + window_width/2), int(y*window_height*bg_polygon_zoom_factor + window_height/2)) for x, y in self.points_of_path[0]])
        # 背景边缘线
        border_path = QPainterPath()
        border_zoom_factor = 0.87
        border_path.moveTo(self.points_of_path[1][self.path_start_index][0]*window_width*border_zoom_factor + window_width/2,
                           self.points_of_path[1][self.path_start_index][1]*window_height*border_zoom_factor + window_height/2)
        # 边框
        for i in range(self.path_start_index, self.points_num + self.path_start_index - 1, 3):
            p1 = self.points_of_path[1][i%self.points_num]
            p2 = self.points_of_path[1][(i + 1)%self.points_num]
            p3 = self.points_of_path[1][(i + 2)%self.points_num]
            border_path.cubicTo(p1[0]*window_width*border_zoom_factor + window_width/2,
                                p1[1]*window_height*border_zoom_factor + window_height/2,
                                p2[0]*window_width*border_zoom_factor + window_width/2,
                                p2[1]*window_height*border_zoom_factor + window_height/2,
                                p3[0]*window_width*border_zoom_factor + window_width/2,
                                p3[1]*window_height*border_zoom_factor + window_height/2)
        border_zoom_factor = 0.9
        for i in range(self.path_start_index, self.points_num + self.path_start_index - 1, 3):
            p1 = self.points_of_path[2][i%self.points_num]
            p2 = self.points_of_path[2][(i + 1)%self.points_num]
            p3 = self.points_of_path[2][(i + 2)%self.points_num]
            border_path.cubicTo(p1[0]*window_width*border_zoom_factor + window_width/2,
                                p1[1]*window_height*border_zoom_factor + window_height/2,
                                p2[0]*window_width*border_zoom_factor + window_width/2,
                                p2[1]*window_height*border_zoom_factor + window_height/2,
                                p3[0]*window_width*border_zoom_factor + window_width/2,
                                p3[1]*window_height*border_zoom_factor + window_height/2)
        # 绘画背景和边框
        painter.setPen(QPen(QColor(0, 0, 0, 210), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QBrush(QColor(0, 0, 0), Qt.SolidPattern))
        painter.drawPolygon(bg_polygon)
        painter.setBrush(QBrush())
        painter.setPen(QPen(QColor(252, 58, 170, 255), 8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
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
        self.name_font = QFont("荆南波波黑",self.name_size, QFont.Bold)
    def change_text_size(self, size: int) -> None:
        self.text_size = size
        self.text_font = QFont("荆南波波黑",self.text_size)
        self.text_fm = QFontMetrics(self.text_font)
    def change_row_spacing(self, height: int) -> None:
        self.row_spacing = height

    def contextMenuEvent(self, event):
        """右键菜单"""
        talk_bubble_menu = QMenu()
        talk_bubble_menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid #ff0084;
            }
            QMenu::item:selected {
                background-color: gray;
            }
        """)
        hide = talk_bubble_menu.addAction('隐藏')
        action = talk_bubble_menu.exec_(self.mapToGlobal(event.pos()))
        if action == hide:
            self.setWindowOpacity(0)


def font_size_in_pixels(font_size_pt: int) -> int:
    
    dpi = app.primaryScreen().logicalDotsPerInch()  # 获取屏幕 DPI
    font_size_px = font_size_pt * (dpi / 72) # 转换
    return font_size_px

def get_required_point_coordinates(points_num: int, noise_level: float):
    # 生成背景和边界QPainterPath所需路径
    points = []
    a, b = 0.5, 0.5
    pi_2 = np.pi / 2
    pi_3_2 = 3 * np.pi / 2
    for i in range(points_num):
        theta = (np.pi * 2.0 * i / points_num)
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        _len = (a * b) / np.power(np.power(a * sin_theta, 4) + np.power(b * cos_theta, 4), 0.25)
        x = _len * cos_theta
        y = _len * sin_theta
        noise_x = 1 + (np.random.rand() * 2 - 1) * noise_level
        noise_y = 1 + (np.random.rand() * 2 - 1) * noise_level
        x *= noise_x
        y *= noise_y
        points.append((x, y))
    if not points:
        print("Warning: points list is empty")
        return None
    return points


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = talkBubble()
    ex.show()
    sys.exit(app.exec_())