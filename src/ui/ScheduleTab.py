"""调度面板：配置间隔与上次运行时间，实时显示下次运行时间。"""
import json
import os
from datetime import datetime, timedelta

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel, CheckBox, FluentIcon, LineEdit,
    SubtitleLabel, TitleLabel, InfoBar, InfoBarPosition,
)

from ok.gui.widget.CustomTab import CustomTab
from ok.util.config import Config
from src.globals import ALL_TASK_NAMES

CONFIG_FILE = os.path.join(Config.config_folder, "schedule_runner.json")


def parse_time(s):
    try:
        date_part, time_part = str(s).strip().split()
        y, m, d = [int(x) for x in date_part.split(".")]
        h, mi = [int(x) for x in time_part.split(":")]
        return datetime(y, m, d, h, mi)
    except (ValueError, IndexError):
        return None

def fmt_time(dt):
    return f"{dt.year}.{dt.month}.{dt.day} {dt.hour}:{dt.minute:02d}"

def parse_interval(s):
    try:
        s = str(s).strip()
        if ":" in s:
            h, m = s.split(":")
            return max(1, int(h.strip() or 0) * 60 + int(m.strip() or 0))
        return max(1, int(float(s)) * 60)
    except (ValueError, IndexError):
        return 60

def calc_next(last_run_str, interval_str):
    last = parse_time(last_run_str)
    if last is None:
        return None
    m = parse_interval(interval_str)
    nr = last + timedelta(minutes=m)
    if nr <= datetime.now():
        elapsed = (datetime.now() - last).total_seconds()
        nr = last + timedelta(minutes=int(elapsed / (m * 60) + 1) * m)
    return nr

def _default_schedules():
    return {n: {"enabled": False, "last_run": "2000.1.1 0:0", "interval": "24:0",
                "next_run": "2000.1.1 0:0"} for n in ALL_TASK_NAMES}

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


class ScheduleTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.icon = FluentIcon.SYNC
        self._rows = {}
        self._setup_ui()

    def _setup_ui(self):
        self.add_widget(TitleLabel("调度面板"))
        self.add_widget(BodyLabel("格式：上次运行 YYYY.M.D HH:MM  间隔 H:MM  例：2026.7.14 14:00  24:00"))

        # 表头
        hdr = QWidget()
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(0, 4, 0, 4)
        hl.addSpacing(78)
        hl.addWidget(SubtitleLabel("启用"))
        hl.addSpacing(27)
        hl.addWidget(SubtitleLabel("上次运行时间"), 0)
        hl.addSpacing(30)
        hl.addWidget(SubtitleLabel("间 隔"), 0)
        hl.addSpacing(40)
        hl.addWidget(SubtitleLabel("下次运行"), 0)
        hl.addStretch()
        self.add_widget(hdr)

        # 任务行
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(2)

        cfg = _load_cfg()
        schedules = cfg.get("schedules", _default_schedules())
        for name in ALL_TASK_NAMES:
            s = schedules.get(name, _default_schedules()[name])
            layout.addWidget(self._row(name, s))
        layout.addStretch()
        self.add_widget(content)

    def _row(self, name, cfg):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 3, 0, 3)
        l.setSpacing(0)

        nl = BodyLabel(name)
        nl.setFixedWidth(140)
        l.addWidget(nl)
        l.addSpacing(6)

        cb = CheckBox()
        cb.setChecked(cfg.get("enabled", False))
        l.addWidget(cb)
        l.addSpacing(20)

        lr = LineEdit()
        lr.setText(str(cfg.get("last_run", "2000.1.1 0:0")))
        lr.setPlaceholderText("YYYY.M.D HH:MM")
        lr.setFixedWidth(155)
        l.addWidget(lr)
        l.addSpacing(8)

        iv = LineEdit()
        iv.setText(str(cfg.get("interval", "24:00")))
        iv.setPlaceholderText("H:MM")
        iv.setFixedWidth(60)
        l.addWidget(iv)
        l.addSpacing(12)

        nx = BodyLabel(cfg.get("next_run", "2000.1.1 0:00") if cfg.get("enabled") else "—")
        nx.setFixedWidth(170)
        l.addWidget(nx)
        l.addStretch()

        self._rows[name] = {"enabled": cb, "last_run": lr, "interval": iv, "next": nx}

        # 用户编辑时实时刷新下次运行时间 + 自动保存
        def update_next():
            if cb.isChecked():
                nr = calc_next(lr.text().strip(), iv.text().strip())
                nx.setText(fmt_time(nr) if nr else "—")
            else:
                nx.setText("—")
            self._save(show_toast=False)

        cb.stateChanged.connect(lambda _: update_next())
        lr.textChanged.connect(lambda _: update_next())
        iv.textChanged.connect(lambda _: update_next())

        return w

    def _save(self, show_toast=True):
        schedules = {}
        for name, r in self._rows.items():
            lr_text = r["last_run"].text().strip()
            iv_text = r["interval"].text().strip()
            enabled = r["enabled"].isChecked()

            nr = calc_next(lr_text, iv_text) if enabled else None
            schedules[name] = {
                "enabled": enabled,
                "last_run": lr_text,
                "interval": iv_text,
                "next_run": fmt_time(nr) if nr else "2000.1.1 0:0",
            }

        _save_cfg({"schedules": schedules})
        if show_toast:
            InfoBar.success("已保存", "调度配置已更新", duration=1500,
                            position=InfoBarPosition.TOP, parent=self)

    @property
    def name(self):
        return "调度面板"
