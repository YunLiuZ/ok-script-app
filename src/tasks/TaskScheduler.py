"""任务编排器：按顺序执行选中的任务。"""
from src.tasks.BaseOmjTask import BaseOmjTask
from src.tasks.DailyTask import DailyTask
from src.tasks.AreaBossTask import AreaBossTask
from src.tasks.SoulZonesTask import SoulZonesTask
from src.tasks.GameEventsBattleTask import GameEventsBattleTask


class TaskScheduler(BaseOmjTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "任务编排"
        self.description = "按顺序执行日常任务"

        self.default_config.update({
            "任务列表": ["每日签到", "地域鬼王", "魂土"],
            "魂土模式": "单人",
        })

        self.config_description.update({
            "任务列表": "勾选要执行的任务，按列表顺序依次运行。",
            "魂土模式": "魂土任务使用的模式。",
        })

        self.config_type.update({
            "任务列表": {
                "type": "multi_selection",
                "options": ["每日签到", "地域鬼王", "魂土", "活动"],
            },
            "魂土模式": {
                "type": "drop_down",
                "options": ["队长", "队员", "单人"],
            },
        })

    def run(self):
        

        TASK_MAP = {
            "每日签到": DailyTask,
            "地域鬼王": AreaBossTask,
            "魂土": SoulZonesTask,
            "活动": GameEventsBattleTask,
        }

        for name in self.config["任务列表"]:
            task_cls = TASK_MAP.get(name)
            if task_cls is None:
                self.log_warning(f"未找到任务: {name}")
                continue

            self.log_info(f"--- 开始: {name} ---")
            t = task_cls(self.executor, self.scene)
            t.after_init(executor=self.executor, scene=self.scene)

            # 同步关键配置：魂土模式
            if name == "魂土":
                t.config["UserStatus"] = self.config["魂土模式"]

            t.run()
            self.log_info(f"--- 结束: {name} ---")
