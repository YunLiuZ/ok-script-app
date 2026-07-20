import re

from src.tasks.BaseOmjTask import BaseOmjTask
from src.tasks.BaseBattleTask import BaseBattleTask

class DemonEncounter(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "封魔之时"
        self.default_config.update({
            "Monday": "",
            "Tuesday": "",
            "Wednesday": "",
            "Thursday": "",
            "Friday": "",
            "Saturday": "",
            "Sunday": "",
        })
        self.config_description.update({
            "Monday": "每天的队伍",
        })
    def run(self):
        pass
    