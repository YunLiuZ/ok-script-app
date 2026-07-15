from src.tasks.BaseOmjTask import BaseOmjTask


class RestartGameTask(BaseOmjTask):
    """重启游戏：通过 ADB 强制停止并重新启动阴阳师。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "重启游戏"
        self.description = "强制停止阴阳师并重新启动"

    def run(self):
        if self.restart_game():
            self.log_info("游戏重启成功", notify=True)
        else:
            self.log_error("游戏重启失败")
