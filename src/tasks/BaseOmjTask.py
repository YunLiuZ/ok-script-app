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
        self.rows = {1: 0.09, 2: 0.18, 3: 0.27, 4: 0.35, 5: 0.42, 6: 0.53, 7: 0.62,8: 0.71, 9: 0.80, 10: 0.88}#0.89


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
#region Home
    def in_home_and_back(self):
        if self.In_Home():
            self.log_info("在主页")
        else:
            self.log_info("不在主页")
            self.Back_Home()
        return True

    def In_Home(self):
        self.log_info("寻找町中")
        town = self.find_feature('Home_Town', threshold=0.8, box=self.B('Home_Town'))
        if town:
            self.log_info("町中")
            return True
        else:
            self.log_info("不寻找町中")
        store = self.find_feature('Home_Store', threshold=0.8, box=self.B('Home_Store'))
        self.log_info("寻找商店")
        if store:
            self.log_info("寻找到了商店")
            self.reset()
            if self.wait_feature('Home_Town', threshold=0.8, box=self.B('Home_Town'),time_out=3):
                return True
        else:return False
    def Back_Home(self):
        """快速路径：Home_Button → Back → Home_Button。"""
        self.log_info('进入backhome')
        if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
            self.click(btns[0], after_sleep=2)
            self.log_info('点击 Home_Button')
            if self.In_Home():
                return True
        self.sleep(0.3)
        if btns := self.find_feature('Back', box=self.B('Back'), threshold=0.8):
            self.click(btns[0], after_sleep=0.5)
            self.log_info('点击 Back')
            if self.In_Home():
                return True
        self.sleep(0.3)
        if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
            self.click(btns[0], after_sleep=2)
            self.log_info('点击 Home_Button')
            if self.In_Home():
                return True
        return self.Back_Home_loop()

    def Back_Home_loop(self):
        """顽固路径：循环消弹窗直到回到主页。"""
        self.log_info('进入backhome循环')

        cancel_box = self.box_of_screen(0.5, 0, 1, 0.5)

        def try_back():
            if btns := self.find_feature('Daily_New_Cancel',
                                          box=cancel_box, threshold=0.8):
                self.click(btns[0], after_sleep=0.2)
                self.log_info('关闭弹窗')
                return
            if btns := self.find_feature( 'Cancel_Old',
                                          box=cancel_box, threshold=0.8):
                self.click(btns[0], after_sleep=0.2)
                self.log_info('关闭弹窗')
                return
            if btns := self.find_feature('Back', box=self.B('Back'), threshold=0.8):
                self.click(btns[0], after_sleep=0.5)
                self.log_info('点击 Back')
                return
            if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
                self.click(btns[0], after_sleep=0.3)
                self.log_info('点击 Home_Button')

        return self.wait_until(
            self.In_Home,
            time_out=30,
            post_action=try_back,
            raise_if_not_found=False,
        )

    def reset(self):
        """从阴阳寮返回主页。"""
        self.log_info("寻从阴阳寮返回主页")
        if not self.wait_click_feature('YinYang_Lodge', threshold=0.7,
                                        box=self.B('YinYang_Lodge'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到YinYang_Lodge")
        self.info_set("步骤", "进入YinYang_Lodge")
        self.wait_click_feature('Home_Button', threshold=0.8, box=self.B('Home_Button'),
                                after_sleep=2,time_out=5,raise_if_not_found=False)

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
#endregion     
    
    
    def ocr_and_click(self, match, sleep: float = 0.5,time_out :float =3, box=None, random_click: bool = False,raise_if_not_found=False) -> bool:
        """OCR 指定区域按优先级模糊匹配文字并点击。返回 True/False。
        match: str 或 list[str]，内部自动转正则（包含即匹配）。
        random_click=True 时在识别区域内随机选点点击。
        """
        import re, random
        if isinstance(match, str):
            match = [match]
        for m in match:
            results = self.wait_ocr(match=re.compile(m), box=box, threshold=0.7,time_out=time_out,raise_if_not_found=raise_if_not_found)
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
    