"""后台调度器：按用户配置的时间表自动执行任务。"""
import json
import os
from datetime import datetime

from ok import TriggerTask

# ---- 任务名 → 任务类（用于实例化并执行具体任务） ----
from src.tasks.DailyTask import DailyTask
from src.tasks.ExplorationTask import ExplorationTask
from src.tasks.DelegationTask import DelegationTask
from src.tasks.SoulZonesTask import SoulZonesTask
from src.tasks.AreaBossTask import AreaBossTask
from src.tasks.RealmRaidTask import RealmRaidTask
from src.tasks.GameEventsBattleTask import GameEventsBattleTask
from src.tasks.UtilizeTask import UtilizeTask

TASK_MAP = {
    "每日签到": DailyTask,
    "困28": ExplorationTask,
    "式神委派": DelegationTask,
    "魂土": SoulZonesTask,
    "地域鬼王": AreaBossTask,
    "个人突破": RealmRaidTask,
    "活动": GameEventsBattleTask,
    "结界": UtilizeTask,
}

ALL_TASK_NAMES = list(TASK_MAP.keys())

# ---- 调度配置/状态文件路径（由 ScheduleTab 写入，ScheduleRunner 读取） ----
CONFIG_FILE = os.path.join("configs", "schedule_runner.json")       # 用户设置的调度规则
STATE_FILE = os.path.join("configs", "schedule_runner_state.json") # 上次执行时间记录


def parse_interval(s):
    """解析间隔 "时,分" → 总分钟数。例："1,30"→90, "2"→120, "0,45"→45"""
    try:
        s = str(s).strip()
        if "," in s:
            h, m = s.split(",")
            return max(1, int(h.strip() or 0) * 60 + int(m.strip() or 0))
        return max(1, int(float(s)) * 60)
    except (ValueError, IndexError):
        return 60  # 解析失败，默认 1 小时


def parse_start(s):
    """解析起始时间 "年,月,日,时,分" → datetime。例："2026,7,10,16,0"。
       失败返回 None（格式不对时安全跳过，不会崩溃）。"""
    try:
        parts = [int(x.strip()) for x in str(s).split(",")]
        if len(parts) != 5:
            return None
        return datetime(*parts)
    except (ValueError, TypeError):
        return None


def _default_schedules():
    """生成默认调度配置：所有任务未启用，起始时间为今天 0:00。"""
    now = datetime.now()
    start_str = f"{now.year},{now.month},{now.day},0,0"
    return {name: {"enabled": False, "start": start_str, "interval": "6,0"}
            for name in ALL_TASK_NAMES}


class ScheduleRunner(TriggerTask):
    """
    后台调度器 — 继承 TriggerTask 实现周期性检查。
    由框架的 trigger_tasks 循环驱动，每 trigger_interval 秒调用一次 run()。
    不显示在 TriggerTask 面板 (visible=False)，由「调度面板」Tab 控制启停。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "后台调度器"
        self.description = "按设定的时间表自动执行日常任务"
        self.trigger_interval = 1       # 每秒检查一次（轻量 IO 操作，无性能压力）
        self.visible = False           # 不在 TriggerTask 面板显示，由 ScheduleTab 管理

    # ==================== JSON 持久化工具 ====================

    def _load_json(self, path, default):
        """读取 JSON 文件，不存在或损坏则返回默认值。"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def _save_json(self, path, data):
        """写入 JSON 文件，自动创建目录。"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_state(self):
        """读取执行状态：{任务名: "2026-07-10 16:00"}"""
        return self._load_json(STATE_FILE, {})

    def _save_state(self, state):
        """保存执行状态。"""
        self._save_json(STATE_FILE, state)

    def _load_schedules(self):
        """读取调度配置：{任务名: {enabled, start, interval}}"""
        cfg = self._load_json(CONFIG_FILE, {"schedules": _default_schedules()})
        return cfg.get("schedules", _default_schedules())

    # ==================== 主循环（由框架定期调用） ====================

    def run(self):
        """
        每 trigger_interval 秒被框架调用一次。
        遍历所有已启用的调度，检查是否到时间执行。
        返回 True 表示有任务被执行（提高下次检查优先级）。
        """
        now = datetime.now()
        state = self._load_state()          # 上次各任务执行时间
        schedules = self._load_schedules()  # 用户设定的调度规则
        ran_any = False                     # 本轮是否有任务被执行

        for name, cfg in schedules.items():
            # --- 过滤未启用或未知任务 ---
            if not cfg.get("enabled", False):
                continue
            if name not in TASK_MAP:
                continue

            # --- 检查起始时间：还没到就不执行 ---
            start = parse_start(cfg.get("start", ""))
            if start is None or now < start:
                continue

            # --- 检查间隔：距离上次执行是否已过足够时间 ---
            interval_min = parse_interval(cfg.get("interval", "6,0"))
            last_str = state.get(name)      # 从状态文件中读取上次执行时间
            last_run = None
            if last_str:
                try:
                    last_run = datetime.strptime(last_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    pass
            if last_run is None:
                last_run = start            # 首次执行：从起始时间开始算

            # 计算还需等待多久；≤0 表示到时间了
            remaining = interval_min * 60 - (now - last_run).total_seconds()
            if remaining <= 0:
                # === 到时间，执行任务 ===
                self._execute_task(name)
                state[name] = now.strftime("%Y-%m-%d %H:%M")
                self._save_state(state)     # 立即持久化，防止重复执行
                ran_any = True

        return ran_any  # 返回 True 会使触发循环重置优先级

    # ==================== 执行具体任务 ====================

    def _execute_task(self, name: str):
        """实例化指定任务类并执行 run()。
           包含完整的 try/except，单个任务异常不影响其他任务。"""
        task_cls = TASK_MAP.get(name)
        if task_cls is None:
            self.log_warning(f"[调度] 未找到任务类: {name}")
            return

        try:
            t = task_cls(self.executor, self._app)      # 创建任务实例
            t.after_init(executor=self.executor, scene=self.scene)  # 加载配置
            t.run()                                      # 执行
        except Exception as e:
            self.log_error(f"[调度] 任务 {name} 执行异常", e)
