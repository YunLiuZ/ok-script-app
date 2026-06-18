"""
使用项目自身的 find_one API 测试模板匹配。

关键区别：
- find_one(name) 默认只在模板标注位置附近搜索（variance=0.002，即 0.2% 屏幕范围）
- find_one(name, box=box_of_screen(0,0,1,1)) 才全图搜索

用法：
    python tests/test2.py
    python tests/test2.py --feature Daily_New_Cancel --threshold 0.6
    python tests/test2.py --feature Home_Button --full  # 全图搜索
"""
import argparse
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from ok.test import init_ok, destroy_ok

config["debug"] = True
config["trigger_tasks"] = []
init_ok(config)

from ok import og
from src.tasks.DailyTask import DailyTask

task = DailyTask(og.executor, None)
from ok.test import ok as ok_test

task.feature_set = ok_test.feature_set
task.after_init(executor=ok_test.task_executor, scene=ok_test.task_executor.scene)


def test_find_one(
    feature_name: str,
    image_path: str,
    threshold: float = 0.6,
    full_search: bool = False,
):
    """用项目的 find_one 在静态图片上测试模板匹配。"""
    ok_test.device_manager.capture_method.set_images([image_path])
    frame = task.next_frame()
    if task.executor.feature_set:
        task.executor.feature_set.check_size(frame)

    h, w = frame.shape[:2]
    print(f"Image: {image_path}")
    print(f"Size: {w} x {h}")
    print(f"Feature: {feature_name}")
    print(f"Threshold: {threshold}")
    print()

    # ---- 获取模板在源图中的标注位置 ----
    fs = task.executor.feature_set
    fs.ensure_feature(feature_name)
    feat = fs.feature_dict.get(feature_name)
    if feat:
        print(f"Template source position: ({feat.x}, {feat.y}), size={feat.width}x{feat.height}")

    # ---- 展示默认搜索区域 ----
    tm_config = config.get("template_matching", {})
    h_var = tm_config.get("default_horizontal_variance", 0.002)
    v_var = tm_config.get("default_vertical_variance", 0.002)

    if feat:
        default_x1 = feat.x - w * h_var
        default_y1 = feat.y - h * v_var
        default_x2 = feat.x + feat.width + w * h_var
        default_y2 = feat.y + feat.height + h * v_var
        print(f"Default search region (variance h={h_var}, v={v_var}):")
        print(f"  x: [{default_x1:.0f}, {default_x2:.0f}]  y: [{default_y1:.0f}, {default_y2:.0f}]")
    print()

    # ===== 方式1：模拟项目实际调用（默认搜索区域） =====
    if not full_search:
        print("--- Mode 1: find_one with DEFAULT search region (as used in task code) ---")
        box = task.find_one(feature_name, threshold=threshold)
    else:
        print("--- Mode 1: find_one with FULL image search ---")
        box = task.find_one(feature_name, threshold=threshold,
                            box=task.box_of_screen(0, 0, 1, 1))

    if box:
        print(f"[MATCH] conf={box.confidence:.4f}  pos=({box.x},{box.y})  size={box.width}x{box.height}")
    else:
        print(f"[MISS] not found with default search region")
        # 用全图搜索来对比
        print()
        print("--- Mode 2: find_one with custom box (0.7, 0, 1, 0.7) ---")
        box_full = task.find_one(feature_name, threshold=threshold,
                                 box=task.box_of_screen(0.7, 0, 1, 0.7))
        if box_full:
            print(f"[MATCH] conf={box_full.confidence:.4f}  pos=({box_full.x},{box_full.y})  size={box_full.width}x{box_full.height}")
            if feat:
                in_region = (default_x1 <= box_full.x <= default_x2 and
                             default_y1 <= box_full.y <= default_y2)
                print(f"In default search region? {'YES' if in_region else 'NO -- match is OUTSIDE default search window!'}")
            box = box_full
        else:
            print(f"[MISS] not found even with full image search")
            # 降到最低看最佳
            box_low = task.find_one(feature_name, threshold=0.0,
                                    box=task.box_of_screen(0.7,0,1,0.7))
            if box_low:
                print(f"Best possible: conf={box_low.confidence:.4f} at ({box_low.x},{box_low.y})")
                box = box_low

    # ===== 可视化 =====
    result_img = frame.copy()

    if box:
        x, y, bw, bh = box.x, box.y, box.width, box.height
        if box.confidence >= threshold:
            color = (0, 255, 0)
            label = f"{feature_name} conf={box.confidence:.2f}"
        else:
            color = (0, 0, 255)
            label = f"{feature_name} best={box.confidence:.2f} (below {threshold})"
        cv2.rectangle(result_img, (x, y), (x + bw, y + bh), color, 3)
        cv2.putText(result_img, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 画出默认搜索区域（蓝色虚线框）
    if feat and not full_search:
        cv2.rectangle(result_img,
                      (int(default_x1), int(default_y1)),
                      (int(default_x2), int(default_y2)),
                      (255, 0, 0), 2)
        cv2.putText(result_img, "default search region",
                    (int(default_x1), int(default_y1) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    base, ext = os.path.splitext(image_path)
    output_path = f"{base}_{feature_name}_result{ext}"
    cv2.imwrite(output_path, result_img)
    print(f"\nResult saved: {output_path}")
    print("Green = matched, Red = below threshold, Blue box = default search region")

    return box


def test_multiple_features(
    feature_names: list[str],
    image_path: str,
    threshold: float = 0.6,
):
    """批量测试，每个模板先用默认区域，匹配不到则全图搜索。"""
    ok_test.device_manager.capture_method.set_images([image_path])
    frame = task.next_frame()
    if task.executor.feature_set:
        task.executor.feature_set.check_size(frame)

    h, w = frame.shape[:2]
    print(f"Image: {image_path}")
    print(f"Size: {w} x {h}")
    print(f"Threshold: {threshold}")
    print()

    result_img = frame.copy()
    matched = 0
    missed = 0
    outside_count = 0

    full_box = task.box_of_screen(0, 0, 1, 1)

    for fname in feature_names:
        # 先用默认搜索区域
        box = task.find_one(fname, threshold=threshold)

        if box:
            matched += 1
            print(f"MATCH  {fname:30s}  conf={box.confidence:.4f}  pos=({box.x:4d},{box.y:4d})")
            color = (0, 255, 0)
            label = f"{fname} {box.confidence:.2f}"
        else:
            # 全图搜索
            box_full = task.find_one(fname, threshold=threshold, box=full_box)
            if box_full:
                missed += 1
                outside_count += 1
                print(f"MISS*  {fname:30s}  conf={box_full.confidence:.4f}  pos=({box_full.x:4d},{box_full.y:4d})  [outside default region!]")
                color = (0, 165, 255)  # orange = found but outside default region
                label = f"{fname} {box_full.confidence:.2f} (outside region)"
                box = box_full
            else:
                # 看最佳
                box_low = task.find_one(fname, threshold=0.0, box=full_box)
                if box_low:
                    missed += 1
                    print(f"MISS   {fname:30s}  best_conf={box_low.confidence:.4f}  best_at=({box_low.x:4d},{box_low.y:4d})")
                    color = (0, 0, 255)
                    label = f"{fname} {box_low.confidence:.2f} (<{threshold})"
                    box = box_low
                else:
                    missed += 1
                    print(f"MISS   {fname:30s}  no match at all")
                    continue

        cv2.rectangle(result_img, (box.x, box.y),
                      (box.x + box.width, box.y + box.height), color, 3)
        cv2.putText(result_img, label, (box.x, box.y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    base, ext = os.path.splitext(image_path)
    output_path = f"{base}_multi_result{ext}"
    cv2.imwrite(output_path, result_img)

    print(f"\nMatched (in default region): {matched}")
    print(f"Missed (outside or below threshold): {missed}")
    print(f"  - outside default search region: {outside_count}")
    print(f"Result saved: {output_path}")


FEATURE_NAMES = [
    "Home_Button",
    "Home_Town",
    "Home_Store",
    "Home_Sign",
    "Back",
    "Cancel_Old",
    "Daily_New_Cancel",
    "Sign_Button",
    "Sign_Daily_Skip",
    "Daily_Sign_Success",
    "Gift_Store",
    "Gift_Daily",
    "Gift_Daily_Finish",
    "Gift_Finish",
]

DEFAULT_IMAGE = "tests/img/ADB command line Capture_2560x1440_1781683447325.9812_original.png"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="template matching test with find_one")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="test image path")
    parser.add_argument("--feature", default=None, help="single feature name")
    parser.add_argument("--threshold", type=float, default=0.6, help="match threshold")
    parser.add_argument("--full", action="store_true", help="use full image search")
    args = parser.parse_args()

    try:
        if args.feature:
            test_find_one(args.feature, args.image, args.threshold, args.full)
        else:
            test_multiple_features(FEATURE_NAMES, args.image, args.threshold)
    finally:
        destroy_ok()
