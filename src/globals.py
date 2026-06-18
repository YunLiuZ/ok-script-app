import os

from PySide6.QtCore import QObject

from ok import Logger, get_path_relative_to_exe

logger = Logger.get_logger(__name__)


class Globals(QObject):

    def __init__(self, exit_event):
        super().__init__()
        self.logged_in = False  # 登录状态

        from src.state import StateManager
        self.state = StateManager(
            get_path_relative_to_exe(os.path.join("configs", "daily_state.json"))
        )

