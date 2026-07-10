"""调度面板：可视化配置任务自动执行时间，实时显示下次运行时间。"""
import json
import os
from datetime import datetime, timedelta

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel, CheckBox, FluentIcon, LineEdit, PrimaryPushButton,
    SubtitleLabel, TitleLabel, InfoBar, InfoBarPosition,
)

from ok.gui.widget.CustomTab import CustomTab

CONFIG_FILE = os.path.join("configs", "schedule_runner.json")
STATE_FILE = os.path.join("configs", "schedule_runner_state.json")

ALL_TASK_NAMES = [
    "结界", "魂土", "困28", "式神委派", "地域鬼王", "个人突破", "活动", "每日签到",
]


def parse_interval(s):
    """解析间隔 "时,分" → 总分钟数。例："1,30"→90, "2"→120"""
    try:
        s = str(s).strip()
        if "," in s:
            h, m = s.split(",")
            return max(1, int(h.strip() or 0) * 60 + int(m.strip() or 0))
        return max(1, int(float(s)) * 60)
    except (ValueError, IndexError):
        return 60


def parse_start(s):
    """解析起始时间 "年,月,日,时,分" → datetime。例："2026,7,10,16,0"
    失败返回 None。"""
    try:
        parts = [int(x.strip()) for x in str(s).split(",")]
        if len(parts) != 5:
            return None
        return datetime(*parts)
    except (ValueError, TypeError):
        return None


def format_start(dt):
    """datetime → "年,月,日,时,分" 字符串"""
    return f"{dt.year},{dt.month},{dt.day},{dt.hour},{dt.minute}"


def _default_schedules():
    return {name: {"enabled": False, "start": "2000,0,0,0,0", "interval": "0,0"}
            for name in ALL_TASK_NAMES}


def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calc_next(start_str, interval_str, last_run_str=None):
    start = parse_start(start_str)
    if start is None:
        return None
    interval_min = parse_interval(interval_str)
    now = datetime.now()
    if last_run_str:
        try:
            last_run = datetime.strptime(last_run_str, "%Y-%m-%d %H:%M")
        except ValueError:
            last_run = start
    else:
        last_run = start
    next_run = last_run + timedelta(minutes=interval_min)
    if next_run <= now:
        elapsed_min = (now - start).total_seconds() / 60
        next_run = start + timedelta(minutes=int(elapsed_min // interval_min + 1) * interval_min)
    if next_run <= now:
        next_run = now + timedelta(minutes=interval_min)
    return next_run


class ScheduleTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.icon = FluentIcon.SYNC
        self._rows = {}
        self._setup_ui()
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1000)

    def _setup_ui(self):
        self.add_widget(TitleLabel("调度面板"))
        tip = BodyLabel("格式：起始 年,月,日,时,分（24h）  间隔 时,分  例：2026,7,10,16,0  1,30")
        tip.setWordWrap(True)
        self.add_widget(tip)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(2)

        # 表头 — 与行内控件对齐
        hdr = QWidget()
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(0, 4, 0, 4)
        hl.addSpacing(72 + 6)                        # 任务名宽度
        hl.addWidget(SubtitleLabel("启用"))
        hl.addSpacing(27)
        hl.addWidget(SubtitleLabel("起始年,月,日,时,分"), 0)
        hl.addSpacing(30)
        hl.addWidget(SubtitleLabel("间 隔"), 0)
        hl.addSpacing(40)
        hl.addWidget(SubtitleLabel("下次运行"), 0)
        hl.addStretch()
        layout.addWidget(hdr)

        config = _load_json(CONFIG_FILE, {"schedules": _default_schedules()})
        schedules = config.get("schedules", _default_schedules())

        for name in ALL_TASK_NAMES:
            cfg = schedules.get(name, {"enabled": False,
                                        "start": "2000,0,0,0,0",
                                        "interval": "0,0"})
            layout.addWidget(self._row(name, cfg))

        layout.addStretch()
        self.add_widget(content)

        # 保存 + 调度器开关，同一行
        btn_area = QWidget()
        bl = QHBoxLayout(btn_area)
        bl.setContentsMargins(0, 8, 0, 0)

        save = PrimaryPushButton(FluentIcon.SAVE, "保存")
        save.clicked.connect(self._save)
        bl.addWidget(save)

        bl.addSpacing(12)

        self._toggle_btn = PrimaryPushButton(FluentIcon.PLAY, "启用调度器")
        self._toggle_btn.clicked.connect(self._toggle_scheduler)
        bl.addWidget(self._toggle_btn)

        bl.addWidget(BodyLabel("控制后台调度器的启动与停止"))
        bl.addStretch()
        self.add_widget(btn_area)

    def _row(self, name, cfg):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 3, 0, 3)
        l.setSpacing(0)

        nl = BodyLabel(name)
        nl.setFixedWidth(72)
        l.addWidget(nl)
        l.addSpacing(6)

        cb = CheckBox()
        cb.setChecked(cfg.get("enabled", False))
        l.addWidget(cb)
        l.addSpacing(41)

        st = LineEdit()
        st.setText(str(cfg.get("start", "2000,0,0,0,0")))
        st.setPlaceholderText("年,月,日,时,分")
        st.setFixedWidth(155)
        l.addWidget(st)
        l.addSpacing(8)

        iv = LineEdit()
        iv.setText(str(cfg.get("interval", "0,0")))
        iv.setPlaceholderText("时,分")
        iv.setFixedWidth(60)
        l.addWidget(iv)
        l.addSpacing(8)

        nx = BodyLabel("计算中...")
        nx.setFixedWidth(170)
        l.addWidget(nx)
        l.addStretch()

        self._rows[name] = {"enabled": cb, "start": st, "interval": iv, "next": nx}
        return w

    def _refresh(self):
        state = _load_json(STATE_FILE, {})
        for name, r in self._rows.items():
            nr = calc_next(r["start"].text().strip(), r["interval"].text().strip(), state.get(name))
            r["next"].setText(nr.strftime("%Y-%m-%d %H:%M") if nr else "—")

    def _save(self):
        schedules = {}
        has_error = False
        for name, r in self._rows.items():
            if not r["enabled"].isChecked():
                schedules[name] = {"enabled": False,
                                   "start": r["start"].text().strip(),
                                   "interval": r["interval"].text().strip()}
                continue  # 未启用的不校验

            start_text = r["start"].text().strip()
            interval_text = r["interval"].text().strip()

            if parse_start(start_text) is None:
                InfoBar.error("格式错误", f"[{name}] 起始时间格式不对，应为 年,月,日,时,分（如 2026,7,10,16,0）",
                              duration=5000, position=InfoBarPosition.TOP, parent=self)
                has_error = True
                continue

            if parse_interval(interval_text) is None:
                InfoBar.error("格式错误", f"[{name}] 间隔格式不对，应为 时,分（如 1,30）",
                              duration=5000, position=InfoBarPosition.TOP, parent=self)
                has_error = True
                continue

            schedules[name] = {"enabled": r["enabled"].isChecked(),
                               "start": start_text, "interval": interval_text}

        if not has_error:
            _save_json(CONFIG_FILE, {"schedules": schedules})
            InfoBar.success("保存成功", "调度配置已保存，请在下方启用/停止调度器", duration=2000,
                            position=InfoBarPosition.TOP, parent=self)
            self.logger.info("调度配置已保存")

    @property
    def name(self):
        return "调度面板"

    def _find_sr(self):
        if not self.executor:
            return None
        for t in self.executor.trigger_tasks:
            if "ScheduleRunner" in type(t).__name__:
                return t
        return None

    def _toggle_scheduler(self):
        sr = self._find_sr()
        if sr is None:
            InfoBar.error("错误", "未找到后台调度器", duration=3000,
                          position=InfoBarPosition.TOP, parent=self)
            return
        if sr.enabled:
            sr.disable()
            self._toggle_btn.setText("启用调度器")
            self._toggle_btn.setIcon(FluentIcon.PLAY)
            InfoBar.warning("已停止", "后台调度器已停止", duration=2000,
                            position=InfoBarPosition.TOP, parent=self)
        else:
            sr.enable()
            self._toggle_btn.setText("停止调度器")
            self._toggle_btn.setIcon(FluentIcon.CANCEL)
            InfoBar.success("已启用", "后台调度器已启用，将按时间表执行", duration=2000,
                            position=InfoBarPosition.TOP, parent=self)
