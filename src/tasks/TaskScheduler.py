"""任务编排器：勾选任务，数字越小越先执行（1-30，不可重复）。"""
from src.tasks.BaseOmjTask import BaseOmjTask
from src.tasks.DailyTask import DailyTask
from src.tasks.ExplorationTask import ExplorationTask
from src.tasks.DelegationTask import DelegationTask
from src.tasks.SoulZonesTask import SoulZonesTask
from src.tasks.AreaBossTask import AreaBossTask
from src.tasks.RealmRaidTask import RealmRaidTask
from src.tasks.GameEventsBattleTask import GameEventsBattleTask
from src.tasks.UtilizeTask import UtilizeTask


class TaskScheduler(BaseOmjTask):

    TASK_MAP = {
        "每日签到": DailyTask,
        "困28": ExplorationTask,
        "式神委派": DelegationTask,
        "魂土": SoulZonesTask,
        "地域鬼王": AreaBossTask,
        "RealmRaid": RealmRaidTask,
        "活动": GameEventsBattleTask,
        "Utilize": UtilizeTask,
    }

    ALL_TASKS = [
        "每日签到", "困28", "式神委派", "魂土",
        "地域鬼王", "个人突破", "活动", "结界",
    ]

    # 默认顺序
    DEFAULT_ORDER = {name: i + 1 for i, name in enumerate(ALL_TASKS)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "任务编排"
        self.description = "按数字顺序执行日常任务（数字越小越先执行）"

        self.default_config.update({
            "任务列表": self.ALL_TASKS.copy(),
        })
        # 每个任务的顺序数字（1-30）
        for name in self.ALL_TASKS:
            self.default_config[f"{name}顺序"] = self.DEFAULT_ORDER[name]

        self.config_description.update({
            "任务列表": "勾选要执行的任务。",
        })

        self.config_type.update({
            "任务列表": {
                "type": "multi_selection",
                "options": self.ALL_TASKS.copy(),
            },
        })

    def run(self):
        enabled = self.config.get("任务列表", [])

        # 收集 (顺序, 名称)
        tasks_to_run = []
        for name in enabled:
            order = self.config.get(f"{name}顺序", 99)
            tasks_to_run.append((order, name))

        # 检查顺序重复
        orders = [o for o, _ in tasks_to_run]
        if len(orders) != len(set(orders)):
            dupes = [o for o in orders if orders.count(o) > 1]
            self.log_warning(f"任务顺序有重复: {set(dupes)}，请确保每个数字只用一次！")

        # 按数字排序
        tasks_to_run.sort(key=lambda x: x[0])

        for order, name in tasks_to_run:
            task_cls = self.TASK_MAP.get(name)
            if task_cls is None:
                self.log_warning(f"未找到任务: {name}")
                continue

            self.log_info(f"--- [{order}] 开始: {name} ---")
            t = task_cls(self.executor, self.scene)
            t.after_init(executor=self.executor, scene=self.scene)

            t.run()
            self.log_info(f"--- [{order}] 结束: {name} ---")
