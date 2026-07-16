import os

from PySide6.QtCore import QObject

from ok import Logger, get_path_relative_to_exe

logger = Logger.get_logger(__name__)


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

