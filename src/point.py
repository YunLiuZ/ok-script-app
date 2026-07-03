"""
图片坐标拾取工具

用法:
    python point.py <图片路径>

操作:
    - 鼠标左键点击：标记"点"，输出该点坐标及相对于 2560×1440 的比例
    - 按住左键拖拽/点击两个点：标记"矩形区域"，输出 (x1, y1, x2, y2) 及相对坐标

快捷键:
    q / ESC — 退出
    c       — 清除所有标记
    s       — 保存带标记的截图
"""

import sys
import cv2
import os

BASE_WIDTH = 2560
BASE_HEIGHT = 1440

clicked_points = []
current_rect = None  # (x1, y1) 起点（拖拽中）
temp_point = None    # 鼠标当前位置


def to_relative(x, y):
    """转换为相对坐标 (x/2560, y/1440)"""
    return round(x / BASE_WIDTH, 2), round(y / BASE_HEIGHT, 2)


def format_output():
    """根据已标记的点输出格式化结果"""
    if not clicked_points:
        return
    pts = clicked_points[:]
    if len(pts) == 1:
        x, y = pts[0]
        rx, ry = to_relative(x, y)
        print(f"\n>>> 点: ({x}, {y})  |  相对: ({rx}, {ry})")
    elif len(pts) >= 2:
        # 取最后两个点组成矩形
        x1, y1 = pts[-2]
        x2, y2 = pts[-1]
        # 确保 x1<=x2, y1<=y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        rx1, ry1 = to_relative(x1, y1)
        rx2, ry2 = to_relative(x2, y2)
        print(f"\n>>> 矩形: ({x1}, {y1}, {x2}, {y2})")
        print(f"    相对: ({rx1}, {ry1}, {rx2}, {ry2})")
        print(f"    宽×高: {x2 - x1} × {y2 - y1}")


def draw_overlay(img, scale):
    """在图像副本上绘制标记"""
    overlay = img.copy()

    # 绘制已确认的点
    for i, pt in enumerate(clicked_points):
        sx, sy = int(pt[0] * scale), int(pt[1] * scale)
        cv2.circle(overlay, (sx, sy), 5, (0, 255, 0), -1)
        cv2.putText(overlay, f"P{i + 1}({pt[0]},{pt[1]})", (sx + 8, sy - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # 绘制矩形（成对的点）
    for i in range(0, len(clicked_points) - 1, 2):
        p1 = clicked_points[i]
        p2 = clicked_points[i + 1]
        sx1, sy1 = int(p1[0] * scale), int(p1[1] * scale)
        sx2, sy2 = int(p2[0] * scale), int(p2[1] * scale)
        cv2.rectangle(overlay, (sx1, sy1), (sx2, sy2), (255, 0, 0), 2)

    # 绘制拖拽中的临时矩形
    if current_rect is not None and temp_point is not None:
        sx1, sy1 = int(current_rect[0] * scale), int(current_rect[1] * scale)
        sx2, sy2 = int(temp_point[0] * scale), int(temp_point[1] * scale)
        cv2.rectangle(overlay, (sx1, sy1), (sx2, sy2), (0, 165, 255), 1)

    # 底栏信息
    h, w = overlay.shape[:2]
    cv2.rectangle(overlay, (0, h - 30), (w, h), (30, 30, 30), -1)
    cv2.putText(overlay, "LeftClick: point | Drag: rect | C: clear | S: save | Q/ESC: quit",
                (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    return overlay


def mouse_callback(event, x, y, flags, param):
    global clicked_points, current_rect, temp_point
    img, scale = param['img'], param['scale']

    # 原始坐标
    ox, oy = round(x / scale), round(y / scale)

    if event == cv2.EVENT_LBUTTONDOWN:
        current_rect = (ox, oy)
        temp_point = (ox, oy)

    elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
        if current_rect is not None:
            temp_point = (ox, oy)

    elif event == cv2.EVENT_LBUTTONUP:
        if current_rect is None:
            return
        ox2, oy2 = ox, oy
        ox1, oy1 = current_rect

        # 判断是点击（移动距离很小）还是拖拽（形成矩形）
        dist = ((ox2 - ox1) ** 2 + (oy2 - oy1) ** 2) ** 0.5
        if dist < 5:
            # 点击：只记录一个点
            clicked_points.append((ox, oy))
            print(f"点: ({ox:>4}, {oy:>4})  |  相对: {to_relative(ox, oy)}")
        else:
            # 矩形：记录两个点
            clicked_points.append((ox1, oy1))
            clicked_points.append((ox2, oy2))
            # 确保顺序
            x1, x2 = (ox1, ox2) if ox1 <= ox2 else (ox2, ox1)
            y1, y2 = (oy1, oy2) if oy1 <= oy2 else (oy2, oy1)
            rx1, ry1 = to_relative(x1, y1)
            rx2, ry2 = to_relative(x2, y2)
            print(f"矩形: ({x1:>4}, {y1:>4}, {x2:>4}, {y2:>4})  |  相对: ({rx1}, {ry1}, {rx2}, {ry2})")

        current_rect = None
        temp_point = None


def main():
    if len(sys.argv) < 2:
        print("用法: python point.py <图片路径>")
        sys.exit(1)

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"文件不存在: {img_path}")
        sys.exit(1)

    img = cv2.imread(img_path)
    if img is None:
        print(f"无法读取图片: {img_path}")
        sys.exit(1)

    # 缩放图片，适应屏幕（高不超过 900）
    h, w = img.shape[:2]
    scale = min(1.0, 900 / h)
    display_w, display_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (display_w, display_h))

    window_name = f"Coordinate Picker — {os.path.basename(img_path)}  [{w}×{h}]  scale={scale:.2f}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, display_w, display_h)
    cv2.setMouseCallback(window_name, mouse_callback,
                         param={'img': img, 'scale': scale})

    print("=" * 60)
    print(f"图片: {img_path}  ({w} × {h})")
    print(f"基准分辨率: {BASE_WIDTH} × {BASE_HEIGHT}")
    print("操作: 单击=标记点 | 拖拽=矩形区域 | C=清除 | S=保存截图 | Q/ESC=退出")
    print("=" * 60)

    while True:
        display = draw_overlay(img_resized, scale)
        cv2.imshow(window_name, display)
        key = cv2.waitKey(50) & 0xFF

        if key == ord('q') or key == 27:  # q 或 ESC
            break
        elif key == ord('c'):
            clicked_points.clear()
            current_rect = None
            temp_point = None
            print("--- 已清除所有标记 ---")
        elif key == ord('s'):
            save_path = os.path.splitext(img_path)[0] + "_marked.png"
            cv2.imwrite(save_path, draw_overlay(img_resized, scale))
            print(f"已保存截图: {save_path}")

    cv2.destroyAllWindows()

    # 最终汇总输出
    if clicked_points:
        print("\n" + "=" * 60)
        print(f"最终汇总 ({len(clicked_points)} 个点):")
        for i, (x, y) in enumerate(clicked_points, 1):
            rx, ry = to_relative(x, y)
            print(f"  P{i}: ({x:>4}, {y:>4})  ->  ({rx}, {ry})")
        # 矩形汇总
        rects = []
        for i in range(0, len(clicked_points) - 1, 2):
            x1, y1 = clicked_points[i]
            x2, y2 = clicked_points[i + 1]
            if x1 > x2: x1, x2 = x2, x1
            if y1 > y2: y1, y2 = y2, y1
            rx1, ry1 = to_relative(x1, y1)
            rx2, ry2 = to_relative(x2, y2)
            rects.append((x1, y1, x2, y2, rx1, ry1, rx2, ry2))
        if rects:
            print(f"\n矩形汇总 ({len(rects)} 个):")
            for i, r in enumerate(rects, 1):
                print(f"  R{i}: ({r[0]}, {r[1]}, {r[2]}, {r[3]})  ->  ({r[4]}, {r[5]}, {r[6]}, {r[7]})")


if __name__ == "__main__":
    main()
