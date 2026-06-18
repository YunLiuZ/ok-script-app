# 全局状态管理实现指南

本指南带你一步步实现与项目相同的全局状态管理模式：**`ok` 框架 IOC 容器 + `og` 全局命名空间 + `Globals` 状态对象**。

---

## 第 1 步：创建全局状态类 `Globals`

新建文件 `src/globals.py`，将需要全局共享的状态集中管理：

```python
# src/globals.py
import os.path
from ok import Logger, get_path_relative_to_exe, og

logger = Logger.get_logger(__name__)


class Globals(QObject):  # 继承 QObject 以获得信号/槽能力（可选）
    """
    全局共享状态容器。
    所有 Task 通过 og.my_app 访问同一个实例。
    """

    def __init__(self, exit_event):
        super().__init__()
        # ========== 在这里声明所有需要全局共享的状态 ==========
        self._yolo_model = None       # 懒加载的模型实例
        self.logged_in = False        # 登录状态
        self.current_task_name = ""   # 当前执行的任务名
        # 可以继续添加更多状态...

    # ========== 懒加载属性示例 ==========
    @property
    def yolo_model(self):
        """首次访问时才加载模型，避免启动时耗时"""
        if self._yolo_model is None:
            weights = get_path_relative_to_exe(
                os.path.join("assets", "echo_model", "echo.onnx")
            )
            # 根据配置选择不同后端
            if og.config.get("ocr").get("params").get("use_openvino"):
                from src.OpenVinoYolo8Detect import OpenVinoYolo8Detect
                self._yolo_model = OpenVinoYolo8Detect(weights=weights)
            else:
                from src.OnnxYolo8Detect import OnnxYolo8Detect
                self._yolo_model = OnnxYolo8Detect(weights=weights)
        return self._yolo_model

    # ========== 封装方法 ==========
    def yolo_detect(self, image, threshold=0.6, label=-1):
        """统一检测入口，所有 Task 调用同一方法"""
        return self.yolo_model.detect(image, threshold=threshold, label=label)
```

**要点：**
- 继承 `QObject` 可获得 PySide6 信号/槽能力（不需要可以省略）
- 构造函数接收 `exit_event`（ok 框架传入）
- 所有状态变量在 `__init__` 中初始化，确保不会在类级别共享可变对象

---

## 第 2 步：在 `config.py` 中注册

在项目根目录的 `config.py` 中添加 `my_app` 配置：

```python
# config.py
config = {
    'debug': False,
    'use_gui': True,
    'config_folder': 'configs',
    # ... 其他配置 ...

    # ⬇ 关键：告诉 ok 框架加载 Globals 并挂载到 og.my_app
    'my_app': ['src.globals', 'Globals'],
    #           ↑ 模块路径      ↑ 类名

    # ... 其他配置 ...
}
```

**原理：** ok 框架启动时会：
1. `import src.globals`
2. `getattr(src.globals, 'Globals')`
3. 实例化 `Globals(exit_event)`
4. 将实例赋值给 `og.my_app`

完成这一步后，项目中任何地方 `from ok import og; og.my_app` 都能拿到同一个 `Globals` 实例。

---

## 第 3 步：在 Task 基类中通过 Property 代理访问

在你的 Task 基类（如 `BaseTask.py`）中，用 property 封装对全局状态的读写：

```python
# src/task/BaseTask.py
from ok import BaseTask, Logger, og

logger = Logger.get_logger(__name__)


class BaseWWTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 可以从全局配置中拿特定子配置
        self.key_config = self.get_global_config('Game Hotkey')

    # ========== 通过 property 代理全局状态 ==========
    @property
    def logged_in(self):
        """读全局登录状态"""
        return og.my_app.logged_in

    @logged_in.setter
    def logged_in(self, value):
        """写全局登录状态 — 所有 Task 实例立刻可见"""
        og.my_app.logged_in = value

    # ========== 使用全局方法 ==========
    def find_echos(self, threshold=0.3):
        """使用全局 YOLO 模型检测"""
        return og.my_app.yolo_detect(self.frame, threshold=threshold, label=0)
```

**要点：**
- 用 `@property` 做读写代理，Task 内部 `self.logged_in` 即可读写全局状态
- 全局方法直接调用 `og.my_app.xxx()`
- 也可以把全局配置读出来缓存到实例变量中（如 `self.key_config`）

---

## 第 4 步：在具体 Task 中使用

所有继承 `BaseWWTask` 的任务类自动共享全局状态，无需额外代码：

```python
# src/task/DailyTask.py
class DailyTask(BaseWWTask):

    def run(self):
        # 检查是否需要登录（读全局状态）
        if not self.logged_in:
            self.login()
        # ...
        # 某处修改登录状态（写全局状态）
        self.logged_in = True

        # 使用全局 YOLO 模型
        echos = self.find_echos(threshold=0.5)
```

**效果：** `DailyTask` 设为 `logged_in = True` 后，`FarmEchoTask`、`AutoCombatTask` 等其他任务读取 `self.logged_in` 时也会得到 `True`，因为大家都在读写 `og.my_app` 上的同一个变量。

---

## 第 5 步（可选）：添加更多全局状态或配置

有两种方式扩展全局状态：

### 方式 A：加到 `Globals` 中（运行时状态）

适合：模型实例、计数器、当前运行状态等**运行时可变**的状态。

```python
# src/globals.py
class Globals(QObject):
    def __init__(self, exit_event):
        # ... 原有状态 ...
        self.echo_count = 0          # 声骸计数
        self.total_run_time = 0      # 总运行时间
        self.error_count = 0         # 错误计数
```

Task 中访问：`og.my_app.echo_count`

### 方式 B：加到 `config.py` 的 `global_configs` 中（用户配置）

适合：热键映射、功能开关等**用户可在 GUI 修改**的配置。

```python
# config.py
from ok import ConfigOption

my_config_option = ConfigOption('My Config Tab', {
    'Enable Feature A': True,
    'Max Retry Count': 3,
}, description='My feature settings', show_at_tab=True)

config = {
    # ...
    'global_configs': [
        my_config_option,
        # ... 其他 ConfigOption ...
    ],
    # ...
}
```

Task 中读取：`self.get_global_config('My Config Tab')`

---

## 架构总览

```
┌─────────────────────────────────────────────────┐
│  config.py                                      │
│  'my_app': ['src.globals', 'Globals']           │  ← 注册
└──────────────────┬──────────────────────────────┘
                   │ ok 框架实例化
                   ▼
┌─────────────────────────────────────────────────┐
│  og.my_app  (全局单例)                           │
│  ┌───────────────────────────────────────────┐  │
│  │  Globals 实例                              │  │
│  │  ├── logged_in: bool                      │  │
│  │  ├── _yolo_model: Model                   │  │
│  │  ├── mini_map_arrow: ...                  │  │
│  │  └── yolo_detect(image, threshold)        │  │
│  └───────────────────────────────────────────┘  │
└────────┬───────────────┬───────────────┬────────┘
         │               │               │
    ┌────▼────┐    ┌─────▼────┐    ┌─────▼────┐
    │ Task A   │    │ Task B   │    │ Task C   │
    │ property │    │ property │    │ property │
    │ logged_in│    │ logged_in│    │ logged_in│
    └──────────┘    └──────────┘    └──────────┘
    
    所有 Task 通过 property 代理 → 读写同一个 og.my_app
```

---

## 关键原则

| 原则 | 说明 |
|------|------|
| **单一实例** | `og.my_app` 在整个进程中只有一个，由 ok 框架保证 |
| **集中声明** | 所有全局状态变量集中在 `Globals.__init__` 中声明，一目了然 |
| **Property 代理** | Task 层通过 `@property` 访问，不直接写 `og.my_app.xxx`，便于后续重构 |
| **懒加载** | 耗资源的对象（如模型）用 `@property` + `if x is None` 模式延迟创建 |
| **不直接耦合** | Task 不直接 import Globals，通过 `og.my_app` 中转，解耦 |

---

## 快速检查清单

- [ ] 创建了 `src/globals.py`，`Globals` 类继承 `QObject`
- [ ] 在 `__init__` 中初始化了所有共享状态变量
- [ ] 在 `config.py` 中添加了 `'my_app': ['src.globals', 'Globals']`
- [ ] 在 Task 基类中用 `@property` 代理了需要的全局状态
- [ ] 具体 Task 中通过 `self.xxx` 读写全局状态
- [ ] 新状态优先考虑应该放在 `Globals`（运行时）还是 `ConfigOption`（用户配置）
