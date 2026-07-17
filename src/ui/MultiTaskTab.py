"""一键完成多个任务：勾选 → 设优先级 → 一键启动。"""
import json
import os

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel, CheckBox, FluentIcon, LineEdit, PrimaryPushButton,
    SubtitleLabel, TitleLabel,
)

from ok.gui.widget.CustomTab import CustomTab
from ok.util.config import Config
from src.globals import ALL_TASK_NAMES

CFG_FILE = os.path.join(Config.config_folder, "TaskScheduler.json")


def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── 公开接口（TaskScheduler 调用）───────────────────────────

def get_enabled_in_order():
    """返回按优先级排序的已启用任务列表。"""
    cfg = _load_json(CFG_FILE, {"任务列表": ALL_TASK_NAMES[:]})
    enabled = cfg.get("任务列表", ALL_TASK_NAMES[:])
    order = cfg.get("任务优先级", {})

    tasks = []
    for name in enabled:
        pri = int(order.get(name, 1)) if order.get(name, "1") else 1
        default_idx = ALL_TASK_NAMES.index(name) if name in ALL_TASK_NAMES else 99
        tasks.append((pri, default_idx, name))

    tasks.sort(key=lambda x: (x[0], x[1]))
    return [t[2] for t in tasks]


# ─── UI Tab ──────────────────────────────────────────────────

class MultiTaskTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.icon = FluentIcon.CHECKBOX
        self._cbs = {}
        self._priorities = {}
        self._rows_widget = None
        self._rows_layout = None
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        self.add_widget(TitleLabel("一键完成多个任务"))
        self.add_widget(BodyLabel("勾选任务 → 设优先级 → 一键启动"))
        self.add_widget(SubtitleLabel("任务列表"))

        # ── 多选框（分组）──
        cfg = _load_json(CFG_FILE, {"任务列表": ALL_TASK_NAMES[:]})
        checked = cfg.get("任务列表", ALL_TASK_NAMES[:])

        groups = [
            [n for n in ALL_TASK_NAMES if n.startswith("日常-") and "战斗" not in n],
            [n for n in ALL_TASK_NAMES if n.startswith("日常-战斗")],
            [n for n in ALL_TASK_NAMES if n.startswith("战斗-")],
        ]
        for g_names in groups:
            if not g_names:
                continue
            cb_row = QWidget()
            cb_layout = QHBoxLayout(cb_row)
            cb_layout.setContentsMargins(0, 2, 0, 2)
            cb_layout.setSpacing(12)
            for name in g_names:
                cb = CheckBox(name)
                cb.setChecked(name in checked)
                cb.stateChanged.connect(self._on_check)
                self._cbs[name] = cb
                cb_layout.addWidget(cb)
            cb_layout.addStretch()
            self.add_widget(cb_row)

        # ── 优先级输入区 ──
        self.add_widget(SubtitleLabel("优先级（数字越小越先，默认 1）"))
        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 4, 0, 0)
        self._rows_layout.setSpacing(2)
        self.add_widget(self._rows_widget)

        self.vBoxLayout.addStretch()

        # ── 启动 / 停止按钮 ──（固定在底部）
        btn_row = QWidget()
        bl = QHBoxLayout(btn_row)
        bl.setContentsMargins(0, 12, 0, 0)
        self._start_btn = PrimaryPushButton(FluentIcon.PLAY, "一键启动")
        self._start_btn.clicked.connect(self._on_start)
        bl.addWidget(self._start_btn)
        self._stop_btn = PrimaryPushButton(FluentIcon.CLOSE, "一键停止")
        self._stop_btn.clicked.connect(self._on_stop)
        bl.addWidget(self._stop_btn)
        bl.addStretch()
        self.add_widget(btn_row)

    def _on_check(self):
        cfg = _load_json(CFG_FILE, {"任务列表": ALL_TASK_NAMES[:]})
        cfg["任务列表"] = [n for n, cb in self._cbs.items() if cb.isChecked()]
        _save_json(CFG_FILE, cfg)
        self._refresh()

    def _on_priority_change(self, name, text):
        try:
            val = int(text.strip() or 1)
        except ValueError:
            val = 1
        cfg = _load_json(CFG_FILE, {"任务列表": ALL_TASK_NAMES[:]})
        pri = cfg.get("任务优先级", {})
        pri[name] = str(val)
        cfg["任务优先级"] = pri
        _save_json(CFG_FILE, cfg)

    def _refresh(self):
        """根据勾选状态重建优先级输入行。"""
        # 清空旧行
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._priorities.clear()
        cfg = _load_json(CFG_FILE, {"任务列表": ALL_TASK_NAMES[:]})
        priority = cfg.get("任务优先级", {})
        checked = cfg.get("任务列表", ALL_TASK_NAMES[:])

        for name in ALL_TASK_NAMES:
            if name not in checked:
                continue
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(8)

            label = BodyLabel(name)
            label.setFixedWidth(160)
            rl.addWidget(label)

            le = LineEdit()
            le.setText(str(priority.get(name, "1")))
            le.setPlaceholderText("1")
            le.setFixedWidth(60)
            le.textChanged.connect(lambda t, n=name: self._on_priority_change(n, t))
            self._priorities[name] = le
            rl.addWidget(le)
            rl.addStretch()

            self._rows_layout.addWidget(row)

    def _on_start(self):
        from ok import og
        # 找到 TaskScheduler 在 onetime_tasks 中的索引，走框架标准启动流程
        for i, t in enumerate(og.executor.onetime_tasks):
            if t.__class__.__name__ == 'TaskScheduler':
                og.app.start_controller.start(i)
                return

    def _on_stop(self):
        from ok import og
        og.executor.stop_current_task()

    @property
    def name(self):
        return "一键多任务"
