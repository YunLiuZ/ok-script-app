from src.tasks.BaseOmjTask import BaseOmjTask
from ok import TriggerTask , Logger
logger = Logger.get_logger(__name__)

class AutoLoginTask(TriggerTask, BaseOmjTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_config = {'_enabled': True}
        self.trigger_interval = 5
        self.count = 1
        self.name = "Auto Login"
        self.description = "Auto Login After Game Starts"

    def on_create(self):
        super().on_create()
        self._enabled = True
        self.logged_in = False  # 每次启动强制重置

    def run(self):
        if self.logged_in:
            print(self.logged_in)
            pass
        elif self.base_scene():
            self.logged_in = True
        else:
            return self.log_page()
