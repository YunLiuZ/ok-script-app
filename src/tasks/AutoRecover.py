from src.tasks.BaseOmjTask import BaseOmjTask
from ok import TriggerTask, og

class AutoRecover(TriggerTask, BaseOmjTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_config = {'_enabled': True}
        self.trigger_interval = 20
        self.trigger_count = 0
        self.name = "Auto Recover"

    def on_create(self):
        super().on_create()
        self._enabled = True

    def run(self):
        need = self.onetime_failed or self.schedule_failed
        self.log_info(f"如果onetime={self.onetime_failed} "
                      f"schedule={self.schedule_failed} task={self.failed_task}")
        if not self.logged_in:
            self.log_info("未登录，等待 AutoLoginTask...")
            return False
        if not need:
            return False
        # ── 恢复环境 ──
        for i in range(2):
            if self.in_home_and_back():
                break
            self.log_info(f"in_home_and_back 第{i+1}次失败")
        else:
            if self.unexpected_error():
                return True
            self.log_info("恢复失败，重启游戏")
            self.restart_game()
            return True

        # ── 环境 OK，分情况处理 ──
        if self.schedule_failed:
            # 调度器会自己重试（next_run 未更新），只清标志
            self.log_info("schedule 失败已恢复，交给调度器重试")
            self._clear_flags()
            return True

        # onetime 失败 → 重试
        return self._handle_onetime_retry()

    def _handle_onetime_retry(self):
        """依次执行 pending_tasks（含失败任务 + 后续任务）。"""
        pending = list(og.my_app.pending_tasks)
        og.my_app.pending_tasks = []

        if not pending:
            self.log_warning("pending_tasks 为空，无法重试")
            self._clear_flags()
            return True

        for i, (order, name) in enumerate(pending):
            count = og.my_app.fail_count.get(name, 0)
            if count >= 2:
                self.log_warning(f"[{name}] 已连续失败2次，跳过（不再执行）")
                og.my_app.fail_count[name] = 0
                continue

            self.log_info(f"[{order}] {name} 续跑...")
            self._clear_flags()
            ok = self._retry_task(name)

            if not ok:
                new_count = og.my_app.fail_count.get(name, 0)
                if new_count >= 2:
                    self.log_warning(f"[{name}] 第二次执行失败，跳过（不再执行）")
                    og.my_app.fail_count[name] = 0
                    continue
                else:
                    # 还没到上限，存入剩余任务等下轮恢复再试
                    og.my_app.pending_tasks = pending[i:]
                    self.log_info(f"[{name}] 再次失败，剩余 {len(pending[i:])} 个任务等下轮恢复")
                    return True

        # 全部跑完
        self._clear_flags()
        self.log_info("all pending tasks done")
        return True

    def _retry_task(self, name):
        from src.tasks.AutoScheduleRunner import TASK_MAP
        task_cls = TASK_MAP.get(name)
        if task_cls is None:
            self.log_warning(f"未找到任务: {name}")
            return False
        t = task_cls(self.executor, self._app)
        t.after_init(executor=self.executor, scene=self.scene)
        return t.run_safe()

    def _clear_flags(self):
        self.onetime_failed = False
        self.schedule_failed = False
        self.failed_task = ""
