import os

from PySide6.QtCore import QObject

from ok import Logger, get_path_relative_to_exe

logger = Logger.get_logger(__name__)

# ── 全局任务注册（新增任务只改这里）──
from src.tasks.DailyTask import DailyTask
from src.tasks.ExplorationTask import ExplorationTask
from src.tasks.DelegationTask import DelegationTask
from src.tasks.SoulZonesTask import SoulZonesTask
from src.tasks.AreaBossTask import AreaBossTask
from src.tasks.RealmRaidTask import RealmRaidTask
from src.tasks.GameEventsBattleTask import GameEventsBattleTask
from src.tasks.UtilizeTask import UtilizeTask
from src.tasks.OrchidsTask import OrchidsTask

TASK_MAP = {
    "日常-签到": DailyTask,
    "日常-式神委派": DelegationTask,
    "日常-结界": UtilizeTask,
    "日常-同心之兰": OrchidsTask,
    "日常-战斗-地域鬼王": AreaBossTask,
    "日常-战斗-个人突破": RealmRaidTask,
    "战斗-魂土": SoulZonesTask,
    "战斗-困28": ExplorationTask,
    "战斗-活动": GameEventsBattleTask,
}

ALL_TASK_NAMES = list(TASK_MAP.keys())


class Globals(QObject):

    def __init__(self, exit_event):
        super().__init__()
        self.logged_in = False      # 登录状态
        self.onetime_failed = False # onetime 任务失败 → AutoRecover 恢复 + 重试
        self.schedule_failed = False# 调度器触发的任务失败 → AutoRecover 只恢复，调度器自己重试
        self.failed_task = ""       # 是哪个任务挂了
        self.fail_count = {}        # {task_name: int} 连续失败计数
        self.pending_tasks = []     # [(order, name), ...] 待续跑的任务列表

        from src.state import StateManager
        self.state = StateManager(
            get_path_relative_to_exe(os.path.join("configs", "daily_state.json"))
        )

