import os, sys, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from ok.test import init_ok, destroy_ok

config["debug"] = True
config["trigger_tasks"] = []
init_ok(config)

from ok import og
from src.tasks.DailyTask import DailyTask
from ok.test import ok as ok_test

task = DailyTask(og.executor, None)
task.feature_set = ok_test.feature_set
task.after_init(executor=ok_test.task_executor, scene=ok_test.task_executor.scene)

# ---- 设置测试图片 ----
IMAGE = "tests\img\events/battlefinish.png"
ok_test.device_manager.capture_method.set_images([IMAGE])
frame = task.next_frame()
h, w = frame.shape[:2]

# ---- 配置：一行定义 特征名 + 搜索区域，代码自动画框+查找 ----
# 修改 box= 参数即可，蓝色区域会自动跟着变
searches = [
    ("Cancel_Old",                   task.box_of_screen(0.65, 0.1, 0.75, 0.20)),
    ("Home_Store",                  task.box_of_screen(0,0,1,1)),
    ("Home_Town",   task.box_of_screen(0,0,1,1)),
    ("Battle_Finish",   task.box_of_screen(0.39,0.67,0.61,0.86)),
]

colors = [(255, 0, 0), (255, 255, 0), (0, 255, 255)]  # 蓝/黄/青 区分各搜索区域

# ---- 画搜索区域 + 查找 + 画结果 ----
for i, (name, region) in enumerate(searches):
    color = colors[i % len(colors)]

    # 画搜索区域
    cv2.rectangle(frame, (region.x, region.y),
                  (region.x + region.width, region.y + region.height), color, 2)
    cv2.putText(frame, f"{name} search", (region.x + 5, region.y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 查找
    box = task.find_one(name, threshold=0.6, box=region)

    # 画结果
    if box:
        print(f"MATCH {name}: conf={box.confidence:.4f} pos=({box.x},{box.y})")
        cv2.rectangle(frame, (box.x, box.y),
                      (box.x + box.width, box.y + box.height), (0, 255, 0), 3)
        cv2.putText(frame, f"{name} {box.confidence:.2f}", (box.x, box.y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        print(f"MISS  {name}")

cv2.imwrite("tests/img/2.png", frame)
print("saved to tests/img/2.png")

destroy_ok()
