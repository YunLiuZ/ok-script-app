"""后台调度器：按用户配置的时间表自动执行任务。"""
import json
import os
import re
from datetime import datetime, timedelta

from ok import TriggerTask
from ok.util.config import Config

# ---- 任务名 → 任务类 ----
from src.tasks.DailyTask import DailyTask
from src.tasks.ExplorationTask import ExplorationTask
from src.tasks.DelegationTask import DelegationTask
from src.tasks.SoulZonesTask import SoulZonesTask
from src.tasks.AreaBossTask import AreaBossTask
from src.tasks.RealmRaidTask import RealmRaidTask
from src.tasks.GameEventsBattleTask import GameEventsBattleTask
from src.tasks.UtilizeTask import UtilizeTask

TASK_MAP = {
    "每日签到": DailyTask, "困28": ExplorationTask, "式神委派": DelegationTask,
    "魂土": SoulZonesTask, "地域鬼王": AreaBossTask, "个人突破": RealmRaidTask,
    "活动": GameEventsBattleTask, "结界": UtilizeTask,
}
ALL_TASK_NAMES = list(TASK_MAP.keys())


# ---- 文件路径 ----
def _cfg_path(filename):
    return os.path.join(Config.config_folder, filename)

CONFIG_FILE = _cfg_path("schedule_runner.json")       # 唯一数据源：{任务: {enabled, last_run, interval, next_run}}


# ---- 解析工具 ----
def parse_time(s):
    """ "YYYY.M.D HH:MM" → datetime，失败返回 None """
    try:
        date_part, time_part = str(s).strip().split()
        y, m, d = [int(x) for x in date_part.split(".")]
        h, mi = [int(x) for x in time_part.split(":")]
        return datetime(y, m, d, h, mi)
    except (ValueError, IndexError):
        return None

def parse_interval(s):
    """ "H:MM" → 分钟数 """
    try:
        s = str(s).strip()
        if ":" in s:
            h, m = s.split(":")
            return max(1, int(h.strip() or 0) * 60 + int(m.strip() or 0))
        return max(1, int(float(s)) * 60)
    except (ValueError, IndexError):
        return 60

def fmt_time(dt):
    """ datetime → "2026.7.14 15:35" """
    return f"{dt.year}.{dt.month}.{dt.day} {dt.hour}:{dt.minute:02d}"

def calc_next(last_run_str, interval_str):
    """ 下次运行 = last_run + interval，跳过已过时间点 """
    last = parse_time(last_run_str)
    if last is None:
        return None
    m = parse_interval(interval_str)
    nr = last + timedelta(minutes=m)
    if nr <= datetime.now():
        elapsed = (datetime.now() - last).total_seconds()
        nr = last + timedelta(minutes=int(elapsed / (m * 60) + 1) * m)
    return nr


# ---- 默认配置 ----
def _default_schedules():
    return {n: {"enabled": False, "last_run": "2000.1.1 0:0", "interval": "24:0",
                "next_run": "2000.1.1 0:0"} for n in ALL_TASK_NAMES}


# ---- JSON 读写 ----
def _load_cfg():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"schedules": _default_schedules()}

def _save_cfg(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class ScheduleRunner(TriggerTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "后台调度器"
        self.description = "按设定的时间表自动执行日常任务"
        self.trigger_count = 0
        self.default_config = {'_enabled': True}
        self.default_config.update({"轮询间隔(秒)": 1 })
        self.config_description.update({"轮询间隔(秒)": "检查间隔，默认 1 秒。"})

    def enable(self):
        super().enable()
        # 如果设备未连接，通过 StartController 启动游戏（和 onetime 任务行为一致）
        if self.executor.device_manager and not self.executor.device_manager.device_connected():
            from ok import og
            og.app.start_controller.start()
        self.executor.start()          # 确保 executor 线程启动

    def on_create(self):
        super().on_create()
        self.trigger_interval = self.config.get("轮询间隔(秒)", 1)
        # 每次启动强制关闭，不记住上次勾选状态
        self._enabled = False
        self.config['_enabled'] = False

    # ==================== 主循环 ====================

    def run(self):
        """
        now >= next_run → 执行 → 更新 last_run 和 next_run。
        """
        self.trigger_count += 1
        print(self.trigger_count)
        self.log_debug(f'MyTriggerTask run {self.trigger_count}')
        now = datetime.now()
        cfg = _load_cfg()
        schedules = cfg.get("schedules", _default_schedules())
        changed = False
        self.log_info(f"{fmt_time(now)},{self.trigger_interval}")
        for name, s in schedules.items():
            if not s.get("enabled") or name not in TASK_MAP:
                continue
            self.log_info(f"{name},{s.get('next_run', '未设置')}")
            next_run = parse_time(s.get("next_run", ""))
            if next_run is None:
                continue

            if now >= next_run:                                    # 时间到了
                from ok import og
                if not og.my_app.logged_in:
                    self.log_info(f"  {name}: 未登录，跳过（等待 AutoLoginTask）")
                    continue                                     # 不更新 next_run，下一轮再试
                ok = self._execute_task(name)                     # → 执行
                if ok:                                           # 成功才更新
                    s["last_run"] = fmt_time(now)
                    s["next_run"] = fmt_time(now + timedelta(
                        minutes=parse_interval(s.get("interval", "6:0"))))
                    changed = True
                elif og.my_app.fail_count.get(name, 0) >= 2:
                    self.log_warning(f"[{name}] 第二次执行失败，取消调度")
                    s["enabled"] = False
                    og.my_app.fail_count[name] = 0
                    changed = True
                else:
                    self.log_info(f"  {name}: 执行失败，next_run 保持不变，下轮重试")

        if changed:
            _save_cfg(cfg)                                         # 持久化
        return changed

    # ==================== 执行任务 ====================

    def _execute_task(self, name: str):
        task_cls = TASK_MAP.get(name)
        if task_cls is None:
            return False
        try:
            t = task_cls(self.executor, self._app)
            t.after_init(executor=self.executor, scene=self.scene)
            ok = t.run_safe()
            if not ok:
                from ok import og
                og.my_app.schedule_failed = True  # 调度器额外标记
            return ok
        except Exception as e:
            self.log_error(f"[调度] {name} 执行异常", e)
            from ok import og
            og.my_app.schedule_failed = True
            return False
