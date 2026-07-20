from datetime import datetime

from src.tasks.BaseOmjTask import BaseOmjTask
from ok import TriggerTask , Logger
logger = Logger.get_logger(__name__)

class AutoLoginTask(TriggerTask, BaseOmjTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_config = {'_enabled': True}
        self.trigger_interval = 5
        self.count = 0
        self.name = "Auto Login"
        self.description = "Auto Login After Game Starts"

    def on_create(self):
        super().on_create()
        self._enabled = False
        self.logged_in = False  # 每次启动强制重置
        self.recovery_needed = False

    def run(self):
        if self.logged_in:
            self.log_info(f"{self.logged_in} logged in")
            print(self.logged_in)
            pass
        elif self.base_scene():
            self.logged_in = True
            self.recovery_needed = False
            self.onetime_failed =False
        else:
            while self.count < 10 and self.logged_in is False:
                self.count += 1
                if self.log_page():
                    return True
            self.count = 0
            self.restart_game()