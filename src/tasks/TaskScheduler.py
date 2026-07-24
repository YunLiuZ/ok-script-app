"""任务编排器：勾选任务后在「一键多任务」设优先级。"""
from ok import communicate
from src.globals import ALL_TASK_NAMES, TASK_MAP as TM
from src.tasks.BaseOmjTask import BaseOmjTask


class TaskScheduler(BaseOmjTask):

    TASK_MAP = TM
    ALL_TASKS = ALL_TASK_NAMES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "任务编排"
        self.description = "在「一键多任务」中勾选任务、设置优先级后启动"

        self.default_config.update({
            "任务列表": self.ALL_TASKS.copy(),
        })

        self.config_description.update({
            "任务列表": "勾选要执行的任务。优先级在「一键多任务」Tab 中设置。",
        })

        self.config_type.update({
            "任务列表": {
                "type": "multi_selection",
                "options": self.ALL_TASKS.copy(),
            },
        })

    def run(self):

        enabled = self.config.get("任务列表", [])

        # 从「一键多任务」获取优先级排序后的任务列表
        from src.ui.MultiTaskTab import get_enabled_in_order
        ordered = get_enabled_in_order()

        self._clear_flags()

        for i, name in enumerate(ordered, 1):
            task_cls = self.TASK_MAP.get(name)
            if task_cls is None:
                self.log_warning(f"未找到任务: {name}")
                continue
            
            self.log_info(f"--- [{i}] 开始: {name} ---")
            t = task_cls(self.executor, self.scene)
            t.after_init(executor=self.executor, scene=self.scene)
            t._enabled = True
            self.executor.current_task = t
            communicate.task.emit(t)

            ok = t.run_safe()

            self.executor.current_task = self
            communicate.task.emit(self)
            self.log_info(f"--- [{i}] 结束: {name} ---")
            if not ok:
                self.log_warning(f"--- [{i}] {name} 失败，继续下一任务 ---")
                continue
