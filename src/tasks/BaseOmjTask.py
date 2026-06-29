import math
import re
import time
from datetime import datetime, timedelta
from typing import List

import numpy as np

from ok import BaseTask, Logger, og, CannotFindException

class BaseOmjTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # ---- 自动代理：self.xxx → og.my_app.xxx ----
    _GLOBAL_ATTRS = {"logged_in", "state"}

    def __getattr__(self, name):
        if name in self._GLOBAL_ATTRS:
            return getattr(og.my_app, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self._GLOBAL_ATTRS:
            setattr(og.my_app, name, value)
        else:
            super().__setattr__(name, value)

    def in_home_and_back(self):
        if not self.In_Home():
            self.Back_Home()
        
    def In_Home(self):
        town = self.find_one('Home_Town', threshold=0.8, box=self.B('Home_Town'))
        if town:
            return True
        store = self.find_one('Home_Store', threshold=0.8, box=self.B('Home_Store'))
        if store:
            return True
        ocr1 = self.ocr_and_click(['町','中'],box=self.B('Home_Town'))
        if ocr1:
            return True
        return False

    def reset(self):
        """从商店返回主页。"""
        self.log_info("只找到 Home_Store，尝试返回主页")
        self.wait_click_feature('Home_Button', threshold=0.8, box=self.B('Home_Button'))
    def reset_home(self):
        if not self.ocr_and_click(['町','中'],box=self.B('Home_Town')):
            self.ocr_and_click(['町'],box=self.box_of_screen(0.2,0.3,0.8,0.8))
        self.click_relative(0.82,0.36)

    def in_store(self):
        self.log_info('进入判断')
        if self.find_one(
            ['Gift_Store','Grocery_Store'],
            threshold=0.8,box=self.box_of_screen(0, 0.8, 1, 1)
        ):
            self.log_info('in store')
            self.sleep(1)
            return True
        return False
       
    def findone_and_click(self):
        pass
    def ocr_and_click(self, match, sleep: float = 0.5,time_out :float =3, box=None, random_click: bool = False) -> bool:
        """OCR 指定区域按优先级模糊匹配文字并点击。返回 True/False。
        match: str 或 list[str]，内部自动转正则（包含即匹配）。
        random_click=True 时在识别区域内随机选点点击。
        """
        import re, random
        if isinstance(match, str):
            match = [match]
        for m in match:
            results = self.wait_ocr(match=re.compile(m), box=box, threshold=0.7,time_out=time_out)
            if results:
                r = results[0]
                if random_click:
                    h = self.frame.shape[0] if hasattr(self, 'frame') else 1440
                    w = self.frame.shape[1] if hasattr(self, 'frame') else 2560
                    rx = random.randint(r.x, r.x + r.width)
                    ry = random.randint(r.y, r.y + r.height)
                    self.click_relative(rx / w, ry / h, after_sleep=sleep)
                else:
                    self.click_box(r, after_sleep=sleep)
                self.log_info(f"OCR '{m}' -> '{r.name}' 并点击")
                return True
        return False
    def Find_And_Click_Home(self, text: str) -> bool:
        """OCR 底部区域 (0, 0.8 ~ 1, 1)，匹配到 text 则点击。"""
        results = self.ocr(0, 0.8, 1, 1, match=text)
        if results:
            self.click_box(results[0], after_sleep=0.5)
            self.log_info(f"OCR 识别到 '{results[0].name}' 并点击")
            self.log_warning(f"OCR 识别到 '{results[0].name}' 并点击")
            self.sleep(2)
            return True
        return False

    def B(self, name: str):
        """快捷获取特征搜索 Box：self.B('Home_Sign') → Box 对象。"""
        from src.feature_boxes import BOX
        coords = BOX.get(name, BOX["full"])
        return self.box_of_screen(*coords)

    def click_nth(self, axis: str, fixed: float, pos_map: dict, n: int, label: str = ""):
        """点击列表中第 n 项。
        axis='x': X 固定，Y 从 pos_map 查（纵向列表）
        axis='y': Y 固定，X 从 pos_map 查（横向列表）
        """
        coord = pos_map.get(n)
        if coord is None:
            self.log_warning(f"第 {n} 个{label} 不在坐标表中")
            return
        x, y = (fixed, coord) if axis == 'x' else (coord, fixed)
        self.click_relative(x, y, after_sleep=1)
        print(x,y)
        self.log_info(f"选择第 {n} 个{label}")
    def _swipe(self,x:float,y:float,to_x:float,to_y:float,duration:float):
        h, w = self.frame.shape[:2]
        self.swipe(
            int(x * w), int(y * h),  # 起点像素
            int(to_x * w), int(to_y * h),  # 终点像素
            duration=duration,
        )
        
        self.log_info('滑动完成')

    def Back_Home(self):
        self.log_info('进入backhome')
        if self.In_Home():
            return True
        def try_back():
            if home_button:= self.find_one(
                'Home_Button',
                box=self.B('Home_Button'),
                threshold=0.8
            ):
                self.click(home_button, after_sleep=1)
                self.log_info('点击Home_Button')
                if self.In_Home():
                    return
            if Back1 := self.find_one('Daily_New_Cancel',box=self.box_of_screen(0.5,0,1,0.5),threshold=0.8):
                self.click(Back1, after_sleep=0.5)
                self.log_info('关闭了某个窗口')
                return
            self.log_info('什么都没点击')
            if Back2 := self.find_one('Cancel_Old',box=self.box_of_screen(0.5,0,1,0.5),threshold=0.8):
                self.click(Back2, after_sleep=0.5)
                self.log_info('关闭了某个窗口')
                return
            self.log_info('什么都没点击')

            if back_button:= self.find_one(
                'Back',
                box=self.B('Back'),
                threshold=0.8
            ):
                self.click(back_button, after_sleep=3)
                self.log_info('点击Back')
                if self.In_Home():
                    return
        return self.wait_until(
            self.In_Home,
            time_out=30,
            post_action=try_back,
            raise_if_not_found=False
        )
    
    