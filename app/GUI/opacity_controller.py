from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget


class opacity_controller(QWidget):
    opacityModeChange = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def setup_opacity_controller(
        self,
        opacity_modes_list: dict = {"normal": 0.99, "await": 0.3, "hide": 0},
        opacity_mode_keep_time: dict = {"normal": 5 * 1000, "await": 30 * 1000, "hide": 60 * 1000},
        opacity_next_mode_list: dict = {"normal": "await", "await": "hide", "hide": "hide"},
        opacity_current_mode: str = "normal",
    ):
        self.opacity_update_time = 50
        self.opacity_update_delta = 0.1
        self.opacity_update_timer = QTimer()
        self.opacity_update_timer.timeout.connect(self._window_opacity_control)
        self.opacity_update_timer.start(self.opacity_update_time)

        self.opacity_modes_list = opacity_modes_list
        self.opacity_mode_keep_time = opacity_mode_keep_time
        self.opacity_next_mode_list = opacity_next_mode_list
        self.opacity_current_mode = opacity_current_mode

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
            self.setWindowOpacity(nxt_opacity)
            if (
                abs(self.windowOpacity() - self.opacity_modes_list[self.opacity_current_mode])
                < self.opacity_update_delta
            ):
                self.opacityModeChange.emit(self.opacity_current_mode)
                if self.keep_opacity_after_change:
                    self.keep_opacity = True
                    self.opacity_update_timer.stop()

    def _mode_change_control(self):
        self.opacity_change_timer.stop()
        self.opacity_current_mode = self.opacity_next_mode_list[self.opacity_current_mode]
        self.opacity_change_timer.start(self.opacity_mode_keep_time[self.opacity_current_mode])

    def set_keep_opacity(self, clear_status: bool, keep_opacity: bool):
        if clear_status:
            self.keep_opacity = False
        self.keep_opacity_after_change = keep_opacity

    def set_opacity_mode(
        self, mode: str, clear_keep_opacity_status: bool = False, is_keep_opacity: bool = False, delay: int = 0
    ):
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

    def _change_opacity(self, mode: str, clear_keep_opacity_status: bool, is_keep_opacity: bool):
        self.opacity_delay_timer.stop()
        self.set_keep_opacity(clear_keep_opacity_status, is_keep_opacity)
        self.opacity_current_mode = mode
        self.opacity_update_timer.start(self.opacity_update_time)
        self.opacity_change_timer.start(self.opacity_mode_keep_time[self.opacity_current_mode])
