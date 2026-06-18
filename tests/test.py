"""
模板匹配测试工具
对 tests/img/ 下的测试图片运行所有相关模板的匹配，可视化结果。

用法：
    python tests/test.py
    python tests/test.py --image tests/img/your_screenshot.png
    python tests/test.py --threshold 0.7
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np


# ========== 配置 ==========

COCO_JSON = "assets/coco_annotations.json"
DEFAULT_TEST_IMAGE = "tests/img/ADB command line Capture_2560x1440_1781683447325.9812_original.png"
DEFAULT_THRESHOLD = 0.6

# BaseOmjTask & DailyTask 中使用的所有模板名
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


def load_coco(coco_path: str) -> tuple[dict, dict]:
    """加载 COCO 标注，返回 (cat_id->name, img_id->file_name)。"""
    with open(coco_path, "r", encoding="utf-8") as f:
        coco = json.load(f)
    cat_id_to_name = {c["id"]: c["name"] for c in coco["categories"]}
    img_id_to_file = {i["id"]: i["file_name"] for i in coco["images"]}
    return cat_id_to_name, img_id_to_file, coco


def get_template(coco: dict, feature_name: str) -> tuple[np.ndarray, tuple[int, int, int, int]] | None:
    """
    根据特征名从 COCO 标注中裁剪模板。
    返回 (template_image, (bbox_x, bbox_y, bbox_w, bbox_h)) 或 None。
    """
    cat = next((c for c in coco["categories"] if c["name"] == feature_name), None)
    if cat is None:
        return None

    ann = next((a for a in coco["annotations"] if a["category_id"] == cat["id"]), None)
    if ann is None:
        return None

    img_id = ann["image_id"]
    img_entry = next((i for i in coco["images"] if i["id"] == img_id), None)
    if img_entry is None:
        return None

    src_file = os.path.join("assets", img_entry["file_name"])
    x, y, w, h = ann["bbox"]

    src_img = cv2.imread(src_file)
    if src_img is None:
        return None

    template = src_img[y : y + h, x : x + w]
    return template, (x, y, w, h)


def match_template(
    test_img: np.ndarray,
    template: np.ndarray,
    threshold: float,
) -> dict:
    """
    在 test_img 上运行 cv2.matchTemplate，返回匹配结果字典。
    """
    result = cv2.matchTemplate(test_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    best_x, best_y = max_loc
    _, _, w, h = template.shape[1], template.shape[0], template.shape[1], template.shape[0]

    return {
        "score": max_val,
        "matched": max_val >= threshold,
        "x": best_x,
        "y": best_y,
        "center_x": best_x + w // 2,
        "center_y": best_y + h // 2,
        "w": w,
        "h": h,
    }


def draw_result(img: np.ndarray, fname: str, res: dict, threshold: float):
    """在图片上绘制匹配框和标签。"""
    x, y, w, h = res["x"], res["y"], res["w"], res["h"]
    score = res["score"]

    if res["matched"]:
        color = (0, 255, 0)  # 绿色 = 匹配成功
        label = f"{fname} {score:.2f}"
    else:
        color = (0, 0, 255)  # 红色 = 未达标
        label = f"{fname} {score:.2f} (<{threshold})"

    cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
    cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main():
    parser = argparse.ArgumentParser(description="模板匹配测试工具")
    parser.add_argument("--image", default=DEFAULT_TEST_IMAGE, help="测试图片路径")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="匹配阈值 (默认 0.6)")
    parser.add_argument(
        "--features", nargs="*", default=FEATURE_NAMES, help="要测试的模板名列表"
    )
    args = parser.parse_args()

    # 加载 COCO
    cat_id_to_name, img_id_to_file, coco = load_coco(COCO_JSON)

    # 加载测试图
    test_img = cv2.imread(args.image)
    if test_img is None:
        print(f"错误: 无法加载测试图片: {args.image}")
        sys.exit(1)
    test_h, test_w = test_img.shape[:2]
    print(f"测试图片: {args.image}")
    print(f"尺寸: {test_w} x {test_h}")
    print(f"阈值: {args.threshold}")
    print(f"模板数量: {len(args.features)}")
    print()

    result_img = test_img.copy()
    matched_count = 0
    miss_count = 0

    for fname in args.features:
        tp = get_template(coco, fname)
        if tp is None:
            print(f"SKIP  {fname:30s} - 在 COCO 中找不到")
            continue

        template, (bx, by, bw, bh) = tp
        res = match_template(test_img, template, args.threshold)

        if res["matched"]:
            matched_count += 1
            print(
                f"MATCH {fname:30s} "
                f"score={res['score']:.4f}  "
                f"pos=({res['x']:4d},{res['y']:4d})  "
                f"center=({res['center_x']:4d},{res['center_y']:4d})  "
                f"template={res['w']}x{res['h']}"
            )
        else:
            miss_count += 1
            print(
                f"MISS  {fname:30s} "
                f"score={res['score']:.4f}  "
                f"best_at=({res['x']:4d},{res['y']:4d})  "
                f"template={res['w']}x{res['h']}"
            )

        draw_result(result_img, fname, res, args.threshold)

    # 保存
    base, ext = os.path.splitext(args.image)
    output_path = f"{base}_matching_result{ext}"
    cv2.imwrite(output_path, result_img)

    print()
    print(f"匹配成功: {matched_count}  未匹配: {miss_count}")
    print(f"结果已保存: {output_path}")
    print("绿色框 = 匹配成功, 红色框 = 最佳匹配但低于阈值")


if __name__ == "__main__":
    main()
