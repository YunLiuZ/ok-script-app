import re

from src.tasks.BaseBattleTask import BaseBattleTask

class BuffBattleTask(BaseBattleTask):
    BUFF_NAMES = ["觉醒", "御魂", "金币增加100", "经验增加100", "经验增加50"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_config.update({
            "加成选择": [],
            "优先搜索": "最近",
        })

        self.config_description.update({
            "加成选择": "选择需要打开的加成，不选则不开任何加成。",
            "优先搜索": "邀请好友时优先查看哪个标签页（最近/好友/跨区/寮友）。",
        })

        self.config_type.update({
            "加成选择": {
                "type": "multi_selection",
                "options": self.BUFF_NAMES.copy(),
            },
            "优先搜索": {
                "type": "drop_down",
                "options": ["最近", "好友", "跨区", "寮友"],
            },
        })