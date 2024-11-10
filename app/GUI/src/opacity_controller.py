from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget


class opacity_controller(QWidget):
    opacityModeChange = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def setup_opacity_controller(
        self,
        opacity_modes_list: dict = {"normal": 0.99, "await": 0.3, "hide": 0},
        opacity_mode_keep_time: dict = {
            "normal": 6 * 1000,
            "await": 22 * 1000,
            "hide": 60 * 1000,
        },
        opacity_next_mode_list: dict = {
            "normal": "await",
            "await": "hide",
            "hide": "hide",
        },
        opacity_current_mode: str = "normal",
    ):
        self.opacity_update_time = 25
        self.opacity_update_delta = 0.1
        self.opacity_update_timer = QTimer()
        self.opacity_update_timer.timeout.connect(self._window_opacity_control)
        self.opacity_update_timer.start(self.opacity_update_time)

        self.opacity_modes_list = opacity_modes_list
        self.opacity_mode_keep_time = opacity_mode_keep_time
        self.opacity_next_mode_list = opacity_next_mode_list
        self.opacity_current_mode = opacity_current_mode
        self.opacity_mode_change_lock = False

        self.opacity_delay_timer = QTimer()

        self.opacity_change_timer = QTimer()
        self.opacity_change_timer.timeout.connect(self._mode_change_control)
        self.keep_opacity = False
        self.keep_opacity_after_change = False

        self.opacity_change_timer.start(self.opacity_mode_keep_time[self.opacity_current_mode])

    def _window_opacity_control(self):
        if not self.keep_opacity:
            nxt_opacity = self.opacity_modes_list[self.opacity_current_mode]
            if self.windowOpacity() - self.opacity_update_delta > nxt_opacity:
                nxt_opacity = self.windowOpacity() - self.opacity_update_delta
            elif self.windowOpacity() + self.opacity_update_delta < nxt_opacity:
                nxt_opacity = self.windowOpacity() + self.opacity_update_delta
            if (
                abs(self.windowOpacity() - self.opacity_modes_list[self.opacity_current_mode])
                < self.opacity_update_delta
            ):
                self.opacityModeChange.emit(self.opacity_current_mode)
                self.opacity_mode_change_lock = False
                if self.keep_opacity_after_change:
                    self.keep_opacity = True
                    self.opacity_update_timer.stop()
            self.setWindowOpacity(nxt_opacity)

    def _mode_change_control(self) -> None:
        if self.opacity_mode_change_lock:
            return None
        self.opacity_change_timer.stop()
        self.opacity_current_mode = self.opacity_next_mode_list[self.opacity_current_mode]
        self.opacity_change_timer.start(self.opacity_mode_keep_time[self.opacity_current_mode])

    def set_keep_opacity(self, clear_status: bool, keep_opacity: bool) -> None:
        if clear_status:
            self.keep_opacity = False
        self.keep_opacity_after_change = keep_opacity

    def set_opacity_mode(
        self,
        mode: str,
        clear_keep_opacity_status: bool = False,
        is_keep_opacity: bool = False,
        lock_when_change: bool = False,
        is_enforce: bool = False,
        delay: int = 0,
    ) -> bool:
        """调整窗口透明度模式. 当有加锁的更改进行时会失败.

        Args:
            mode (str): 指定的窗口透明度模式
            clear_keep_opacity_status (bool, optional): 清除上一次设置窗口透明度模式时设置的keep_opacity(无论有没有设置). Defaults to False.
            is_keep_opacity (bool, optional): 设置是否保持当前设置的窗口透明度模式. Defaults to False.
            lock_when_change (bool, optional): 设置这次窗口透明度模式更改是否加锁(不能别的更改打断). Defaults to False.
            is_enforce (bool, optional): 设置是否强制更改窗口透明度模式(设置加锁为False). Defaults to False.
            delay (int, optional): 设置窗口透明度模式在一定延迟后开始更改. 单位为毫秒. Defaults to 0.

        Returns:
            bool: 返回当前更改是否被成功应用. 成功返回 True, 失败返回 False.
        """
        if is_enforce:
            self.opacity_mode_change_lock = False
        if self.opacity_mode_change_lock:
            return False
        self.opacity_mode_change_lock = lock_when_change
        self.opacity_delay_timer.stop()
        if delay > 0:
            if self.opacity_delay_timer.receivers(self.opacity_delay_timer.timeout) > 0:
                self.opacity_delay_timer.timeout.disconnect()
            self.opacity_delay_timer.timeout.connect(
                lambda: self._change_opacity(mode, clear_keep_opacity_status, is_keep_opacity)
            )
            self.opacity_delay_timer.start(delay)
        else:
            self._change_opacity(mode, clear_keep_opacity_status, is_keep_opacity)
        return True

    def _change_opacity(self, mode: str, clear_keep_opacity_status: bool, is_keep_opacity: bool):
        self.opacity_delay_timer.stop()
        self.set_keep_opacity(clear_keep_opacity_status, is_keep_opacity)
        self.opacity_current_mode = mode
        self.opacity_update_timer.start(self.opacity_update_time)
        self.opacity_change_timer.start(self.opacity_mode_keep_time[self.opacity_current_mode])

    def hide_window(self):
        self.set_opacity_mode(
            mode="hide",
            clear_keep_opacity_status=True,
            is_keep_opacity=True,
            lock_when_change=True,
            is_enforce=True,
        )

    def show_window(self):
        self.set_opacity_mode(
            mode="normal",
            clear_keep_opacity_status=True,
            lock_when_change=True,
            is_enforce=True,
        )

    def enterEvent(self, event):
        self.set_opacity_mode(mode="normal", clear_keep_opacity_status=True, is_keep_opacity=True)

    def leaveEvent(self, event):
        if self.opacity_current_mode != "hide":
            self.set_opacity_mode(mode="await", clear_keep_opacity_status=True, delay=3000)
