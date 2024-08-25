import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSoundEffect

from asset.GUI.PetView import PetGraphicsView
#from PetView import PetGraphicsView
import asset.GUI.res_rc
#import res_rc

class DesktopPet(QWidget):
    S_NORMAL = 0
    S_INTENSE = 1
    S_SURPRISE = 2
    S_EYE_HALF_CLOSED = 3
    S_EYE_CLOSE_NORMAL = 4
    S_EYE_CLOSE_DEPRESSED = 5
    S_EYE_CLOSE_SMILE = 6
    def __init__(self, parent: QWidget = None, use_tts:bool = False) -> None:
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
        self.init_mouse_click()

    def init_mouse_click(self):
        self.is_follow_mouse = False
        self.check_mouse_press_time = QTimer()
        self.check_mouse_press_time.timeout.connect(self.start_following_mouse)
        self.portraitView.mousePressEvent = self.onMousePress
        self.portraitView.mouseReleaseEvent = self.onMouseRelease
        self.portraitView.mouseMoveEvent = self.onMouseMove

    def init_subWindow(self) -> None:
        """初始化窗体
        窗口属性：无标题栏、保持在最上层、透明背景
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent; border: none;")
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.is_hide = True
        self.repaint()

    def init_pet_image(self):
        # 立绘的显示组件
        self.portraitView = PetGraphicsView(self)
        self.portraitView.setMinimumSize(300, 400)
        self.layout().addWidget(self.portraitView)
        screen = QDesktopWidget().screenGeometry()
        self.adjustSize()
        self.move(QPoint(int(screen.width()*0.95-self.width()), int(screen.height()*0.95-self.height())))

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'portraitView'):
            self.portraitView.setGeometry(self.rect())

    def contextMenuEvent(self, event):
        """右键菜单"""
        pet_menu = QMenu()
        pet_menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid #ff0084;
            }
            QMenu::item:selected {
                background-color: gray;
            }
        """)
        quit_action = pet_menu.addAction('退出')
        hide = pet_menu.addAction('隐藏')
        action = pet_menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            self.closeEvent(QCloseEvent())
        if action == hide:
            self.hide_window()

### 根据鼠标拖动方法（需手动重写组件的方法）
    def onMousePress(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos = self.pos()
            self.check_mouse_press_time.start(200)

    def onMouseRelease(self, event: QMouseEvent):
        # 释放时停止计时器、鼠标样式
        self.check_mouse_press_time.stop()
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.portraitView.unlock_facial_expr()
        self.portraitView.change_emo(self.facial_expr_state)
        if self.is_follow_mouse:
            self.is_follow_mouse = False

    def onMouseMove(self, event: QMouseEvent):
        # 更新移动时鼠标样式
        self.setCursor(QCursor(Qt.ClosedHandCursor))
        if self.is_follow_mouse:
            new_pos = self.window_pos + (event.globalPos() - self.mouse_press_pos)
            self.move(new_pos)

    def start_following_mouse(self):
        # 更新鼠标样式
        self.setCursor(QCursor(Qt.OpenHandCursor))
        #更新面部表情
        #self.facial_expr_state = self.S_EYE_CLOSE_DEPRESSED
        self.portraitView.change_emo(self.S_EYE_CLOSE_DEPRESSED, True)
        # 更新跟随鼠标状态
        self.is_follow_mouse = True
        # 停止计时器防止重复调用此函数
        self.check_mouse_press_time.stop()


if __name__ == '__main__' :
    
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())