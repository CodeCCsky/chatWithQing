import sys
import random
from typing import Literal
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import app.asset.res_rc
#import res_rc

blink_time_list = [7000,100,200,100]

class PetGraphicsView(QGraphicsView):
    EYE_NORMAL = 0
    EYE_INTENSE = 1
    EYE_SURPRISE = 2
    EYE_HALF_CLOSED = 3
    EYE_CLOSE_NORMAL = 4
    EYE_CLOSE_DEPRESSED = 5
    EYE_CLOSE_SMILE = 6
    REFRESH_TIME = 400 # 刷新时间
    speak_gap = 150 # 说话状态嘴部切换时间
    stroke_upd_time = 600 # 摸头表情重置时间
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background:transparent; border: none;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.init_resources()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(Qt.transparent)

        self.show_state = {
            'body': 0,
            'eyes': self.EYE_NORMAL,
            'mouth' : 0,
            'hand': 0
        }

        self.parts = {
            'body': self.body,
            'eyes': self.eyes,
            'mouth' : self.mouth_say,
            'hand': self.hand
        }

        self.img_items = {
            'body': QGraphicsPixmapItem(self.parts['body'][self.show_state['body']][0]),
            'eyes': QGraphicsPixmapItem(self.parts['eyes'][self.show_state['eyes']][0]),
            'mouth': QGraphicsPixmapItem(self.parts['mouth'][self.show_state['mouth']][0]),
            'hand': QGraphicsPixmapItem(self.parts['hand'][self.show_state['hand']][0])
        }

        self.positions = {
            'body': (0, 0),
            'eyes': (200, 600),
            'mouth' : (535,995),
            'hand': (300, 890)
        }

        self.current_indices = {
            'body': 0,
            'eyes': 0,
            'mouth': 0,
            'hand': 0
        }

        for part, item in self.img_items.items():
            item.setPos(*self.positions[part])
            self.scene.addItem(item)
        self.img_items['mouth'].setVisible(False)

        #表情锁定，防止在播放一个表情时和另一个表情冲突
        self.facial_lock = False

        self.img_items['body'].setZValue(1)
        self.img_items['eyes'].setZValue(2)
        self.img_items['mouth'].setZValue(3)
        self.img_items['hand'].setZValue(4)

        self.timers = {
            'body' : QTimer(),
            'eyes' : QTimer(),
            'mouth' : QTimer(),
            'hand' : QTimer()
        }
        # 说话时长倒计时
        self.speak_time = QTimer()
        self.speak_time.timeout.connect(self.stop_speak)
        # 退出摸头表情倒计时
        self.stroke_timer = QTimer()
        self.stroke_timer.timeout.connect(self.stop_stroke)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.progress_blink)
        self.blink_index = 0
        self.blink_timer.start(blink_time_list[self.blink_index])

        self.set_image_change_timer()

        self.resizeEvent(None)

    def init_resources(self) -> None:
        self.eyes = (
            (   # normal - 0
                QPixmap(':/image/eye-1a.png'),
                QPixmap(':/image/eye-1b.png')
            ),
            (   # intense - 1
                QPixmap(':/image/eye-2a.png'),
                QPixmap(':/image/eye-2b.png')
            ),
            (   # surprise - 2
                QPixmap(':/image/eye-4a.png'),
                QPixmap(':/image/eye-4b.png')
            ),
            (   # half_closed - 3
                QPixmap(':/image/eye-12a.png'),
                QPixmap(':/image/eye-12b.png')
            ),
            (   # close_normal - 4
                QPixmap(':/image/eye-13a.png'),
            ),
            (   # close_with_depress - 5
                QPixmap(':/image/eye-3a.png'),
            ),
            (   # close_with_smile - 6
                QPixmap(':/image/eye-5a.png'),
                QPixmap(':/image/eye-5b.png')
            )
        )
        self.mouth_say = ((
            QPixmap(':/image/say-1.png'), 
            QPixmap(':/image/say-2.png'),
            QPixmap(':/image/say-3.png'),
            QPixmap(':/image/say-4.png')
        ),)
        self.hand = ((
            QPixmap(':/image/hand-a.png'),
            QPixmap(':/image/hand-b.png')
        ),)
        self.body = ((
            QPixmap(':/image/body-a.png'),
            QPixmap(':/image/body-b.png')
        ),)

    ### 以下三个方法控制除嘴部之外的部件的更新状态
    def set_image_change_timer(self) -> None:
        for part, timer in self.timers.items():
            if part != 'mouth':
                timer.timeout.connect(lambda p=part: self.update_animation(p))
                timer.start(self.REFRESH_TIME)
        self.timers['mouth'].timeout.connect(lambda p='mouth': self.update_animation(p))

    def restart_image_change_timer(self) -> None:
        for part, timer in self.timers.items():
            if part != 'mouth':
                timer.start(self.REFRESH_TIME)

    def stop_image_change_timer(self) -> None:
        for part, timer in self.timers.items():
            if part != 'mouth':
                timer.stop()
    ###
    def progress_stroke(self):
        self.blink_index = -1
        self.change_emo(self.EYE_CLOSE_SMILE)
        self.stroke_timer.start(self.stroke_upd_time)

    def stop_stroke(self):
        self.stroke_timer.stop()
        self.blink_index = 3
        self.progress_blink()

    def progress_blink(self):
        if self.blink_index == -1:
            return None
        self.blink_index = (self.blink_index + 1) % 4
        if self.blink_index == 0:
            blink_time_list[self.blink_index] = random.randint(6000,10000)
            self.change_emo(self.EYE_NORMAL)
        elif self.blink_index == 1:
            self.change_emo(self.EYE_HALF_CLOSED)
        elif self.blink_index == 2:
            self.change_emo(self.EYE_CLOSE_NORMAL)
        else:
            self.change_emo(self.EYE_HALF_CLOSED)
        self.blink_timer.start(blink_time_list[self.blink_index])


    ###
    def update_animation(self, part: str) -> None:
        """更新组件"""
        current_index = self.current_indices[part]
        next_index = (current_index + 1) % len(self.parts[part][self.show_state[part]])
        self.img_items[part].setPixmap(self.parts[part][self.show_state[part]][next_index])
        self.current_indices[part] = next_index

    def change_emo(self, index: int, add_lock: bool = False) -> bool:
        """切换眼部（面部表情？），只有在未上锁时才能生效

        Args:
            index (int): 表情编号
            add_lock (bool): 是否要给当前表情加锁（注意，只有未上锁时才能生效）. Defaults to False.

        Returns:
            bool: 返回是否成功切换表情
        """
        if self.facial_lock is False:
            #self.stop_image_change_timer()
            self.show_state['eyes'] = index
            self.current_indices['eyes'] = 0
            self.img_items['eyes'].setPixmap(
                self.parts['eyes'][self.show_state['eyes']][self.current_indices['eyes']])
            #self.restart_image_change_timer()
        else :
            return False
        self.facial_lock = add_lock
        return True

    def unlock_facial_expr(self) -> None:
        self.facial_lock = False

    def set_speak(self, keep_time : int = -1) -> None:
        """设置说话动作时长
        Args:
            keep_time (int, optional): 说话动作时长，单位为**毫秒**。默认为-1时为保持显示说话动作. Defaults to -1.
        """
        self.stop_image_change_timer()
        if keep_time == -1:
            self.timers['mouth'].start(self.speak_gap)
        elif keep_time >= 0:
            self.timers['mouth'].start(self.speak_gap)
            self.speak_time.start(keep_time)
        else :
            print(f"illegal value of 'keep_time': {keep_time}")# TODO logging
        self.img_items['mouth'].setVisible(True)
        self.restart_image_change_timer()

    def stop_speak(self):
        """停止说话动作"""
        self.speak_time.stop()
        self.timers['mouth'].stop()
        self.img_items['mouth'].setVisible(False)

    def resizeEvent(self, event):
        """让所有立绘部分跟随组件缩放"""
        scale_factor = min(self.width() / self.parts['body'][self.show_state['body']][self.current_indices['body']].width(), self.height() / self.parts['body'][self.show_state['body']][self.current_indices['body']].height())
        for part, item in self.img_items.items():
            item.setScale(scale_factor)
            item.setPos(self.positions[part][0] * scale_factor, self.positions[part][1] * scale_factor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = PetGraphicsView()
    pet.show()
    sys.exit(app.exec_())
