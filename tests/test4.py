import json, cv2, numpy as np

# ---- 加载模板：从COCO标注裁剪 ----
with open("assets/coco_annotations.json", "r") as f:
    coco = json.load(f)

def get_template(name):
    cat = next(c for c in coco["categories"] if c["name"] == name)
    ann = next(a for a in coco["annotations"] if a["category_id"] == cat["id"])
    img_entry = next(i for i in coco["images"] if i["id"] == ann["image_id"])
    src = cv2.imread(f"assets/{img_entry['file_name']}")
    x, y, w, h = ann["bbox"]
    return src[y:y+h, x:x+w]

# ---- 加载测试图片 ----
frame = cv2.imread("tests/img/home/1.png")
h, w = frame.shape[:2]

# ---- 搜索区域（蓝色：cv2 默认全图搜索） ----
cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (255, 0, 0), 2)
cv2.putText(frame, "cv2 full image search", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

# ---- 核心：cv2 全图匹配 ----
for name in ["Home_Sign", "Home_Store", "Home_Shikigami_Chronicles"]:
    template = get_template(name)
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    _, _, w, h = template.shape[1], template.shape[0], template.shape[1], template.shape[0]

    if max_val >= 0.6:
        print(f"MATCH {name}: conf={max_val:.4f} pos=({max_loc[0]},{max_loc[1]})")
        cv2.rectangle(frame, max_loc, (max_loc[0]+w, max_loc[1]+h), (0, 255, 0), 3)
        cv2.putText(frame, f"{name} {max_val:.2f}", (max_loc[0], max_loc[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        print(f"MISS  {name}: best={max_val:.4f}")

cv2.imwrite("tests/img/3.png", frame)
print("saved to tests/img/3.png")
