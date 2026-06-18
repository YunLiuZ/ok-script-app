"""
每日状态持久化管理。

每个 daily flag 记录最近一次完成的时间戳。
读取时自动判断是否"今天"已完成，跨天自动失效。
"""
import json
import os
from datetime import datetime, date
from typing import Optional


class DailyState:
    """单个每日任务的持久化状态。"""

    def __init__(self, data: Optional[dict] = None):
        data = data or {}
        self._date: Optional[str] = data.get("date")      # "2026-06-18"
        self._time: Optional[str] = data.get("time")      # "09:30:00"

    def is_done_today(self) -> bool:
        """今天是否已完成。"""
        return self._date == str(date.today())

    @property
    def done_at(self) -> Optional[str]:
        """完成时间字符串，如 '2026-06-18 09:30:00'，未完成则为 None。"""
        if self._date and self._time:
            return f"{self._date} {self._time}"
        return None

    def mark_done(self):
        """标记今天已完成（记录当前时间）。"""
        now = datetime.now()
        self._date = str(now.date())
        self._time = now.strftime("%H:%M:%S")

    def to_dict(self) -> dict:
        return {"date": self._date, "time": self._time}


class StateManager:
    """
    管理所有每日标记的持久化读写。

    用法:
        sm = StateManager("configs/daily_state.json")
        if sm.is_done_today("daily_sign"):
            print("今天已签到")
        else:
            do_sign()
            sm.mark_done("daily_sign")
    """

    def __init__(self, file_path: str):
        self._file = file_path
        self._states: dict[str, DailyState] = {}
        self._load()

    # ---- 公共 API ----

    def is_done_today(self, key: str) -> bool:
        """查询 key 对应的任务今天是否已完成。"""
        return self._get(key).is_done_today()

    def done_at(self, key: str) -> Optional[str]:
        """查询 key 上次完成的时间字符串。"""
        return self._get(key).done_at

    def mark_done(self, key: str):
        """标记 key 对应的任务今天已完成，并持久化。"""
        self._get(key).mark_done()
        self._save()

    # ---- 内部 ----

    def _get(self, key: str) -> DailyState:
        if key not in self._states:
            self._states[key] = DailyState()
        return self._states[key]

    def _load(self):
        if not os.path.exists(self._file):
            return
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for key, data in raw.items():
                self._states[key] = DailyState(data)
        except (json.JSONDecodeError, TypeError):
            pass  # 文件损坏就当作全新开始

    def _save(self):
        os.makedirs(os.path.dirname(self._file), exist_ok=True)
        data = {k: v.to_dict() for k, v in self._states.items()}
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
