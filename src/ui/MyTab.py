import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, FluentIcon, PrimaryPushButton, SpinBox, SubtitleLabel, TitleLabel

from ok import Config
from ok.gui.widget.CustomTab import CustomTab


class MyTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.logger.info(f'MyTab init {self.__class__.__name__}')
        self.config = Config(self.__class__.__name__, {
            'config1': 0,
            'config2': "test_value"
        })
        self.icon = FluentIcon.FLAG

        # ---- 多开说明 ----
        self.title = TitleLabel("多开助手")
        self.add_widget(self.title)

        desc = BodyLabel(
            "如果你有多个游戏账号，可以在这里打开新的程序窗口，"
            "每个窗口独立记录设置，互不影响。"
        )
        desc.setWordWrap(True)
        self.add_widget(desc)

        # ---- 操作区 ----
        op_widget = QWidget()
        op_layout = QVBoxLayout(op_widget)
        op_layout.setContentsMargins(0, 12, 0, 0)

        # 编号选择
        row1 = QWidget()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.addWidget(BodyLabel("选择账号编号："))

        self.instance_spin = SpinBox()
        self.instance_spin.setRange(2, 10)
        self.instance_spin.setValue(2)
        self.instance_spin.setToolTip("每个账号一个编号，已用过的编号下次会自动记住设置")
        row1_layout.addWidget(self.instance_spin)
        row1_layout.addStretch()
        op_layout.addWidget(row1)

        # 启动按钮
        row2 = QWidget()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 4, 0, 0)
        self.launch_btn = PrimaryPushButton(FluentIcon.ADD, "打开新窗口")
        self.launch_btn.clicked.connect(self.launch_instance)
        row2_layout.addWidget(self.launch_btn)
        row2_layout.addStretch()
        op_layout.addWidget(row2)

        self.add_widget(op_widget)

        # ---- 使用提示 ----
        tips = SubtitleLabel("使用说明")
        self.add_widget(tips)

        tips_text = BodyLabel(
            "1. 选择一个编号（如 2），点击「打开新窗口」\n"
            "2. 新窗口标题会显示为「ok-Onmyoji #2」\n"
            "3. 每个编号的设置独立保存，下次打开自动恢复\n"
            "4. 编号 1 就是当前这个窗口，所以从 2 开始选"
        )
        tips_text.setWordWrap(True)
        self.add_widget(tips_text)

    @property
    def name(self):
        return "多开助手"

    def launch_instance(self):
        n = self.instance_spin.value()
        main_py = Path(__file__).resolve().parents[2] / "main.py"
        self.logger.info(f"启动实例 #{n}: {main_py}")
        subprocess.Popen(
            [sys.executable, str(main_py), "--instance", str(n)],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

    def showEvent(self, event):
        super().showEvent(event)
        if event.type() == QEvent.Show:
            self.logger.info(f'MyTab Show {self.__class__.__name__}')

    def hideEvent(self, event: QEvent):
        super().hideEvent(event)
        self.logger.info(f'MyTab hide {self.__class__.__name__}')
