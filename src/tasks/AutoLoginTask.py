import json
import os
import re
from datetime import datetime, timedelta
from src.tasks.BaseOmjTask import BaseOmjTask
from ok import TriggerTask , Logger
from ok.util.config import Config
logger = Logger.get_logger(__name__)
class AutoLoginTask(TriggerTask,BaseOmjTask):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.default_config = {'_enabled': True}
        self.trigger_interval = 5
        self.name = "Auto Login"
        self.description = "Auto Login After Game Starts"
    def run(self):
        if self.logged_in:
            pass
        elif self.base_scene():
            self.logged_in = True
        else:
            return self.log_page()