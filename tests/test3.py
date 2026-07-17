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
IMAGE = "tests\img/2.png"
ok_test.device_manager.capture_method.set_images([IMAGE])
frame = task.next_frame()
h, w = frame.shape[:2]

# ---- 配置：一行定义 特征名 + 搜索区域，代码自动画框+查找 ----
# 修改 box= 参数即可，蓝色区域会自动跟着变
searches = [
    ("Cancel_Old",  task.box_of_screen(0.85, 0.08, 0.99, 0.25)),
    ("Back",  task.box_of_screen(0,0,0.2,0.2)),
    ("Exploration_RealmRaid",  task.box_of_screen(0,0.8,1,1)),
    ("Exploration_GoryouRealm",  task.box_of_screen(0,0.8,1,1)),
    
    # ("Areaboss_Not_Lock",   task.box_of_screen(0.86,0.88,1,1)),
    # ("Areaboss_Lock",   task.box_of_screen(0.86,0.88,1,1)),
    # ("RealmRaid_Not_Lock",   task.box_of_screen(0.86,0.88,1,1)),
    # ("RealmRaid_Lock",   task.box_of_screen(0.86,0.88,1,1)),
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

    # 查找（返回所有匹配的 Box 列表）
    boxes = task.find_feature(name, threshold=0.8, box=region)

    # 画结果
    if boxes:
        for b in boxes:
            print(f"MATCH {name}: conf={b.confidence:.4f} pos=({b.x},{b.y})")
            cv2.rectangle(frame, (b.x, b.y),
                          (b.x + b.width, b.y + b.height), (0, 255, 0), 3)
            cv2.putText(frame, f"{name} {b.confidence:.2f}", (b.x, b.y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        print(f"MISS  {name}")

cv2.imwrite("tests/img/i.png", frame)
print("saved to tests/img/2.png")

destroy_ok()
