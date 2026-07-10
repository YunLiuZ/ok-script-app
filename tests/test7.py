import os, sys, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from ok.test import init_ok, destroy_ok

config["debug"] = False
config["trigger_tasks"] = []
init_ok(config)

from ok import og
from src.tasks.DailyTask import DailyTask
from ok.test import ok as ok_test

task = DailyTask(og.executor, None)
task.feature_set = ok_test.feature_set
task.after_init(executor=ok_test.task_executor, scene=ok_test.task_executor.scene)

# ---- 设置测试图片 ----
IMAGE = "tests/img/2.png"
ok_test.device_manager.capture_method.set_images([IMAGE])
frame = task.next_frame()
h, w = frame.shape[:2]

# rgb(242,139,43) → BGR(43,139,242) ±20
boxes = task.calculate_color_percentage({"b": (116, 156), "g": (179, 219), "r": (201, 241)},
                                         box=task.box_of_screen(0.8, 0.75, 0.93, 0.93))
print("11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")
print(boxes)
print("11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")

destroy_ok()
