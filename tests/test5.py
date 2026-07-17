import os, sys, cv2, re
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
IMAGE = "tests\img/5.png"
ok_test.device_manager.capture_method.set_images([IMAGE])
frame = task.next_frame()
h, w = frame.shape[:2]

# ---- 配置：一行定义 识别区域 + 匹配文本，代码自动画框+OCR ----
# 改 x,y,to_x,to_y 或 match 即可，区域框会自动跟着变
ocr_configs = [
    # (OCR区域 x,y,to_x,to_y,  匹配文本/正则,  框颜色)
    (0.11, 0.18, 0.29, 0.87,           None,            (255, 0, 0)),
    # (0.93, 0.1, 0.99, 0.91 ,None,(255, 0, 0)),
    # (0.41, 0.78, 0.58, 0.88, None, (255, 0, 0)),

]

for x, y, to_x, to_y, match, color in ocr_configs:
    region = task.box_of_screen(x, y, to_x, to_y)

    # 画搜索区域
    cv2.rectangle(frame, (region.x, region.y),
                  (region.x + region.width, region.y + region.height), color, 2)
    label = f"OCR [{x},{y} ~ {to_x},{to_y}]"
    cv2.putText(frame, label, (region.x + 5, region.y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 执行 OCR
    results = task.ocr(x=x, y=y, to_x=to_x, to_y=to_y, match=match, frame=frame, log=True)

    print(f"OCR region [{x},{y} ~ {to_x},{to_y}] match={match}: found {len(results)} results")
    for r in results:
        cx, cy = r.x + r.width // 2, r.y + r.height // 2
        print(f"  -> text='{r.name}' conf={r.confidence:.3f} xy=({r.x},{r.y}) wh=({r.width},{r.height}) center=({cx},{cy})")
        cv2.rectangle(frame, (r.x, r.y), (r.x + r.width, r.y + r.height), (0, 255, 0), 2)
        cv2.putText(frame, f"'{r.name}' {r.confidence:.2f}", (r.x, r.y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

cv2.imwrite("tests/img/test5.png", frame)
print("\nsaved to tests/img/5.png")

destroy_ok()
