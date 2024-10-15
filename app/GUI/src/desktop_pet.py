import sys
import time

from PyQt5.QtCore import QObject, QPoint, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QCursor, QMouseEvent, QPolygon, QPolygonF
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMenu, QVBoxLayout, QWidget


# from pet_view import PetGraphicsView
import app.asset.res_rc
from app.GUI.src.pet_view import PetGraphicsView

# import res_rc


class strokeArea(QObject):
    stroked_area_signal = pyqtSignal(int)
    check_time = 1500
    BASIC_WIDTH = 300
    BASIC_HEIGHT = 400

    # TODO 将坐标换为相对窗口的坐标
    def __init__(self, width: int, height: int, parent=None) -> None:
        super().__init__()
        self.init_poly(width, height)
        self.init_timer()
        self.init_calc_dis()

    def init_poly(self, width: int, height: int) -> None:
        self.head = [
            (0, 125),
            (250, 40),
            (300, 140),
            (175, 170),
            (175, 195),
            (80, 220),
            (75, 200),
            (0, 210),
        ]
        head_point = [
            QPoint(
                int(x * (width / self.BASIC_WIDTH)),
                int(y * (height / self.BASIC_HEIGHT)),
            )
            for x, y in self.head
        ]
        self.head_poly = QPolygon(head_point)

        self.carrot = [(175, 170), (200, 165), (200, 190), (175, 195)]
        carrot_point = [
            QPoint(
                int(x * (width / self.BASIC_WIDTH)),
                int(y * (height / self.BASIC_HEIGHT)),
            )
            for x, y in self.carrot
        ]
        self.carrot_poly = QPolygon(carrot_point)

        self.hair_l = [(0, 211), (75, 200), (90, 305), (55, 355)]
        hair_l_point = [
            QPoint(
                int(x * (width / self.BASIC_WIDTH)),
                int(y * (height / self.BASIC_HEIGHT)),
            )
            for x, y in self.hair_l
        ]
        self.hair_l_poly = QPolygon(hair_l_point)

        self.hair_r = [
            (200, 165),
            (207, 238),
            (231, 256),
            (209, 283),
            (225, 305),
            (300, 315),
            (300, 140),
        ]
        hair_r_point = [
            QPoint(
                int(x * (width / self.BASIC_WIDTH)),
                int(y * (height / self.BASIC_HEIGHT)),
            )
            for x, y in self.hair_r
        ]
        self.hair_r_poly = QPolygon(hair_r_point)

        self.face = [
            (80, 220),
            (200, 192),
            (207, 238),
            (178, 276),
            (134, 290),
            (90, 265),
        ]
        face_point = [
            QPoint(
                int(x * (width / self.BASIC_WIDTH)),
                int(y * (height / self.BASIC_HEIGHT)),
            )
            for x, y in self.face
        ]
        self.face_poly = QPolygon(face_point)

    def resize_poly(self, width: int, height: int):
        self.init_poly(width, height)
        self.init_calc_dis()

    def init_timer(self):
        self.last_time = time.time()
        self.lst_time_is_rcd = True
        self.stroke_timer = QTimer()
        self.stroke_timer.timeout.connect(self.check_dis)
        self.stroke_timer.start(self.check_time)

    def init_calc_dis(self):
        self.extent = [
            self.polygon_area(self.head_poly),
            self.polygon_area(self.carrot_poly),
            self.polygon_area(self.hair_l_poly),
            self.polygon_area(self.hair_r_poly),
            self.polygon_area(self.face_poly),
        ]
        self.dis = [0.0 for _ in range(5)]
        self.last_point = [QPoint(0, 0) for _ in range(5)]

    def calc_dis(self, event: QMouseEvent):
        current_area = self.check_current_pos(event)
        pos = event.pos()
        if current_area is not None:
            for i in range(5):
                if i != current_area:
                    self.last_point[i] = QPoint(0, 0)
                elif self.last_point[i].isNull() is False:
                    last_pos = self.last_point[i]
                    dis = pow(
                        (pow((pos.x() - last_pos.x()), 2) + pow((pos.y() - last_pos.y()), 2)),
                        0.5,
                    )
                    self.dis[i] += dis
                    self.last_point[i] = pos
                else:
                    self.last_point[i] = pos

    def check_dis(self):
        self.stroke_timer.stop()
        self.lst_time_is_rcd = False
        current_time = time.time()
        max_rate = 0
        max_index = 0
        for i in range(5):
            move_rate = pow(self.dis[i], 2) / self.extent[i] / (current_time - self.last_time)
            if move_rate > max_rate:
                max_rate = move_rate
                max_index = i
        if current_time - self.last_time < 2.0 or max_rate < 5.0:
            return None
        self.stroked_area_signal.emit(max_index)
        self.dis = [0.0 for _ in range(5)]
        self.last_time = time.time()

    def check_current_pos(self, event: QMouseEvent):
        pos = event.pos()
        if self.head_poly.containsPoint(pos, Qt.OddEvenFill):
            self.stroke_timer.start()
            if self.lst_time_is_rcd is False:
                self.last_time = time.time()
            self.lst_time_is_rcd = True
            return 0
        elif self.carrot_poly.containsPoint(pos, Qt.OddEvenFill):
            self.stroke_timer.start()
            if self.lst_time_is_rcd is False:
                self.last_time = time.time()
            self.lst_time_is_rcd = True
            return 1
        elif self.hair_l_poly.containsPoint(pos, Qt.OddEvenFill):
            self.stroke_timer.start()
            if self.lst_time_is_rcd is False:
                self.last_time = time.time()
            self.lst_time_is_rcd = True
            return 2
        elif self.hair_r_poly.containsPoint(pos, Qt.OddEvenFill):
            self.stroke_timer.start()
            if self.lst_time_is_rcd is False:
                self.last_time = time.time()
            self.lst_time_is_rcd = True
            return 3
        elif self.face_poly.containsPoint(pos, Qt.OddEvenFill):
            self.stroke_timer.start()
            if self.lst_time_is_rcd is False:
                self.last_time = time.time()
            self.lst_time_is_rcd = True
            return 4
        else:
            return None

    @staticmethod
    def polygon_area(polygon: QPolygon):
        polygon = QPolygonF(polygon)
        n = polygon.size()
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += polygon[i].x() * polygon[j].y()
            area -= polygon[j].x() * polygon[i].y()
        area = abs(area) / 2.0
        return area


class DesktopPet(QWidget):
    S_NORMAL = 0
    S_INTENSE = 1
    S_SURPRISE = 2
    S_EYE_HALF_CLOSED = 3
    S_EYE_CLOSE_NORMAL = 4
    S_EYE_CLOSE_DEPRESSED = 5
    S_EYE_CLOSE_SMILE = 6

    def __init__(self, parent: QWidget = None, use_tts: bool = False) -> None:
        super().__init__(parent)
        self.init_subWindow()
        self.use_tts = use_tts

        # 垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.is_speaking = False
        self.facial_expr_state = self.S_NORMAL
        self.init_pet_image()
        self.init_mouse_event()

    def init_mouse_event(self):
        self.is_follow_mouse = False
        self.check_mouse_press_timer = QTimer()
        self.check_mouse_press_timer.timeout.connect(self.start_following_mouse)
        self.portraitView.mousePressEvent = self.onMousePress
        self.portraitView.mouseReleaseEvent = self.onMouseRelease
        self.portraitView.mouseMoveEvent = self.onMouseMove
        self.stroke_area = strokeArea(self.width(), self.height())

    def init_subWindow(self) -> None:
        """初始化窗体
        窗口属性：无标题栏、保持在最上层、透明背景
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent; border: none;")
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setMouseTracking(True)
        self.is_hide = True
        self.repaint()

    def init_pet_image(self):
        """初始化立绘(?)组件"""
        self.portraitView = PetGraphicsView(self)
        self.portraitView.setMinimumSize(150, 200)
        self.portraitView.setMouseTracking(True)
        self.layout().addWidget(self.portraitView)
        screen = QDesktopWidget().screenGeometry()
        self.adjustSize()
        self.move(
            QPoint(
                int(screen.width() * 0.95 - self.width()),
                int(screen.height() * 0.95 - self.height()),
            )
        )

    def show_window(self):
        self.is_hide = False
        self.setWindowOpacity(0.99)

    def hide_window(self):
        self.is_hide = True
        self.setWindowOpacity(0)

    def set_speak(self):
        self.portraitView.set_speak()

    def stop_speak(self):
        self.portraitView.stop_speak()

    def change_emo(self, index: int, force_update: bool = False) -> None:
        if self.facial_expr_state != index or force_update:
            self.facial_expr_state = index
            if self.facial_expr_state == self.S_NORMAL:
                self.portraitView.unlock_facial_expr()
                self.portraitView.change_emo(index=index)
            else:
                self.portraitView.unlock_facial_expr()
                self.portraitView.change_emo(index=index, add_lock=True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "portraitView"):
            self.portraitView.setGeometry(self.rect())
        self.stroke_area.resize_poly(self.width(), self.height())

    def contextMenuEvent(self, event):
        """右键菜单"""
        # 重置摸头模块, 防止误判
        self.stroke_area.init_calc_dis()
        self.stroke_area.init_timer()
        pet_menu = QMenu()
        pet_menu.setStyleSheet(
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
        quit_action = pet_menu.addAction("退出")
        hide = pet_menu.addAction("隐藏")
        action = pet_menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            self.closeEvent(QCloseEvent())
        if action == hide:
            self.hide_window()

    ### 根据鼠标拖动方法 (需手动重写组件的方法)
    def onMousePress(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos = self.pos()
            self.check_mouse_press_timer.start(200)

    def onMouseRelease(self, event: QMouseEvent):
        # 释放时停止计时器、鼠标样式
        self.check_mouse_press_timer.stop()
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.change_emo(self.facial_expr_state)
        if self.is_follow_mouse:
            self.is_follow_mouse = False

    def onMouseMove(self, event: QMouseEvent):
        if self.is_follow_mouse:
            # 拖动时
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            new_pos = self.window_pos + (event.globalPos() - self.mouse_press_pos)
            self.move(new_pos)
            # 重置摸头模块 (总不可能边拖动边摸头吧..)
            self.stroke_area.init_calc_dis()
            self.stroke_area.init_timer()
        else:
            # 摸头模块计算
            self.stroke_area.calc_dis(event)
            self.portraitView.progress_stroke()
            self.facial_expr_state = self.S_NORMAL

    def start_following_mouse(self):
        # 更新鼠标样式
        self.setCursor(QCursor(Qt.OpenHandCursor))
        # 更新面部表情
        self.change_emo(self.S_EYE_CLOSE_DEPRESSED)
        # 更新跟随鼠标状态
        self.is_follow_mouse = True
        # 停止计时器防止重复调用此函数
        self.check_mouse_press_timer.stop()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())
